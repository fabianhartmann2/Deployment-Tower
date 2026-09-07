"""Reinforced cap and positively screw-mounted removable handle."""

from __future__ import annotations

import cadquery as cq

from .geometry import box_at, cylinder_axis, rounded_rect_prism
from .parameters import DEFAULT, StationParameters


def cap_fastener_positions(p: StationParameters = DEFAULT) -> tuple[tuple[float, float], ...]:
    """General cap screws plus two screws directly over the handle spines."""

    del p
    return (
        (-61.0, -61.0),
        (61.0, -61.0),
        (-61.0, 61.0),
        (61.0, 61.0),
        (-54.0, -68.0),
        (54.0, -68.0),
    )


def handle_mount_fastener_positions(p: StationParameters = DEFAULT) -> tuple[tuple[float, float], ...]:
    """Four M3 axes, two outside each handle leg for direct tool access."""

    h = p.handle
    anchor_y = -42.0
    return tuple(
        (anchor_x + offset_x, anchor_y)
        for anchor_x in (-h.anchor_spacing / 2.0, h.anchor_spacing / 2.0)
        for offset_x in (-h.fastener_offset_x, h.fastener_offset_x)
    )


def upper_cap(p: StationParameters = DEFAULT) -> cq.Workplane:
    e = p.enclosure
    h = p.handle
    f = p.fasteners
    z0 = e.shell_top
    cap = rounded_rect_prism(e.width, e.depth, e.cap_height, e.outer_corner_radius, z0)

    # Hollow underside leaves a 4 mm top skin and a substantial perimeter frame.
    cavity = rounded_rect_prism(e.width - 18.0, e.depth - 18.0, e.cap_height - 4.0, e.outer_corner_radius - 9.0, z0 - 1.0)
    cap = cap.cut(cavity)
    anchor_y = -42.0
    # A full-width crossmember and two solid local bearing pads carry the handle
    # feet into both side walls and the reinforced upper-shell ribs.  The pads
    # fill the cap below each foot instead of loading the 4 mm top skin alone.
    cap = cap.union(box_at(e.width - 16.0, 12.0, 8.0, (0.0, anchor_y, z0 + 4.0)))
    for x in (-h.anchor_spacing / 2.0, h.anchor_spacing / 2.0):
        bearing_pad = box_at(
            h.foot_width + 6.0,
            h.foot_depth + 6.0,
            e.cap_height - 4.0,
            (x, anchor_y, z0 + (e.cap_height - 4.0) / 2.0),
        )
        longitudinal_tie = box_at(12.0, h.foot_depth + 12.0, 8.0, (x, anchor_y, z0 + 4.0))
        cap = cap.union(bearing_pad).union(longitudinal_tie)

    # Four blind top-entry M3 insert pilots sit inside full-depth bosses.  The
    # two axes per foot are outside the leg footprint, so every low-head screw
    # seats on the full 5 mm foot and remains accessible after installation.
    for x, y in handle_mount_fastener_positions(p):
        boss = (
            cq.Workplane("XY")
            .center(x, y)
            .circle(f.m3_boss_diameter / 2.0)
            .extrude(e.cap_height)
            .translate((0, 0, z0))
        )
        insert = cylinder_axis(
            f.m3_insert_hole_diameter / 2.0,
            f.insert_depth + 0.2,
            (x, y, e.height + 0.1),
            (0, 0, -1),
        )
        cap = cap.union(boss).cut(insert)

    # Four perimeter screws retain the cap; two additional screws sit directly
    # over continuous front structural spines in the upper/lower shells.  Each
    # hole has an integral compression sleeve down to the shell-boss datum, so a
    # tightened screw bears through solid material instead of flexing the 4 mm
    # top skin across the hollow cap cavity.
    sleeve_height = e.cap_height - 4.0
    for x, y in cap_fastener_positions(p):
        sleeve = (
            cq.Workplane("XY")
            .center(x, y)
            .circle(f.m4_boss_diameter / 2.0)
            .extrude(sleeve_height)
            .translate((0, 0, z0))
        )
        cap = cap.union(sleeve)
        hole = cq.Workplane("XY").center(x, y).circle(f.m4_clearance_diameter / 2.0).extrude(e.cap_height + 2.0).translate((0, 0, z0 - 1.0))
        cap = cap.cut(hole)
    return cap


def removable_handle(p: StationParameters = DEFAULT) -> cq.Workplane:
    e = p.enclosure
    h = p.handle
    f = p.fasteners
    anchor_y = -42.0
    handle = cq.Workplane("XY")
    leg_center_z = e.height + h.rise / 2.0
    for x in (-h.anchor_spacing / 2.0, h.anchor_spacing / 2.0):
        foot = box_at(
            h.foot_width,
            h.foot_depth,
            h.foot_thickness,
            (x, anchor_y, e.height + h.foot_thickness / 2.0),
        )
        leg = box_at(h.leg_width, h.leg_depth, h.rise, (x, anchor_y, leg_center_z))
        handle = handle.union(foot).union(leg)
        # Broad front/rear stiffening ribs spread leg bending across nearly the
        # full foot width without obstructing the two screw heads on its centreline.
        for offset_y in (-h.leg_depth / 2.0 - 1.5, h.leg_depth / 2.0 + 1.5):
            gusset = box_at(
                h.foot_width - 6.0,
                3.0,
                12.0,
                (x, anchor_y + offset_y, e.height + 6.0),
            )
            handle = handle.union(gusset)

    for x, y in handle_mount_fastener_positions(p):
        clearance = cylinder_axis(
            f.m3_clearance_diameter / 2.0,
            h.foot_thickness + 1.0,
            (x, y, e.height - 0.5),
            (0, 0, 1),
        )
        handle = handle.cut(clearance)

    grip_z = e.height + h.rise + h.grip_height / 2.0
    grip = rounded_rect_prism(h.grip_span, h.grip_depth, h.grip_height, min(7.0, h.grip_depth / 2.0 - 0.5), grip_z - h.grip_height / 2.0).translate((0, anchor_y, 0))
    handle = handle.union(grip)
    # Under-grip relief improves finger comfort without thinning the loaded top.
    relief = rounded_rect_prism(h.grip_span - 28.0, h.grip_depth + 2.0, 7.0, 4.0, grip_z - h.grip_height / 2.0 - 1.0).translate((0, anchor_y, 0))
    return handle.cut(relief)


def handle_mount_coupon(p: StationParameters = DEFAULT) -> cq.Workplane:
    """One-foot M3 mounting coupon with the production grip and pilot depths."""

    h = p.handle
    f = p.fasteners
    cap_sample = box_at(h.foot_width + 8.0, h.foot_depth + 4.0, 12.0, (0.0, 0.0, 6.0))
    foot_sample = box_at(h.foot_width, h.foot_depth, h.foot_thickness, (54.0, 0.0, h.foot_thickness / 2.0))
    for x in (-h.fastener_offset_x, h.fastener_offset_x):
        insert = cylinder_axis(
            f.m3_insert_hole_diameter / 2.0,
            f.insert_depth + 0.2,
            (x, 0.0, 12.1),
            (0, 0, -1),
        )
        cap_sample = cap_sample.cut(insert)
        clearance = cylinder_axis(
            f.m3_clearance_diameter / 2.0,
            h.foot_thickness + 1.0,
            (54.0 + x, 0.0, -0.5),
            (0, 0, 1),
        )
        foot_sample = foot_sample.cut(clearance)
    return cap_sample.union(foot_sample)
