"""Automated geometry, packaging, print-volume, and mesh checks."""

from __future__ import annotations

import json
from itertools import combinations
from math import pi, sqrt
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable, Mapping

import cadquery as cq
import trimesh

from .assembly import part_definitions, printable_parts
from .components import ReferenceModel, build_reference_model, mac_intake_exclusion, router_source_kind
from .coupons import fit_coupons
from .geometry import bbox_dimensions, box_at, compound, cylinder_axis
from .handle import cap_fastener_positions, handle_mount_fastener_positions
from .logo_panel import logo_mount_positions
from .mac_mount import (
    mac_cradle_fastener_positions,
    mac_release_rail_datums,
    mac_vertical_retainer_centres,
    mac_vertical_retainer_lead_in,
)
from .layout import packaging_layout
from .parameters import DEFAULT, StationParameters
from .power_compartment import (
    apv_mount_fastener_positions,
    power_cover_boss_height,
    power_cover_fastener_positions,
    power_mount_fastener_positions,
    power_tie_bridge_centres,
)
from .rear_panel import mac_extension_mount_positions, router_extension_mount_positions
from .router_tray import router_support_pad_positions, router_tray_fastener_positions
from .shell import shell_seam_fastener_positions


# OCC boolean operations can leave microscopic numerical residue at nominally
# coincident faces.  Anything larger than this is treated as real material
# overlap unless the pair has a narrowly bounded, intentional interference fit.
INTERSECTION_VOLUME_TOLERANCE_MM3 = 0.10
BOUNDING_BOX_TOLERANCE_MM = 1e-6

# Screw-mounted service parts require no modeled interpenetration.  Keep this
# explicit so a future press/snap fit cannot silently bypass pairwise checking.
ASSEMBLY_INTERFERENCE_ALLOWLIST: dict[frozenset[str], tuple[float, str]] = {}


@dataclass(frozen=True)
class CheckResult:
    name: str
    status: str
    detail: str


def _check(name: str, condition: bool, pass_detail: str, fail_detail: str) -> CheckResult:
    return CheckResult(name, "PASS" if condition else "FAIL", pass_detail if condition else fail_detail)


def _bounding_boxes_overlap(a: cq.Workplane, b: cq.Workplane) -> bool:
    """Return whether two shapes can have a non-trivial volume intersection."""

    a_shape = a.val()
    b_shape = b.val()
    if a_shape is None or b_shape is None or a_shape.Volume() <= 0.0 or b_shape.Volume() <= 0.0:
        return False
    a_box = a_shape.BoundingBox()
    b_box = b_shape.BoundingBox()
    overlaps = (
        min(a_box.xmax, b_box.xmax) - max(a_box.xmin, b_box.xmin),
        min(a_box.ymax, b_box.ymax) - max(a_box.ymin, b_box.ymin),
        min(a_box.zmax, b_box.zmax) - max(a_box.zmin, b_box.zmin),
    )
    return all(overlap > BOUNDING_BOX_TOLERANCE_MM for overlap in overlaps)


def _intersection_volume(a: cq.Workplane, b: cq.Workplane) -> float:
    if not _bounding_boxes_overlap(a, b):
        return 0.0
    try:
        return a.val().intersect(b.val()).Volume()
    except Exception as exc:
        # Treat an indeterminate boolean as an indeterminate validation, never as
        # proof of clearance.  The caller/CLI will therefore fail closed.
        raise RuntimeError("OpenCascade could not evaluate an intersection") from exc


def _annular_axis_witness(
    outer_radius: float,
    inner_radius: float,
    length: float,
    start: tuple[float, float, float],
    direction: tuple[float, float, float],
) -> cq.Workplane:
    """Return a thin annulus used to prove material surrounds a clear axis."""

    if not 0.0 < inner_radius < outer_radius or length <= 0.0:
        raise ValueError("annular witness dimensions must be positive and nested")
    overshoot = 0.1
    inner_start = tuple(start[index] - overshoot * direction[index] for index in range(3))
    outer = cylinder_axis(outer_radius, length, start, direction)
    inner = cylinder_axis(inner_radius, length + 2.0 * overshoot, inner_start, direction)
    return outer.cut(inner)


def _sampled_translation_clearance(
    name: str,
    moving: Mapping[str, cq.Workplane],
    stationary: Mapping[str, cq.Workplane],
    translations: tuple[tuple[float, float, float], ...],
    motion_description: str,
) -> CheckResult:
    """Sample a service translation and fail on any material intersection."""

    if not moving or not stationary or not translations:
        raise ValueError("sampled motion requires moving parts, obstacles, and translations")
    worst_volume = 0.0
    worst_pair = "none"
    worst_translation = translations[0]
    moving_data = {
        item_name: (item, item.val().BoundingBox()) for item_name, item in moving.items()
    }
    stationary_data = {
        item_name: (item.val(), item.val().BoundingBox())
        for item_name, item in stationary.items()
    }
    for translation in translations:
        dx, dy, dz = translation
        for moving_name, (moving_part, moving_box) in moving_data.items():
            translated_bounds = (
                moving_box.xmin + dx,
                moving_box.xmax + dx,
                moving_box.ymin + dy,
                moving_box.ymax + dy,
                moving_box.zmin + dz,
                moving_box.zmax + dz,
            )
            moved = moving_part.translate(translation)
            moved_shape = moved.val()
            for stationary_name, (obstacle_shape, obstacle_box) in stationary_data.items():
                overlaps = (
                    min(translated_bounds[1], obstacle_box.xmax)
                    - max(translated_bounds[0], obstacle_box.xmin),
                    min(translated_bounds[3], obstacle_box.ymax)
                    - max(translated_bounds[2], obstacle_box.ymin),
                    min(translated_bounds[5], obstacle_box.zmax)
                    - max(translated_bounds[4], obstacle_box.zmin),
                )
                if not all(overlap > BOUNDING_BOX_TOLERANCE_MM for overlap in overlaps):
                    continue
                try:
                    volume = moved_shape.intersect(obstacle_shape).Volume()
                except Exception as exc:
                    raise RuntimeError(
                        f"OpenCascade could not evaluate sampled intersection {moving_name}/{stationary_name}"
                    ) from exc
                if volume > worst_volume:
                    worst_volume = volume
                    worst_pair = f"{moving_name}/{stationary_name}"
                    worst_translation = translation
    return _check(
        name,
        worst_volume <= INTERSECTION_VOLUME_TOLERANCE_MM3,
        f"{len(translations)} sampled positions along {motion_description}; maximum obstruction "
        f"{worst_volume:.4f} mm^3",
        f"{worst_pair} intersects by {worst_volume:.3f} mm^3 at translation "
        f"({worst_translation[0]:.1f},{worst_translation[1]:.1f},{worst_translation[2]:.1f}) mm",
    )


def assembly_interference_checks(parts: Mapping[str, cq.Workplane]) -> list[CheckResult]:
    """Check every pair of parts installed in the final assembly.

    Bounding-box-disjoint pairs are still recorded as checked but do not incur an
    OpenCascade boolean.  All other pairs use actual solid intersection volume.
    """

    definitions = part_definitions()
    installed_names = [name for name, definition in definitions.items() if definition.assembly_part]
    missing = [name for name in installed_names if name not in parts]
    if missing:
        raise ValueError(f"missing installed parts for collision validation: {', '.join(missing)}")

    results: list[CheckResult] = []
    for first, second in combinations(installed_names, 2):
        volume = _intersection_volume(parts[first], parts[second])
        pair = frozenset((first, second))
        allowance, rationale = ASSEMBLY_INTERFERENCE_ALLOWLIST.get(
            pair,
            (INTERSECTION_VOLUME_TOLERANCE_MM3, "no intended material overlap"),
        )
        results.append(
            _check(
                f"assembly interference: {first} / {second}",
                volume <= allowance,
                f"intersection {volume:.4f} mm^3 <= {allowance:.2f} mm^3 allowance ({rationale})",
                f"intersection {volume:.3f} mm^3 exceeds {allowance:.2f} mm^3 allowance ({rationale})",
            )
        )
    return results


def _mac_button_swept_path(
    p: StationParameters,
    button: cq.Workplane,
) -> tuple[cq.Workplane, float]:
    """Build a conservative straight one-finger probe from the lower rear."""

    e = p.enclosure
    c = p.components
    button_box = button.val().BoundingBox()
    button_center_x = (button_box.xmin + button_box.xmax) / 2.0
    button_center_y = (button_box.ymin + button_box.ymax) / 2.0

    # The photo-derived button diameter supplies a conservative minimum probe;
    # the configured well must remain wider than it with equipment clearance.
    probe_radius = min(
        c.mac_button_diameter / 2.0,
        p.interfaces.finger_well_width / 2.0 - p.fits.equipment_clearance,
    )
    if probe_radius <= 0.0:
        raise ValueError("configured finger well cannot contain a positive-diameter probe")

    start = (
        button_center_x,
        e.depth / 2.0 + probe_radius + 1.0,
        e.desk_air_gap + probe_radius,
    )
    target = (
        button_center_x,
        button_center_y,
        button_box.zmin - c.mac_button_free_clearance,
    )
    vector = tuple(target[index] - start[index] for index in range(3))
    length = sqrt(sum(component * component for component in vector))
    return cylinder_axis(probe_radius, length, start, vector), 2.0 * probe_radius


def _equipment_mount_checks(
    parts: Mapping[str, cq.Workplane],
    equipment: Mapping[str, cq.Workplane],
) -> list[CheckResult]:
    interfaces = (
        ("mac_mini_m4", "mac_cradle"),
        ("rutm30", "router_tray"),
        ("apv_35_36", "power_compartment"),
        ("apv_35_36", "power_compartment_cover"),
    )
    results: list[CheckResult] = []
    for equipment_name, mount_name in interfaces:
        volume = _intersection_volume(equipment[equipment_name], parts[mount_name])
        results.append(
            _check(
                f"equipment/mount interference: {equipment_name} / {mount_name}",
                volume <= INTERSECTION_VOLUME_TOLERANCE_MM3,
                f"intersection {volume:.4f} mm^3 <= {INTERSECTION_VOLUME_TOLERANCE_MM3:.2f} mm^3 tolerance",
                f"intersection {volume:.3f} mm^3; equipment penetrates its mount/compartment",
            )
        )
    return results


