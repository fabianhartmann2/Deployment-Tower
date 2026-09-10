"""Two external antenna transport docks with compliant C-clips."""

from __future__ import annotations

import cadquery as cq

from .geometry import box_at, cylinder_axis, rounded_panel_yz
from .parameters import DEFAULT, StationParameters


def _vertical_recessed_clip(
    radius_inner: float,
    wall: float,
    width: float,
    center: tuple[float, float, float],
    side: int,
    exterior_x: float,
    lip_radius: float = 1.0,
    lip_intrusion: float = 0.75,
) -> cq.Workplane:
    """Vertical-axis half-annulus with small rounded snap noses."""

    cx, cy, cz = center
    outer_radius = radius_inner + wall
    outer = cylinder_axis(outer_radius, width, (cx, cy, cz - width / 2.0), (0, 0, 1))
    inner = cylinder_axis(radius_inner, width + 2.0, (cx, cy, cz - width / 2.0 - 1.0), (0, 0, 1))
    ring = outer.cut(inner)
    # Keep only the enclosure-side semicircle.  The antenna enters laterally from
    # outside, so neither clip nor backplate exceeds the fixed body datum.
    keep = box_at(50.0, 2.0 * outer_radius + 4.0, width + 2.0, (exterior_x - side * 25.0, cy, cz))
    ring = ring.intersect(keep)
    # Small rounded noses provide a lead-in and controlled retention.  The old
    # 6 mm rectangular lips reduced a nominal 30 mm mouth to about 22.8 mm and
    # demanded impossible deflection; these noses intrude only 0.75 mm/side.
    for y_sign in (-1.0, 1.0):
        nose_center_y = cy + y_sign * (radius_inner - lip_intrusion + lip_radius)
        nose = cylinder_axis(
            lip_radius,
            width,
            (exterior_x - side * lip_radius, nose_center_y, cz - width / 2.0),
            (0, 0, 1),
        )
        ring = ring.union(nose)
    return ring


def wifi_dock(side: str, p: StationParameters = DEFAULT) -> cq.Workplane:
    if side not in {"left", "right"}:
        raise ValueError("side must be 'left' or 'right'")
    e = p.enclosure
    w = p.wifi
    sign = 1 if side == "right" else -1
    # Dock material stays within the body envelope; the antenna (excluded from
    # that envelope) is centred on the exterior side datum.
    x0 = sign * (e.width / 2.0 - w.backplate_thickness)
    backplate = rounded_panel_yz(
        w.backplate_width,
        w.backplate_height,
        w.backplate_thickness,
        5.0,
        x0,
        w.dock_center_y,
        w.dock_center_z,
        sign,
    )
    clip_center_x = sign * e.width / 2.0
    base_z = w.dock_center_z - 35.0
    stem_z = w.dock_center_z + 25.0
    base_clip = _vertical_recessed_clip(
        w.antenna_base_diameter / 2.0 + p.fits.wifi_clip_radial,
        w.clip_wall,
        w.clip_width,
        (clip_center_x, w.dock_center_y, base_z),
        sign,
        clip_center_x,
        w.clip_lip_radius,
        w.clip_lip_intrusion,
    )
    stem_clip = _vertical_recessed_clip(
        w.antenna_stem_diameter / 2.0 + p.fits.wifi_clip_radial,
        w.clip_wall,
        w.clip_width,
        (clip_center_x, w.dock_center_y, stem_z),
        sign,
        clip_center_x,
        w.clip_lip_radius,
        w.clip_lip_intrusion,
    )
    # Shelf carries the Ø30 hub mass; the radial-cable side remains open.
    shelf = box_at(
        w.antenna_base_diameter / 2.0 + p.fits.wifi_clip_radial + w.clip_wall,
        w.backplate_width - 4.0,
        3.0,
        (sign * (e.width / 2.0 - (w.antenna_base_diameter / 2.0 + p.fits.wifi_clip_radial + w.clip_wall) / 2.0), w.dock_center_y, w.dock_center_z - w.antenna_length / 2.0 - 1.5),
    )
    cable_notch = box_at(
        w.antenna_base_diameter / 2.0 + p.fits.wifi_clip_radial + w.clip_wall + 2.0,
        w.cable_exit_width,
        8.0,
        (sign * (e.width / 2.0 - (w.antenna_base_diameter / 2.0 + p.fits.wifi_clip_radial + w.clip_wall) / 2.0), w.dock_center_y + w.backplate_width / 2.0 - 3.0, w.dock_center_z - w.antenna_length / 2.0 + 2.0),
    )
    dock = backplate.union(base_clip).union(stem_clip).union(shelf).cut(cable_notch)

    # The lower shell-attachment web passes behind a local shelf relief so the
    # support and removable dock meet only at their fastened datum faces.
    shelf_width = w.antenna_base_diameter / 2.0 + p.fits.wifi_clip_radial + w.clip_wall
    relief = box_at(
        shelf_width - w.backplate_thickness + 0.5,
        10.0,
        5.0,
        (sign * (e.width / 2.0 - w.backplate_thickness - (shelf_width - w.backplate_thickness) / 2.0), 41.0, w.dock_center_z - w.antenna_length / 2.0 - 1.5),
    )
    dock = dock.cut(relief)

    # Two outside-accessible M3 clearances match the shell insert bosses.
    f = p.fasteners
    for z in (171.0, 258.0):
        hole = cylinder_axis(
            f.m3_clearance_diameter / 2.0,
            w.backplate_thickness + 2.0,
            (sign * (e.width / 2.0 + 1.0), 41.0, z),
            (-sign, 0, 0),
        )
        dock = dock.cut(hole)
    return dock


def wifi_dock_coupon(p: StationParameters = DEFAULT) -> cq.Workplane:
    w = p.wifi
    # Three hub diameters are provided in one coupon, matching the photo-analysis
    # recommendation: 30.0, 30.5 and 31.0 mm nominal captures.
    coupon = cq.Workplane("XY")
    for index, diameter in enumerate((30.0, 30.5, 31.0)):
        y = (index - 1) * 42.0
        back = box_at(5.0, 36.0, 42.0, (0.0, y, 21.0))
        clip = _vertical_recessed_clip(
            diameter / 2.0,
            w.clip_wall,
            10.0,
            (2.5, y, 23.0),
            1,
            2.5,
            w.clip_lip_radius,
            w.clip_lip_intrusion,
        )
        # One/two/three through-markers identify 30.0/30.5/31.0 mm even if the
        # exporter reorders disconnected solids while packing them on the bed.
        marker_count = index + 1
        for marker_index in range(marker_count):
            marker_y = y + (marker_index - (marker_count - 1) / 2.0) * 5.0
            marker = cylinder_axis(1.2, 7.0, (-3.5, marker_y, 6.0), (1, 0, 0))
            back = back.cut(marker)
        coupon = coupon.union(back).union(clip)
    return coupon
