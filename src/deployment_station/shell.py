"""Split rounded-square cosmetic shell and structural interfaces."""

from __future__ import annotations

import cadquery as cq

from .geometry import box_at, cylinder_axis, rounded_panel_xz, rounded_rect_ring
from .handle import cap_fastener_positions
from .logo_panel import logo_mount_positions
from .mac_mount import mac_cradle_fastener_positions
from .parameters import DEFAULT, StationParameters
from .power_compartment import power_mount_fastener_positions
from .router_tray import router_tray_fastener_positions


def _rear_opening_cut(p: StationParameters, z0: float, height: float) -> cq.Workplane:
    e = p.enclosure
    return box_at(
        e.rear_opening_width,
        e.wall * 6.0,
        height + 2.0,
        (0.0, e.depth / 2.0, z0 + height / 2.0),
    )


def _rear_panel_seat_cut(p: StationParameters) -> cq.Workplane:
    e = p.enclosure
    center_z = (e.rear_opening_bottom + e.rear_opening_top) / 2.0
    return rounded_panel_xz(
        e.rear_panel_width + 0.5,
        e.rear_panel_height + 0.5,
        e.wall + 2.0,
        e.rear_panel_corner_radius + 0.25,
        e.depth / 2.0 - e.wall - 1.0,
        0.0,
        center_z,
        1,
    )


def _rear_bosses(part: cq.Workplane, p: StationParameters, z_min: float, z_max: float) -> cq.Workplane:
    e = p.enclosure
    i = p.interfaces
    f = p.fasteners
    for z in i.rear_panel_screw_z:
        if z_min + 5.0 <= z <= z_max - 5.0:
            for x in (-i.rear_panel_screw_x, i.rear_panel_screw_x):
                panel_inner_y = e.depth / 2.0 - e.rear_panel_thickness
                boss = cylinder_axis(f.m3_boss_diameter / 2.0, 9.0, (x, panel_inner_y, z), (0, -1, 0))
                insert = cylinder_axis(f.m3_insert_hole_diameter / 2.0, 7.0, (x, panel_inner_y + 0.5, z), (0, -1, 0))
                part = part.union(boss).cut(insert)
    return part