def mac_vertical_retention_check(
    p: StationParameters,
    cradle: cq.Workplane,
    mac: cq.Workplane,
    lower_shell: cq.Workplane | None = None,
) -> CheckResult:
    """Verify clear overhang, lead-ins, and bottom-reachable release rails."""

    c = p.components
    retention = p.mac_retention
    mac_half_width = c.mac_width / 2.0
    mac_top_z = c.mac_support_plane_z + c.mac_retained_body_height
    installed_collision = _intersection_volume(mac, cradle)
    overhang_volumes: list[float] = []
    gap_obstructions: list[float] = []
    cam_obstructions: list[float] = []

    # Each witness lies inside the Mac plan envelope: material in the upper
    # witness is therefore a true Z-retaining overhang, while the lower witness
    # proves the configured insertion/rattle gap remains free of printed ASA.
    for side, _stem_x, clip_y in mac_vertical_retainer_centres(p):
        witness_x = side * (mac_half_width - retention.overhang / 2.0)
        overhang_witness = box_at(
            retention.overhang,
            retention.clip_depth,
            retention.tab_thickness,
            (
                witness_x,
                clip_y,
                mac_top_z + retention.top_gap + retention.tab_thickness / 2.0,
            ),
        )
        gap_witness = box_at(
            retention.overhang,
            retention.clip_depth,
            retention.top_gap,
            (witness_x, clip_y, mac_top_z + retention.top_gap / 2.0),
        )
        overhang_volumes.append(_intersection_volume(overhang_witness, cradle))
        gap_obstructions.append(_intersection_volume(gap_witness, cradle))
        cam_obstructions.append(
            _intersection_volume(mac_vertical_retainer_lead_in(p, side, clip_y), cradle)
        )

    release_volumes: list[float] = []
    release_access_obstructions: list[float] = []
    outer_stem_face = (
        mac_half_width
        + retention.side_clearance
        + retention.stem_thickness
    )
    bridge_depth = max(retention.y_offsets) - min(retention.y_offsets) - retention.clip_depth - 1.0
    release_witness_width = retention.release_rail_outreach - 0.4
    for side, _rail_x, rail_y, _rail_width, _rail_depth, rail_bottom_z in mac_release_rail_datums(p):
        if bridge_depth <= 0.0 or release_witness_width <= 0.0:
            continue
        witness_x = side * (outer_stem_face + retention.release_rail_outreach / 2.0)
        release_witness = box_at(
            release_witness_width,
            bridge_depth,
            retention.release_rail_height,
            (
                witness_x,
                rail_y,
                rail_bottom_z + retention.release_rail_height / 2.0,
            ),
        )
        release_volumes.append(_intersection_volume(release_witness, cradle))

        # With the base removed, this narrow vertical finger/tool approach lies
        # outside the cradle plate and terminates immediately below the rail.
        access_height = rail_bottom_z - p.enclosure.base_height - 0.2
        if access_height <= 0.0:
            release_access_obstructions.append(float("inf"))
            continue
        release_access = box_at(
            min(2.4, release_witness_width),
            min(6.0, bridge_depth),
            access_height,
            (
                witness_x,
                rail_y,
                p.enclosure.base_height + access_height / 2.0,
            ),
        )
        obstruction = _intersection_volume(release_access, cradle)
        if lower_shell is not None:
            obstruction += _intersection_volume(release_access, lower_shell)
        release_access_obstructions.append(obstruction)

    nominal_overhang_volume = retention.overhang * retention.clip_depth * retention.tab_thickness
    minimum_overhang_volume = 0.5 * nominal_overhang_volume
    enough_clips = len(overhang_volumes) >= 4
    has_overhang = enough_clips and min(overhang_volumes) >= minimum_overhang_volume
    gap_is_clear = bool(gap_obstructions) and max(gap_obstructions) <= INTERSECTION_VOLUME_TOLERANCE_MM3
    cams_are_clear = len(cam_obstructions) >= 4 and max(cam_obstructions) <= INTERSECTION_VOLUME_TOLERANCE_MM3
    release_witness_volume = release_witness_width * bridge_depth * retention.release_rail_height
    releases_present = len(release_volumes) == 2 and min(release_volumes) >= 0.5 * release_witness_volume
    releases_reachable = (
        len(release_access_obstructions) == 2
        and max(release_access_obstructions) <= INTERSECTION_VOLUME_TOLERANCE_MM3
    )
    collision_free = installed_collision <= INTERSECTION_VOLUME_TOLERANCE_MM3
    measured_overhang = ", ".join(f"{volume:.1f}" for volume in overhang_volumes)
    maximum_gap_obstruction = max(gap_obstructions, default=0.0)
    maximum_cam_obstruction = max(cam_obstructions, default=0.0)
    measured_releases = ", ".join(f"{volume:.1f}" for volume in release_volumes)
    maximum_release_access_obstruction = max(release_access_obstructions, default=0.0)
    return _check(
        "Mac positive-Z clip retention",
        collision_free
        and gap_is_clear
        and has_overhang
        and cams_are_clear
        and releases_present
        and releases_reachable,
        f"{len(overhang_volumes)} cantilevers overhang the Mac by {retention.overhang:.1f} mm "
        f"({measured_overhang} mm^3 witnesses); {retention.top_gap:.1f} mm top gap is clear and "
        f"installed intersection is {installed_collision:.4f} mm^3; four underside cam voids and "
        f"two linked release rails have clear bottom approaches",
        f"installed intersection {installed_collision:.3f} mm^3; maximum top-gap obstruction "
        f"{maximum_gap_obstruction:.3f} mm^3; maximum cam obstruction {maximum_cam_obstruction:.3f} mm^3; "
        f"maximum bottom-approach obstruction {maximum_release_access_obstruction:.3f} mm^3; overhang "
        f"witnesses {measured_overhang or 'none'} mm^3 (need >=4 at >= {minimum_overhang_volume:.1f} each); "
        f"release witnesses {measured_releases or 'none'} mm^3 (need two at >= {0.5 * release_witness_volume:.1f} each)",
    )


def handle_structural_mount_check(
    p: StationParameters,
    parts: Mapping[str, cq.Workplane],
) -> CheckResult:
    """Verify the four-screw handle load path and broad cap bearing interfaces."""

    handle = parts["removable_handle"]
    cap = parts["upper_cap"]
    h = p.handle
    f = p.fasteners
    e = p.enclosure
    axes = handle_mount_fastener_positions(p)
    axis_obstructions: list[float] = []
    boss_witnesses: list[float] = []
    outer_radius = f.m3_boss_diameter / 2.0 - 0.1
    inner_radius = f.m3_insert_hole_diameter / 2.0 + 0.1
    expected_ring = pi * (outer_radius**2 - inner_radius**2)
    for x, y in axes:
        handle_axis = cylinder_axis(
            f.m3_clearance_diameter / 2.0 - 0.05,
            h.foot_thickness + 0.2,
            (x, y, e.height - 0.1),
            (0, 0, 1),
        )
        cap_axis = cylinder_axis(
            f.m3_insert_hole_diameter / 2.0 - 0.05,
            f.insert_depth - 0.2,
            (x, y, e.height - f.insert_depth + 0.1),
            (0, 0, 1),
        )
        ring = _annular_axis_witness(
            outer_radius,
            inner_radius,
            1.0,
            (x, y, e.height - 3.5),
            (0, 0, 1),
        )
        axis_obstructions.append(
            _intersection_volume(handle_axis, handle) + _intersection_volume(cap_axis, cap)
        )
        boss_witnesses.append(_intersection_volume(ring, cap))

    # Sample each foot over nearly its full plan area on both sides of the
    # contact plane.  The small bore deductions are acceptable; a missing foot
    # or cap pad is not.
    bearing_witnesses: list[float] = []
    expected_bearing = (h.foot_width - 2.0) * (h.foot_depth - 2.0) * 0.2
    for anchor_x in (-h.anchor_spacing / 2.0, h.anchor_spacing / 2.0):
        below = box_at(
            h.foot_width - 2.0,
            h.foot_depth - 2.0,
            0.2,
            (anchor_x, -42.0, e.height - 0.1),
        )
        above = below.translate((0.0, 0.0, 0.2))
        bearing_witnesses.append(
            min(_intersection_volume(below, cap), _intersection_volume(above, handle))
        )

    installed_overlap = _intersection_volume(handle, cap)
    screw_penetration = f.handle_screw_length - h.foot_thickness
    design_load_n = h.provisional_complete_mass_kg * 9.80665 * h.design_static_factor
    nominal_per_screw_n = design_load_n / len(axes)
    sufficient = (
        len(axes) == 4
        and installed_overlap <= INTERSECTION_VOLUME_TOLERANCE_MM3
        and max(axis_obstructions) <= INTERSECTION_VOLUME_TOLERANCE_MM3
        and min(boss_witnesses) >= 0.95 * expected_ring
        and min(bearing_witnesses) >= 0.85 * expected_bearing
        and f.minimum_thread_engagement <= screw_penetration <= f.insert_depth
        and h.design_static_factor >= 4.0
    )
    return _check(
        "handle four-screw reinforced mounting stack",
        sufficient,
        f"four clear M3 axes, two {h.foot_width:.0f} x {h.foot_depth:.0f} x {h.foot_thickness:.0f} mm feet, "
        f"full-depth cap bosses/pads, and {screw_penetration:.1f} mm nominal engagement; "
        f"CAD design target {design_load_n:.1f} N total ({nominal_per_screw_n:.1f} N/screw) at "
        f"{h.design_static_factor:.0f}x provisional assembled mass",
        f"axes={len(axes)}, installed overlap={installed_overlap:.3f}, axis obstructions={axis_obstructions}, "
        f"boss witnesses={boss_witnesses}, bearing witnesses={bearing_witnesses}, engagement={screw_penetration:.2f}, "
        f"factor={h.design_static_factor:.2f}",
    )


