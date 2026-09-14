"""Independently removable RUTM30 tray."""

from __future__ import annotations

import cadquery as cq

from .geometry import box_at, cylinder_axis, rounded_rect_prism
from .layout import packaging_layout
from .parameters import DEFAULT, StationParameters


def router_support_pad_positions(p: StationParameters = DEFAULT) -> tuple[tuple[float, float], ...]:
    """Four support lands clear of vents and tray-fastener heads."""

    layout = packaging_layout(p)
    x0, y0, _ = layout.router_center
    return tuple((x0 + x, y0 + y) for y in (-24.0, 24.0) for x in (-45.0, 45.0))


def router_tray_fastener_positions(p: StationParameters = DEFAULT) -> tuple[tuple[float, float], ...]:
    layout = packaging_layout(p)
    x0, y0, _ = layout.router_center
    plate_d = p.components.router_depth + 4.0
    row = plate_d / 2.0 - 6.0
    return tuple((x, y) for y in (y0 - row, y0 + row) for x in (x0 - 42.0, x0 + 42.0))


def router_rear_retainer_screw_positions(
    p: StationParameters = DEFAULT,
) -> tuple[tuple[float, float, float], ...]:
    """Two top-access M3 axes for the adjustable rigid corner retainers."""

    c = p.components
    layout = packaging_layout(p)
    x0, _y0, _ = layout.router_center
    z = layout.router_tray_z + 3.0 + 9.0
    return tuple(
        (x0 + side * c.router_rear_retainer_screw_x, c.router_rear_retainer_screw_y, z)
        for side in (-1, 1)
    )


def router_rear_retainer(side: str, p: StationParameters = DEFAULT) -> cq.Workplane:
    """One rigid rear corner stop, installed after the router with an M3 screw."""

    if side not in {"left", "right"}:
        raise ValueError("side must be 'left' or 'right'")
    c = p.components
    f = p.fasteners
    sign = -1.0 if side == "left" else 1.0
    layout = packaging_layout(p)
    _x0, y0, _z0 = layout.router_center
    x, screw_y, _z = router_rear_retainer_screw_positions(p)[0 if side == "left" else 1]
    thickness = c.router_rear_retainer_thickness
    height = c.router_rear_retainer_height
    chassis_rear = y0 + c.router_depth / 2.0 - c.router_rear_chassis_correction
    face_y = chassis_rear + c.router_rear_retainer_clearance
    router_bottom = layout.router_tray_z + 3.0 + p.fits.equipment_clearance

    # A narrow vertical tongue stops the rear chassis corner without entering
    # the outer SMA connector envelope.  The outside top arm carries a long slot
    # so the owner can fine-adjust the stop around the physically reported
    # five-millimetre correction without approaching the rear panel.
    tongue_x = sign * (c.router_width / 2.0 - 2.5)
    tongue = box_at(5.0, thickness, height, (tongue_x, face_y + thickness / 2.0, router_bottom + height / 2.0))
    arm_inner_x = c.router_width / 2.0 - 0.5
    arm_outer_x = abs(x) + 5.0
    arm_x = sign * ((arm_inner_x + arm_outer_x) / 2.0)
    arm_width = arm_outer_x - arm_inner_x
    arm_y0 = face_y
    arm_y1 = screw_y + c.router_rear_retainer_adjustment + f.m3_clearance_diameter / 2.0 + 1.5
    arm = box_at(
        arm_width,
        arm_y1 - arm_y0,
        3.0,
        (arm_x, (arm_y0 + arm_y1) / 2.0, router_bottom + height - 1.0),
    )
    # Extend only the portion outside the official 100 mm router width.  This
    # leaves solid bearing material around the forward end of the adjustment
    # slot without moving any plastic into the router chassis envelope.
    slot_bearing_y0 = screw_y - c.router_rear_retainer_adjustment - f.m3_clearance_diameter / 2.0 - 1.8
    outside_pad_x0 = c.router_width / 2.0 + 1.0
    outside_pad_x1 = arm_outer_x
    outside_pad = box_at(
        outside_pad_x1 - outside_pad_x0,
        arm_y1 - slot_bearing_y0,
        3.0,
        (
            sign * ((outside_pad_x0 + outside_pad_x1) / 2.0),
            (slot_bearing_y0 + arm_y1) / 2.0,
            router_bottom + height - 1.0,
        ),
    )
    part = tongue.union(arm).union(outside_pad)

    slot_length = f.m3_clearance_diameter + 2.0 * c.router_rear_retainer_adjustment
    slot_box = box_at(
        f.m3_clearance_diameter,
        slot_length - f.m3_clearance_diameter,
        5.0,
        (x, screw_y, router_bottom + height - 1.0),
    )
    slot_front = cylinder_axis(
        f.m3_clearance_diameter / 2.0,
        5.0,
        (x, screw_y - (slot_length - f.m3_clearance_diameter) / 2.0, router_bottom + height - 4.0),
        (0.0, 0.0, 1.0),
    )
    slot_rear = cylinder_axis(
        f.m3_clearance_diameter / 2.0,
        5.0,
        (x, screw_y + (slot_length - f.m3_clearance_diameter) / 2.0, router_bottom + height - 4.0),
        (0.0, 0.0, 1.0),
    )
    return part.cut(slot_box).cut(slot_front).cut(slot_rear)


