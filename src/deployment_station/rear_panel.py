"""Single removable rear service panel with all external interfaces."""

from __future__ import annotations

import cadquery as cq

from .geometry import box_at, cylinder_axis, rounded_panel_xz, rounded_rect_prism
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


def mac_extension_mount_positions(
    p: StationParameters = DEFAULT,
) -> tuple[tuple[float, float], ...]:
    """Four blind USB-C boss axes for the two accepted identical adapters."""

    i = p.interfaces
    half_pitch = p.prototype_v4.usbc_mount_pitch / 2.0
    return tuple(
        (x + dx, z)
        for x, z in (
            (i.usbc_position_x, i.usbc_position_z),
            (i.usbc_second_position_x, i.usbc_second_position_z),
        )
        for dx in (-half_pitch, half_pitch)
    )


def ethernet_mount_positions(p: StationParameters = DEFAULT) -> tuple[tuple[float, float], ...]:
    i = p.interfaces
    v = p.prototype_v4
    return tuple(
        (i.ethernet_position_x + dx, i.ethernet_position_z + v.ethernet_mount_z_offset_selected)
        for dx in (-v.ethernet_mount_pitch / 2.0, v.ethernet_mount_pitch / 2.0)
    )


def hdmi_mount_positions(p: StationParameters = DEFAULT) -> tuple[tuple[float, float, float], ...]:
    """Top-down M3 insert axes in the accepted 13 mm HDMI shelf."""

    e = p.enclosure
    i = p.interfaces
    v = p.prototype_v4
    shelf_top = i.hdmi_position_z - (
        v.hdmi_connector_top_above_board - v.hdmi_cutout_height / 2.0
    ) - v.hdmi_shelf_drop_selected
    y = e.depth / 2.0 - v.hdmi_mount_axis_setback_selected
    return tuple((i.hdmi_position_x + dx, y, shelf_top) for dx in (-v.hdmi_mount_pitch / 2.0, v.hdmi_mount_pitch / 2.0))


def router_bulkhead_positions(p: StationParameters = DEFAULT) -> tuple[tuple[float, float], ...]:
    """Mobile/Wi-Fi/Mobile/Mobile/Wi-Fi/Mobile bulkhead row."""

    i = p.interfaces
    return tuple(
        ((index - 2.5) * i.router_bulkhead_pitch + i.router_interface_center_x, i.router_bulkhead_z)
        for index in range(6)
    )