def shell_seam_access_check(
    p: StationParameters,
    parts: Mapping[str, cq.Workplane],
) -> CheckResult:
    """Verify six hidden seam screws, their head seats, and tool access."""

    e = p.enclosure
    f = p.fasteners
    lower = parts["lower_shell"]
    upper = parts["upper_shell"]
    upper_z0 = e.lower_shell_top + e.shadow_gap / 2.0
    lug_top = upper_z0 + e.seam_lug_height
    axes = shell_seam_fastener_positions(p)
    axis_obstructions: list[float] = []
    head_obstructions: list[float] = []
    driver_obstructions: list[float] = []
    lateral_obstructions: list[float] = []
    insert_obstructions: list[float] = []
    lower_boss_witnesses: list[float] = []
    upper_bearing_witnesses: list[float] = []
    exterior_skin_witnesses: list[float] = []
    lower_outer = e.seam_boss_diameter / 2.0 - 0.1
    lower_inner = f.m4_insert_hole_diameter / 2.0 + 0.1
    expected_lower_ring = pi * (lower_outer**2 - lower_inner**2)
    bearing_outer = e.seam_head_clearance_diameter / 2.0 - 0.1
    bearing_inner = f.m4_clearance_diameter / 2.0 + 0.1
    expected_bearing_ring = pi * (bearing_outer**2 - bearing_inner**2) * 0.5
    expected_skin = 0.5 * (e.seam_head_clearance_diameter - 0.2) * (e.seam_head_clearance_height - 0.2)

    for x, y in axes:
        side = 1.0 if x > 0.0 else -1.0
        axis = cylinder_axis(
            f.m4_clearance_diameter / 2.0 - 0.05,
            e.seam_lug_height + 0.2,
            (x, y, upper_z0 - 0.1),
            (0, 0, 1),
        )
        head = cylinder_axis(
            e.seam_head_clearance_diameter / 2.0 - 0.05,
            e.seam_head_clearance_height - 0.1,
            (x, y, lug_top + 0.05),
            (0, 0, 1),
        )
        driver_start = lug_top + e.seam_head_clearance_height + 0.05
        driver = cylinder_axis(
            e.seam_driver_clearance_diameter / 2.0 - 0.05,
            e.shell_top - driver_start + 0.5,
            (x, y, driver_start),
            (0, 0, 1),
        )
        lateral_start_x = side * 60.0
        lateral = box_at(
            abs(x) - 60.0,
            e.seam_head_clearance_diameter - 0.1,
            e.seam_head_clearance_height - 0.1,
            (
                (lateral_start_x + x) / 2.0,
                y,
                lug_top + e.seam_head_clearance_height / 2.0,
            ),
        )
        insert = cylinder_axis(
            f.m4_insert_hole_diameter / 2.0 - 0.05,
            f.insert_depth - 0.2,
            (x, y, e.lower_shell_top - f.insert_depth + 0.1),
            (0, 0, 1),
        )
        lower_ring = _annular_axis_witness(
            lower_outer,
            lower_inner,
            1.0,
            (x, y, e.lower_shell_top - 2.0),
            (0, 0, 1),
        )
        upper_ring = _annular_axis_witness(
            bearing_outer,
            bearing_inner,
            0.5,
            (x, y, lug_top - 0.55),
            (0, 0, 1),
        )
        skin = box_at(
            0.5,
            e.seam_head_clearance_diameter - 0.2,
            e.seam_head_clearance_height - 0.2,
            (side * (e.width / 2.0 - 0.25), y, lug_top + e.seam_head_clearance_height / 2.0),
        )
        axis_obstructions.append(_intersection_volume(axis, upper))
        head_obstructions.append(_intersection_volume(head, upper))
        driver_obstructions.append(_intersection_volume(driver, upper))
        lateral_obstructions.append(_intersection_volume(lateral, upper))
        insert_obstructions.append(_intersection_volume(insert, lower))
        lower_boss_witnesses.append(_intersection_volume(lower_ring, lower))
        upper_bearing_witnesses.append(_intersection_volume(upper_ring, upper))
        exterior_skin_witnesses.append(_intersection_volume(skin, upper))

    passed = (
        len(axes) == 6
        and _intersection_volume(lower, upper) <= INTERSECTION_VOLUME_TOLERANCE_MM3
        and max(axis_obstructions) <= INTERSECTION_VOLUME_TOLERANCE_MM3
        and max(head_obstructions) <= INTERSECTION_VOLUME_TOLERANCE_MM3
        and max(driver_obstructions) <= INTERSECTION_VOLUME_TOLERANCE_MM3
        and max(lateral_obstructions) <= INTERSECTION_VOLUME_TOLERANCE_MM3
        and max(insert_obstructions) <= INTERSECTION_VOLUME_TOLERANCE_MM3
        and min(lower_boss_witnesses) >= 0.95 * expected_lower_ring
        and min(upper_bearing_witnesses) >= 0.90 * expected_bearing_ring
        and min(exterior_skin_witnesses) >= 0.95 * expected_skin
    )
    return _check(
        "six-M4 hidden structural shell seam access",
        passed,
        "six internal M4x18 axes have open head pockets, lateral screw insertion, top driver corridors, "
        "lower insert pilots, bearing rings, and closed exterior skins",
        f"axes={len(axes)}, axis={axis_obstructions}, head={head_obstructions}, driver={driver_obstructions}, "
        f"lateral={lateral_obstructions}, insert={insert_obstructions}, lower bosses={lower_boss_witnesses}, "
        f"upper bearings={upper_bearing_witnesses}, exterior skins={exterior_skin_witnesses}",
    )


def rear_sill_reinforcement_check(
    p: StationParameters,
    lower_shell: cq.Workplane,
) -> CheckResult:
    """Verify the rear-panel sill has an internal angle beam and boss ties."""

    e = p.enclosure
    rear_y = e.depth / 2.0
    flange = box_at(1.0, 6.2, 3.8, (0.0, rear_y - 8.0, e.base_height + 2.0))
    web = box_at(1.0, 3.8, 9.8, (0.0, rear_y - 9.0, e.base_height + 5.0))
    expected_flange = 1.0 * 6.2 * 3.8
    expected_web = 1.0 * 3.8 * 9.8
    flange_volume = _intersection_volume(flange, lower_shell)
    web_volume = _intersection_volume(web, lower_shell)
    tie_volumes: list[float] = []
    rear_boss_y = e.width / 2.0 - 13.0
    for x in (-rear_boss_y, rear_boss_y):
        tie = box_at(2.0, 2.0, 3.0, (x, rear_y - 10.0, e.base_height + 1.5))
        tie_volumes.append(_intersection_volume(tie, lower_shell))
    expected_tie = 2.0 * 2.0 * 3.0
    passed = (
        flange_volume >= 0.98 * expected_flange
        and web_volume >= 0.98 * expected_web
        and min(tie_volumes) >= 0.90 * expected_tie
    )
    return _check(
        "rear-panel lower sill angle-beam reinforcement",
        passed,
        "the 4 mm sill has an internal flange/web beam tied into both rear base-boss regions; "
        "the separate Mac-button swept-path check remains authoritative for the local notch",
        f"flange={flange_volume:.2f}/{expected_flange:.2f}, web={web_volume:.2f}/{expected_web:.2f}, "
        f"boss ties={tie_volumes}/{expected_tie:.2f} mm^3",
    )
def logo_screw_mount_check(
    p: StationParameters,
    parts: Mapping[str, cq.Workplane],
) -> CheckResult:
    """Verify both logo panels have two clear, supported screw axes."""

    e = p.enclosure
    f = p.fasteners
    logo = p.logo
    shell = parts["upper_shell"]
    axis_obstructions: list[float] = []
    boss_witnesses: list[float] = []
    installed_overlaps: list[float] = []
    outer_radius = f.m3_boss_diameter / 2.0 - 0.1
    inner_radius = f.m3_insert_hole_diameter / 2.0 + 0.1
    expected_ring = pi * (outer_radius**2 - inner_radius**2)
    pocket_inner = e.width / 2.0 - logo.thickness - p.fits.logo_panel_per_side
    for side_name, side in (("left", -1.0), ("right", 1.0)):
        panel = parts[f"logo_panel_{side_name}"]
        installed_overlaps.append(_intersection_volume(panel, shell))
        for _x, y, z in logo_mount_positions(side_name, p):
            panel_axis = cylinder_axis(
                f.m3_clearance_diameter / 2.0 - 0.05,
                logo.thickness + 0.2,
                (side * (e.width / 2.0 + 0.1), y, z),
                (-side, 0, 0),
            )
            shell_axis = cylinder_axis(
                f.m3_insert_hole_diameter / 2.0 - 0.05,
                f.insert_depth - 0.2,
                (side * (e.width / 2.0 - logo.thickness + 0.1), y, z),
                (-side, 0, 0),
            )
            ring = _annular_axis_witness(
                outer_radius,
                inner_radius,
                1.0,
                (side * (pocket_inner - 3.5), y, z),
                (side, 0, 0),
            )
            axis_obstructions.append(
                _intersection_volume(panel_axis, panel) + _intersection_volume(shell_axis, shell)
            )
            boss_witnesses.append(_intersection_volume(ring, shell))

    penetration = f.logo_screw_length - logo.thickness
    passed = (
        len(axis_obstructions) == 4
        and max(installed_overlaps) <= INTERSECTION_VOLUME_TOLERANCE_MM3
        and max(axis_obstructions) <= INTERSECTION_VOLUME_TOLERANCE_MM3
        and min(boss_witnesses) >= 0.95 * expected_ring
        and min(penetration, f.insert_depth) >= f.minimum_thread_engagement
        and penetration <= f.insert_depth + 0.7
    )
    return _check(
        "logo panels four-screw replaceable mounting stack",
        passed,
        f"two outward-accessible M3 screws per panel; four clear axes, solid shell-webbed bosses, "
        f"{min(penetration, f.insert_depth):.1f} mm nominal insert overlap, and zero installed interference",
        f"axis obstructions={axis_obstructions}, boss witnesses={boss_witnesses}, "
        f"panel/shell overlaps={installed_overlaps}, penetration={penetration:.2f}",
    )


def wifi_dock_capture_geometry_check(p: StationParameters) -> CheckResult:
    """Bound the rigid hub clearance and elastic movement demanded at each lip."""

    w = p.wifi
    radial_clearance = p.fits.wifi_clip_radial
    base_cavity = w.antenna_base_diameter + 2.0 * radial_clearance
    stem_cavity = w.antenna_stem_diameter + 2.0 * radial_clearance
    base_mouth = base_cavity - 2.0 * w.clip_lip_intrusion
    stem_mouth = stem_cavity - 2.0 * w.clip_lip_intrusion
    base_arm_movement = (w.antenna_base_diameter - base_mouth) / 2.0
    stem_arm_movement = (w.antenna_stem_diameter - stem_mouth) / 2.0
    passed = (
        base_cavity > w.antenna_base_diameter
        and stem_cavity > w.antenna_stem_diameter
        and 0.10 <= base_arm_movement <= 0.60
        and 0.10 <= stem_arm_movement <= 0.60
        and w.clip_lip_radius > w.clip_lip_intrusion
        and w.clip_wall >= p.enclosure.minimum_wall
    )
    return _check(
        "Wi-Fi dock rounded-lip insertion geometry",
        passed,
        f"Ø{w.antenna_base_diameter:.1f} mm hub enters a {base_mouth:.1f} mm rounded mouth with "
        f"{base_arm_movement:.2f} mm nominal movement per arm and seats in a {base_cavity:.1f} mm cavity; "
        f"stem movement is {stem_arm_movement:.2f} mm/arm",
        f"base cavity={base_cavity:.2f}, base mouth={base_mouth:.2f}, base arm movement={base_arm_movement:.2f}, "
        f"stem cavity={stem_cavity:.2f}, stem mouth={stem_mouth:.2f}, stem arm movement={stem_arm_movement:.2f}, "
        f"lip radius/intrusion={w.clip_lip_radius:.2f}/{w.clip_lip_intrusion:.2f}",
    )


def c8_terminal_passage_check(
    p: StationParameters,
    compartment: cq.Workplane,
) -> CheckResult:
    """Prove the C8 terminal tunnel opens into the main covered cavity."""

    e = p.enclosure
    pw = p.power
    interface = p.interfaces
    rear_wall_y = pw.center_y + pw.outer_depth / 2.0
    main_cavity_sample_y = rear_wall_y - pw.wall - p.fits.equipment_clearance
    panel_inner_y = e.depth / 2.0 - e.rear_panel_thickness
    tunnel_sample_y = (rear_wall_y + panel_inner_y) / 2.0
    passage_depth = tunnel_sample_y - main_cavity_sample_y
    if passage_depth <= 0.0:
        raise ValueError("C8 passage probe has no positive route length")

    # A cutout-sized rectangular probe is more meaningful than a centreline: it
    # rejects both a complete wall and an undersized pinhole between the cavity
    # and the terminal shroud.  Both endpoints lie safely inside their respective
    # voids, so only compartment material can obstruct the intended route.
    passage = box_at(
        interface.c8_cutout_width,
        passage_depth,
        interface.c8_cutout_height,
        (
            interface.c8_position_x,
            (main_cavity_sample_y + tunnel_sample_y) / 2.0,
            interface.c8_position_z,
        ),
    )
    barrier_volume = _intersection_volume(passage, compartment)
    return _check(
        "C8 terminal tunnel/main-compartment passage",
        barrier_volume <= INTERSECTION_VOLUME_TOLERANCE_MM3,
        f"{interface.c8_cutout_width:.1f} x {interface.c8_cutout_height:.1f} mm passage is continuous; obstruction {barrier_volume:.4f} mm^3",
        f"compartment material obstructs the intended passage by {barrier_volume:.3f} mm^3",
    )


