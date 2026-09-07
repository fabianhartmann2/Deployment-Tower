from pathlib import Path

import cadquery as cq
import pytest
import trimesh

from deployment_station import export as export_module
from deployment_station.assembly import printable_parts
from deployment_station.coupons import fit_coupons
from deployment_station.export import (
    ExportValidationError,
    _export_shape,
    _print_oriented,
    _require_validation_pass,
    _stl_component_check,
)
from deployment_station.parameters import DEFAULT
from deployment_station.rear_panel import c8_cutout_coupon
from deployment_station.validation import CheckResult


def test_step_and_stl_round_trip(tmp_path: Path):
    source = c8_cutout_coupon()
    step = tmp_path / "coupon.step"
    stl = tmp_path / "coupon.stl"
    cq.exporters.export(source, str(step), exportType="STEP")
    cq.exporters.export(source, str(stl), exportType="STL", tolerance=0.08, angularTolerance=0.12)

    reopened = cq.importers.importStep(str(step))
    assert reopened.val().isValid()
    mesh = trimesh.load(stl, force="mesh")
    assert mesh.is_watertight
    assert mesh.is_winding_consistent


def test_export_validation_gate_rejects_failed_geometry():
    _require_validation_pass([CheckResult("clearance", "PASS", "clear")])
    with pytest.raises(ExportValidationError, match="interference"):
        _require_validation_pass([CheckResult("interference", "FAIL", "12.0 mm^3")])


def test_export_cli_returns_nonzero_on_validation_failure(monkeypatch: pytest.MonkeyPatch):
    def fail_export(_parameters):
        raise ExportValidationError("geometry failed")

    monkeypatch.setattr(export_module, "export_all", fail_export)
    assert export_module.main() == 1


def test_export_rejects_actual_print_orientation_outside_build_volume(tmp_path: Path):
    oversized = cq.Workplane("XY").box(DEFAULT.printer.build_x + 1.0, 10.0, 10.0)
    with pytest.raises(ExportValidationError, match="outside build volume"):
        _export_shape(
            oversized,
            tmp_path / "oversized.step",
            tmp_path / "oversized.stl",
            "oversized",
        )


def test_every_print_oriented_solid_and_stl_component_contacts_the_bed(tmp_path: Path):
    """Every CAD solid and connected output-mesh body must independently be grounded."""

    for name, source in {**printable_parts(), **fit_coupons()}.items():
        oriented = _print_oriented(name, source)
        bounds = oriented.val().BoundingBox()
        assert bounds.xlen <= DEFAULT.printer.build_x, (name, bounds.xlen)
        assert bounds.ylen <= DEFAULT.printer.build_y, (name, bounds.ylen)
        assert bounds.zlen <= DEFAULT.printer.build_z, (name, bounds.zlen)
        z_mins = [solid.BoundingBox().zmin for solid in oriented.solids().vals()]
        assert z_mins, name
        assert all(abs(z_min) <= 1e-5 for z_min in z_mins), (name, z_mins)

        stl = tmp_path / f"{name}.stl"
        cq.exporters.export(oriented, str(stl), exportType="STL", tolerance=0.08, angularTolerance=0.12)
        result = _stl_component_check(stl)
        assert result.status == "PASS", f"{name}: {result.detail}"


def test_stl_component_check_rejects_a_lifted_secondary_body(tmp_path: Path):
    grounded = cq.Workplane("XY").box(10.0, 10.0, 2.0).translate((0.0, 0.0, 1.0))
    lifted = cq.Workplane("XY").box(8.0, 8.0, 2.0).translate((16.0, 0.0, 6.0))
    source = cq.Workplane(obj=cq.Compound.makeCompound([grounded.val(), lifted.val()]))
    stl = tmp_path / "lifted_secondary_body.stl"
    cq.exporters.export(source, str(stl), exportType="STL", tolerance=0.08, angularTolerance=0.12)

    result = _stl_component_check(stl)
    assert result.status == "FAIL"
    assert "floating=[1]" in result.detail
    with pytest.raises(ExportValidationError, match="grounded STL components"):
        _require_validation_pass([result])