def rear_panel(p: StationParameters = DEFAULT) -> cq.Workplane:
    e = p.enclosure
    i = p.interfaces
    f = p.fasteners
    y0 = e.depth / 2.0 - e.rear_panel_thickness
    center_z = (e.rear_opening_bottom + e.rear_opening_top) / 2.0
    part = rounded_panel_xz(
        e.rear_panel_width,
        e.rear_panel_height,
        e.rear_panel_thickness,
        e.rear_panel_corner_radius,
        y0,
        0.0,
        center_z,
        1,
    )
    cut_y = y0 - 1.0
    cut_d = e.rear_panel_thickness + 2.0

    # Accepted rear-I/O geometry: one Ethernet flange, one horizontal top-down HDMI
    # board, and two identical inside-mounted USB-C boards.  Only connector
    # mouths and the Ethernet flange screws penetrate the cosmetic panel.
    v = p.prototype_v4
    ethernet = _rounded_cutout_xz(
        v.ethernet_cutout_width + 2.0 * v.cutout_allowance,
        v.ethernet_cutout_height + 2.0 * v.cutout_allowance,
        1.2,
        i.ethernet_position_x,
        i.ethernet_position_z,
        cut_y,
        cut_d,
    )
    part = part.cut(ethernet)
    for x, z in ethernet_mount_positions(p):
        part = part.cut(
            cylinder_axis(
                (v.ethernet_mount_hole_diameter + v.mounting_hole_allowance) / 2.0,
                cut_d,
                (x, cut_y, z),
                (0, 1, 0),
            )
        )

    hdmi = _rounded_cutout_xz(
        i.hdmi_cutout_width,
        i.hdmi_cutout_height,
        1.5,
        i.hdmi_position_x,
        i.hdmi_position_z,
        cut_y,
        cut_d,
    )
    part = part.cut(hdmi)
    shelf_top = hdmi_mount_positions(p)[0][2]
    shelf_depth = v.hdmi_shelf_depth_selected
    hdmi_shelf = box_at(
        41.5,
        shelf_depth,
        7.0,
        (i.hdmi_position_x, y0 - shelf_depth / 2.0, shelf_top - 3.5),
    )
    part = part.union(hdmi_shelf)
    for x, y, z in hdmi_mount_positions(p):
        part = part.cut(
            cylinder_axis(
                f.m3_insert_hole_diameter / 2.0,
                f.insert_depth + 0.2,
                (x, y, z + 0.01),
                (0, 0, -1),
            )
        )

    usb_boss_face_y = y0 - v.usbc_board_standoff_selected
    for usb_x, usb_z in (
        (i.usbc_position_x, i.usbc_position_z),
        (i.usbc_second_position_x, i.usbc_second_position_z),
    ):
        bridge = box_at(
            v.usbc_mount_bridge_width,
            v.usbc_board_standoff_selected,
            v.usbc_mount_bridge_height,
            (usb_x, y0 - v.usbc_board_standoff_selected / 2.0, usb_z),
        )
        part = part.union(bridge)
        connector_tunnel = _rounded_cutout_xz(
            i.usbc_cutout_width,
            i.usbc_cutout_height,
            i.usbc_cutout_height / 2.0 - 0.1,
            usb_x,
            usb_z,
            usb_boss_face_y - 1.0,
            e.depth / 2.0 - usb_boss_face_y + 2.0,
        )
        part = part.cut(connector_tunnel)
        for dx in (-v.usbc_mount_pitch / 2.0, v.usbc_mount_pitch / 2.0):
            boss_x = usb_x + dx
            boss = cylinder_axis(
                f.m3_boss_diameter / 2.0,
                v.usbc_board_standoff_selected,
                (boss_x, usb_boss_face_y, usb_z),
                (0, 1, 0),
            )
            insert = cylinder_axis(
                f.m3_insert_hole_diameter / 2.0,
                f.insert_depth + 0.2,
                (boss_x, usb_boss_face_y - 0.01, usb_z),
                (0, 1, 0),
            )
            part = part.union(boss).cut(insert)
        reinforcement_pocket = box_at(
            v.usbc_reinforcement_pocket_width_selected,
            v.usbc_reinforcement_pocket_depth_selected + 0.2,
            v.usbc_reinforcement_pocket_height_selected,
            (
                usb_x,
                usb_boss_face_y + (v.usbc_reinforcement_pocket_depth_selected - 0.2) / 2.0,
                usb_z,
            ),
        )
        part = part.cut(reinforcement_pocket)

    # Six individual SMA/RP-SMA bulkheads mount directly in the rear panel.
    # An inside Ø12 rebate leaves the physically selected 2.0 mm exterior
    # clamping land; no separate bezel, snap hooks, or second Ethernet outlet
    # is required.
    rebate_depth = e.rear_panel_thickness - v.rf_bulkhead_wall_selected + 0.1
    for x, z in router_bulkhead_positions(p):
        rebate = cylinder_axis(6.0, rebate_depth, (x, y0 - 0.1, z), (0, 1, 0))
        hole = cylinder_axis(
            v.rf_bulkhead_hole_selected / 2.0,
            cut_d,
            (x, cut_y, z),
            (0, 1, 0),
        )
        part = part.cut(rebate).cut(hole)

    # Clearance around the *fixed* C8 island, which belongs to the closed power
    # compartment.  Rear-panel removal therefore does not move or uncover live
    # terminals.
    c8_island = _rounded_cutout_xz(42.7, 28.7, 4.35, i.c8_position_x, i.c8_position_z, cut_y, cut_d)
    part = part.cut(c8_island)

    # Open lower-edge notch completes the external finger path to the underside
    # Mac power button without lifting or tilting the enclosure.
    c = p.components
    bx = c.mac_button_x_side * (c.mac_width / 2.0 - c.mac_button_edge_offset_x)
    button_notch = _rounded_cutout_xz(i.finger_well_width + 1.0, 22.0, 4.0, bx, 20.0, cut_y, cut_d)
    part = part.cut(button_notch)

    # Passive high-level exhaust slots.  The APV remains in its closed inner box;
    # these slots ventilate the general upper equipment zone.
    for x in (-42.0, -28.0, -14.0, 0.0, 14.0, 28.0, 42.0):
        slot = _rounded_cutout_xz(5.0, 22.0, 2.0, x, 226.0, cut_y, cut_d)
        part = part.cut(slot)

    for z in i.rear_panel_screw_z:
        for x in (-i.rear_panel_screw_x, i.rear_panel_screw_x):
            hole = cylinder_axis(f.m3_clearance_diameter / 2.0, cut_d, (x, cut_y, z), (0, 1, 0))
            counterbore = cylinder_axis(6.2 / 2.0, 1.6, (x, y0 + e.rear_panel_thickness - 1.1, z), (0, 1, 0))
            part = part.cut(hole).cut(counterbore)
    return part


