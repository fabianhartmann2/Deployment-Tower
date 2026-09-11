"""Removable recessed base with airflow and concealed button approach."""

from __future__ import annotations

import cadquery as cq

from .geometry import box_at, rounded_rect_prism
from .parameters import DEFAULT, StationParameters


def base(p: StationParameters = DEFAULT) -> cq.Workplane:
    e = p.enclosure
    i = p.interfaces
    f = p.fasteners
    # Dark base is visually inset 1.5 mm per side.  The skin starts at the top of
    # the feet so the complete exterior height remains the Z=0..height envelope.
    inset = 1.5
    skin_h = e.base_height - e.foot_height
    part = rounded_rect_prism(
        e.width - 2.0 * inset,
        e.depth - 2.0 * inset,
        skin_h,
        e.outer_corner_radius - inset,
        e.foot_height,
    )
    intake = cq.Workplane("XY").circle(e.underside_intake_opening_diameter / 2.0).extrude(skin_h + 2.0).translate(
        (0, p.components.mac_center_y, e.foot_height - 1.0)
    )
    part = part.cut(intake)

    # Four desk feet keep every opening and the native button above the desk.
    foot_xy = e.width / 2.0 - 20.0
    for x in (-foot_xy, foot_xy):
        for y in (-foot_xy, foot_xy):
            foot = cq.Workplane("XY").center(x, y).circle(7.0).extrude(e.foot_height)
            part = part.union(foot)

    # A rear/underside tunnel terminates below the photo-derived button centre.
    c = p.components
    bx = c.mac_button_x_side * (c.mac_width / 2.0 - c.mac_button_edge_offset_x)
    by = c.mac_center_y + c.mac_depth / 2.0 - c.mac_button_edge_offset_y
    reach = e.depth / 2.0 + 2.0 - by
    well = box_at(i.finger_well_width, reach, e.base_height + 2.0, (bx, by + reach / 2.0, e.base_height / 2.0))
    tip = cq.Workplane("XY").center(bx, by).circle(i.finger_well_width / 2.0).extrude(e.base_height + 2.0).translate(
        (0, 0, -1.0)
    )
    part = part.cut(well.union(tip))

    # Captive screw clearances; matching inserts are in the lower shell bosses.
    screw_xy = e.width / 2.0 - 13.0
    for x in (-screw_xy, screw_xy):
        for y in (-screw_xy, screw_xy):
            hole = cq.Workplane("XY").center(x, y).circle(f.m3_clearance_diameter / 2.0).extrude(e.base_height + 2.0)
            part = part.cut(hole)
    return part


def mac_button_coupon(p: StationParameters = DEFAULT) -> cq.Workplane:
    i = p.interfaces
    block = rounded_rect_prism(54.0, 58.0, 12.0, 7.0)
    well = box_at(i.finger_well_width, i.finger_well_reach, 14.0, (0.0, 15.0, 6.0))
    tip = cq.Workplane("XY").circle(i.finger_well_width / 2.0).extrude(14.0).translate((0, -4.0, -1.0))
    return block.cut(well.union(tip))
