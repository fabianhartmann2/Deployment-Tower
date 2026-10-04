"""Small v4 fit coupons based on measured owner-supplied hardware."""

from __future__ import annotations

import cadquery as cq

from .geometry import box_at, compound, cylinder_axis, rounded_panel_xz, rounded_panel_yz
from .parameters import DEFAULT, StationParameters


def _rounded_cutout_xz(
    width: float,
    height: float,
    radius: float,
    x: float,
    z: float,
    y0: float,
    depth: float,
) -> cq.Workplane:
    return rounded_panel_xz(width, height, depth, radius, y0, x, z, 1)


def _horizontal_slot_xz(
    width: float,
    height: float,
    x: float,
    z: float,
    y0: float,
    depth: float,
) -> cq.Workplane:
    """Capsule slot in an X/Z panel, elongated along X."""

    radius = height / 2.0
    straight = max(0.0, width - height)
    result = box_at(straight, depth, height, (x, y0 + depth / 2.0, z))
    for dx in (-straight / 2.0, straight / 2.0):
        result = result.union(cylinder_axis(radius, depth, (x + dx, y0, z), (0.0, 1.0, 0.0)))
    return result


def rear_io_fit_coupon_v1(p: StationParameters = DEFAULT) -> cq.Workplane:
    """Measured Ethernet, HDMI, USB-C, and C8 rear-panel interfaces."""

    v = p.prototype_v4
    panel_t = v.rear_panel_thickness
    width = 180.0
    height = 45.0
    center_z = height / 2.0
    coupon = rounded_panel_xz(width, height, panel_t, 4.0, 0.0, 0.0, center_z, 1)
    cut_y = -1.0
    cut_d = panel_t + 2.0
    centres = (-67.5, -22.5, 22.5, 67.5)

    # Ethernet: measured rectangular opening and 27.6 mm two-screw flange.
    x = centres[0]
    coupon = coupon.cut(
        _rounded_cutout_xz(
            v.ethernet_cutout_width + 2.0 * v.cutout_allowance,
            v.ethernet_cutout_height + 2.0 * v.cutout_allowance,
            1.2,
            x,
            center_z,
            cut_y,
            cut_d,
        )
    )
    for dx in (-v.ethernet_mount_pitch / 2.0, v.ethernet_mount_pitch / 2.0):
        coupon = coupon.cut(
            cylinder_axis(
                (v.ethernet_mount_hole_diameter + v.mounting_hole_allowance) / 2.0,
                cut_d,
                (x + dx, cut_y, center_z),
                (0.0, 1.0, 0.0),
            )
        )

    # HDMI: measured face opening and 27 mm bracket-hole pitch.
    x = centres[1]
    coupon = coupon.cut(
        _rounded_cutout_xz(
            v.hdmi_cutout_width + 2.0 * v.cutout_allowance,
            v.hdmi_cutout_height + 2.0 * v.cutout_allowance,
            1.5,
            x,
            center_z,
            cut_y,
            cut_d,
        )
    )
    for dx in (-v.hdmi_mount_pitch / 2.0, v.hdmi_mount_pitch / 2.0):
        coupon = coupon.cut(
            cylinder_axis(
                (v.hdmi_mount_hole_diameter + v.mounting_hole_allowance) / 2.0,
                cut_d,
                (x + dx, cut_y, center_z),
                (0.0, 1.0, 0.0),
            )
        )

    # USB-C: small visible aperture plus a shallow inner rebate for the 12 x 5
    # connector shell.  The oval PCB slots reproduce the measured 19 mm pitch.
    x = centres[2]
    coupon = coupon.cut(
        _rounded_cutout_xz(
            v.usbc_through_width + 2.0 * v.cutout_allowance,
            v.usbc_through_height + 2.0 * v.cutout_allowance,
            (v.usbc_through_height + 2.0 * v.cutout_allowance) / 2.0 - 0.1,
            x,
            center_z,
            cut_y,
            cut_d,
        )
    )
    coupon = coupon.cut(
        _rounded_cutout_xz(
            v.usbc_shell_width + 2.0 * v.cutout_allowance,
            v.usbc_shell_height + 2.0 * v.cutout_allowance,
            (v.usbc_shell_height + 2.0 * v.cutout_allowance) / 2.0 - 0.1,
            x,
            center_z,
            -0.2,
            v.usbc_shell_depth + v.cutout_allowance,
        )
    )
    for dx in (-v.usbc_mount_pitch / 2.0, v.usbc_mount_pitch / 2.0):
        coupon = coupon.cut(
            _horizontal_slot_xz(
                v.usbc_slot_width + v.mounting_hole_allowance,
                v.usbc_slot_height + v.mounting_hole_allowance,
                x + dx,
                center_z,
                cut_y,
                cut_d,
            )
        )

    # New measured C8 inlet; this coupon is mechanical-only and does not release
    # the unverified marketplace part for mains use.
    x = centres[3]
    coupon = coupon.cut(
        _rounded_cutout_xz(
            v.c8_cutout_width + 2.0 * v.cutout_allowance,
            v.c8_cutout_height + 2.0 * v.cutout_allowance,
            3.5,
            x,
            center_z,
            cut_y,
            cut_d,
        )
    )
    for dx in (-v.c8_mount_pitch / 2.0, v.c8_mount_pitch / 2.0):
        coupon = coupon.cut(
            cylinder_axis(
                (v.c8_mount_hole_diameter + v.mounting_hole_allowance) / 2.0,
                cut_d,
                (x + dx, cut_y, center_z),
                (0.0, 1.0, 0.0),
            )
        )
    return coupon


