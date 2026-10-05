"""Externally replaceable square logo panels and generation template."""

from __future__ import annotations

import cadquery as cq

from .geometry import box_at, cylinder_axis, rounded_panel_yz
from .parameters import DEFAULT, StationParameters


def logo_magnet_positions(side: str, p: StationParameters = DEFAULT) -> tuple[tuple[float, float, float], ...]:
    """Return the two concealed magnet axes for one logo panel."""

    if side not in {"left", "right"}:
        raise ValueError("side must be 'left' or 'right'")
    sign = 1.0 if side == "right" else -1.0
    return tuple(
        (sign * p.enclosure.width / 2.0, y, p.logo.center_z)
        for y in (-p.logo.fastener_offset_y, p.logo.fastener_offset_y)
    )


def logo_mount_positions(side: str, p: StationParameters = DEFAULT) -> tuple[tuple[float, float, float], ...]:
    """Compatibility alias for the former screw-axis API."""

    return logo_magnet_positions(side, p)


def logo_panel(side: str, p: StationParameters = DEFAULT, embossed: bool = False) -> cq.Workplane:
    """Create a left/right blank panel, optionally with an abstract raised mark."""

    if side not in {"left", "right"}:
        raise ValueError("side must be 'left' or 'right'")
    e = p.enclosure
    logo = p.logo
    sign = 1 if side == "right" else -1
    inner_face = sign * (e.width / 2.0 - logo.thickness)
    panel = rounded_panel_yz(
        logo.size,
        logo.size,
        logo.thickness,
        logo.corner_radius,
        inner_face,
        0.0,
        logo.center_z,
        sign,
    )
    # Two 6 x 1.5 mm magnets enter from the hidden face and leave roughly
    # 0.7 mm cosmetic skin.  The surrounding shell recess locates the panel,
    # so no extra ledge, visible screw, or finger notch is needed.
    v = p.prototype_v4
    pocket_diameter = v.magnet_diameter + v.magnet_pocket_diametral_clearance
    pocket_depth = v.panel_magnet_thickness + v.magnet_pocket_depth_allowance
    for _x, y, z in logo_magnet_positions(side, p):
        pocket = cylinder_axis(
            pocket_diameter / 2.0,
            pocket_depth + 0.1,
            (inner_face - sign * 0.1, y, z),
            (sign, 0, 0),
        )
        panel = panel.cut(pocket)

    if embossed:
        outer_x = sign * e.width / 2.0
        mark_x = sign * (e.width / 2.0 + logo.emboss_height / 2.0)
        # Neutral three-bar sample mark; callers can replace this block with text,
        # SVG-derived wires, an engraving cut, or multibody inlay geometry.
        bars = [
            box_at(logo.emboss_height, 7.0, 34.0, (mark_x, -12.0, logo.center_z)),
            box_at(logo.emboss_height, 7.0, 24.0, (mark_x, 0.0, logo.center_z)),
            box_at(logo.emboss_height, 7.0, 14.0, (mark_x, 12.0, logo.center_z)),
        ]
        for bar in bars:
            panel = panel.union(bar)
    return panel


def blank_logo_panel(p: StationParameters = DEFAULT) -> cq.Workplane:
    return logo_panel("right", p, embossed=False)


def example_embossed_logo_panel(p: StationParameters = DEFAULT) -> cq.Workplane:
    return logo_panel("right", p, embossed=True)


def logo_mount_coupon(p: StationParameters = DEFAULT) -> cq.Workplane:
    """Two-hole logo joint coupon for insert, screw, and panel seating tests."""

    logo = p.logo
    f = p.fasteners
    receiver = box_at(10.0, 32.0, 18.0, (5.0, 0.0, 9.0))
    panel = box_at(logo.thickness, 32.0, 18.0, (22.0, 0.0, 9.0))
    for y in (-8.0, 8.0):
        insert = cylinder_axis(
            f.m3_insert_hole_diameter / 2.0,
            f.insert_depth + 0.7,
            (10.2, y, 9.0),
            (-1, 0, 0),
        )
        clearance = cylinder_axis(
            f.m3_clearance_diameter / 2.0,
            logo.thickness + 0.8,
            (20.4, y, 9.0),
            (1, 0, 0),
        )
        receiver = receiver.cut(insert)
        panel = panel.cut(clearance)
    return receiver.union(panel)
