"""Independently removable RUTM30 tray."""

from __future__ import annotations

import cadquery as cq

from .geometry import box_at, rounded_rect_prism
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
    # The router still slides rearward once the two rear latch fingers are spread.
    router_bottom = z0 + plate_h + p.fits.equipment_clearance
    router_top = router_bottom + c.router_height
    ledge_bottom = router_top + 0.6
    rail_height = ledge_bottom - (z0 + plate_h)
    rail_z = z0 + plate_h + rail_height / 2.0
    rail_x = c.router_width / 2.0 + p.fits.equipment_clearance + 1.5
    for side in (-1, 1):
        rail = box_at(3.0, c.router_depth - 8.0, rail_height, (x0 + side * rail_x, y0 - 1.0, rail_z))
        ledge = box_at(5.0, c.router_depth - 20.0, 3.0, (x0 + side * (rail_x - 2.5), y0 - 4.0, ledge_bottom + 1.5))
        latch = box_at(3.0, 2.4, 25.0, (x0 + side * rail_x, y0 + c.router_depth / 2.0 + 1.2, z0 + plate_h + 12.25))
        nib = box_at(5.0, 2.4, 6.0, (x0 + side * (rail_x - 2.5), y0 + c.router_depth / 2.0 + 1.2, router_bottom + c.router_height / 2.0))
        tray = tray.union(rail).union(ledge).union(latch).union(nib)
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
