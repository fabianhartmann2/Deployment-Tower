"""Split rounded-square cosmetic shell and structural interfaces."""

from __future__ import annotations

import cadquery as cq

from .geometry import box_at, cylinder_axis, rounded_panel_xz, rounded_rect_prism, rounded_rect_ring
from .handle import cap_dovetail_rail, cap_dovetail_y_positions, cap_fastener_positions
from .logo_panel import logo_magnet_positions
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
    fits = p.fits
    center_z = (e.rear_opening_bottom + e.rear_opening_top) / 2.0
    return rounded_panel_xz(
        e.rear_panel_width + 2.0 * fits.rear_panel_x_per_side,
        e.rear_panel_height + 2.0 * fits.rear_panel_z_per_side,
        e.wall + 2.0,
        e.rear_panel_corner_radius + fits.rear_panel_x_per_side,
        e.depth / 2.0 - e.wall - 1.0,
        0.0,
        center_z,
        1,
    )


def _exterior_profile_clip(p: StationParameters, z0: float, z1: float) -> cq.Workplane:
    """Limit late-added reinforcements to the rounded cosmetic footprint."""

    e = p.enclosure
    return rounded_rect_prism(
        e.width,
        e.depth,
        z1 - z0,
        e.outer_corner_radius,
        z0,
    )


def shell_seam_fastener_positions(p: StationParameters = DEFAULT) -> tuple[tuple[float, float], ...]:
    """Six hidden vertical M4 axes, three along each side wall."""

    e = p.enclosure
    return tuple((side * e.seam_axis_x, y) for side in (-1.0, 1.0) for y in e.seam_fastener_y)


def m4_seam_insert_coupon(p: StationParameters = DEFAULT) -> cq.Workplane:
    """Reproduce the tested vertical M4 pilots: 5.4, 5.6, and 5.8 mm."""

    e = p.enclosure
    coupon = rounded_rect_prism(54.0, 24.0, 4.0, 3.0)
    for index, (x, pilot_diameter) in enumerate(zip((-18.0, 0.0, 18.0), (5.4, 5.6, 5.8)), start=1):
        boss = (
            cq.Workplane("XY")
            .center(x, 0.0)
            .circle(e.seam_boss_diameter / 2.0)
            .extrude(12.0)
            .translate((0.0, 0.0, 4.0))
        )
        pilot = (
            cq.Workplane("XY")
            .center(x, 0.0)
            .circle(pilot_diameter / 2.0)
            .extrude(7.2)
            .translate((0.0, 0.0, 8.9))
        )
        coupon = coupon.union(boss).cut(pilot)
        # One, two, or three edge notches identify 5.4, 5.6, and 5.8 mm.
        for notch_index in range(index):
            notch = box_at(1.2, 1.2, 2.0, (x - 1.8 + 1.8 * notch_index, -11.7, 3.2))
            coupon = coupon.cut(notch)
    return coupon


def _lower_seam_belt(p: StationParameters) -> cq.Workplane:
    """U-shaped internal lower belt that distributes seam loads into the shell."""

    e = p.enclosure
    z0 = e.lower_shell_top - 12.0
    side_x = e.width / 2.0 - 2.5
    side_depth = e.depth - 33.0
    belt = box_at(5.0, side_depth, 12.0, (-side_x, 0.0, z0 + 6.0))
    belt = belt.union(box_at(5.0, side_depth, 12.0, (side_x, 0.0, z0 + 6.0)))
    belt = belt.union(box_at(e.width - 33.0, 5.0, 12.0, (0.0, -side_x, z0 + 6.0)))
    return belt