def router_tray(p: StationParameters = DEFAULT) -> cq.Workplane:
    c = p.components
    f = p.fasteners
    layout = packaging_layout(p)
    plate_w = c.router_width + 20.0
    # The router is biased rearward for direct RF access.  A close-fitting tray
    # avoids colliding with the removable rear panel while leaving its native
    # front RJ45 plugs room to turn into the side cable lane.
    plate_d = c.router_depth + 4.0
    plate_h = 3.0
    x0, y0, _ = layout.router_center
    z0 = layout.router_tray_z
    tray = rounded_rect_prism(plate_w, plate_d, plate_h, 6.0, z0).translate((x0, y0, 0.0))

    # Broad vents avoid creating a hot shelf while leaving longitudinal load ribs.
    for x in (x0 - 32.0, x0, x0 + 32.0):
        vent = box_at(18.0, 62.0, plate_h + 2.0, (x, y0 - 4.0, z0 + plate_h / 2.0))
        tray = tray.cut(vent)

    # Four printed lands carry replaceable compliant pads up to the official
    # router-bottom datum.  The pad thickness includes a small provisional
    # compression; the hardware fit and preload remain a physical test item.
    effective_pad = c.router_pad_thickness - c.router_pad_nominal_compression
    land_height = p.fits.equipment_clearance - effective_pad
    if land_height <= 0.0:
        raise ValueError("router pad stack leaves no positive printed support land")
    for x, y in router_support_pad_positions(p):
        land = rounded_rect_prism(c.router_pad_width, c.router_pad_depth, land_height, 1.5, z0 + plate_h).translate((x, y, 0.0))
        tray = tray.union(land)

    # Tall side guides and inward top ledges provide positive vertical retention.
    # The router still slides rearward once the two screw-mounted stops are removed.
    router_bottom = z0 + plate_h + p.fits.equipment_clearance
    router_top = router_bottom + c.router_height
    ledge_bottom = router_top + 0.6 - c.router_top_ledge_inset
    rail_height = ledge_bottom - (z0 + plate_h)
    rail_z = z0 + plate_h + rail_height / 2.0
    rail_x = c.router_width / 2.0 + p.fits.equipment_clearance + 1.5 - c.router_side_guide_inset
    for side in (-1, 1):
        # End the rails ahead of the separate stop's closed-slot bearing pad.
        rail = box_at(3.0, c.router_depth - 12.0, rail_height, (x0 + side * rail_x, y0 - 1.0, rail_z))
        ledge = box_at(5.0, c.router_depth - 20.0, 3.0, (x0 + side * (rail_x - 2.5), y0 - 4.0, ledge_bottom + 1.5))
        tray = tray.union(rail).union(ledge)

    # Robust vertical M3 insert towers replace the failed rear flexures.
    # They remain outside the router width and let the corrected corner stops
    # be fine-adjusted before their screws are tightened.
    for x, screw_y, _screw_z in router_rear_retainer_screw_positions(p):
        boss = (
            cq.Workplane("XY")
            .center(x, screw_y)
            .circle(4.5)
            .extrude(9.0)
            .translate((0.0, 0.0, z0 + plate_h))
        )
        insert = (
            cq.Workplane("XY")
            .center(x, screw_y)
            .circle(f.m3_insert_hole_diameter / 2.0)
            .extrude(5.7)
            .translate((0.0, 0.0, z0 + plate_h + 3.4))
        )
        web = box_at(5.0, 13.0, 9.0, (x, screw_y - 5.0, z0 + plate_h + 4.5))
        tray = tray.union(boss).union(web).cut(insert)
    front_stop = box_at(c.router_width + 7.0, 3.0, 8.0, (x0, y0 - c.router_depth / 2.0 - 1.5, z0 + plate_h + 4.0))
    tray = tray.union(front_stop)

    # Rear-edge finger scallop is reachable as soon as the service panel is off.
    finger = cq.Workplane("XY").center(x0, y0 + plate_d / 2.0).circle(7.0).extrude(6.0).translate((0, 0, z0 - 1.0))
    tray = tray.cut(finger)

    # Four screws are exposed after the router slides out and enter insert bosses
    # on two shell-tied cross rails.
    for x, y in router_tray_fastener_positions(p):
        hole = cq.Workplane("XY").center(x, y).circle(f.m3_clearance_diameter / 2.0).extrude(plate_h + 2.0).translate((0, 0, z0 - 1.0))
        head_recess = (
            cq.Workplane("XY")
            .center(x, y)
            .circle(f.m3_low_head_recess_diameter / 2.0)
            .extrude(f.m3_low_head_recess_depth + 1.0)
            .translate((0, 0, z0 + plate_h - f.m3_low_head_recess_depth))
        )
        tray = tray.cut(hole).cut(head_recess)
    return tray


def router_compliant_pad_template(p: StationParameters = DEFAULT) -> cq.Workplane:
    """One replaceable router support pad; make four after material testing."""

    c = p.components
    return rounded_rect_prism(c.router_pad_width, c.router_pad_depth, c.router_pad_thickness, 1.5)