def power_tie_bridge_floor_check(
    p: StationParameters,
    compartment: cq.Workplane,
) -> CheckResult:
    """Verify both internal tie tunnels sit over an unbroken box floor."""

    pw = p.power
    floor_probe_height = min(2.0, pw.bottom - 0.4)
    sealed_floor_volumes: list[float] = []
    tunnel_obstructions: list[float] = []
    crown_volumes: list[float] = []
    expected_floor = pw.tie_bridge_tunnel_width * pw.tie_bridge_depth * floor_probe_height
    crown_height = pw.tie_bridge_height - pw.tie_bridge_tunnel_height
    expected_crown = pw.tie_bridge_tunnel_width * (pw.tie_bridge_depth - 0.4) * crown_height
    for x, y in power_tie_bridge_centres(p):
        floor_witness = box_at(
            pw.tie_bridge_tunnel_width,
            pw.tie_bridge_depth,
            floor_probe_height,
            (x, y, pw.bottom_z + floor_probe_height / 2.0),
        )
        tunnel_witness = box_at(
            pw.tie_bridge_tunnel_width - 0.2,
            pw.tie_bridge_depth + 0.4,
            pw.tie_bridge_tunnel_height - 0.2,
            (
                x,
                y,
                pw.bottom_z + pw.bottom + pw.tie_bridge_tunnel_height / 2.0 + 0.1,
            ),
        )
        crown_witness = box_at(
            pw.tie_bridge_tunnel_width,
            pw.tie_bridge_depth - 0.4,
            crown_height,
            (
                x,
                y,
                pw.bottom_z + pw.bottom + pw.tie_bridge_tunnel_height + crown_height / 2.0,
            ),
        )
        sealed_floor_volumes.append(_intersection_volume(floor_witness, compartment))
        tunnel_obstructions.append(_intersection_volume(tunnel_witness, compartment))
        crown_volumes.append(_intersection_volume(crown_witness, compartment))

    passed = (
        len(sealed_floor_volumes) == 2
        and min(sealed_floor_volumes) >= 0.98 * expected_floor
        and max(tunnel_obstructions) <= INTERSECTION_VOLUME_TOLERANCE_MM3
        and min(crown_volumes) >= 0.95 * expected_crown
    )
    return _check(
        "sealed-floor raised power tie bridges",
        passed,
        f"two open strap tunnels have solid crowns and >=98% solid floor witnesses "
        f"({', '.join(f'{volume:.1f}' for volume in sealed_floor_volumes)} mm^3)",
        f"floor witnesses {sealed_floor_volumes}, tunnel obstructions {tunnel_obstructions}, "
        f"crown witnesses {crown_volumes}",
    )


def mac_ac_gland_passage_check(
    p: StationParameters,
    compartment: cq.Workplane,
) -> CheckResult:
    """Guard against later unions refilling the nominal Mac-AC gland cut."""

    pw = p.power
    x = pw.center_x + pw.mac_ac_exit_offset_x
    y = pw.center_y + pw.mac_ac_exit_offset_y
    witness = cylinder_axis(
        pw.mac_ac_gland_diameter / 2.0,
        pw.bottom + 1.8,
        (x, y, pw.bottom_z - 0.9),
        (0, 0, 1),
    )
    obstruction = _intersection_volume(witness, compartment)
    return _check(
        "Mac AC nominal gland aperture",
        obstruction <= INTERSECTION_VOLUME_TOLERANCE_MM3,
        f"full diameter-{pw.mac_ac_gland_diameter:.1f} floor passage remains open; obstruction {obstruction:.4f} mm^3",
        f"nominal gland witness is obstructed by {obstruction:.3f} mm^3",
    )


def apv_top_service_mount_check(
    p: StationParameters,
    compartment: cq.Workplane,
) -> CheckResult:
    """Verify two blind insert pods and clear top-service screw axes."""

    pw = p.power
    c = p.components
    layout = packaging_layout(p)
    boss_top = layout.psu_center[2] - c.psu_case_height / 2.0 - pw.apv_support_clearance
    pocket_clearances: list[float] = []
    floor_closures: list[float] = []
    access_obstructions: list[float] = []
    closure_height = boss_top - pw.apv_insert_pocket_depth - pw.bottom_z
    closure_witness_height = min(1.0, closure_height - 0.2)
    expected_closure = 3.141592653589793 * (pw.apv_insert_pocket_diameter / 2.0 - 0.05) ** 2 * closure_witness_height
    service_length = pw.bottom_z + pw.outer_height - boss_top - 0.1
    for x, y in apv_mount_fastener_positions(p):
        pocket = cylinder_axis(
            pw.apv_insert_pocket_diameter / 2.0 - 0.05,
            pw.apv_insert_pocket_depth - 0.2,
            (x, y, boss_top - pw.apv_insert_pocket_depth + 0.1),
            (0, 0, 1),
        )
        closure = cylinder_axis(
            pw.apv_insert_pocket_diameter / 2.0 - 0.05,
            closure_witness_height,
            (x, y, pw.bottom_z + 0.1),
            (0, 0, 1),
        )
        access = cylinder_axis(
            c.psu_mount_hole_diameter / 2.0,
            service_length,
            (x, y, boss_top + 0.05),
            (0, 0, 1),
        )
        pocket_clearances.append(_intersection_volume(pocket, compartment))
        floor_closures.append(_intersection_volume(closure, compartment))
        access_obstructions.append(_intersection_volume(access, compartment))

    passed = (
        len(pocket_clearances) == 2
        and closure_height >= p.enclosure.minimum_wall
        and max(pocket_clearances) <= INTERSECTION_VOLUME_TOLERANCE_MM3
        and min(floor_closures) >= 0.98 * expected_closure
        and max(access_obstructions) <= INTERSECTION_VOLUME_TOLERANCE_MM3
    )
    return _check(
        "APV top-service blind insert mounts",
        passed,
        f"two supplier-coordinate diameter-{c.psu_mount_hole_diameter:.1f} axes are open from above; "
        f"{pw.apv_insert_pocket_depth:.1f} mm blind pilots retain {closure_height:.1f} mm sealed floor",
        f"pocket obstructions {pocket_clearances}, floor closures {floor_closures}, "
        f"access obstructions {access_obstructions}, residual floor {closure_height:.2f} mm",
    )


def power_cover_column_check(
    p: StationParameters,
    compartment: cq.Workplane,
    cover: cq.Workplane,
) -> CheckResult:
    """Verify wall-tied upper bosses align with four cover clearance holes."""

    pw = p.power
    f = p.fasteners
    cover_underside = pw.bottom_z + pw.outer_height
    pilot_obstructions: list[float] = []
    cover_obstructions: list[float] = []
    column_witnesses: list[float] = []
    witness_radius = f.m3_boss_diameter / 2.0 - 0.1
    expected_column = 3.141592653589793 * witness_radius**2
    boss_height = power_cover_boss_height(p)
    for x, y in power_cover_fastener_positions(p):
        pilot = cylinder_axis(
            f.m3_insert_hole_diameter / 2.0 - 0.05,
            f.insert_depth - 0.2,
            (x, y, cover_underside - f.insert_depth + 0.1),
            (0, 0, 1),
        )
        cover_axis = cylinder_axis(
            f.m3_clearance_diameter / 2.0 - 0.05,
            pw.cover_thickness + 3.6,
            (x, y, cover_underside - 1.8),
            (0, 0, 1),
        )
        mid_column = cylinder_axis(
            witness_radius,
            1.0,
            (x, y, cover_underside - boss_height + 0.5),
            (0, 0, 1),
        )
        pilot_obstructions.append(_intersection_volume(pilot, compartment))
        cover_obstructions.append(_intersection_volume(cover_axis, cover))
        column_witnesses.append(_intersection_volume(mid_column, compartment))

    engagement = pw.cover_screw_length - pw.cover_thickness
    passed = (
        len(column_witnesses) == 4
        and min(column_witnesses) >= 0.98 * expected_column
        and max(pilot_obstructions) <= INTERSECTION_VOLUME_TOLERANCE_MM3
        and max(cover_obstructions) <= INTERSECTION_VOLUME_TOLERANCE_MM3
        and pw.cover_min_thread_engagement <= engagement <= f.insert_depth
        and _intersection_volume(compartment, cover) <= INTERSECTION_VOLUME_TOLERANCE_MM3
    )
    return _check(
        "power-cover wall-tied upper insert bosses",
        passed,
        f"four {boss_height:.1f} mm upper bosses align with open cover axes; provisional M3x{pw.cover_screw_length:.0f} gives "
        f"{engagement:.1f} mm nominal engagement into {f.insert_depth:.1f} mm pilots",
        f"column witnesses {column_witnesses}, pilot obstructions {pilot_obstructions}, "
        f"cover-axis obstructions {cover_obstructions}, nominal engagement {engagement:.2f} mm",
    )


def power_shell_mount_access_check(
    p: StationParameters,
    compartment: cq.Workplane,
) -> CheckResult:
    """Prove all four floor screws have an open bore, head seat, and driver path."""

    pw = p.power
    f = p.fasteners
    floor_top = pw.bottom_z + pw.bottom
    cover_underside = pw.bottom_z + pw.outer_height
    axis_obstructions: list[float] = []
    head_obstructions: list[float] = []
    driver_obstructions: list[float] = []
    for x, y in power_mount_fastener_positions(p):
        axis = cylinder_axis(
            f.m3_clearance_diameter / 2.0 - 0.05,
            pw.bottom + 1.8,
            (x, y, pw.bottom_z - 0.9),
            (0, 0, 1),
        )
        head = cylinder_axis(
            f.m3_low_head_recess_diameter / 2.0,
            3.2,
            (x, y, floor_top + 0.05),
            (0, 0, 1),
        )
        driver = cylinder_axis(
            2.25,
            cover_underside - floor_top - 3.25,
            (x, y, floor_top + 3.25),
            (0, 0, 1),
        )
        axis_obstructions.append(_intersection_volume(axis, compartment))
        head_obstructions.append(_intersection_volume(head, compartment))
        driver_obstructions.append(_intersection_volume(driver, compartment))

    passed = (
        len(axis_obstructions) == 4
        and max(axis_obstructions) <= INTERSECTION_VOLUME_TOLERANCE_MM3
        and max(head_obstructions) <= INTERSECTION_VOLUME_TOLERANCE_MM3
        and max(driver_obstructions) <= INTERSECTION_VOLUME_TOLERANCE_MM3
    )
    return _check(
        "power-compartment four-screw shell-mount access",
        passed,
        "four diameter-3.4 floor bores plus diameter-6.2 head and diameter-4.5 driver corridors are open from above",
        f"axis obstructions {axis_obstructions}, head obstructions {head_obstructions}, "
        f"driver obstructions {driver_obstructions}",
    )


