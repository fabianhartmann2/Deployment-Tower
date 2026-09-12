"""Closed, separately serviced APV/mains compartment.

This is mechanical containment geometry only.  It intentionally does not encode
creepage, clearance, fuse selection, branch protection, or a final wiring topology.
Those require competent electrical review before energization.
"""

from __future__ import annotations

import cadquery as cq

from .geometry import box_at, cylinder_axis, rounded_panel_xz, rounded_rect_prism, rounded_rect_ring
from .layout import packaging_layout
from .parameters import DEFAULT, StationParameters


def _outer_box(p: StationParameters) -> cq.Workplane:
    pw = p.power
    z0 = pw.bottom_z
    return rounded_rect_prism(pw.outer_width, pw.outer_depth, pw.outer_height, 6.0, z0).translate((pw.center_x, pw.center_y, 0.0))


def power_mount_fastener_positions(p: StationParameters = DEFAULT) -> tuple[tuple[float, float], ...]:
    pw = p.power
    return tuple(
        (pw.center_x + x, pw.center_y + y)
        for y in (-50.0, 50.0)
        for x in (-28.0, 28.0)
    )


def apv_mount_fastener_positions(p: StationParameters = DEFAULT) -> tuple[tuple[float, float], ...]:
    """Supplier-drawing APV lug-hole axes after the station's 90-degree rotation."""

    pw = p.power
    body_half_length = p.components.psu_case_length / 2.0
    body_half_width = p.components.psu_case_width / 2.0
    holes_uv = ((-7.3, 15.3), (91.3, 41.7))
    return tuple(
        (
            pw.center_x + (v - body_half_width),
            pw.center_y + (body_half_length - u),
        )
        for u, v in holes_uv
    )


def power_tie_bridge_centres(p: StationParameters = DEFAULT) -> tuple[tuple[float, float], ...]:
    """Internal Mac-AC and DC tie-down bridge centres, respectively."""

    pw = p.power
    inner_front_y = pw.center_y - pw.outer_depth / 2.0 + pw.wall
    y = inner_front_y + pw.tie_bridge_depth / 2.0 + 0.6
    # The bridges remain in the front floor strip but are separated from the
    # relocated diameter-12 gland, APV fixing pods, and cover columns.
    # The left bridge is kept inboard of the front-left shell-mount screw head.
    return ((pw.center_x - 16.0, y), (pw.center_x - 1.0, y))


def power_cover_fastener_positions(p: StationParameters = DEFAULT) -> tuple[tuple[float, float], ...]:
    pw = p.power
    # Keep the cover columns clear of the four shell-mount screw axes.  The
    # former 7 mm edge offset placed each column only sqrt(10) mm from a floor
    # screw, which refilled the through-hole and blocked its head/driver path.
    dx = pw.outer_width / 2.0 - 15.0
    dy = pw.outer_depth / 2.0 - 5.0
    return tuple((x, y) for x in (pw.center_x - dx, pw.center_x + dx) for y in (pw.center_y - dy, pw.center_y + dy))


def power_cover_boss_height(p: StationParameters = DEFAULT) -> float:
    return p.fasteners.insert_depth + 6.5


