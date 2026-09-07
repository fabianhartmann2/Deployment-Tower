"""Removable rear service panel and replaceable router-interface bezel."""

from __future__ import annotations

import cadquery as cq

from .geometry import box_at, cylinder_axis, rounded_panel_xz
from .layout import packaging_layout
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
    """Provisional two-screw flange pattern for each Mac port extension."""

    i = p.interfaces
    half_pitch = i.mac_extension_mount_vertical_pitch / 2.0
    return tuple(
        (x, z + dz)
        for x, z in (
            (i.hdmi_position_x, i.hdmi_position_z),
            (i.usbc_position_x, i.usbc_position_z),
        )
        for dz in (-half_pitch, half_pitch)
    )


def router_extension_mount_positions(
    p: StationParameters = DEFAULT,
) -> tuple[tuple[float, float], ...]:
    """Provisional two-screw flange pattern for each Ethernet extension."""

    i = p.interfaces
    half_pitch = i.router_extension_mount_horizontal_pitch / 2.0
    z = i.router_interface_center_z + 18.0
    return tuple(
        (x + dx, z)
        for x in (i.router_interface_center_x - 17.0, i.router_interface_center_x + 17.0)
        for dx in (-half_pitch, half_pitch)
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

    # Through aperture and shallow outer rebate for the replaceable snap-in
    # router bezel.  Its broad face is flush without occupying panel material.
    bezel = _rounded_cutout_xz(
        i.router_bezel_aperture_width + 0.6,
        i.router_bezel_aperture_height + 0.6,
        5.0,
        i.router_bezel_center_x,
        i.router_interface_center_z,
        cut_y,
        cut_d,
    )
    part = part.cut(bezel)
    bezel_seat = _rounded_cutout_xz(
        i.router_bezel_width + 0.5,
        i.router_bezel_height + 0.5,
        5.0,
        i.router_bezel_center_x,
        i.router_interface_center_z,
        e.depth / 2.0 - 2.5,
        2.6,
    )
    part = part.cut(bezel_seat)

    # Provisional two-screw flanged extensions are selected for HDMI and USB-C
    # because exact Mac native-port coordinates and cable overmoulds were not
    # supplied.  The keyed opening reacts rotation; the explicit through-holes
    # transfer insertion loads into the removable panel through selected flange
    # screws/locking hardware rather than into the native Mac ports.
    hdmi = _rounded_cutout_xz(i.hdmi_cutout_width, i.hdmi_cutout_height, 2.0, i.hdmi_position_x, i.hdmi_position_z, cut_y, cut_d)
    usbc = _rounded_cutout_xz(i.usbc_cutout_width, i.usbc_cutout_height, 2.2, i.usbc_position_x, i.usbc_position_z, cut_y, cut_d)
    part = part.cut(hdmi).cut(usbc)
    for x, z in mac_extension_mount_positions(p):
        part = part.cut(cylinder_axis(f.m3_clearance_diameter / 2.0, cut_d, (x, cut_y, z), (0, 1, 0)))

    # Clearance around the *fixed* C8 island, which belongs to the closed power
    # compartment.  Rear-panel removal therefore does not move or uncover live
    # terminals.
    c8_island = _rounded_cutout_xz(42.7, 28.7, 4.35, i.c8_position_x, i.c8_position_z, cut_y, cut_d)
    part = part.cut(c8_island)

    # Open lower-edge notch completes the external finger path to the underside
    # Mac power button without lifting or tilting the enclosure.
    c = p.components
    bx = c.mac_width / 2.0 - c.mac_button_edge_offset_x
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


def router_interface_bezel(p: StationParameters = DEFAULT) -> cq.Workplane:
    e = p.enclosure
    i = p.interfaces
    c = p.components
    f = p.fasteners
    y0 = e.depth / 2.0 - i.router_bezel_thickness
    face_thickness = 2.4
    face = rounded_panel_xz(
        i.router_bezel_width,
        i.router_bezel_height,
        face_thickness,
        4.5,
        e.depth / 2.0 - face_thickness,
        i.router_bezel_center_x,
        i.router_interface_center_z,
        1,
    )
    insert = rounded_panel_xz(
        i.router_bezel_aperture_width - 0.2,
        i.router_bezel_aperture_height - 0.2,
        i.router_bezel_thickness - face_thickness,
        4.0,
        y0,
        i.router_bezel_center_x,
        i.router_interface_center_z,
        1,
    )
    part = face.union(insert)
    cut_y = y0 - 1.0
    cut_d = i.router_bezel_thickness + 2.0
    layout = packaging_layout(p)
    sma_z = layout.router_center[2] - c.router_height / 2.0 + 12.0
    # One radiused RF service window follows the six native connector centres.
    # Separate Ø14 mm holes at the official 14.8 mm pitch would leave fragile
    # 0.8 mm webs, below the printable wall requirement.
    rf_window_width = 5.0 * c.router_sma_pitch + c.router_sma_clearance_diameter
    rf_window = _rounded_cutout_xz(
        rf_window_width,
        i.router_rf_window_height,
        5.0,
        i.router_interface_center_x,
        sma_z,
        cut_y,
        cut_d,
    )
    part = part.cut(rf_window)
    # Ethernet jacks use provisional two-screw flanged extensions because the
    # native LAN/WAN face points toward the enclosure front, opposite the six
    # direct RF ports.  The replaceable bezel carries the explicit through-hole
    # pattern; selected flange screws/locking hardware carry insertion loads.
    rj_z = i.router_interface_center_z + 18.0
    for x in (i.router_interface_center_x - 17.0, i.router_interface_center_x + 17.0):
        rj = _rounded_cutout_xz(c.router_rj45_clearance_width, c.router_rj45_clearance_height, 1.5, x, rj_z, cut_y, cut_d)
        part = part.cut(rj)
    for x, z in router_extension_mount_positions(p):
        part = part.cut(cylinder_axis(f.m3_clearance_diameter / 2.0, cut_d, (x, cut_y, z), (0, 1, 0)))

    # Four concealed cantilever hooks engage the inner edge of the rear-panel
    # aperture.  They flex inward for replacement and sit behind—not inside—the
    # panel material in the installed model.
    for side in (-1.0, 1.0):
        for z in (184.0, 209.0):
            stem = box_at(3.0, 4.0, 6.0, (side * 54.0, y0 - 2.0, z))
            hook = box_at(5.0, 2.4, 4.0, (side * 57.0, e.depth / 2.0 - e.rear_panel_thickness - 1.3, z))
            part = part.union(stem).union(hook)
    return part


def rear_panel_fit_coupon(p: StationParameters = DEFAULT) -> cq.Workplane:
    clearance = p.fits.service_panel_per_side
    frame = rounded_panel_xz(54.0, 34.0, 5.0, 4.0, 0.0, 0.0, 0.0, 1)
    opening = rounded_panel_xz(42.0 + 2.0 * clearance, 22.0 + 2.0 * clearance, 6.0, 3.0, -0.5, 0.0, 0.0, 1)
    insert = rounded_panel_xz(42.0, 22.0, 3.0, 3.0, 6.0, 0.0, 0.0, 1)
    return frame.cut(opening).union(insert)


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