def rear_panel_fit_coupon(p: StationParameters = DEFAULT) -> cq.Workplane:
    """Production-orientation rear fit: upright shell frame and flat panel insert."""

    fits = p.fits
    frame_center_z = 20.0
    frame = rounded_panel_xz(54.0, 34.0, 5.0, 4.0, 0.0, 0.0, frame_center_z, 1)
    opening = rounded_panel_xz(
        42.0 + 2.0 * fits.rear_panel_x_per_side,
        22.0 + 2.0 * fits.rear_panel_z_per_side,
        6.0,
        3.0 + fits.rear_panel_x_per_side,
        -0.5,
        0.0,
        frame_center_z,
        1,
    )
    # The foot makes the receiver self-supporting in the same upright Z
    # orientation as the shell.  The separate insert lies flat like the actual
    # rear panel, so the coupon captures the two different print directions.
    foot = box_at(58.0, 18.0, 3.0, (0.0, 2.5, 1.5))
    frame = frame.cut(opening).union(foot)
    insert = rounded_rect_prism(42.0, 22.0, 3.0, 3.0).translate((70.0, 0.0, 0.0))
    return frame.union(insert)


def c8_cutout_coupon(p: StationParameters = DEFAULT) -> cq.Workplane:
    i = p.interfaces
    plate = rounded_panel_xz(55.0, 35.0, 3.2, 4.0, 0.0, 0.0, 0.0, 1)
    cw = i.c8_cutout_width + i.c8_panel_fit_allowance
    ch = i.c8_cutout_height + i.c8_panel_fit_allowance
    cut = _rounded_cutout_xz(cw, ch, i.c8_cutout_corner_radius, 0.0, 0.0, -1.0, 5.2)
    plate = plate.cut(cut)
    for x in (-i.c8_hole_pitch / 2.0, i.c8_hole_pitch / 2.0):
        plate = plate.cut(cylinder_axis(i.c8_hole_diameter / 2.0, 5.2, (x, -1.0, 0.0), (0, 1, 0)))
    return plate


def router_rf_access_coupon(p: StationParameters = DEFAULT) -> cq.Workplane:
    """Full six-port RF window section for real coupling-nut/finger trials."""

    c = p.components
    i = p.interfaces
    width = 5.0 * c.router_sma_pitch + c.router_sma_clearance_diameter
    plate = rounded_panel_xz(110.0, 46.0, 3.2, 5.0, 0.0, 0.0, 0.0, 1)
    opening = _rounded_cutout_xz(width, i.router_rf_window_height, 5.0, 0.0, 0.0, -1.0, 5.2)
    return plate.cut(opening)
