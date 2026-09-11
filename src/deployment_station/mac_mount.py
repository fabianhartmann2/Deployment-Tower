"""Mac cradle with replaceable pad locations and open intake field."""

from __future__ import annotations

from math import atan2, cos, degrees, sin

import cadquery as cq

from .geometry import box_at, rounded_rect_prism
from .parameters import DEFAULT, StationParameters


def mac_cradle_fastener_positions(p: StationParameters = DEFAULT) -> tuple[tuple[float, float], ...]:
    """Downward-accessible cradle screws kept outside the Mac footprint."""

    y0 = p.components.mac_center_y
    return ((-70.0, y0 - 34.0), (70.0, y0 - 34.0), (-70.0, y0 + 28.0), (70.0, y0 + 28.0))


def mac_vertical_retainer_centres(
    p: StationParameters = DEFAULT,
) -> tuple[tuple[float, float, float], ...]:
    """Return ``(side, x, y)`` datums for the four side clips."""

    c = p.components
    r = p.mac_retention
    stem_inner_x = c.mac_width / 2.0 + r.side_clearance
    return tuple(
        (
            side,
            side * (stem_inner_x + r.stem_thickness / 2.0),
            c.mac_center_y + y_offset,
        )
        for side in (-1.0, 1.0)
        for y_offset in r.y_offsets
    )


def mac_vertical_retainer_lead_in(
    p: StationParameters,
    side: float,
    clip_y: float,
) -> cq.Workplane:
    """Return one underside cam-relief prism for a Mac side clip."""

    if side not in (-1.0, 1.0):
        raise ValueError("side must be -1.0 or 1.0")
    c = p.components
    retention = p.mac_retention
    mac_half_width = c.mac_width / 2.0
    tab_bottom_z = c.mac_support_plane_z + c.mac_retained_body_height + retention.top_gap
    inner_tip_x = side * (mac_half_width - retention.overhang)
    mac_side_x = side * mac_half_width
    return (
        cq.Workplane("XZ")
        # The XZ workplane normal points toward -Y, so its signed offset is the
        # negative of the desired global-Y start face.
        .workplane(offset=-clip_y - retention.clip_depth / 2.0)
        .polyline(
            (
                (inner_tip_x, tab_bottom_z),
                (inner_tip_x, tab_bottom_z + retention.lead_in_height),
                (mac_side_x, tab_bottom_z),
            )
        )
        .close()
        .extrude(retention.clip_depth)
    )


def mac_release_rail_datums(
    p: StationParameters = DEFAULT,
) -> tuple[tuple[float, float, float, float, float, float], ...]:
    """Return ``(side, x, y, width, depth, bottom_z)`` for two release rails."""

    c = p.components
    retention = p.mac_retention
    if len(retention.y_offsets) < 2:
        raise ValueError("at least two clip stations are required for linked release rails")
    outer_stem_face = (
        c.mac_width / 2.0
        + retention.side_clearance
        + retention.stem_thickness
    )
    rail_width = retention.release_rail_outreach + retention.release_rail_root_overlap
    rail_depth = max(retention.y_offsets) - min(retention.y_offsets) + retention.clip_depth
    rail_y = c.mac_center_y + (max(retention.y_offsets) + min(retention.y_offsets)) / 2.0
    rail_bottom_z = c.mac_support_plane_z + retention.release_rail_bottom_offset
    return tuple(
        (
            side,
            side
            * (
                outer_stem_face
                + (retention.release_rail_outreach - retention.release_rail_root_overlap) / 2.0
            ),
            rail_y,
            rail_width,
            rail_depth,
            rail_bottom_z,
        )
        for side in (-1.0, 1.0)
    )