def lower_shell(p: StationParameters = DEFAULT) -> cq.Workplane:
    e = p.enclosure
    gap = e.shadow_gap
    z0 = e.base_height
    height = e.lower_shell_top - gap / 2.0 - z0
    part = rounded_rect_ring(e.width, e.depth, height, e.outer_corner_radius, e.wall, z0)
    part = part.cut(_rear_opening_cut(p, e.rear_opening_bottom, e.lower_shell_top - e.rear_opening_bottom))
    part = part.cut(_rear_panel_seat_cut(p))

    # The rear/bottom power-button path must remain open through every stationary
    # printed part, not merely through the base skin.
    c = p.components
    bx = c.mac_width / 2.0 - c.mac_button_edge_offset_x
    button_entry = box_at(28.0, 10.0, 20.0, (bx, e.depth / 2.0 - 3.0, 22.0))
    part = part.cut(button_entry)

    # Base insert bosses transfer the removable-bottom fasteners into substantial
    # corner material, not the cosmetic wall alone.
    f = p.fasteners
    boss_xy = e.width / 2.0 - 13.0
    for x in (-boss_xy, boss_xy):
        for y in (-boss_xy, boss_xy):
            boss = cq.Workplane("XY").center(x, y).circle(f.m3_boss_diameter / 2.0).extrude(12.0).translate((0, 0, z0))
            hole = cq.Workplane("XY").center(x, y).circle(f.m3_insert_hole_diameter / 2.0).extrude(7.0).translate((0, 0, z0 - 0.5))
            # Orthogonal webs tie each boss into both adjacent shell walls.
            web_x = box_at(11.0, 5.0, 8.0, (x + (5.0 if x > 0 else -5.0), y, z0 + 4.0))
            web_y = box_at(5.0, 11.0, 8.0, (x, y + (5.0 if y > 0 else -5.0), z0 + 4.0))
            part = part.union(boss).union(web_x).union(web_y).cut(hole)

    # Downward-accessible Mac cradle insert bosses.  Short side webs connect each
    # boss directly to a substantial shell wall without entering the Mac envelope.
    for x, y in mac_cradle_fastener_positions(p):
        sign = 1.0 if x > 0 else -1.0
        boss = cq.Workplane("XY").center(x, y).circle(f.m3_boss_diameter / 2.0).extrude(12.0).translate((0, 0, c.mac_support_plane_z - 1.0))
        web = box_at(10.0, 10.0, 12.0, (x + sign * 5.0, y, c.mac_support_plane_z + 5.0))
        insert = cq.Workplane("XY").center(x, y).circle(f.m3_insert_hole_diameter / 2.0).extrude(7.0).translate((0, 0, c.mac_support_plane_z - 1.5))
        part = part.union(boss).union(web).cut(insert)

    # Two shell-tied rails and four insert bosses support the closed power box.
    pw = p.power
    rail_left_x = -(e.width / 2.0 - e.wall + 0.7)
    rail_right_x = pw.center_x + pw.outer_width / 2.0 + 0.5
    rail_center_x = (rail_left_x + rail_right_x) / 2.0
    rail_width = rail_right_x - rail_left_x
    power_positions = power_mount_fastener_positions(p)
    for y in sorted({pos[1] for pos in power_positions}):
        part = part.union(box_at(rail_width, 9.0, 3.5, (rail_center_x, y, pw.bottom_z - 1.75)))
    for x, y in power_positions:
        boss = cq.Workplane("XY").center(x, y).circle(f.m3_boss_diameter / 2.0).extrude(8.0).translate((0, 0, pw.bottom_z - 8.0))
        insert = cq.Workplane("XY").center(x, y).circle(f.m3_insert_hole_diameter / 2.0).extrude(6.5).translate((0, 0, pw.bottom_z - 5.8))
        part = part.union(boss).cut(insert)

    # Reinforced front spines carry handle loads through a positively bolted
    # lower/upper seam and continue to the base-fastened lower shell.
    seam_z0 = e.lower_shell_top - 12.0
    for x in (-61.0, 61.0):
        spine = box_at(8.0, 8.0, e.lower_shell_top - z0, (x, -76.0, (z0 + e.lower_shell_top) / 2.0))
        seam_boss = cq.Workplane("XY").center(x, -76.0).circle(f.m4_boss_diameter / 2.0).extrude(12.0).translate((0, 0, seam_z0))
        seam_insert = cq.Workplane("XY").center(x, -76.0).circle(f.m4_insert_hole_diameter / 2.0).extrude(7.0).translate((0, 0, e.lower_shell_top - 7.0))
        part = part.union(spine).union(seam_boss).cut(seam_insert)

    # Three male alignment keys bridge the deliberate shadow seam.  The upper
    # shell contains clearance pockets for the same features.
    inner_face = e.width / 2.0 - e.wall - 1.5
    keys = [(-45.0, -inner_face, 14.0, 5.0), (inner_face, -42.0, 5.0, 14.0), (-inner_face, -42.0, 5.0, 14.0)]
    for x, y, sx, sy in keys:
        part = part.union(box_at(sx, sy, 8.0, (x, y, e.lower_shell_top + 2.0)))
    return _rear_bosses(part, p, z0, e.lower_shell_top)


