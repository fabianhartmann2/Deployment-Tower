"""Reinforced cap and tool-free sliding T-lock handle."""

from __future__ import annotations

import cadquery as cq

from .geometry import box_at, rounded_rect_prism
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
    # Cross members connect each lock to both side walls and the reinforced upper
    # shell ribs.  They are integral to the cap, not cosmetic surface features.
    cap = cap.union(box_at(e.width - 16.0, 12.0, 8.0, (0.0, anchor_y, z0 + 4.0)))
    for x in (-h.anchor_spacing / 2.0, h.anchor_spacing / 2.0):
        cap = cap.union(box_at(12.0, 32.0, 8.0, (x, -56.0, z0 + 4.0)))
        boss = cq.Workplane("XY").center(x, anchor_y).circle(h.insert_boss_diameter / 2.0).extrude(e.cap_height).translate((0, 0, z0))
        cap = cap.union(boss)

        # Two-stage T-slot: narrow mouth over a broader structural undercut.  A
        # top entry pocket allows the handle keys to drop in, then slide forward.
        slot_clear = p.fits.handle_lock_per_side
        lower = box_at(
            h.tongue_width + 2.0 * slot_clear,
            h.socket_length + 2.0 * slot_clear,
            h.tongue_height / 2.0 + slot_clear,
            (x, anchor_y, e.height - h.tongue_height * 0.72),
        )
        neck = box_at(
            h.dovetail_top_width + 2.0 * slot_clear,
            h.socket_length + 2.0 * slot_clear,
            h.tongue_height / 2.0 + 2.0,
            (x, anchor_y, e.height - h.tongue_height * 0.25),
        )
        entry = box_at(
            h.tongue_width + 2.0 * slot_clear + 2.0,
            12.0,
            h.socket_depth + 1.0,
            (x, anchor_y + h.socket_length / 2.0 + 4.0, e.height - h.socket_depth / 2.0),
        )
        cap = cap.cut(lower.union(neck).union(entry))

        # Longitudinal clearance lets the lateral spring pawl ride compressed
        # during insertion.  At the locked position it expands into the local
        # outer pocket; squeezing both exposed handle tabs retracts the pawls.
        side = 1.0 if x > 0 else -1.0
        arm_x = x + side * (h.leg_width / 2.0 - 0.4)
        pawl_channel = box_at(2.8, 45.0, 7.5, (arm_x, -34.0, e.height - 2.75))
        pawl_pocket = box_at(4.8, 5.2, 5.0, (x + side * (h.leg_width / 2.0 + 1.2), -51.0, e.height - 3.0))
        cap = cap.cut(pawl_channel.union(pawl_pocket))

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
    anchor_y = -42.0
    anchor_z = e.height - h.tongue_height
    handle = cq.Workplane("XY")
    leg_center_z = e.height + h.rise / 2.0
    for x in (-h.anchor_spacing / 2.0, h.anchor_spacing / 2.0):
        leg = box_at(h.leg_width, h.leg_depth, h.rise, (x, anchor_y, leg_center_z))
        crossbar = box_at(h.tongue_width, h.tongue_length, h.tongue_height / 2.0, (x, anchor_y, anchor_z + h.tongue_height / 4.0))
        neck = box_at(h.dovetail_top_width, h.tongue_length, h.tongue_height / 2.0 + 2.0, (x, anchor_y, anchor_z + h.tongue_height * 0.75))
        handle = handle.union(leg).union(crossbar).union(neck)
        # Exposed lateral squeeze arm and positive pawl.  The arm is anchored to
        # the leg above the cap, remains free below it, and retracts toward the
        # centre when the user pinches both release pads.
        side = 1.0 if x > 0 else -1.0
        arm_x = x + side * (h.leg_width / 2.0 - 0.4)
        arm = box_at(2.4, 7.0, 14.0, (arm_x, -49.0, e.height + 1.0))
        pawl = box_at(2.8, 4.0, 3.2, (x + side * (h.leg_width / 2.0 + 1.0), -51.0, e.height - 3.0))
        release_pad = box_at(3.2, 12.0, 10.0, (x + side * (h.leg_width / 2.0 + 0.6), -49.0, e.height + 6.0))
        handle = handle.union(arm).union(pawl).union(release_pad)

    grip_z = e.height + h.rise + h.grip_height / 2.0
    grip = rounded_rect_prism(h.grip_span, h.grip_depth, h.grip_height, min(7.0, h.grip_depth / 2.0 - 0.5), grip_z - h.grip_height / 2.0).translate((0, anchor_y, 0))
    handle = handle.union(grip)
    # Under-grip relief improves finger comfort without thinning the loaded top.
    relief = rounded_rect_prism(h.grip_span - 28.0, h.grip_depth + 2.0, 7.0, 4.0, grip_z - h.grip_height / 2.0 - 1.0).translate((0, anchor_y, 0))
    return handle.cut(relief)


def handle_lock_coupon(p: StationParameters = DEFAULT) -> cq.Workplane:
    h = p.handle
    clear = p.fits.handle_lock_per_side
    socket = rounded_rect_prism(42.0, 48.0, 10.0, 5.0)
    lower = box_at(h.tongue_width + 2.0 * clear, h.socket_length, h.tongue_height / 2.0 + clear, (0, 0, 7.4))
    neck = box_at(h.dovetail_top_width + 2.0 * clear, h.socket_length, h.tongue_height / 2.0 + 2.0, (0, 0, 10.0))
    entry = box_at(h.tongue_width + 2.0 * clear + 2.0, 12.0, h.socket_depth + 1.0, (0, 18.0, 7.0))
    pawl_channel = box_at(2.8, 38.0, 7.5, (8.4, 1.0, 6.2))
    pawl_pocket = box_at(4.8, 5.2, 5.0, (10.0, -13.0, 6.0))
    socket = socket.cut(lower.union(neck).union(entry).union(pawl_channel).union(pawl_pocket))
    # Separate mating key printed beside the socket.
    key = box_at(h.tongue_width, h.tongue_length, h.tongue_height / 2.0, (34.0, 0.0, h.tongue_height / 4.0))
    key = key.union(box_at(h.dovetail_top_width, h.tongue_length, h.tongue_height / 2.0 + 2.0, (34.0, 0.0, h.tongue_height * 0.75)))
    leg = box_at(h.leg_width, h.leg_depth, 18.0, (34.0, 0.0, 14.0))
    arm = box_at(2.4, 7.0, 14.0, (42.6, -7.0, 7.0))
    pawl = box_at(2.8, 4.0, 3.2, (44.0, -9.0, 3.0))
    pad = box_at(3.2, 12.0, 10.0, (43.6, -7.0, 12.0))
    key = key.union(leg).union(arm).union(pawl).union(pad)
    return socket.union(key)