def mac_ac_corridor_packaging_check(
    p: StationParameters,
    parts: Mapping[str, cq.Workplane],
    model: ReferenceModel,
) -> CheckResult:
    """Check only geometric continuity of the reserved Mac-AC route envelope."""

    pw = p.power
    route = model.interfaces["mac_ac_branch_corridor"]
    gland_axis = cylinder_axis(
        pw.mac_ac_gland_diameter / 2.0,
        pw.bottom + 2.0,
        (
            pw.center_x + pw.mac_ac_exit_offset_x,
            pw.center_y + pw.mac_ac_exit_offset_y,
            pw.bottom_z - 1.0,
        ),
        (0, 0, 1),
    )
    endpoint_overlap = _intersection_volume(route, model.clearances["mac_internal_ac"])
    gland_overlap = _intersection_volume(route, gland_axis)
    blockers = {
        "Mac": _intersection_volume(route, model.equipment["mac_mini_m4"]),
        "cradle": _intersection_volume(route, parts["mac_cradle"]),
        "lower_shell": _intersection_volume(route, parts["lower_shell"]),
        "low_voltage_lane": _intersection_volume(route, model.interfaces["low_voltage_lane"]),
    }
    passed = (
        len(route.solids().vals()) == 1
        and gland_overlap > INTERSECTION_VOLUME_TOLERANCE_MM3
        and endpoint_overlap > INTERSECTION_VOLUME_TOLERANCE_MM3
        and max(blockers.values()) <= INTERSECTION_VOLUME_TOLERANCE_MM3
    )
    return _check(
        "Mac AC reserved corridor continuity",
        passed,
        f"one connected {pw.mac_ac_corridor_width:.1f} mm packaging envelope joins the gland and provisional "
        "Mac connector without intersecting the Mac, cradle, lower shell, or low-voltage keep-out",
        f"gland overlap {gland_overlap:.3f}, connector overlap {endpoint_overlap:.3f}, blockers {blockers}",
    )


def rear_service_removal_sweep_check(
    p: StationParameters,
    parts: Mapping[str, cq.Workplane],
    model: ReferenceModel | None = None,
) -> CheckResult:
    """Move the rear panel, bezel, and placeholder extensions together along +Y."""

    if model is None:
        model = build_reference_model(p)
    moving = {
        "rear_panel": parts["rear_panel"],
        "router_interface_bezel": parts["router_interface_bezel"],
        "mac_hdmi_panel_extension": model.hardware["mac_hdmi_panel_extension"],
        "mac_usbc_panel_extension": model.hardware["mac_usbc_panel_extension"],
        "router_lan_panel_extension": model.hardware["router_lan_panel_extension"],
        "router_wan_panel_extension": model.hardware["router_wan_panel_extension"],
    }
    stationary_names = (
        "base",
        "mac_cradle",
        "lower_shell",
        "upper_shell",
        "router_tray",
        "power_compartment",
        "power_compartment_cover",
        "upper_cap",
        "removable_handle",
        "wifi_dock_left",
        "wifi_dock_right",
        "logo_panel_left",
        "logo_panel_right",
    )
    stationary = {name: parts[name] for name in stationary_names}
    stationary.update({f"equipment_{name}": obj for name, obj in model.equipment.items()})
    stationary["fixed_c8_inlet"] = model.hardware["c8_inlet"]
    distances = tuple(float(value) for value in range(0, 13)) + tuple(
        float(value) for value in range(16, 81, 4)
    )
    translations = tuple((0.0, distance, 0.0) for distance in distances)
    return _sampled_translation_clearance(
        "rear panel+bezel sampled +Y service sweep",
        moving,
        stationary,
        translations,
        "+Y from 0 to 80 mm with the four disconnected extension placeholders moving with the panel/bezel",
    )


def mac_cradle_downward_removal_sweep_check(
    p: StationParameters,
    parts: Mapping[str, cq.Workplane],
    model: ReferenceModel | None = None,
) -> CheckResult:
    """Sample Mac plus cradle withdrawal in -Z after removing the base."""

    if model is None:
        model = build_reference_model(p)
    moving = {
        "mac_mini_m4": model.equipment["mac_mini_m4"],
        "mac_cradle": parts["mac_cradle"],
    }
    # The base and its screws are removed first.  Every other installed printed
    # part remains stationary, including the closed power enclosure and router.
    stationary_names = (
        "lower_shell",
        "upper_shell",
        "router_tray",
        "power_compartment",
        "power_compartment_cover",
        "rear_panel",
        "router_interface_bezel",
        "upper_cap",
        "removable_handle",
        "wifi_dock_left",
        "wifi_dock_right",
        "logo_panel_left",
        "logo_panel_right",
    )
    stationary = {name: parts[name] for name in stationary_names}
    stationary["equipment_rutm30"] = model.equipment["rutm30"]
    stationary["equipment_apv_35_36"] = model.equipment["apv_35_36"]
    distances = (0.0, 1.0, 2.0) + tuple(float(value) for value in range(4, 81, 4))
    translations = tuple((0.0, 0.0, -distance) for distance in distances)
    return _sampled_translation_clearance(
        "Mac+cradle sampled downward service sweep",
        moving,
        stationary,
        translations,
        "-Z from 0 to -80 mm after base removal; Mac and cradle are the moving set",
    )


def router_rearward_removal_sweep_check(
    p: StationParameters,
    parts: Mapping[str, cq.Workplane],
    model: ReferenceModel | None = None,
) -> CheckResult:
    """Sample router-only +Y withdrawal with the rear retainers spread."""

    if model is None:
        model = build_reference_model(p)
    c = p.components
    layout = packaging_layout(p)
    x0, y0, z0 = layout.router_center
    rail_x = c.router_width / 2.0 + p.fits.equipment_clearance + 1.5
    rear_latch_y = y0 + c.router_depth / 2.0 + 1.2
    released_tray = parts["router_tray"]
    # These two local cuts represent the two rear latch/nib flexures being held
    # outward.  The tray otherwise remains installed and is checked as an obstacle.
    for side in (-1.0, 1.0):
        nib_x = x0 + side * (rail_x - 2.5)
        release_relief = box_at(8.0, 6.0, c.router_height + 4.0, (nib_x, rear_latch_y, z0))
        released_tray = released_tray.cut(release_relief)

    stationary_names = (
        "lower_shell",
        "upper_shell",
        "power_compartment",
        "power_compartment_cover",
        "upper_cap",
        "wifi_dock_left",
        "wifi_dock_right",
    )
    stationary = {name: parts[name] for name in stationary_names}
    stationary["router_tray_retainers_spread"] = released_tray
    stationary["equipment_mac_mini_m4"] = model.equipment["mac_mini_m4"]
    stationary["equipment_apv_35_36"] = model.equipment["apv_35_36"]
    distances = (0.0, 1.0, 2.0, 4.0, 8.0) + tuple(
        float(value) for value in range(16, 113, 8)
    )
    translations = tuple((0.0, distance, 0.0) for distance in distances)
    router_service_envelope = box_at(c.router_width, c.router_depth, c.router_height, layout.router_center)
    return _sampled_translation_clearance(
        "RUTM30 sampled rearward service sweep (retainers released)",
        {"rutm30_conservative_body_envelope": router_service_envelope},
        stationary,
        translations,
        "+Y from 0 to 112 mm; a conservative 100 x 93.7 x 30 mm router body envelope alone moves, "
        "panel/bezel are removed, and both rear retainers are spread",
    )