def rear_io_mount_coupon_v2(p: StationParameters = DEFAULT) -> cq.Workplane:
    """Revised rear-I/O coupon with the intended inside mounting directions.

    The outside face is at Y=0 and the enclosure interior is +Y.  Ethernet and
    C8 remain flange-fit stations.  USB-C mounts from the interior against two
    blind M3-insert bosses; only HDMI uses a horizontal shelf with top-down M4
    mounting points.
    """

    v = p.prototype_v4
    panel_t = v.rear_panel_thickness
    width = 180.0
    height = 50.0
    center_z = height / 2.0
    coupon = rounded_panel_xz(width, height, panel_t, 4.0, 0.0, 0.0, center_z, 1)
    cut_y = -1.0
    cut_d = panel_t + 2.0
    centres = (-67.5, -22.5, 22.5, 67.5)

    # Ethernet: the opening remains centred while the two flange axes move
    # 1.0 mm down when the RJ45 latch is at the bottom.
    x = centres[0]
    coupon = coupon.cut(
        _rounded_cutout_xz(
            v.ethernet_cutout_width + 2.0 * v.cutout_allowance,
            v.ethernet_cutout_height + 2.0 * v.cutout_allowance,
            1.2,
            x,
            center_z,
            cut_y,
            cut_d,
        )
    )
    ethernet_hole_z = center_z + v.ethernet_mount_z_offset_selected
    for dx in (-v.ethernet_mount_pitch / 2.0, v.ethernet_mount_pitch / 2.0):
        coupon = coupon.cut(
            cylinder_axis(
                (v.ethernet_mount_hole_diameter + v.mounting_hole_allowance) / 2.0,
                cut_d,
                (x + dx, cut_y, ethernet_hole_z),
                (0.0, 1.0, 0.0),
            )
        )

    # HDMI: the PCB lies horizontally.  Its underside rests 5.0 mm below the
    # opening centre because the physical connector spans Z=2...8 mm above the
    # PCB underside.  Two blind Ø5.4 M4 insert pockets sit 8.0 mm behind the
    # connector face; the screws enter vertically from above through the PCB.
    x = centres[1]
    coupon = coupon.cut(
        _rounded_cutout_xz(
            v.hdmi_cutout_width + 2.0 * v.cutout_allowance,
            v.hdmi_cutout_height + 2.0 * v.cutout_allowance,
            1.5,
            x,
            center_z,
            cut_y,
            cut_d,
        )
    )
    hdmi_connector_center_above_board = (
        v.hdmi_connector_top_above_board - v.hdmi_cutout_height / 2.0
    )
    shelf_top = center_z - hdmi_connector_center_above_board
    # Seven millimetres leaves 1.5 mm solid material below the tested 5.5 mm
    # insert after heat-setting; the pocket must not break through the shelf.
    shelf_thickness = 7.0
    shelf_depth = 28.0
    shelf = box_at(
        42.0,
        shelf_depth,
        shelf_thickness,
        (x, panel_t + shelf_depth / 2.0, shelf_top - shelf_thickness / 2.0),
    )
    coupon = coupon.union(shelf)
    for dx in (-v.hdmi_mount_pitch / 2.0, v.hdmi_mount_pitch / 2.0):
        pocket = cylinder_axis(
            p.fasteners.m4_insert_hole_diameter / 2.0,
            p.fasteners.insert_depth,
            (x + dx, v.hdmi_mount_axis_setback, shelf_top + 0.01),
            (0.0, 0.0, -1.0),
        )
        coupon = coupon.cut(pocket)

    # USB-C: unlike HDMI, the PCB is fastened from behind, parallel to the rear
    # panel.  Four-millimetre stand-offs reduce the measured 4.5 mm projection
    # to the selected 0.5 mm.  The exterior skin remains closed at both screw
    # positions; screws enter the blind M3 insert pockets from the interior.
    x = centres[2]
    coupon = coupon.cut(
        _rounded_cutout_xz(
            v.usbc_through_width + 2.0 * v.cutout_allowance,
            v.usbc_through_height + 2.0 * v.cutout_allowance,
            (v.usbc_through_height + 2.0 * v.cutout_allowance) / 2.0 - 0.1,
            x,
            center_z,
            cut_y,
            cut_d,
        )
    )
    coupon = coupon.cut(
        _rounded_cutout_xz(
            v.usbc_shell_width + 2.0 * v.cutout_allowance,
            v.usbc_shell_height + 2.0 * v.cutout_allowance,
            (v.usbc_shell_height + 2.0 * v.cutout_allowance) / 2.0 - 0.1,
            x,
            center_z,
            -0.2,
            v.usbc_shell_depth + v.cutout_allowance,
        )
    )
    boss_face_y = panel_t + v.usbc_board_standoff
    for dx in (-v.usbc_mount_pitch / 2.0, v.usbc_mount_pitch / 2.0):
        boss_x = x + dx
        boss = cylinder_axis(
            p.fasteners.m3_boss_diameter / 2.0,
            v.usbc_board_standoff,
            (boss_x, panel_t, center_z),
            (0.0, 1.0, 0.0),
        )
        coupon = coupon.union(boss)
        insert_pocket = cylinder_axis(
            p.fasteners.m3_insert_hole_diameter / 2.0,
            p.fasteners.insert_depth,
            (boss_x, boss_face_y + 0.01, center_z),
            (0.0, -1.0, 0.0),
        )
        coupon = coupon.cut(insert_pocket)

    # C8: retain the measured opening and increase the physical hole pitch from
    # the v1 trial's 29.0 mm to the selected 30.0 mm.
    x = centres[3]
    coupon = coupon.cut(
        _rounded_cutout_xz(
            v.c8_cutout_width + 2.0 * v.cutout_allowance,
            v.c8_cutout_height + 2.0 * v.cutout_allowance,
            3.5,
            x,
            center_z,
            cut_y,
            cut_d,
        )
    )
    for dx in (-v.c8_mount_pitch_selected / 2.0, v.c8_mount_pitch_selected / 2.0):
        coupon = coupon.cut(
            cylinder_axis(
                (v.c8_mount_hole_diameter + v.mounting_hole_allowance) / 2.0,
                cut_d,
                (x + dx, cut_y, center_z),
                (0.0, 1.0, 0.0),
            )
        )
    return coupon