def upper_shell(p: StationParameters = DEFAULT) -> cq.Workplane:
    e = p.enclosure
    logo = p.logo
    f = p.fasteners
    gap = e.shadow_gap
    z0 = e.lower_shell_top + gap / 2.0
    height = e.shell_top - z0
    part = rounded_rect_ring(e.width, e.depth, height, e.outer_corner_radius, e.wall, z0)
    part = part.cut(_rear_opening_cut(p, z0, height))
    part = part.cut(_rear_panel_seat_cut(p))

    # Full-depth shallow pockets seat the panels with 0.25 mm face clearance.
    # Two blind M3 insert bosses per side are webbed to the intact shell outside
    # the pocket; visible screws provide an unambiguous, reversible load path.
    for side in (-1, 1):
        pocket_inner = e.width / 2.0 - logo.thickness - p.fits.logo_panel_per_side
        pocket_outer = e.width / 2.0 + 1.0
        pocket_depth = pocket_outer - pocket_inner
        pocket = box_at(
            pocket_depth,
            logo.size + 2.0 * logo.reveal,
            logo.size + 2.0 * logo.reveal,
            (side * ((pocket_inner + pocket_outer) / 2.0), 0.0, logo.center_z),
        )
        part = part.cut(pocket)
        # The boss face reaches the panel's inner face, eliminating clamp-up
        # bending while the surrounding pocket retains 0.25 mm assembly relief.
        boss_length = 7.0 + p.fits.logo_panel_per_side
        for _axis_x, y, z in logo_mount_positions("right" if side > 0 else "left", p):
            boss_start_x = side * (pocket_inner - boss_length)
            boss = cylinder_axis(
                f.m3_boss_diameter / 2.0,
                boss_length,
                (boss_start_x, y, z),
                (side, 0, 0),
            )
            pilot = cylinder_axis(
                f.m3_insert_hole_diameter / 2.0,
                f.insert_depth + 0.7,
                (side * (pocket_inner + 0.1), y, z),
                (-side, 0, 0),
            )
            web_y = 31.5 if y > 0.0 else -31.5
            web = box_at(
                boss_length,
                14.0,
                f.m3_boss_diameter,
                (side * (pocket_inner - boss_length / 2.0), web_y, z),
            )
            part = part.union(boss).union(web).cut(pilot)
        notch = cylinder_axis(
            logo.finger_notch_diameter / 2.0 + 0.4,
            e.wall + 2.0,
            (side * (e.width / 2.0 + 1.0), 0.0, logo.center_z - logo.size / 2.0 + 2.0),
            (-side, 0, 0),
        )
        part = part.cut(notch)

        # Flush-recessed Wi-Fi dock pocket at the rear side edge.  The dock's
        # backing plate restores the surface while the clips project inward and
        # capture an antenna centred on the exterior side datum.
        w = p.wifi
        dock_depth = w.antenna_base_diameter / 2.0 + p.fits.wifi_clip_radial + w.clip_wall + 0.6
        dock_pocket = box_at(
            dock_depth,
            w.backplate_width + 1.0,
            w.backplate_height + 1.0,
            (side * (e.width / 2.0 - dock_depth / 2.0), w.dock_center_y, w.dock_center_z),
        )
        part = part.cut(dock_pocket)

        # Two M3 insert bosses retain each dock.  They stop 0.4 mm short of the
        # dock backplate and are webbed to the upper/lower pocket boundaries.
        pocket_inner_x = e.width / 2.0 - dock_depth
        boss_length = dock_depth - w.backplate_thickness - 0.4
        for z, toward_top in ((171.0, False), (258.0, True)):
            start_x = side * pocket_inner_x
            boss = cylinder_axis(f.m3_boss_diameter / 2.0, boss_length, (start_x, 41.0, z), (side, 0, 0))
            hole = cylinder_axis(
                f.m3_insert_hole_diameter / 2.0,
                min(7.0, boss_length),
                (side * (e.width / 2.0 - w.backplate_thickness - 0.2), 41.0, z),
                (-side, 0, 0),
            )
            edge_z = w.dock_center_z + (w.backplate_height + 1.0) / 2.0 if toward_top else w.dock_center_z - (w.backplate_height + 1.0) / 2.0
            web_center_z = (edge_z + z) / 2.0
            inner_web = box_at(
                boss_length,
                9.0,
                abs(edge_z - z) + 1.5,
                (side * (pocket_inner_x + boss_length / 2.0), 41.0, web_center_z),
            )
            anchor_z = edge_z + (1.0 if toward_top else -1.0)
            anchor = box_at(
                dock_depth,
                9.0,
                2.0,
                (side * (e.width / 2.0 - dock_depth / 2.0), 41.0, anchor_z),
            )
            part = part.union(boss).union(inner_web).union(anchor).cut(hole)

    # Matching seam-key pockets.
    clearance = p.fits.sliding_fit_per_side
    inner_face = e.width / 2.0 - e.wall - 1.5
    keys = [(-45.0, -inner_face, 14.0, 5.0), (inner_face, -42.0, 5.0, 14.0), (-inner_face, -42.0, 5.0, 14.0)]
    for x, y, sx, sy in keys:
        pocket = box_at(sx + 2.0 * clearance, sy + 2.0 * clearance, 9.0, (x, y, e.lower_shell_top + 2.0))
        part = part.cut(pocket)

    # Matching upper seam lugs accept M4 screws from above into lower-shell
    # inserts.  Continuous 8 mm front spines carry the load to the cap zone.
    for x in (-61.0, 61.0):
        spine = box_at(8.0, 8.0, height, (x, -76.0, z0 + height / 2.0))
        seam_lug = cq.Workplane("XY").center(x, -76.0).circle(f.m4_boss_diameter / 2.0).extrude(11.0).translate((0, 0, z0))
        seam_clear = cq.Workplane("XY").center(x, -76.0).circle(f.m4_clearance_diameter / 2.0).extrude(13.0).translate((0, 0, z0 - 1.0))
        part = part.union(spine).union(seam_lug).cut(seam_clear)

    # Shell-tied router cross rails and top-loaded M3 insert bosses.
    tray_positions = router_tray_fastener_positions(p)
    rows = sorted({round(pos[1], 6) for pos in tray_positions})
    for index, y in enumerate(rows):
        rail_width = e.width - 2.0 * e.wall + (1.0 if index == 0 else -7.5)
        part = part.union(box_at(rail_width, 8.0, 4.0, (0.0, y, p.components.router_tray_z - 2.0)))
    for x, y in tray_positions:
        boss = cq.Workplane("XY").center(x, y).circle(f.m3_boss_diameter / 2.0).extrude(8.0).translate((0, 0, p.components.router_tray_z - 8.0))
        insert = cq.Workplane("XY").center(x, y).circle(f.m3_insert_hole_diameter / 2.0).extrude(6.5).translate((0, 0, p.components.router_tray_z - 5.8))
        part = part.union(boss).cut(insert)

    # Two deep vertical ribs carry cap/handle loads down into both side walls.
    rib_x = p.handle.anchor_spacing / 2.0
    for x in (-rib_x, rib_x):
        rib = box_at(p.handle.reinforcement_rib_thickness, 22.0, 54.0, (x, -48.0, e.shell_top - 27.0))
        tie = box_at(24.0, 24.0, 54.0, (x, -68.0, e.shell_top - 27.0))
        part = part.union(rib).union(tie)

    # All cap clearances now have matching insert bosses; the two front positions
    # lie directly on the handle spines and the four perimeter bosses stabilize
    # the removable cap.
    for x, y in cap_fastener_positions(p):
        boss = cq.Workplane("XY").center(x, y).circle(f.m4_boss_diameter / 2.0).extrude(12.0).translate((0, 0, e.shell_top - 12.0))
        insert = cq.Workplane("XY").center(x, y).circle(f.m4_insert_hole_diameter / 2.0).extrude(7.0).translate((0, 0, e.shell_top - 7.0))
        # Short orthogonal ties reach whichever substantial wall/rib is nearest.
        tie_x_width = 22.0 if abs(x) > 58.0 else 18.0
        tie_x_offset = 8.0 if abs(x) > 58.0 else 7.0
        tie_x = box_at(tie_x_width, 6.0, 10.0, (x + (tie_x_offset if x > 0 else -tie_x_offset), y, e.shell_top - 5.0))
        if y < -65.0:
            tie_y = box_at(6.0, 10.0, 10.0, (x, -74.0, e.shell_top - 5.0))
        else:
            tie_y = box_at(6.0, 22.0, 10.0, (x, y + (8.0 if y > 0 else -8.0), e.shell_top - 5.0))
        part = part.union(boss).union(tie_y)
        if y <= 0.0:
            part = part.union(tie_x)
        part = part.cut(insert)
    return _rear_bosses(part, p, z0, e.shell_top)