def fastener_stack_checks(
    p: StationParameters,
    parts: Mapping[str, cq.Workplane],
) -> list[CheckResult]:
    """Check grip, insert overlap, tip relief, clear axes, and surrounding bosses."""

    e = p.enclosure
    f = p.fasteners
    pw = p.power

    def stack_result(
        name: str,
        expected_label: str,
        actual_label: str,
        screw_length: float,
        expected_length: float,
        grip: float,
        pilot_depth: float,
        axis_obstructions: list[float],
        boss_witnesses: list[float],
        expected_boss_witness: float,
    ) -> CheckResult:
        penetration = screw_length - grip
        thread_overlap = min(max(penetration, 0.0), f.insert_depth)
        passed = (
            actual_label == expected_label
            and abs(screw_length - expected_length) <= 0.01
            and thread_overlap >= f.minimum_thread_engagement
            and penetration <= pilot_depth
            and bool(axis_obstructions)
            and max(axis_obstructions) <= INTERSECTION_VOLUME_TOLERANCE_MM3
            and bool(boss_witnesses)
            and min(boss_witnesses) >= 0.95 * expected_boss_witness
        )
        return _check(
            name,
            passed,
            f"{actual_label}: {grip:.1f} mm grip, {penetration:.1f} mm pilot penetration, "
            f"{thread_overlap:.1f} mm nominal insert overlap, {pilot_depth:.1f} mm tip relief; "
            f"{len(axis_obstructions)} clear axes with surrounding structural material",
            f"label={actual_label}, length={screw_length:.2f}, grip={grip:.2f}, penetration={penetration:.2f}, "
            f"thread overlap={thread_overlap:.2f}, pilot depth={pilot_depth:.2f}, axis obstructions={axis_obstructions}, "
            f"boss witnesses={boss_witnesses}",
        )

    results: list[CheckResult] = []

    base_positions = tuple(
        (x, y)
        for x in (-(e.width / 2.0 - 13.0), e.width / 2.0 - 13.0)
        for y in (-(e.depth / 2.0 - 13.0), e.depth / 2.0 - 13.0)
    )
    base_axis_obstructions: list[float] = []
    base_boss_witnesses: list[float] = []
    base_outer_radius = f.m3_boss_diameter / 2.0 - 0.1
    base_inner_radius = f.m3_insert_hole_diameter / 2.0 + 0.1
    base_expected_ring = pi * (base_outer_radius**2 - base_inner_radius**2)
    for x, y in base_positions:
        clearance_axis = cylinder_axis(
            f.m3_clearance_diameter / 2.0 - 0.05,
            e.base_height - e.foot_height + 0.2,
            (x, y, e.foot_height - 0.1),
            (0, 0, 1),
        )
        insert_axis = cylinder_axis(
            f.m3_insert_hole_diameter / 2.0 - 0.05,
            f.insert_depth - 0.2,
            (x, y, e.base_height + 0.1),
            (0, 0, 1),
        )
        ring = _annular_axis_witness(
            base_outer_radius,
            base_inner_radius,
            1.0,
            (x, y, e.base_height + 0.5),
            (0, 0, 1),
        )
        base_axis_obstructions.append(
            _intersection_volume(clearance_axis, parts["base"])
            + _intersection_volume(insert_axis, parts["lower_shell"])
        )
        base_boss_witnesses.append(_intersection_volume(ring, parts["lower_shell"]))
    base_grip = e.base_height - e.foot_height
    base_pilot_depth = f.insert_depth + 1.0
    results.append(
        stack_result(
            "fastener stack: removable base M3x14",
            "M3x14",
            f.base_screw,
            f.base_screw_length,
            14.0,
            base_grip,
            base_pilot_depth,
            base_axis_obstructions,
            base_boss_witnesses,
            base_expected_ring,
        )
    )

    cradle_axis_obstructions: list[float] = []
    cradle_boss_witnesses: list[float] = []
    cradle_bottom = p.components.mac_support_plane_z - 5.0
    cradle_grip = 4.0
    for x, y in mac_cradle_fastener_positions(p):
        clearance_axis = cylinder_axis(
            f.m3_clearance_diameter / 2.0 - 0.05,
            cradle_grip + 0.2,
            (x, y, cradle_bottom - 0.1),
            (0, 0, 1),
        )
        insert_axis = cylinder_axis(
            f.m3_insert_hole_diameter / 2.0 - 0.05,
            f.insert_depth - 0.2,
            (x, y, cradle_bottom + cradle_grip + 0.1),
            (0, 0, 1),
        )
        boss_ring = _annular_axis_witness(
            base_outer_radius,
            base_inner_radius,
            1.0,
            (x, y, cradle_bottom + cradle_grip + 2.0),
            (0, 0, 1),
        )
        cradle_axis_obstructions.append(
            _intersection_volume(clearance_axis, parts["mac_cradle"])
            + _intersection_volume(insert_axis, parts["lower_shell"])
        )
        cradle_boss_witnesses.append(_intersection_volume(boss_ring, parts["lower_shell"]))
    results.append(
        stack_result(
            "fastener stack: Mac cradle M3x10",
            "M3x10",
            f.cradle_screw,
            f.cradle_screw_length,
            10.0,
            cradle_grip,
            f.insert_depth + 1.0,
            cradle_axis_obstructions,
            cradle_boss_witnesses,
            base_expected_ring,
        )
    )

    router_axis_obstructions: list[float] = []
    router_boss_witnesses: list[float] = []
    router_plate_thickness = 3.0
    router_grip = router_plate_thickness - f.m3_low_head_recess_depth
    router_pilot_depth = 5.8
    for x, y in router_tray_fastener_positions(p):
        clearance_axis = cylinder_axis(
            f.m3_clearance_diameter / 2.0 - 0.05,
            router_plate_thickness + 0.2,
            (x, y, p.components.router_tray_z - 0.1),
            (0, 0, 1),
        )
        insert_axis = cylinder_axis(
            f.m3_insert_hole_diameter / 2.0 - 0.05,
            router_pilot_depth - 0.2,
            (x, y, p.components.router_tray_z - router_pilot_depth + 0.1),
            (0, 0, 1),
        )
        boss_ring = _annular_axis_witness(
            base_outer_radius,
            base_inner_radius,
            1.0,
            (x, y, p.components.router_tray_z - 3.0),
            (0, 0, 1),
        )
        router_axis_obstructions.append(
            _intersection_volume(clearance_axis, parts["router_tray"])
            + _intersection_volume(insert_axis, parts["upper_shell"])
        )
        router_boss_witnesses.append(_intersection_volume(boss_ring, parts["upper_shell"]))
    results.append(
        stack_result(
            "fastener stack: router tray M3x6",
            "M3x6",
            f.router_tray_screw,
            f.router_tray_screw_length,
            6.0,
            router_grip,
            router_pilot_depth,
            router_axis_obstructions,
            router_boss_witnesses,
            base_expected_ring,
        )
    )

    handle_axis_obstructions: list[float] = []
    handle_boss_witnesses: list[float] = []
    handle_grip = p.handle.foot_thickness
    handle_pilot_depth = f.insert_depth + 0.2
    for x, y in handle_mount_fastener_positions(p):
        clearance_axis = cylinder_axis(
            f.m3_clearance_diameter / 2.0 - 0.05,
            handle_grip + 0.2,
            (x, y, e.height - 0.1),
            (0, 0, 1),
        )
        insert_axis = cylinder_axis(
            f.m3_insert_hole_diameter / 2.0 - 0.05,
            f.insert_depth - 0.2,
            (x, y, e.height - f.insert_depth + 0.1),
            (0, 0, 1),
        )
        boss_ring = _annular_axis_witness(
            base_outer_radius,
            base_inner_radius,
            1.0,
            (x, y, e.height - 3.5),
            (0, 0, 1),
        )
        handle_axis_obstructions.append(
            _intersection_volume(clearance_axis, parts["removable_handle"])
            + _intersection_volume(insert_axis, parts["upper_cap"])
        )
        handle_boss_witnesses.append(_intersection_volume(boss_ring, parts["upper_cap"]))
    results.append(
        stack_result(
            "fastener stack: reinforced handle M3x10",
            "M3x10",
            f.handle_screw,
            f.handle_screw_length,
            10.0,
            handle_grip,
            handle_pilot_depth,
            handle_axis_obstructions,
            handle_boss_witnesses,
            base_expected_ring,
        )
    )

    logo_axis_obstructions: list[float] = []
    logo_boss_witnesses: list[float] = []
    logo_pilot_depth = f.insert_depth + 0.7
    pocket_inner = e.width / 2.0 - p.logo.thickness - p.fits.logo_panel_per_side
    for side_name, side in (("left", -1.0), ("right", 1.0)):
        panel = parts[f"logo_panel_{side_name}"]
        for _axis_x, y, z in logo_mount_positions(side_name, p):
            clearance_axis = cylinder_axis(
                f.m3_clearance_diameter / 2.0 - 0.05,
                p.logo.thickness + 0.2,
                (side * (e.width / 2.0 + 0.1), y, z),
                (-side, 0, 0),
            )
            insert_axis = cylinder_axis(
                f.m3_insert_hole_diameter / 2.0 - 0.05,
                f.insert_depth - 0.2,
                (side * (e.width / 2.0 - p.logo.thickness + 0.1), y, z),
                (-side, 0, 0),
            )
            boss_ring = _annular_axis_witness(
                base_outer_radius,
                base_inner_radius,
                1.0,
                (side * (pocket_inner - 3.5), y, z),
                (side, 0, 0),
            )
            logo_axis_obstructions.append(
                _intersection_volume(clearance_axis, panel)
                + _intersection_volume(insert_axis, parts["upper_shell"])
            )
            logo_boss_witnesses.append(_intersection_volume(boss_ring, parts["upper_shell"]))
    results.append(
        stack_result(
            "fastener stack: logo panels M3x8",
            "M3x8",
            f.logo_screw,
            f.logo_screw_length,
            8.0,
            p.logo.thickness,
            logo_pilot_depth,
            logo_axis_obstructions,
            logo_boss_witnesses,
            base_expected_ring,
        )
    )

    cap_axis_obstructions: list[float] = []
    cap_boss_witnesses: list[float] = []
    m4_outer_radius = f.m4_boss_diameter / 2.0 - 0.1
    m4_inner_radius = f.m4_insert_hole_diameter / 2.0 + 0.1
    m4_expected_ring = pi * (m4_outer_radius**2 - m4_inner_radius**2)
    for x, y in cap_fastener_positions(p):
        clearance_axis = cylinder_axis(
            f.m4_clearance_diameter / 2.0 - 0.05,
            e.cap_height + 0.2,
            (x, y, e.shell_top - 0.1),
            (0, 0, 1),
        )
        insert_axis = cylinder_axis(
            f.m4_insert_hole_diameter / 2.0 - 0.05,
            6.8,
            (x, y, e.shell_top - 6.9),
            (0, 0, 1),
        )
        sleeve_ring = _annular_axis_witness(
            m4_outer_radius,
            m4_inner_radius,
            1.0,
            (x, y, e.shell_top + 1.0),
            (0, 0, 1),
        )
        cap_axis_obstructions.append(
            _intersection_volume(clearance_axis, parts["upper_cap"])
            + _intersection_volume(insert_axis, parts["upper_shell"])
        )
        cap_boss_witnesses.append(_intersection_volume(sleeve_ring, parts["upper_cap"]))
    results.append(
        stack_result(
            "fastener stack: upper cap M4x18",
            "M4x18",
            f.structural_screw,
            f.structural_screw_length,
            18.0,
            e.cap_height,
            7.0,
            cap_axis_obstructions,
            cap_boss_witnesses,
            m4_expected_ring,
        )
    )

    seam_positions = shell_seam_fastener_positions(p)
    seam_axis_obstructions: list[float] = []
    seam_boss_witnesses: list[float] = []
    seam_lug_bottom = e.lower_shell_top + e.shadow_gap / 2.0
    seam_lug_height = e.seam_lug_height
    seam_grip = seam_lug_bottom + seam_lug_height - e.lower_shell_top
    seam_outer_radius = e.seam_boss_diameter / 2.0 - 0.1
    seam_inner_radius = f.m4_insert_hole_diameter / 2.0 + 0.1
    seam_expected_ring = pi * (seam_outer_radius**2 - seam_inner_radius**2)
    for x, y in seam_positions:
        clearance_axis = cylinder_axis(
            f.m4_clearance_diameter / 2.0 - 0.05,
            seam_lug_height + 0.2,
            (x, y, seam_lug_bottom - 0.1),
            (0, 0, 1),
        )
        insert_axis = cylinder_axis(
            f.m4_insert_hole_diameter / 2.0 - 0.05,
            6.8,
            (x, y, e.lower_shell_top - 6.9),
            (0, 0, 1),
        )
        boss_ring = _annular_axis_witness(
            seam_outer_radius,
            seam_inner_radius,
            1.0,
            (x, y, e.lower_shell_top - 2.0),
            (0, 0, 1),
        )
        seam_axis_obstructions.append(
            _intersection_volume(clearance_axis, parts["upper_shell"])
            + _intersection_volume(insert_axis, parts["lower_shell"])
        )
        seam_boss_witnesses.append(_intersection_volume(boss_ring, parts["lower_shell"]))
    results.append(
        stack_result(
            "fastener stack: structural shell seam M4x18",
            "M4x18",
            f.structural_screw,
            f.structural_screw_length,
            18.0,
            seam_grip,
            7.0,
            seam_axis_obstructions,
            seam_boss_witnesses,
            seam_expected_ring,
        )
    )

    cover_axis_obstructions: list[float] = []
    cover_boss_witnesses: list[float] = []
    m3_outer_radius = f.m3_boss_diameter / 2.0 - 0.1
    m3_inner_radius = f.m3_insert_hole_diameter / 2.0 + 0.1
    m3_expected_ring = pi * (m3_outer_radius**2 - m3_inner_radius**2)
    cover_underside = pw.bottom_z + pw.outer_height
    column_mid_z = cover_underside - power_cover_boss_height(p) / 2.0
    for x, y in power_cover_fastener_positions(p):
        clearance_axis = cylinder_axis(
            f.m3_clearance_diameter / 2.0 - 0.05,
            pw.cover_thickness + 0.2,
            (x, y, cover_underside - 0.1),
            (0, 0, 1),
        )
        insert_axis = cylinder_axis(
            f.m3_insert_hole_diameter / 2.0 - 0.05,
            f.insert_depth - 0.2,
            (x, y, cover_underside - f.insert_depth + 0.1),
            (0, 0, 1),
        )
        column_ring = _annular_axis_witness(
            m3_outer_radius,
            m3_inner_radius,
            1.0,
            (x, y, column_mid_z),
            (0, 0, 1),
        )
        cover_axis_obstructions.append(
            _intersection_volume(clearance_axis, parts["power_compartment_cover"])
            + _intersection_volume(insert_axis, parts["power_compartment"])
        )
        cover_boss_witnesses.append(_intersection_volume(column_ring, parts["power_compartment"]))
    results.append(
        stack_result(
            "fastener stack: power-compartment cover M3x8",
            "M3x8",
            f.service_screw,
            pw.cover_screw_length,
            8.0,
            pw.cover_thickness,
            f.insert_depth,
            cover_axis_obstructions,
            cover_boss_witnesses,
            m3_expected_ring,
        )
    )
    return results