def mac_cradle(p: StationParameters = DEFAULT) -> cq.Workplane:
    c = p.components
    f = p.fasteners
    z0 = c.mac_support_plane_z - 5.0
    cradle_top_z = z0 + 4.0
    outer = rounded_rect_prism(c.mac_width + 10.0, c.mac_depth + 10.0, 4.0, c.mac_corner_radius + 3.0, z0).translate((0.0, c.mac_center_y, 0.0))
    # Physical trial found the previous Ø116 opening 4 mm too large.  Match the
    # measured/photo-derived Ø112 underside ring while leaving the base opening
    # independently larger for airflow.
    opening = cq.Workplane("XY").circle(c.mac_intake_outer_diameter / 2.0).extrude(6.0).translate((0, c.mac_center_y, z0 - 1.0))
    cradle = outer.cut(opening)

    # Four corner pad seats lie outside the annular intake.  The configured
    # recess takes replaceable silicone/TPU pads that finish at the controlled
    # Mac support plane; pads are BOM items, not printed ASA.
    pad_xy = c.mac_width / 2.0 - 10.0
    for x in (-pad_xy, pad_xy):
        for y in (-pad_xy, pad_xy):
            if x * c.mac_button_x_side > 0 and y > 0:
                # Button corner remains clear; support is shifted to the other
                # three corners pending physical underside-relief measurement.
                continue
            # Open the pocket from above and remove exactly the configured
            # depth from the cradle top.  The extra 1 mm is cutting overshoot,
            # not additional recess depth.
            seat = box_at(
                15.0,
                15.0,
                p.mac_retention.base_pad_seat_depth + 1.0,
                (
                    x,
                    y + c.mac_center_y,
                    cradle_top_z
                    + (1.0 - p.mac_retention.base_pad_seat_depth) / 2.0,
                ),
            )
            cradle = cradle.cut(seat)

    # Low mid-side keepers restrain lateral motion while staying out of the shell
    # corner radii and the photo-derived button/connector regions.
    keeper_z = c.mac_support_plane_z + 2.0
    side_offset = c.mac_width / 2.0 + p.mac_retention.side_clearance + 1.5
    for x in (-side_offset, side_offset):
        cradle = cradle.union(box_at(3.0, 44.0, 6.0, (x, c.mac_center_y - 5.0, keeper_z)))
    front_y = c.mac_center_y - c.mac_depth / 2.0 - p.mac_retention.side_clearance - 1.5
    rear_y = c.mac_center_y + c.mac_depth / 2.0 + p.mac_retention.side_clearance + 1.5
    cradle = cradle.union(box_at(48.0, 3.0, 6.0, (0.0, front_y, keeper_z)))
    cradle = cradle.union(box_at(22.0, 3.0, 6.0, (-43.0, rear_y, keeper_z)))

    # Mounting ears accept four screws from below.  Matching insert bosses are
    # integral to the lower shell, so the cradle/Mac can be withdrawn downward
    # after removing the base without disturbing the router.
    for x, y in mac_cradle_fastener_positions(p):
        ear = box_at(12.0, 14.0, 4.0, (x, y, z0 + 2.0))
        hole = cq.Workplane("XY").center(x, y).circle(f.m3_clearance_diameter / 2.0).extrude(8.0).translate((0, 0, z0 - 1.0))
        cradle = cradle.union(ear).cut(hole)

    # Continuous rear/underside finger corridor to the provisional native power
    # button.  The matching base, lower-shell, and rear-panel notches are checked
    # together by the swept-path validation.
    bx = c.mac_button_x_side * (c.mac_width / 2.0 - c.mac_button_edge_offset_x)
    by = c.mac_center_y + c.mac_depth / 2.0 - c.mac_button_edge_offset_y
    rear_edge = p.enclosure.depth / 2.0 + 2.0
    corridor_start_y = by - c.mac_button_diameter / 2.0 - c.mac_button_free_clearance
    reach = rear_edge - corridor_start_y
    corridor = box_at(
        p.interfaces.finger_well_width,
        reach,
        18.0,
        (bx, corridor_start_y + reach / 2.0, c.mac_support_plane_z - 5.0),
    )
    cradle = cradle.cut(corridor)

    # Clear the two front base-fastener boss/web clusters; those remain captive
    # in the lower shell while the cradle moves downward.
    base_boss_xy = p.enclosure.width / 2.0 - 13.0
    for x in (-base_boss_xy, base_boss_xy):
        relief = box_at(22.0, 22.0, 14.0, (x, -base_boss_xy, c.mac_support_plane_z))
        cradle = cradle.cut(relief)
    for x in (-61.0, 61.0):
        cradle = cradle.cut(box_at(13.0, 13.0, 14.0, (x, -75.0, c.mac_support_plane_z)))

    # Four slender side cantilevers provide positive vertical transport
    # retention while leaving a controlled, non-contact gap above the installed
    # Mac.  Underside cams deflect the hooks outward during upward engagement;
    # paired external rails let a technician release both hooks on each side
    # from the open bottom after removing the base.  Small pockets in the cam
    # faces accept replaceable TPU/silicone wear pads.  Exact pad thickness,
    # preload, release force, and fatigue remain intentionally unclaimed until
    # physical fit, shake, and cycle tests have been completed.
    retention = p.mac_retention
    mac_half_width = c.mac_width / 2.0
    mac_top_z = c.mac_support_plane_z + c.mac_retained_body_height
    stem_bottom_z = c.mac_support_plane_z - 1.0
    tab_bottom_z = mac_top_z + retention.top_gap
    tab_top_z = tab_bottom_z + retention.tab_thickness
    tab_width = retention.side_clearance + retention.stem_thickness + retention.overhang
    tab_center_from_origin = mac_half_width + (
        retention.side_clearance + retention.stem_thickness - retention.overhang
    ) / 2.0
    lead_in_angle = atan2(retention.lead_in_height, retention.overhang)

    for side, stem_x, clip_y in mac_vertical_retainer_centres(p):
        stem = box_at(
            retention.stem_thickness,
            retention.clip_depth,
            tab_top_z - stem_bottom_z,
            (stem_x, clip_y, (stem_bottom_z + tab_top_z) / 2.0),
        )
        tab = box_at(
            tab_width,
            retention.clip_depth,
            retention.tab_thickness,
            (side * tab_center_from_origin, clip_y, tab_bottom_z + retention.tab_thickness / 2.0),
        )
        cradle = cradle.union(stem).union(tab).cut(mac_vertical_retainer_lead_in(p, side, clip_y))

        # Rotate each pad pocket into its cam face.  A 0.2 mm overshoot opens the
        # pocket cleanly while retaining the configured recess depth in the hook.
        pad_cut_depth = retention.pad_seat_recess + 0.2
        pad_cut_into_hook = retention.pad_seat_recess / 2.0 - 0.1
        pad_angle = side * lead_in_angle
        pad_seat_x = side * (mac_half_width - retention.overhang / 2.0) + sin(pad_angle) * pad_cut_into_hook
        pad_seat_z = tab_bottom_z + retention.lead_in_height / 2.0 + cos(pad_angle) * pad_cut_into_hook
        pad_seat = (
            box_at(
                retention.pad_seat_width,
                retention.pad_seat_length,
                pad_cut_depth,
                (0.0, 0.0, 0.0),
            )
            .rotate((0.0, 0.0, 0.0), (0.0, 1.0, 0.0), degrees(pad_angle))
            .translate((pad_seat_x, clip_y, pad_seat_z))
        )
        cradle = cradle.cut(pad_seat)

    for _side, rail_x, rail_y, rail_width, rail_depth, rail_bottom_z in mac_release_rail_datums(p):
        release_rail = box_at(
            rail_width,
            rail_depth,
            retention.release_rail_height,
            (rail_x, rail_y, rail_bottom_z + retention.release_rail_height / 2.0),
        )
        cradle = cradle.union(release_rail)
    return cradle


def compliant_pad_template(p: StationParameters = DEFAULT) -> cq.Workplane:
    return rounded_rect_prism(14.6, 14.6, p.mac_retention.base_pad_thickness, 2.0)