def power_compartment(p: StationParameters = DEFAULT) -> cq.Workplane:
    pw = p.power
    f = p.fasteners
    i = p.interfaces
    z0 = pw.bottom_z
    box = _outer_box(p)
    inner_w = pw.outer_width - 2.0 * pw.wall
    inner_d = pw.outer_depth - 2.0 * pw.wall
    cavity_h = pw.outer_height - pw.bottom + 1.0
    cavity = rounded_rect_prism(inner_w, inner_d, cavity_h, 4.0, z0 + pw.bottom).translate((pw.center_x, pw.center_y, 0.0))
    box = box.cut(cavity)

    # Two top-loaded APV fixing pods are registered to the supplier's diagonal
    # diameter-3.6 lug-hole axes.  Each pod includes a short, blind insert pilot
    # open to the service side; it leaves a sealed floor below and never depends
    # on access to the lower-shell support rails.  The exact insert/screw/washer
    # stack remains deliberately unselected pending the actual APV and material.
    floor_top = z0 + pw.bottom
    lug_underside = packaging_layout(p).psu_center[2] - p.components.psu_case_height / 2.0
    boss_top = lug_underside - pw.apv_support_clearance
    boss_height = boss_top - z0
    if boss_height <= pw.apv_insert_pocket_depth:
        raise ValueError("APV boss cannot contain the configured blind insert pocket")
    for x, y in apv_mount_fastener_positions(p):
        boss = (
            cq.Workplane("XY")
            .center(x, y)
            .circle(pw.apv_mount_boss_diameter / 2.0)
            .extrude(boss_height)
            .translate((0, 0, z0))
        )
        insert = cylinder_axis(
            pw.apv_insert_pocket_diameter / 2.0,
            pw.apv_insert_pocket_depth + 0.2,
            (x, y, boss_top - pw.apv_insert_pocket_depth),
            (0, 0, 1),
        )
        box = box.union(boss).cut(insert)

    # Fixed inlet island: the C8 and its closed terminal tunnel remain attached
    # to this compartment when the surrounding rear service panel is removed.
    rear_wall_y = pw.center_y + pw.outer_depth / 2.0
    panel_inner_y = p.enclosure.depth / 2.0 - p.enclosure.rear_panel_thickness
    tunnel_depth = panel_inner_y - rear_wall_y
    tunnel = box_at(38.0, tunnel_depth, 26.0, (i.c8_position_x, rear_wall_y + tunnel_depth / 2.0, i.c8_position_z))
    # Carry the terminal void through the box's rear wall and deliberately into
    # the main cavity.  Merely cutting the external bridge leaves a hidden web
    # equal to the compartment wall thickness and makes the inlet unwireable.
    void_front_y = rear_wall_y - pw.wall - pw.terminal_tunnel_inner_overlap
    void_rear_y = panel_inner_y + 1.0
    tunnel_void = box_at(
        27.0,
        void_rear_y - void_front_y,
        19.0,
        (i.c8_position_x, (void_front_y + void_rear_y) / 2.0, i.c8_position_z),
    )
    box = box.union(tunnel).cut(tunnel_void)

    island = rounded_panel_xz(
        42.0,
        28.0,
        p.enclosure.rear_panel_thickness,
        4.0,
        panel_inner_y,
        i.c8_position_x,
        i.c8_position_z,
        1,
    )
    cw = i.c8_cutout_width + i.c8_panel_fit_allowance
    ch = i.c8_cutout_height + i.c8_panel_fit_allowance
    inlet_cut = rounded_panel_xz(cw, ch, p.enclosure.rear_panel_thickness + 2.0, i.c8_cutout_corner_radius, panel_inner_y - 1.0, i.c8_position_x, i.c8_position_z, 1)
    island = island.cut(inlet_cut)
    for x in (i.c8_position_x - i.c8_hole_pitch / 2.0, i.c8_position_x + i.c8_hole_pitch / 2.0):
        island = island.cut(
            cylinder_axis(i.c8_hole_diameter / 2.0, p.enclosure.rear_panel_thickness + 2.0, (x, panel_inner_y - 1.0, i.c8_position_z), (0, 1, 0))
        )
    box = box.union(island)

    # DC/SELV leaves only through a fitted grommet on the front-right wall.  The
    # opening is isolated from the inlet tunnel and placed beside the data lane.
    grommet_x = pw.center_x + pw.outer_width / 2.0
    grommet = cylinder_axis(
        pw.grommet_hole_diameter / 2.0,
        pw.wall + 2.0,
        (grommet_x + 1.0, pw.center_y - 49.0, z0 + 22.0),
        (-1, 0, 0),
    )
    box = box.cut(grommet)

    # A separate glanded exit carries only the double-insulated Mac AC branch.
    # Final connector, splice, protection, and gland selections remain subject to
    # qualified electrical review; this geometry merely enforces segregation.
    mac_ac_x = pw.center_x + pw.mac_ac_exit_offset_x
    mac_ac_y = pw.center_y + pw.mac_ac_exit_offset_y
    mac_ac = cylinder_axis(pw.mac_ac_gland_diameter / 2.0, pw.bottom + 2.0, (mac_ac_x, mac_ac_y, z0 - 1.0), (0, 0, 1))
    box = box.cut(mac_ac)

    # Raised tie-down bridges replace the former full-through floor slots.  Each
    # U-shaped bridge is cut before unioning it to the enclosure, so its strap
    # tunnel remains open while the continuous compartment floor remains intact.
    for x, y in power_tie_bridge_centres(p):
        bridge = box_at(
            pw.tie_bridge_width,
            pw.tie_bridge_depth,
            pw.tie_bridge_height,
            (x, y, floor_top + pw.tie_bridge_height / 2.0),
        )
        strap_tunnel = box_at(
            pw.tie_bridge_tunnel_width,
            pw.tie_bridge_depth + 2.0,
            pw.tie_bridge_tunnel_height,
            (x, y, floor_top + pw.tie_bridge_tunnel_height / 2.0),
        )
        box = box.union(bridge.cut(strap_tunnel))

    # Short upper bosses carry the four cover inserts directly under the matching
    # cover holes.  Each boss overlaps an end wall, so it is positively tied to
    # the enclosure without occupying the floor-screw head/driver corridor.
    # Keeping these bosses near the top also avoids the cable-restraint bridges
    # and the already-printed lower-shell mounting pattern.
    cover_underside = z0 + pw.outer_height
    column_height = power_cover_boss_height(p)
    column_bottom = cover_underside - column_height
    for x, y in power_cover_fastener_positions(p):
        column = (
            cq.Workplane("XY")
            .center(x, y)
            .circle(f.m3_boss_diameter / 2.0)
            .extrude(column_height)
            .translate((0, 0, column_bottom))
        )
        insert = cylinder_axis(
            f.m3_insert_hole_diameter / 2.0,
            f.insert_depth + 0.2,
            (x, y, z0 + pw.outer_height - f.insert_depth),
            (0, 0, 1),
        )
        box = box.union(column).cut(insert)

    # Four floor screws attach the compartment to shell-tied support rails.
    # Cut these last so later unions can never refill a through-axis.  Their
    # relocated neighbouring cover columns leave room for an M3 low head and
    # its driver while preserving the already-printed lower-shell insert axes.
    for x, y in power_mount_fastener_positions(p):
        mount_hole = (
            cq.Workplane("XY")
            .center(x, y)
            .circle(f.m3_clearance_diameter / 2.0)
            .extrude(pw.bottom + 2.0)
            .translate((0, 0, z0 - 1.0))
        )
        box = box.cut(mount_hole)
    return box