def mac_base_pad_stack_check(
    p: StationParameters,
    cradle: cq.Workplane,
    pad_template: cq.Workplane,
) -> CheckResult:
    """Verify the three base-pad pockets and their nominal finished support plane."""

    c = p.components
    retention = p.mac_retention
    cradle_top = c.mac_support_plane_z - 1.0
    pocket_floor = cradle_top - retention.base_pad_seat_depth
    pad_top = pocket_floor + retention.base_pad_thickness
    pad_xy = c.mac_width / 2.0 - 10.0
    positions = tuple(
        (x, y + c.mac_center_y)
        for x in (-pad_xy, pad_xy)
        for y in (-pad_xy, pad_xy)
        if not (x * c.mac_button_x_side > 0.0 and y > 0.0)
    )
    pocket_obstructions: list[float] = []
    floor_witnesses: list[float] = []
    # A central 10 x 10 mm witness avoids the deliberate adjacent base-boss
    # relief while proving that each compliant pad has a continuous load floor.
    expected_floor = 10.0 * 10.0 * 0.2
    for x, y in positions:
        pocket = box_at(
            14.6,
            14.6,
            retention.base_pad_seat_depth - 0.2,
            (x, y, pocket_floor + retention.base_pad_seat_depth / 2.0),
        )
        floor = box_at(10.0, 10.0, 0.2, (x, y, pocket_floor - 0.1))
        pocket_obstructions.append(_intersection_volume(pocket, cradle))
        floor_witnesses.append(_intersection_volume(floor, cradle))
    template_dims = bbox_dimensions(pad_template)
    passed = (
        len(positions) == 3
        and abs(pad_top - c.mac_support_plane_z) <= 0.01
        and abs(template_dims[2] - retention.base_pad_thickness) <= 0.01
        and template_dims[0] <= 15.0 - 0.2
        and template_dims[1] <= 15.0 - 0.2
        and max(pocket_obstructions) <= INTERSECTION_VOLUME_TOLERANCE_MM3
        and min(floor_witnesses) >= 0.98 * expected_floor
    )
    return _check(
        "Mac three-pad pocket/support-plane stack",
        passed,
        f"three 15 mm pockets are {retention.base_pad_seat_depth:.1f} mm deep with solid floors; "
        f"{retention.base_pad_thickness:.1f} mm pads finish at Z={pad_top:.1f} mm",
        f"positions={len(positions)}, pad top={pad_top:.3f}, template={template_dims}, "
        f"pocket obstructions={pocket_obstructions}, floor witnesses={floor_witnesses}",
    )


def router_support_stack_check(
    p: StationParameters,
    tray: cq.Workplane,
    pad_template: cq.Workplane,
) -> CheckResult:
    """Verify router lands, compliant-pad stack, and recessed screw heads."""

    c = p.components
    f = p.fasteners
    layout = packaging_layout(p)
    plate_thickness = 3.0
    plate_top = layout.router_tray_z + plate_thickness
    effective_pad_height = c.router_pad_thickness - c.router_pad_nominal_compression
    land_height = p.fits.equipment_clearance - effective_pad_height
    land_top = plate_top + land_height
    router_bottom = layout.router_center[2] - c.router_height / 2.0
    positions = router_support_pad_positions(p)
    land_volumes: list[float] = []
    land_probe_height = max(0.05, land_height - 0.1)
    expected_land = (c.router_pad_width - 0.4) * (c.router_pad_depth - 0.4) * land_probe_height
    pad_envelopes: list[cq.Workplane] = []
    for x, y in positions:
        land_witness = box_at(
            c.router_pad_width - 0.4,
            c.router_pad_depth - 0.4,
            land_probe_height,
            (x, y, plate_top + land_probe_height / 2.0),
        )
        land_volumes.append(_intersection_volume(land_witness, tray))
        pad_envelopes.append(
            box_at(
                c.router_pad_width,
                c.router_pad_depth,
                effective_pad_height,
                (x, y, land_top + effective_pad_height / 2.0),
            )
        )

    counterbore_obstructions: list[float] = []
    through_axis_obstructions: list[float] = []
    pad_counterbore_overlaps: list[float] = []
    for x, y in router_tray_fastener_positions(p):
        counterbore = cylinder_axis(
            f.m3_low_head_recess_diameter / 2.0 - 0.05,
            f.m3_low_head_recess_depth - 0.2,
            (x, y, plate_top - f.m3_low_head_recess_depth + 0.1),
            (0, 0, 1),
        )
        through_axis = cylinder_axis(
            f.m3_clearance_diameter / 2.0 - 0.05,
            plate_thickness + 0.2,
            (x, y, layout.router_tray_z - 0.1),
            (0, 0, 1),
        )
        counterbore_obstructions.append(_intersection_volume(counterbore, tray))
        through_axis_obstructions.append(_intersection_volume(through_axis, tray))
        pad_counterbore_overlaps.extend(_intersection_volume(counterbore, pad) for pad in pad_envelopes)

    template_dims = bbox_dimensions(pad_template)
    residual_floor = plate_thickness - f.m3_low_head_recess_depth
    passed = (
        len(positions) == 4
        and len(counterbore_obstructions) == 4
        and land_height > 0.0
        and abs(land_top + effective_pad_height - router_bottom) <= 0.01
        and abs(template_dims[0] - c.router_pad_width) <= 0.01
        and abs(template_dims[1] - c.router_pad_depth) <= 0.01
        and abs(template_dims[2] - c.router_pad_thickness) <= 0.01
        and residual_floor >= 0.8
        and min(land_volumes) >= 0.95 * expected_land
        and max(counterbore_obstructions) <= INTERSECTION_VOLUME_TOLERANCE_MM3
        and max(through_axis_obstructions) <= INTERSECTION_VOLUME_TOLERANCE_MM3
        and max(pad_counterbore_overlaps, default=0.0) <= INTERSECTION_VOLUME_TOLERANCE_MM3
    )
    return _check(
        "RUTM30 four-pad support/counterbore stack",
        passed,
        f"four {land_height:.1f} mm lands plus {c.router_pad_thickness:.1f} mm pads at "
        f"{c.router_pad_nominal_compression:.1f} mm compression finish at router Z={router_bottom:.1f}; "
        f"four {f.m3_low_head_recess_depth:.1f} mm counterbores leave {residual_floor:.1f} mm floor",
        f"land volumes={land_volumes}, pad template={template_dims}, plane error="
        f"{land_top + effective_pad_height - router_bottom:.3f}, counterbore obstructions="
        f"{counterbore_obstructions}, through-axis obstructions={through_axis_obstructions}, "
        f"pad/counterbore overlaps={pad_counterbore_overlaps}",
    )


def extension_mount_hole_checks(
    p: StationParameters,
    rear_panel: cq.Workplane,
    router_bezel: cq.Workplane,
) -> list[CheckResult]:
    """Prove two clear, materially supported M3 axes per provisional extension."""

    e = p.enclosure
    f = p.fasteners
    axis_radius = f.m3_clearance_diameter / 2.0 - 0.05
    ring_outer = f.m3_clearance_diameter / 2.0 + 1.2
    ring_inner = f.m3_clearance_diameter / 2.0 + 0.1

    def panel_result(
        name: str,
        part: cq.Workplane,
        positions: tuple[tuple[float, float], ...],
        y0: float,
        thickness: float,
    ) -> CheckResult:
        axis_obstructions: list[float] = []
        ring_witnesses: list[float] = []
        ring_length = thickness - 0.2
        expected_ring = pi * (ring_outer**2 - ring_inner**2) * ring_length
        for x, z in positions:
            axis = cylinder_axis(axis_radius, thickness + 0.2, (x, y0 - 0.1, z), (0, 1, 0))
            ring = _annular_axis_witness(
                ring_outer,
                ring_inner,
                ring_length,
                (x, y0 + 0.1, z),
                (0, 1, 0),
            )
            axis_obstructions.append(_intersection_volume(axis, part))
            ring_witnesses.append(_intersection_volume(ring, part))
        passed = (
            len(positions) == 4
            and max(axis_obstructions) <= INTERSECTION_VOLUME_TOLERANCE_MM3
            and min(ring_witnesses) >= 0.90 * expected_ring
        )
        return _check(
            name,
            passed,
            f"four clear M3 axes form two two-fastener patterns; surrounding panel annuli retain "
            f">=90% of a {ring_length:.1f} mm witness",
            f"positions={positions}, axis obstructions={axis_obstructions}, ring witnesses={ring_witnesses}, "
            f"expected ring={expected_ring:.3f}",
        )

    panel_y0 = e.depth / 2.0 - e.rear_panel_thickness
    mac_positions = mac_extension_mount_positions(p)
    mac_result = panel_result(
        "provisional HDMI/USB-C two-fastener extension holes",
        rear_panel,
        mac_positions,
        panel_y0,
        e.rear_panel_thickness,
    )

    bezel_face_thickness = 2.4
    bezel_face_y0 = e.depth / 2.0 - bezel_face_thickness
    router_positions = router_extension_mount_positions(p)
    router_result = panel_result(
        "provisional dual-RJ45 two-fastener extension holes",
        router_bezel,
        router_positions,
        bezel_face_y0,
        bezel_face_thickness,
    )
    return [mac_result, router_result]


def _exterior_parts(parts: Mapping[str, cq.Workplane]) -> list[cq.Workplane]:
    return [
        parts[name]
        for name in (
            "base",
            "lower_shell",
            "upper_shell",
            "rear_panel",
            "router_interface_bezel",
            "upper_cap",
            "wifi_dock_left",
            "wifi_dock_right",
            "logo_panel_left",
            "logo_panel_right",
        )
    ]