def _upper_seam_belt(p: StationParameters) -> cq.Workplane:
    """Matching U-shaped upper belt around the six hidden screw lugs."""

    e = p.enclosure
    z0 = e.lower_shell_top + e.shadow_gap / 2.0
    side_x = e.width / 2.0 - 2.5
    side_depth = e.depth - 33.0
    belt = box_at(5.0, side_depth, 12.0, (-side_x, 0.0, z0 + 6.0))
    belt = belt.union(box_at(5.0, side_depth, 12.0, (side_x, 0.0, z0 + 6.0)))
    belt = belt.union(box_at(e.width - 33.0, 5.0, 12.0, (0.0, -side_x, z0 + 6.0)))
    return belt


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
    bx = c.mac_button_x_side * (c.mac_width / 2.0 - c.mac_button_edge_offset_x)
    button_entry_depth = 25.0
    button_entry = box_at(
        28.0,
        button_entry_depth,
        20.0,
        (bx, e.depth / 2.0 + 2.0 - button_entry_depth / 2.0, 22.0),
    )
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
    rail_left_x = pw.center_x - pw.outer_width / 2.0 - 0.5
    rail_right_x = e.width / 2.0 - e.wall + 0.7
    rail_center_x = (rail_left_x + rail_right_x) / 2.0
    rail_width = rail_right_x - rail_left_x
    power_positions = power_mount_fastener_positions(p)
    for y in sorted({pos[1] for pos in power_positions}):
        part = part.union(box_at(rail_width, 9.0, 3.5, (rail_center_x, y, pw.bottom_z - 1.75)))
    for x, y in power_positions:
        boss = cq.Workplane("XY").center(x, y).circle(f.m3_boss_diameter / 2.0).extrude(8.0).translate((0, 0, pw.bottom_z - 8.0))
        insert = cq.Workplane("XY").center(x, y).circle(f.m3_insert_hole_diameter / 2.0).extrude(6.5).translate((0, 0, pw.bottom_z - 5.8))
        part = part.union(boss).cut(insert)

    # Reinforced front spines carry handle loads into a U-shaped lower seam belt.
    seam_z0 = e.lower_shell_top - 12.0
    part = part.union(_lower_seam_belt(p))
    for x in (-61.0, 61.0):
        spine = box_at(8.0, 8.0, e.lower_shell_top - z0, (x, -76.0, (z0 + e.lower_shell_top) / 2.0))
        part = part.union(spine)

    # Six vertical insert bosses sit inside the clean exterior and distribute
    # separation load along both side walls.  They retain 0.6 mm nominal
    # clearance to the already calibrated power-compartment envelope.
    for x, y in shell_seam_fastener_positions(p):
        seam_boss = (
            cq.Workplane("XY")
            .center(x, y)
            .circle(e.seam_boss_diameter / 2.0)
            .extrude(12.0)
            .translate((0, 0, seam_z0))
        )
        seam_insert = (
            cq.Workplane("XY")
            .center(x, y)
            .circle(f.m4_insert_hole_diameter / 2.0)
            .extrude(7.0)
            .translate((0, 0, e.lower_shell_top - 7.0))
        )
        part = part.union(seam_boss).cut(seam_insert)

    # Three male alignment keys bridge the deliberate shadow seam.  The upper
    # shell contains clearance pockets for the same features.
    inner_face = e.width / 2.0 - e.wall - 1.5
    keys = [(0.0, -inner_face, 18.0, 5.0), (inner_face, 25.0, 5.0, 14.0), (-inner_face, 25.0, 5.0, 14.0)]
    for x, y, sx, sy in keys:
        part = part.union(box_at(sx, sy, 8.0, (x, y, e.lower_shell_top + 2.0)))

    # Stiffen the formerly free 4 mm rear sill with an internal angle beam tied
    # into both side walls and the two rear base bosses.  Recut the extended Mac
    # button corridor last so the reinforcement cannot close that access path.
    rear_y = e.depth / 2.0
    sill_flange = box_at(e.rear_panel_width + 13.0, 11.0, 4.0, (0.0, rear_y - 5.5, e.base_height + 2.0))
    sill_web = box_at(e.rear_panel_width + 13.0, 4.0, 10.0, (0.0, rear_y - 9.0, e.base_height + 5.0))
    part = part.union(sill_flange).union(sill_web).cut(_rear_panel_seat_cut(p)).cut(button_entry)
    part = _rear_bosses(part, p, z0, e.lower_shell_top)
    # Cut the insert pilots last so no later reinforcement can refill them.
    for x, y in shell_seam_fastener_positions(p):
        seam_insert = (
            cq.Workplane("XY")
            .center(x, y)
            .circle(f.m4_insert_hole_diameter / 2.0)
            .extrude(7.0)
            .translate((0, 0, e.lower_shell_top - 7.0))
        )
        part = part.cut(seam_insert)
    for x in (-boss_xy, boss_xy):
        for y in (-boss_xy, boss_xy):
            base_insert = (
                cq.Workplane("XY")
                .center(x, y)
                .circle(f.m3_insert_hole_diameter / 2.0)
                .extrude(7.0)
                .translate((0, 0, z0 - 0.5))
            )
            part = part.cut(base_insert)
    # Every reinforcement is internal.  Clip late-added belts, webs, and bosses
    # back to the same rounded footprint as the original shell so none can form
    # a visible ridge in an exterior corner.
    return part.intersect(_exterior_profile_clip(p, z0 - 1.0, e.lower_shell_top + 8.0))


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

    # Full-depth shallow pockets position the magnetic logo panels.  Local
    # internal receiver pads hold 6 x 3 mm magnets behind a 0.6 mm skin; there
    # are no exterior screws, locating lips, finger notches, or old antenna-dock
    # recesses on either side wall.
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
        v = p.prototype_v4
        receiver_depth = v.magnet_thickness + v.magnet_pocket_depth_allowance + v.magnet_cover_skin
        magnet_depth = v.magnet_thickness + v.magnet_pocket_depth_allowance
        magnet_diameter = v.magnet_diameter + v.magnet_pocket_diametral_clearance
        for _axis_x, y, z in logo_magnet_positions("right" if side > 0 else "left", p):
            receiver_start_x = side * (pocket_inner - receiver_depth)
            receiver = cylinder_axis(
                (magnet_diameter + 4.0) / 2.0,
                receiver_depth,
                (receiver_start_x, y, z),
                (side, 0, 0),
            )
            magnet_pocket = cylinder_axis(
                magnet_diameter / 2.0,
                magnet_depth + 0.1,
                (side * (pocket_inner + 0.1), y, z),
                (-side, 0, 0),
            )
            part = part.union(receiver).cut(magnet_pocket)

    # Matching seam-key pockets.
    clearance = p.fits.sliding_fit_per_side
    inner_face = e.width / 2.0 - e.wall - 1.5
    keys = [(0.0, -inner_face, 18.0, 5.0), (inner_face, 25.0, 5.0, 14.0), (-inner_face, 25.0, 5.0, 14.0)]
    for x, y, sx, sy in keys:
        pocket = box_at(sx + 2.0 * clearance, sy + 2.0 * clearance, 9.0, (x, y, e.lower_shell_top + 2.0))
        part = part.cut(pocket)

    # Continuous front spines carry the handle load down into a U-shaped upper
    # seam belt.  The six screw axes are deliberately offset from these spines.
    part = part.union(_upper_seam_belt(p))
    for x in (-61.0, 61.0):
        spine = box_at(8.0, 8.0, height, (x, -76.0, z0 + height / 2.0))
        part = part.union(spine)

    # Six hidden vertical M4 lugs.  Each head sits in a local internal pocket;
    # a long hex driver reaches it from the open top without any printed feature
    # crossing the tool corridor.  The outer skin remains closed and clean.
    lug_top = z0 + e.seam_lug_height
    for x, y in shell_seam_fastener_positions(p):
        seam_lug = (
            cq.Workplane("XY")
            .center(x, y)
            .circle(e.seam_boss_diameter / 2.0)
            .extrude(e.seam_lug_height)
            .translate((0, 0, z0))
        )
        seam_clear = cylinder_axis(
            f.m4_clearance_diameter / 2.0,
            e.seam_lug_height + 2.0,
            (x, y, z0 - 1.0),
            (0, 0, 1),
        )
        head_clear = cylinder_axis(
            e.seam_head_clearance_diameter / 2.0,
            e.seam_head_clearance_height + 0.2,
            (x, y, lug_top),
            (0, 0, 1),
        )
        # An explicit internal-only entry slot prevents the printed shell edge
        # from rubbing the head while it moves laterally into its pocket.
        entry_start_x = (1.0 if x > 0.0 else -1.0) * 60.0
        head_entry = box_at(
            abs(x) - 60.0,
            e.seam_head_entry_width,
            e.seam_head_clearance_height + 0.2,
            ((entry_start_x + x) / 2.0, y, lug_top + (e.seam_head_clearance_height + 0.2) / 2.0),
        )
        driver_clear = cylinder_axis(
            e.seam_driver_clearance_diameter / 2.0,
            e.shell_top - lug_top - e.seam_head_clearance_height + 1.0,
            (x, y, lug_top + e.seam_head_clearance_height),
            (0, 0, 1),
        )
        part = part.union(seam_lug).cut(seam_clear).cut(head_clear).cut(head_entry).cut(driver_clear)

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

    # Two full-width crossbars carry the selected dovetail rails into both side
    # walls.  The detached cap/handle subassembly slides sideways over them.
    for y in cap_dovetail_y_positions(p):
        part = part.union(box_at(e.width - 4.0, 16.0, 4.0, (0.0, y, e.shell_top - 2.0)))
        part = part.union(cap_dovetail_rail(y, p))

    # A central crossbar carries two internal M4 anti-slide screws.  The screws
    # enter blind inserts in the cap from below and never pierce its top face.
    part = part.union(box_at(e.width - 4.0, 10.0, 4.0, (0.0, 0.0, e.shell_top - 2.0)))
    for x, y in cap_fastener_positions(p):
        clearance_hole = cylinder_axis(
            f.m4_clearance_diameter / 2.0,
            6.0,
            (x, y, e.shell_top - 5.0),
            (0, 0, 1),
        )
        part = part.cut(clearance_hole)
    part = _rear_bosses(part, p, z0, e.shell_top)

    # Recut every seam fastener volume after all rails, receivers, cap bosses,
    # and rear bosses have been added.  This makes screw-head and driver access
    # fail-safe against the same late-union defect found in the power box.
    for x, y in shell_seam_fastener_positions(p):
        seam_clear = cylinder_axis(
            f.m4_clearance_diameter / 2.0,
            e.seam_lug_height + 2.0,
            (x, y, z0 - 1.0),
            (0, 0, 1),
        )
        head_clear = cylinder_axis(
            e.seam_head_clearance_diameter / 2.0,
            e.seam_head_clearance_height + 0.2,
            (x, y, lug_top),
            (0, 0, 1),
        )
        entry_start_x = (1.0 if x > 0.0 else -1.0) * 60.0
        head_entry = box_at(
            abs(x) - 60.0,
            e.seam_head_entry_width,
            e.seam_head_clearance_height + 0.2,
            ((entry_start_x + x) / 2.0, y, lug_top + (e.seam_head_clearance_height + 0.2) / 2.0),
        )
        driver_clear = cylinder_axis(
            e.seam_driver_clearance_diameter / 2.0,
            e.shell_top - lug_top - e.seam_head_clearance_height + 1.0,
            (x, y, lug_top + e.seam_head_clearance_height),
            (0, 0, 1),
        )
        part = part.cut(seam_clear).cut(head_clear).cut(head_entry).cut(driver_clear)
    for x, y, sx, sy in keys:
        pocket = box_at(sx + 2.0 * clearance, sy + 2.0 * clearance, 9.0, (x, y, e.lower_shell_top + 2.0))
        part = part.cut(pocket)
    # The dovetail crossbars and handle-load ribs are deliberately oversized
    # before unioning.  This final cosmetic-envelope trim prevents their ends
    # from printing through the strongly rounded upper corners.
    return part.intersect(_exterior_profile_clip(p, z0 - 1.0, e.shell_top + 6.0))