def rf_bulkhead_fit_coupon_v1(p: StationParameters = DEFAULT) -> cq.Workplane:
    """Compare three RF-hole allowances at full and locally thinned walls."""

    v = p.prototype_v4
    panel_t = v.rear_panel_thickness
    coupon = rounded_panel_xz(78.0, 50.0, panel_t, 4.0, 0.0, 0.0, 25.0, 1)
    diameters = (6.6, 6.8, 7.0)
    for row, z in enumerate((35.0, 15.0)):
        for column, (x, diameter) in enumerate(zip((-24.0, 0.0, 24.0), diameters), start=1):
            if row == 1:
                # A 12 mm circular inner rebate leaves a 2.0 mm local panel land
                # if the unknown bulkhead thread cannot clamp the full 3.2 mm.
                rebate = cylinder_axis(6.0, panel_t - 2.0 + 0.1, (x, -0.1, z), (0.0, 1.0, 0.0))
                coupon = coupon.cut(rebate)
            hole = cylinder_axis(diameter / 2.0, panel_t + 2.0, (x, -1.0, z), (0.0, 1.0, 0.0))
            coupon = coupon.cut(hole)
            # One/two/three edge marks identify 6.6/6.8/7.0 mm after printing.
            for mark in range(column):
                marker = box_at(1.2, panel_t + 2.0, 1.2, (x - 2.0 + mark * 2.0, 1.6, 49.7 if row == 0 else 0.3))
                coupon = coupon.cut(marker)
    return coupon