def geometry_checks(p: StationParameters = DEFAULT) -> list[CheckResult]:
    e = p.enclosure
    c = p.components
    results: list[CheckResult] = []
    parts = printable_parts(p)
    definitions = part_definitions()

    results.append(_check("square footprint", abs(e.width - e.depth) <= 0.01, f"{e.width:.1f} x {e.depth:.1f} mm", "width and depth differ"))
    ratio_error = abs(e.actual_height_ratio - e.target_height_ratio)
    results.append(
        _check(
            "exterior proportion",
            ratio_error <= 0.02,
            f"1 : 1 : {e.actual_height_ratio:.4f} (target {e.target_height_ratio:.2f})",
            f"height ratio error {ratio_error:.4f} exceeds 0.02",
        )
    )

    exterior = compound(_exterior_parts(parts))
    ext_dims = bbox_dimensions(exterior)
    results.append(
        _check(
            "fixed enclosure envelope",
            all(abs(a - b) <= 0.15 for a, b in zip(ext_dims, (e.width, e.depth, e.height))),
            f"{ext_dims[0]:.2f} x {ext_dims[1]:.2f} x {ext_dims[2]:.2f} mm; antennas and removable handle excluded",
            f"measured {ext_dims}, expected {(e.width, e.depth, e.height)}",
        )
    )

    for name, obj in parts.items():
        dims = bbox_dimensions(obj)
        fits = sorted(dims)[0] <= p.printer.build_x and sorted(dims)[1] <= p.printer.build_y and sorted(dims)[2] <= p.printer.build_z
        results.append(
            _check(
                f"build volume: {name}",
                fits,
                f"bounding box {dims[0]:.1f} x {dims[1]:.1f} x {dims[2]:.1f} mm fits 256 mm cube after orientation",
                f"bounding box {dims} cannot be oriented inside 256 mm cube",
            )
        )
        results.append(_check(f"valid solid: {name}", obj.val().isValid(), "OpenCascade shape is valid", "OpenCascade reports invalid shape"))
        definition = definitions[name]
        if definition.assembly_part:
            results.append(
                _check(
                    f"connected printable part: {name}",
                    len(obj.solids().vals()) == 1,
                    "one connected solid",
                    f"contains {len(obj.solids().vals())} disconnected solids",
                )
            )

    for name, obj in fit_coupons(p).items():
        dims = bbox_dimensions(obj)
        results.append(
            _check(
                f"coupon build volume: {name}",
                max(dims) <= p.printer.build_x,
                f"bounding box {dims[0]:.1f} x {dims[1]:.1f} x {dims[2]:.1f} mm",
                f"coupon bounding box {dims} exceeds printer",
            )
        )
        results.append(_check(f"coupon validity: {name}", obj.val().isValid(), "valid shape", "invalid shape"))

    results.extend(assembly_interference_checks(parts))

    results.append(
        _check(
            "minimum configured walls",
            min(e.wall, p.power.wall, p.wifi.clip_wall, p.logo.thickness) >= e.minimum_wall,
            f"minimum controlled wall is {min(e.wall, p.power.wall, p.wifi.clip_wall, p.logo.thickness):.2f} mm",
            "a controlled wall parameter is below the 2.4 mm limit",
        )
    )

    model = build_reference_model(p)
    shell_parts = [parts[name] for name in ("lower_shell", "upper_shell", "base", "upper_cap")]
    for name, equipment in model.equipment.items():
        collision = sum(_intersection_volume(equipment, shell) for shell in shell_parts)
        results.append(
            _check(
                f"equipment vs exterior shell: {name}",
                collision <= INTERSECTION_VOLUME_TOLERANCE_MM3,
                f"no shell intersection ({collision:.4f} mm^3 numerical residue)",
                f"intersection volume {collision:.3f} mm^3",
            )
        )
    results.extend(_equipment_mount_checks(parts, model.equipment))
    results.append(
        mac_vertical_retention_check(
            p,
            parts["mac_cradle"],
            model.equipment["mac_mini_m4"],
            parts["lower_shell"],
        )
    )
    results.append(
        mac_base_pad_stack_check(
            p,
            parts["mac_cradle"],
            parts["compliant_pad_template"],
        )
    )
    results.append(
        router_support_stack_check(
            p,
            parts["router_tray"],
            parts["router_compliant_pad_template"],
        )
    )
    results.extend(fastener_stack_checks(p, parts))
    results.extend(
        extension_mount_hole_checks(
            p,
            parts["rear_panel"],
            parts["router_interface_bezel"],
        )
    )
    results.append(c8_terminal_passage_check(p, parts["power_compartment"]))
    results.append(power_tie_bridge_floor_check(p, parts["power_compartment"]))
    results.append(mac_ac_gland_passage_check(p, parts["power_compartment"]))
    results.append(apv_top_service_mount_check(p, parts["power_compartment"]))
    results.append(power_shell_mount_access_check(p, parts["power_compartment"]))
    results.append(
        power_cover_column_check(
            p,
            parts["power_compartment"],
            parts["power_compartment_cover"],
        )
    )
    results.append(mac_ac_corridor_packaging_check(p, parts, model))

    intake = mac_intake_exclusion(p)
    intake_collision = _intersection_volume(intake, parts["base"]) + _intersection_volume(intake, parts["mac_cradle"])
    results.append(
        _check(
            "Mac annular intake exclusion",
            intake_collision <= INTERSECTION_VOLUME_TOLERANCE_MM3,
            "112 mm photo-derived exclusion ring is clear of base and cradle",
            f"intake intersection volume {intake_collision:.3f} mm^3",
        )
    )
    results.append(rear_service_removal_sweep_check(p, parts, model))
    results.append(mac_cradle_downward_removal_sweep_check(p, parts, model))
    results.append(router_rearward_removal_sweep_check(p, parts, model))

    button_path, probe_diameter = _mac_button_swept_path(p, model.clearances["mac_button"])
    button_blockers = {
        name: _intersection_volume(button_path, parts[name])
        for name in ("base", "mac_cradle", "lower_shell", "rear_panel")
    }
    button_collision = sum(button_blockers.values())
    blocker_detail = ", ".join(f"{name}={volume:.3f}" for name, volume in button_blockers.items())
    results.append(
        _check(
            "Mac power-button continuous swept path",
            button_collision <= INTERSECTION_VOLUME_TOLERANCE_MM3,
            f"continuous Ø{probe_diameter:.1f} mm lower-rear probe reaches the button with no printed-part obstruction",
            f"Ø{probe_diameter:.1f} mm swept probe intersects printed parts by {button_collision:.3f} mm^3 ({blocker_detail})",
        )
    )

    mains = model.interfaces["mains_keepout"]
    mac_branch = model.interfaces["mac_ac_branch_corridor"]
    selv = model.interfaces["low_voltage_lane"]
    sep_collision = _intersection_volume(mains, selv) + _intersection_volume(mac_branch, selv)
    results.append(
        CheckResult(
            "mains/SELV modeled keep-out non-overlap",
            "WARN" if sep_collision <= 0.05 else "FAIL",
            (
                f"modeled APV/mains and Mac-AC corridor envelopes overlap the low-voltage keep-out by "
                f"{sep_collision:.4f} mm^3; disjoint geometry is packaging evidence only, not proof of a "
                "physical barrier, insulation system, conductor restraint, or regulatory separation"
                if sep_collision <= 0.05
                else f"modeled power-route keep-outs overlap the low-voltage lane by {sep_collision:.3f} mm^3"
            ),
        )
    )

    rf_window = 5.0 * c.router_sma_pitch + c.router_sma_clearance_diameter
    results.append(
        _check(
            "RF aperture analytic connector-centre span",
            rf_window >= 88.0 and c.router_connector_depth >= 30.0,
            f"radiused {rf_window:.1f} mm opening spans all six official connector axes; "
            "this does not establish plug, finger, or tool access",
            "RF opening does not span the six official connector axes",
        )
    )

    for name in ("logo_panel_left", "logo_panel_right"):
        dims = bbox_dimensions(parts[name])
        square = abs(dims[1] - dims[2]) <= 0.02
        results.append(
            _check(
                f"square replaceable panel: {name}",
                square and abs(dims[1] - p.logo.size) <= 0.05,
                f"{dims[1]:.2f} x {dims[2]:.2f} mm face; {p.fits.logo_panel_per_side:.2f} mm/side rail clearance",
                f"panel face dimensions are {dims[1]:.3f} x {dims[2]:.3f} mm",
            )
        )

    results.append(handle_structural_mount_check(p, parts))
    results.append(shell_seam_access_check(p, parts))
    results.append(rear_sill_reinforcement_check(p, parts["lower_shell"]))
    results.append(logo_screw_mount_check(p, parts))
    results.append(wifi_dock_capture_geometry_check(p))

    results.append(
        CheckResult(
            "RUTM30 reference provenance",
            "PASS" if router_source_kind() == "official_teltonika_step" else "WARN",
            router_source_kind(),
        )
    )
    results.append(
        CheckResult(
            "Ethernet topology concurrency",
            "WARN",
            "Two native router ports exist; one is normally occupied by the internal Mac link. Both extension positions are serviceable, but two simultaneous external links plus the Mac require an approved active switch/topology change.",
        )
    )
    for pending in (
        "physical Mac/button/intake fit coupon",
        "Mac vertical-retainer pad/preload, release-force, and shake-cycle test",
        "as-built cable/forbidden-geometry routing and bend mock-up",
        "APV lead bends and internal branch-hardware packaging",
        "physical RF plug/finger/tool access",
        "local minimum-wall scan of all generated geometry",
        "Wi-Fi dock carry/shake/cable-load and 20-cycle test",
        "logo panel M3 joint torque/rattle/service-cycle test",
        "Mac AC branch hardware, protected conduit/restraint, and qualified separation proof",
        "thermal comparison under representative load",
        "4x measured assembled-mass handle proof-load/creep test",
        "qualified mains design and electrical safety review",
    ):
        results.append(CheckResult(pending, "PENDING", "Requires physical hardware/test; CAD does not claim completion."))
    return results


def mesh_checks(stl_dir: Path) -> list[CheckResult]:
    results: list[CheckResult] = []
    for path in sorted(stl_dir.glob("*.stl")):
        loaded = trimesh.load(path, force="scene")
        geometries = list(loaded.geometry.values()) if isinstance(loaded, trimesh.Scene) else [loaded]
        watertight = bool(geometries) and all(mesh.is_watertight for mesh in geometries)
        winding = bool(geometries) and all(mesh.is_winding_consistent for mesh in geometries)
        results.append(
            _check(
                f"watertight STL: {path.name}",
                watertight and winding,
                f"{len(geometries)} manifold mesh body/bodies; consistent winding",
                f"watertight={watertight}, winding_consistent={winding}",
            )
        )
    if not results:
        results.append(CheckResult("STL mesh validation", "WARN", "No STL files found; run export first."))
    return results


def write_results(results: Iterable[CheckResult], json_path: Path, markdown_path: Path) -> None:
    rows = list(results)
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps([asdict(row) for row in rows], indent=2) + "\n")
    counts = {status: sum(row.status == status for row in rows) for status in ("PASS", "WARN", "PENDING", "FAIL")}
    lines = [
        "# Validation results",
        "",
        "Generated by `deployment_station.validation`; dimensions are millimetres.",
        "",
        f"Summary: {counts['PASS']} PASS, {counts['WARN']} WARN, {counts['PENDING']} PENDING, {counts['FAIL']} FAIL.",
        "",
        "| Check | Status | Detail |",
        "| --- | --- | --- |",
    ]
    for row in rows:
        lines.append(f"| {row.name} | {row.status} | {row.detail.replace('|', '/')} |")
    lines.extend(
        [
            "",
            "A PASS is a computational geometry/mesh result only. PENDING tests require physical hardware or competent electrical review. WARN records a known design decision or unresolved system-level conflict and is not silently promoted to PASS.",
            "",
        ]
    )
    markdown_path.write_text("\n".join(lines))


def main() -> int:
    root = Path(__file__).resolve().parents[2]
    results = geometry_checks(DEFAULT) + mesh_checks(root / "exports" / "stl")
    write_results(results, root / "reports" / "validation.json", root / "reports" / "validation_results.md")
    failures = [result for result in results if result.status == "FAIL"]
    print(f"validation: {len(results)} checks, {len(failures)} failures")
    for failure in failures:
        print(f"FAIL {failure.name}: {failure.detail}")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
