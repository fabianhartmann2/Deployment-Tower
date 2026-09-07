"""Externally replaceable square logo panels and generation template."""

from __future__ import annotations

import cadquery as cq

from .geometry import box_at, cylinder_axis, rounded_panel_yz
from .parameters import DEFAULT, StationParameters


def logo_panel(side: str, p: StationParameters = DEFAULT, embossed: bool = False) -> cq.Workplane:
    """Create a left/right blank panel, optionally with an abstract raised mark."""

    if side not in {"left", "right"}:
        raise ValueError("side must be 'left' or 'right'")
    e = p.enclosure
    logo = p.logo
    sign = 1 if side == "right" else -1
    inner_face = sign * (e.width / 2.0 - logo.thickness)
    panel = rounded_panel_yz(
        logo.size,
        logo.size,
        logo.thickness,
        logo.corner_radius,
        inner_face,
        0.0,
        logo.center_z,
        sign,
    )
    # Four concealed cantilever studs push normally through receiver slots in the
    # shell.  Their small inner barbs sit behind the receiver blocks; no adhesive
    # or visible fastener is required.  The geometry remains a concept until the
    # dedicated cycle coupon establishes filament-specific flexure and clearance.
    plate_inner_x = sign * (e.width / 2.0 - logo.thickness)
    receiver_inner_x = sign * (e.width / 2.0 - 10.5)
    post_length = abs(plate_inner_x - receiver_inner_x) + 0.3
    post_center_x = (plate_inner_x + receiver_inner_x) / 2.0
    for y in (-26.0, 26.0):
        for z in (logo.center_z - 22.0, logo.center_z + 22.0):
            post = box_at(post_length, 3.2, 8.0, (post_center_x, y, z))
            hook_x = receiver_inner_x - sign * 1.2
            hook = box_at(2.4, 6.0, 4.0, (hook_x, y, z - 2.0))
            panel = panel.union(post).union(hook)

    # A thumbnail scallop at the lower edge starts removal without marring the
    # face; the receiver hooks then flex through their slots.
    notch = cylinder_axis(
        logo.finger_notch_diameter / 2.0,
        logo.thickness + 1.0,
        (sign * (e.width / 2.0 - logo.thickness - 0.5), 0.0, logo.center_z - logo.size / 2.0),
        (sign, 0, 0),
    )
    panel = panel.cut(notch)

    if embossed:
        outer_x = sign * e.width / 2.0
        mark_x = sign * (e.width / 2.0 + logo.emboss_height / 2.0)
        # Neutral three-bar sample mark; callers can replace this block with text,
        # SVG-derived wires, an engraving cut, or multibody inlay geometry.
        bars = [
            box_at(logo.emboss_height, 7.0, 34.0, (mark_x, -12.0, logo.center_z)),
            box_at(logo.emboss_height, 7.0, 24.0, (mark_x, 0.0, logo.center_z)),
            box_at(logo.emboss_height, 7.0, 14.0, (mark_x, 12.0, logo.center_z)),
        ]
        for bar in bars:
            panel = panel.union(bar)
    return panel


def blank_logo_panel(p: StationParameters = DEFAULT) -> cq.Workplane:
    return logo_panel("right", p, embossed=False)


def example_embossed_logo_panel(p: StationParameters = DEFAULT) -> cq.Workplane:
    return logo_panel("right", p, embossed=True)


def logo_retention_coupon(p: StationParameters = DEFAULT) -> cq.Workplane:
    logo = p.logo
    clear = p.fits.logo_panel_per_side
    # Receiver and a separate full-length representative cantilever are printed
    # together; the 0.25 mm/side default is visible in the slot dimensions.
    receiver = box_at(8.0, 20.0, 24.0, (4.0, 0.0, 12.0))
    slot = box_at(10.0, 3.2 + 2.0 * clear, 8.0 + 2.0 * clear, (4.0, 0.0, 12.0))
    receiver = receiver.cut(slot)
    plate = box_at(logo.thickness, 20.0, 24.0, (24.0, 0.0, 12.0))
    post = box_at(8.4, 3.2, 8.0, (18.6, 0.0, 12.0))
    hook = box_at(2.4, 6.0, 4.0, (13.2, 0.0, 10.0))
    return receiver.union(plate.union(post).union(hook))
