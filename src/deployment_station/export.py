"""Reproducible STEP/STL/assembly/render export pipeline."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import cadquery as cq
import trimesh

from .assembly import build_assembly, exploded_assembly, packaging_assembly, printable_parts
from .components import component_envelope_compound
from .coupons import fit_coupons
from .geometry import bbox_dimensions, placed_solids_on_bed
from .parameters import DEFAULT, StationParameters
from .render import render_all
from .validation import CheckResult, geometry_checks, mesh_checks, write_results


ROOT = Path(__file__).resolve().parents[2]
STL_BED_TOLERANCE_MM = 1e-4
PRINT_COMPONENT_GAP_MM = 5.0


class ExportValidationError(RuntimeError):
    """Raised after artifacts/reports are written when validation has failed."""


def _require_validation_pass(results: list[CheckResult]) -> None:
    failures = [result for result in results if result.status == "FAIL"]
    if failures:
        summary = "; ".join(f"{result.name}: {result.detail}" for result in failures)
        raise ExportValidationError(f"{len(failures)} validation failure(s): {summary}")


def _ground_and_pack_print_solids(obj: cq.Workplane) -> cq.Workplane:
    """Ground disconnected bodies separately and lay them out without overlap."""

    solids = obj.solids().vals()
    if not solids:
        raise ValueError("cannot orient an object with no printable solids")
    if len(solids) == 1:
        return placed_solids_on_bed(obj)

    packed: list[cq.Shape] = []
    cursor_x = 0.0
    for solid in solids:
        bounds = solid.BoundingBox()
        packed.append(
            solid.translate(
                cq.Vector(
                    cursor_x - bounds.xmin,
                    -(bounds.ymin + bounds.ymax) / 2.0,
                    -bounds.zmin,
                )
            )
        )
        cursor_x += bounds.xlen + PRINT_COMPONENT_GAP_MM

    result = cq.Workplane(obj=cq.Compound.makeCompound(packed))
    bounds = result.val().BoundingBox()
    return result.translate((-(bounds.xmin + bounds.xmax) / 2.0, 0.0, 0.0))


def _print_oriented(name: str, obj: cq.Workplane) -> cq.Workplane:
    if name == "base":
        # Put the broad upper skin on the plate; assembly orientation would
        # suspend it 5 mm above the bed on four small feet.
        obj = obj.rotate((0, 0, 0), (1, 0, 0), 180.0)
    elif name in {"rear_panel", "router_interface_bezel", "coupon_c8_cutout", "coupon_rear_panel_fit", "coupon_router_rf_access"}:
        obj = obj.rotate((0, 0, 0), (1, 0, 0), 90.0)
    elif name in {"logo_panel_left", "wifi_dock_left"}:
        obj = obj.rotate((0, 0, 0), (0, 1, 0), -90.0)
    elif name in {"logo_panel_right", "logo_panel_blank_template", "wifi_dock_right", "coupon_wifi_dock"}:
        obj = obj.rotate((0, 0, 0), (0, 1, 0), 90.0)
    elif name == "logo_panel_example_embossed":
        # Edge-print the raised-face template.  Either face-down orientation
        # would rest on the emboss or inward hooks and suspend the 70 mm face.
        pass
    elif name == "removable_handle":
        obj = obj.rotate((0, 0, 0), (1, 0, 0), 90.0)
    return _ground_and_pack_print_solids(obj)


def _split_mesh_components(mesh: trimesh.Trimesh) -> list[trimesh.Trimesh]:
    """Split face-edge components without optional SciPy/networkx dependencies."""

    face_count = len(mesh.faces)
    if face_count == 0:
        return []
    parents = list(range(face_count))

    def find(face: int) -> int:
        while parents[face] != face:
            parents[face] = parents[parents[face]]
            face = parents[face]
        return face

    for first, second in mesh.face_adjacency:
        first_root = find(int(first))
        second_root = find(int(second))
        if first_root != second_root:
            parents[second_root] = first_root

    groups: dict[int, list[int]] = {}
    for face in range(face_count):
        groups.setdefault(find(face), []).append(face)
    return [mesh.submesh([faces], append=True, repair=False) for faces in groups.values()]


def _stl_component_check(path: Path) -> CheckResult:
    """Check every connected STL body independently for integrity and Z=0 contact."""

    loaded = trimesh.load(path, force="mesh")
    if not isinstance(loaded, trimesh.Trimesh) or loaded.is_empty:
        return CheckResult(
            f"grounded STL components: {path.name}",
            "FAIL",
            "STL did not reopen as a non-empty triangle mesh",
        )

    # The custom splitter retains every face group, including broken ones, so a
    # non-watertight component cannot disappear and let the export pass.
    components = _split_mesh_components(loaded)
    z_mins = [float(component.bounds[0, 2]) for component in components]
    floating = [index for index, z_min in enumerate(z_mins) if abs(z_min) > STL_BED_TOLERANCE_MM]
    non_watertight = [index for index, component in enumerate(components) if not component.is_watertight]
    inconsistent_winding = [
        index for index, component in enumerate(components) if not component.is_winding_consistent
    ]
    passed = bool(components) and not floating and not non_watertight and not inconsistent_winding
    minima_detail = ", ".join(f"{z_min:.5f}" for z_min in z_mins) or "none"
    return CheckResult(
        f"grounded STL components: {path.name}",
        "PASS" if passed else "FAIL",
        (
            f"{len(components)} independently grounded watertight component(s); "
            f"Z minima [{minima_detail}] mm"
            if passed
            else f"component Z minima [{minima_detail}] mm; floating={floating}, "
            f"non_watertight={non_watertight}, inconsistent_winding={inconsistent_winding}"
        ),
    )


def _stl_component_checks(stl_dir: Path) -> list[CheckResult]:
    paths = sorted(stl_dir.glob("*.stl"))
    if not paths:
        return [CheckResult("grounded STL component validation", "WARN", "No STL files found")]
    return [_stl_component_check(path) for path in paths]


def _export_shape(
    obj: cq.Workplane,
    step_path: Path,
    stl_path: Path,
    name: str,
    p: StationParameters = DEFAULT,
) -> None:
    step_path.parent.mkdir(parents=True, exist_ok=True)
    stl_path.parent.mkdir(parents=True, exist_ok=True)
    cq.exporters.export(obj, str(step_path), exportType="STEP")
    reopened = cq.importers.importStep(str(step_path))
    if not reopened.val().isValid():
        raise RuntimeError(f"reopened STEP is invalid: {step_path}")
    oriented = _print_oriented(name, obj)
    print_dims = bbox_dimensions(oriented)
    build_dims = (p.printer.build_x, p.printer.build_y, p.printer.build_z)
    if any(size > limit + 1e-6 for size, limit in zip(print_dims, build_dims)):
        raise ExportValidationError(
            f"print orientation for {name} is {print_dims}, outside build volume {build_dims}"
        )
    cq.exporters.export(oriented, str(stl_path), exportType="STL", tolerance=0.08, angularTolerance=0.12)


def _record(path: Path, kind: str, name: str) -> dict[str, object]:
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    return {"name": name, "kind": kind, "path": str(path.relative_to(ROOT)), "bytes": path.stat().st_size, "sha256": digest}


def export_all(p: StationParameters = DEFAULT) -> list[dict[str, object]]:
    step_dir = ROOT / "exports" / "step"
    stl_dir = ROOT / "exports" / "stl"
    render_dir = ROOT / "renders"
    report_dir = ROOT / "reports"
    for directory in (step_dir, stl_dir, render_dir, report_dir):
        directory.mkdir(parents=True, exist_ok=True)

    manifest: list[dict[str, object]] = []
    for name, obj in printable_parts(p).items():
        step = step_dir / f"{name}.step"
        stl = stl_dir / f"{name}.stl"
        _export_shape(obj, step, stl, name, p)
        entry = _record(step, "printable STEP", name)
        entry["design_bbox_mm"] = [round(value, 4) for value in bbox_dimensions(obj)]
        manifest.append(entry)
        manifest.append(_record(stl, "print-oriented STL", name))

    for name, obj in fit_coupons(p).items():
        step = step_dir / f"{name}.step"
        stl = stl_dir / f"{name}.stl"
        _export_shape(obj, step, stl, name, p)
        manifest.append(_record(step, "coupon STEP", name))
        manifest.append(_record(stl, "coupon STL", name))

    assembly_paths = {
        "complete_assembly": (build_assembly(p), step_dir / "complete_assembly.step"),
        "exploded_assembly": (exploded_assembly(p), step_dir / "exploded_assembly.step"),
        "packaging_study": (packaging_assembly(p), step_dir / "packaging_study.step"),
    }
    for name, (assembly, path) in assembly_paths.items():
        assembly.save(str(path), exportType="STEP", mode="default")
        reopened = cq.importers.importStep(str(path))
        if not reopened.val().isValid():
            raise RuntimeError(f"reopened assembly STEP is invalid: {path}")
        manifest.append(_record(path, "assembly STEP", name))

    component_step = step_dir / "component_envelopes.step"
    cq.exporters.export(component_envelope_compound(p), str(component_step), exportType="STEP")
    if not cq.importers.importStep(str(component_step)).val().isValid():
        raise RuntimeError("reopened component envelope STEP is invalid")
    manifest.append(_record(component_step, "reference STEP", "component_envelopes"))

    for path in render_all(render_dir, p):
        manifest.append(_record(path, "render PNG", path.stem))

    results = geometry_checks(p) + mesh_checks(stl_dir) + _stl_component_checks(stl_dir)
    write_results(results, report_dir / "validation.json", report_dir / "validation_results.md")
    manifest_path = report_dir / "export_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n")
    _require_validation_pass(results)
    print(f"exported {len(manifest)} artifacts; validation passed")
    return manifest


def main() -> int:
    try:
        export_all(DEFAULT)
    except ExportValidationError as exc:
        print(f"export validation failed: {exc}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