def power_compartment_cover(p: StationParameters = DEFAULT) -> cq.Workplane:
    pw = p.power
    f = p.fasteners
    z0 = pw.bottom_z + pw.outer_height
    cover = rounded_rect_prism(pw.outer_width, pw.outer_depth, pw.cover_thickness, 6.0, z0).translate((pw.center_x, pw.center_y, 0.0))
    # Shallow internal locating lip; it does not act as the electrical clearance
    # system and must be reviewed with the final wiring/components.
    lip = rounded_rect_ring(
        pw.outer_width - 2.0 * pw.wall - 2.0 * p.fits.service_panel_per_side,
        pw.outer_depth - 2.0 * pw.wall - 2.0 * p.fits.service_panel_per_side,
        2.0,
        4.0,
        p.enclosure.minimum_wall,
        z0 - 2.0,
    ).translate((pw.center_x, pw.center_y, 0.0))
    cover = cover.union(lip)
    for x, y in power_cover_fastener_positions(p):
        # Clear the locating lip around the column, then continue the smaller
        # M3 clearance axis through the cover plate.
        column_relief = cylinder_axis(
            f.m3_boss_diameter / 2.0 + p.fits.service_panel_per_side,
            2.2,
            (x, y, z0 - 2.1),
            (0, 0, 1),
        )
        hole = cylinder_axis(
            f.m3_clearance_diameter / 2.0,
            pw.cover_thickness + 4.0,
            (x, y, z0 - 2.0),
            (0, 0, 1),
        )
        cover = cover.cut(column_relief).cut(hole)
    return cover


def insert_boss_coupon(p: StationParameters = DEFAULT) -> cq.Workplane:
    f = p.fasteners
    plate = rounded_rect_prism(46.0, 28.0, 4.0, 4.0)
    for index, allowance in enumerate((-0.2, 0.0, 0.2)):
        x = (index - 1) * 14.0
        boss = cq.Workplane("XY").center(x, 0.0).circle(f.m3_boss_diameter / 2.0).extrude(10.0).translate((0, 0, 4.0))
        hole = cq.Workplane("XY").center(x, 0.0).circle((f.m3_insert_hole_diameter + allowance) / 2.0).extrude(f.insert_depth + 1.0).translate((0, 0, 9.0))
        plate = plate.union(boss).cut(hole)
    return plate