def logo_magnet_fit_coupon_v1(p: StationParameters = DEFAULT) -> cq.Workplane:
    """Blind shell pockets and steel-sheet recesses without a finger notch."""

    v = p.prototype_v4
    receiver_t = v.magnet_thickness + v.magnet_pocket_depth_allowance + v.magnet_cover_skin
    receiver = rounded_panel_yz(50.0, 35.0, receiver_t, 4.0, 0.0, -30.0, 17.5, 1)
    panel = rounded_panel_yz(50.0, 35.0, p.logo.thickness, 4.0, 14.0, 30.0, 17.5, 1)
    pocket_d = v.magnet_diameter + v.magnet_pocket_diametral_clearance
    pocket_depth = v.magnet_thickness + v.magnet_pocket_depth_allowance
    for y in (-42.0, -18.0):
        pocket = cylinder_axis(pocket_d / 2.0, pocket_depth + 0.1, (-0.1, y, 17.5), (1.0, 0.0, 0.0))
        receiver = receiver.cut(pocket)
    for y in (18.0, 42.0):
        steel_recess = box_at(
            v.steel_recess_depth + 0.1,
            v.steel_recess_width,
            v.steel_recess_height,
            (14.0 + v.steel_recess_depth / 2.0, y, 17.5),
        )
        panel = panel.cut(steel_recess)
    return receiver.union(panel)


def _dovetail_profile(
    bottom_width: float,
    top_width: float,
    height: float,
    length: float,
    z0: float,
) -> cq.Workplane:
    points = (
        (-bottom_width / 2.0, z0),
        (bottom_width / 2.0, z0),
        (top_width / 2.0, z0 + height),
        (-top_width / 2.0, z0 + height),
    )
    return cq.Workplane("XZ").polyline(points).close().extrude(length, both=True)


def cap_dovetail_fit_coupon_v1(p: StationParameters = DEFAULT) -> cq.Workplane:
    """Three sliding-cap dovetail clearances: 0.25, 0.35, and 0.45 mm."""

    v = p.prototype_v4
    pieces: list[cq.Workplane] = []
    length = 18.0
    for index, clearance in enumerate(v.dovetail_clearances, start=1):
        base = box_at(22.0, length, 3.0, (0.0, 0.0, 1.5))
        rail = _dovetail_profile(
            v.dovetail_rail_bottom_width,
            v.dovetail_rail_top_width,
            v.dovetail_rail_height,
            length / 2.0,
            3.0,
        )
        rail_piece = base.union(rail)
        slider = box_at(22.0, length, 8.0, (34.0, 0.0, 7.0))
        groove = _dovetail_profile(
            v.dovetail_rail_bottom_width + 2.0 * clearance,
            v.dovetail_rail_top_width + 2.0 * clearance,
            v.dovetail_rail_height + clearance,
            length / 2.0 + 0.5,
            2.9,
        ).translate((34.0, 0.0, 0.0))
        slider = slider.cut(groove)
        for mark in range(index):
            notch_x = -4.0 + 4.0 * mark
            rail_piece = rail_piece.cut(box_at(1.2, 2.0, 1.2, (notch_x, -length / 2.0 + 0.5, 0.6)))
            slider = slider.cut(box_at(1.2, 2.0, 1.2, (34.0 + notch_x, -length / 2.0 + 0.5, 3.6)))
        pieces.extend((rail_piece, slider))
    return compound(pieces)
