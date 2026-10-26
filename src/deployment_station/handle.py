"""Sliding top cap and positively screw-mounted removable handle."""

from __future__ import annotations

import cadquery as cq

from .geometry import box_at, cylinder_axis, rounded_rect_prism
from .parameters import DEFAULT, StationParameters


def rigid_handle_anchor_y(p: StationParameters = DEFAULT) -> float:
    """Centre the optional rigid handle on the enclosure balance line."""

    del p
    return 0.0


def cap_fastener_positions(p: StationParameters = DEFAULT) -> tuple[tuple[float, float], ...]:
    """Two internal anti-slide lock axes; neither opens through the top face."""

    del p
    return ((-55.0, 0.0), (55.0, 0.0))


def handle_mount_fastener_positions(p: StationParameters = DEFAULT) -> tuple[tuple[float, float], ...]:
    """Four M3 axes, two outside each handle leg for direct tool access."""

    h = p.handle
    anchor_y = rigid_handle_anchor_y(p)
    return tuple(
        (anchor_x + offset_x, anchor_y)
        for anchor_x in (-h.anchor_spacing / 2.0, h.anchor_spacing / 2.0)
        for offset_x in (-h.fastener_offset_x, h.fastener_offset_x)
    )


def cap_dovetail_y_positions(p: StationParameters = DEFAULT) -> tuple[float, float]:
    """Transverse rails let the cap slide on from either side."""

    del p
    return (-68.0, 68.0)


def _dovetail_along_x(
    bottom_width: float,
    top_width: float,
    height: float,
    half_length: float,
    z0: float,
    y: float,
) -> cq.Workplane:
    """Trapezoidal rail/groove profile in YZ, extruded along X."""

    points = (
        (-bottom_width / 2.0, z0),
        (bottom_width / 2.0, z0),
        (top_width / 2.0, z0 + height),
        (-top_width / 2.0, z0 + height),
    )
    return cq.Workplane("YZ").polyline(points).close().extrude(half_length, both=True).translate((0.0, y, 0.0))


def cap_dovetail_rail(y: float, p: StationParameters = DEFAULT) -> cq.Workplane:
    """Male shell rail carried continuously into the rounded side corners."""

    v = p.prototype_v4
    e = p.enclosure
    rail = _dovetail_along_x(
        v.dovetail_rail_bottom_width,
        v.dovetail_rail_top_width,
        v.dovetail_rail_height,
        e.width / 2.0 + 2.0,
        e.shell_top,
        y,
    )
    # Trimming by the actual rounded enclosure footprint removes the former
    # four square-ended gaps without protruding through the cosmetic corners.
    envelope = rounded_rect_prism(
        e.width,
        e.depth,
        v.dovetail_rail_height + 0.2,
        e.outer_corner_radius,
        e.shell_top - 0.1,
    )
    return rail.intersect(envelope)


def cap_dovetail_groove(y: float, p: StationParameters = DEFAULT) -> cq.Workplane:
    """Female cap groove with the selected 0.10 mm per-side allowance."""

    v = p.prototype_v4
    clearance = v.dovetail_clearance_selected
    return _dovetail_along_x(
        v.dovetail_rail_bottom_width + 2.0 * clearance,
        v.dovetail_rail_top_width + 2.0 * clearance,
        v.dovetail_rail_height + clearance,
        p.enclosure.width / 2.0 + 1.0,
        p.enclosure.shell_top - 0.1,
        y,
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
    anchor_y = rigid_handle_anchor_y(p)
    # A full-width crossmember and two solid local bearing pads carry the handle
    # feet into both side walls and the reinforced upper-shell ribs.  The pads
    # fill the cap below each foot instead of loading the 4 mm top skin alone.
    cap = cap.union(box_at(e.width - 16.0, 12.0, 8.0, (0.0, anchor_y, z0 + 4.0)))
    for x in (-h.anchor_spacing / 2.0, h.anchor_spacing / 2.0):
        bearing_pad = box_at(
            h.foot_width + 6.0,
            h.foot_depth + 6.0,
            e.cap_height - 4.0,
            (x, anchor_y, z0 + (e.cap_height - 4.0) / 2.0),
        )
        longitudinal_tie = box_at(12.0, h.foot_depth + 12.0, 8.0, (x, anchor_y, z0 + 4.0))
        cap = cap.union(bearing_pad).union(longitudinal_tie)

    # The handle screws enter from the cap underside.  Deep internal head
    # pockets leave 9 mm of cap grip under each broad foot while the top face
    # and handle feet hide every fastener from view.
    for x, y in handle_mount_fastener_positions(p):
        clearance = cylinder_axis(
            f.m3_clearance_diameter / 2.0,
            e.cap_height + 2.0,
            (x, y, z0 - 1.0),
            (0, 0, 1),
        )
        head_access = cylinder_axis(
            f.m3_low_head_recess_diameter / 2.0,
            4.0,
            (x, y, z0 - 1.0),
            (0, 0, 1),
        )
        cap = cap.cut(clearance).cut(head_access)

    # Two blind M4 inserts lock the sideways cap motion from inside the shell.
    # The dovetails—not these screws—carry vertical handle load.
    for x, y in cap_fastener_positions(p):
        lock_boss = (
            cq.Workplane("XY")
            .center(x, y)
            .circle(f.m4_boss_diameter / 2.0)
            .extrude(8.0)
            .translate((0, 0, z0))
        )
        insert = cylinder_axis(
            f.m4_insert_hole_diameter / 2.0,
            f.insert_depth + 0.7,
            (x, y, z0 - 0.1),
            (0, 0, 1),
        )
        cap = cap.union(lock_boss).cut(insert)

    # Selected 0.10 mm/side V-grooves retain the cap vertically.  They remain
    # open at both side edges, so the handle can first be bolted to the detached
    # cap and the complete subassembly then slid onto the shell.
    for y in cap_dovetail_y_positions(p):
        cap = cap.cut(cap_dovetail_groove(y, p))
    return cap


def removable_handle(p: StationParameters = DEFAULT) -> cq.Workplane:
    e = p.enclosure
    h = p.handle
    f = p.fasteners
    anchor_y = rigid_handle_anchor_y(p)
    handle = cq.Workplane("XY")
    leg_radius = h.ergonomic_leg_radius
    grip_radius = h.ergonomic_grip_radius
    grip_z = e.height + h.rise + grip_radius
    for x in (-h.anchor_spacing / 2.0, h.anchor_spacing / 2.0):
        # Fully filleted feet retain the accepted four-insert pattern while
        # removing the exposed rectangular edges of the previous handle.
        foot = box_at(
            h.foot_width,
            h.foot_depth,
            h.foot_thickness,
            (x, anchor_y, e.height + h.foot_thickness / 2.0),
        ).edges("|Z").fillet(h.foot_corner_radius).faces(">Z").edges().fillet(h.foot_top_edge_radius)
        # A broad conical root blends each foot into a round load-bearing leg.
        collar = cq.Workplane(
            obj=cq.Solid.makeCone(
                h.ergonomic_root_radius,
                leg_radius,
                16.0,
                cq.Vector(x, anchor_y, e.height + 4.0),
                cq.Vector(0.0, 0.0, 1.0),
            )
        )
        leg = cylinder_axis(
            leg_radius,
            grip_z - (e.height + 14.0),
            (x, anchor_y, e.height + 14.0),
            (0, 0, 1),
        )
        shoulder = cq.Workplane(obj=cq.Solid.makeSphere(grip_radius, cq.Vector(x, anchor_y, grip_z)))
        handle = handle.union(foot).union(collar).union(leg).union(shoulder)

    for x, y in handle_mount_fastener_positions(p):
        insert = cylinder_axis(
            f.m3_insert_hole_diameter / 2.0,
            f.insert_depth + 0.2,
            (x, y, e.height - 0.1),
            (0, 0, 1),
        )
        handle = handle.cut(insert)

    # Cylindrical grip and spherical end blends create a continuous palm
    # surface without hard upper, lower, or end corners.
    # Extend the cylinder 2 mm through each spherical shoulder.  The overlap
    # avoids a coincident end-cap/equator seam which is a valid OCC solid but
    # can tessellate into zero-area triangles in an STL.
    shoulder_overlap = 2.0
    grip = cylinder_axis(
        grip_radius,
        h.anchor_spacing + 2.0 * shoulder_overlap,
        (-h.anchor_spacing / 2.0 - shoulder_overlap, anchor_y, grip_z),
        (1, 0, 0),
    )
    return handle.union(grip)


def leather_strap_mount_positions(
    p: StationParameters = DEFAULT,
) -> tuple[tuple[str, float, float, float], ...]:
    """Left/right side-wall thread axes aligned with the logo-panel centreline."""

    e = p.enclosure
    s = p.leather_strap
    return (
        ("left", -e.width / 2.0, s.mount_y, s.mount_z),
        ("right", e.width / 2.0, s.mount_y, s.mount_z),
    )


def _helical_thread_ridge(
    root_radius: float,
    major_radius: float,
    pitch: float,
    length: float,
    flank_clearance: float = 0.0,
) -> cq.Workplane:
    """Printable coarse helical key ridge on the local +Z axis.

    A twisted closed section tessellates as one watertight body.  The earlier
    swept triangular wire produced a valid OCC solid but fragmented into many
    non-watertight face islands in STL, which made the upper shell unusable.
    """

    root_half_width = 0.26 * pitch + flank_clearance
    crest_half_width = 0.14 * pitch + flank_clearance
    profile = (
        cq.Workplane("XY")
        .polyline(
            (
                (root_radius, -root_half_width),
                (major_radius, -crest_half_width),
                (major_radius, crest_half_width),
                (root_radius, root_half_width),
            )
        )
        .close()
    )
    return profile.twistExtrude(length, 360.0 * length / pitch)


def leather_strap_external_thread(p: StationParameters = DEFAULT) -> cq.Workplane:
    """Local M18x2.5-style male thread with explicit FDM radial clearance."""

    s = p.leather_strap
    major_radius = s.thread_nominal_diameter / 2.0 - s.thread_radial_clearance
    root_radius = major_radius - s.thread_radial_depth
    core = cylinder_axis(root_radius + 0.05, s.thread_engagement, (0.0, 0.0, 0.0), (0, 0, 1))
    ridge = _helical_thread_ridge(root_radius, major_radius, s.thread_pitch, s.thread_engagement)
    clip = cylinder_axis(major_radius + 0.05, s.thread_engagement, (0.0, 0.0, 0.0), (0, 0, 1))
    return core.union(ridge).intersect(clip)


def leather_strap_female_thread_cutter(
    length: float,
    p: StationParameters = DEFAULT,
) -> cq.Workplane:
    """Local matching female-threaded void on +Z; lead-in is cut separately."""

    s = p.leather_strap
    male_major = s.thread_nominal_diameter / 2.0 - s.thread_radial_clearance
    male_root = male_major - s.thread_radial_depth
    female_root = male_root + s.thread_radial_clearance
    female_major = male_major + s.thread_radial_clearance
    bore = cylinder_axis(female_root, length, (0.0, 0.0, 0.0), (0, 0, 1))
    ridge = _helical_thread_ridge(
        female_root,
        female_major,
        s.thread_pitch,
        length,
        flank_clearance=s.thread_radial_clearance,
    )
    # The twisted ridge is already bounded by ``female_major``.  Avoid a
    # redundant cylindrical intersection here: OCC can collapse that boolean
    # to an empty shape for this internal-thread profile at some lengths.
    threaded_void = bore.union(ridge)
    return threaded_void


def _leather_strap_thread_entry_cutter(p: StationParameters = DEFAULT) -> cq.Workplane:
    """Smooth local lead-in, applied as a separate boolean for clean STL."""

    s = p.leather_strap
    male_major = s.thread_nominal_diameter / 2.0 - s.thread_radial_clearance
    male_root = male_major - s.thread_radial_depth
    female_root = male_root + s.thread_radial_clearance
    female_major = s.thread_nominal_diameter / 2.0
    return cq.Workplane(
        obj=cq.Solid.makeCone(
            female_major + 0.8,
            female_root,
            4.5,
            cq.Vector(0.0, 0.0, 0.0),
            cq.Vector(0.0, 0.0, 1.0),
        )
    )


def _leather_strap_screw_local(p: StationParameters = DEFAULT) -> cq.Workplane:
    """Knurled-head strap screw with its under-head plane at local Z=0."""

    s = p.leather_strap
    head = cylinder_axis(
        s.head_diameter / 2.0,
        s.head_thickness,
        (0.0, 0.0, -s.head_thickness),
        (0, 0, 1),
    )
    # Deep axial scallops remain printable with the head face on the bed and
    # provide a robust hand-grip instead of a cosmetic micro-knurl.
    groove = box_at(
        1.6,
        2.2,
        s.head_thickness + 0.4,
        (0.0, s.head_diameter / 2.0, -s.head_thickness / 2.0),
    )
    for index in range(s.knurl_count):
        head = head.cut(groove.rotate((0, 0, 0), (0, 0, 1), 360.0 * index / s.knurl_count))
    return head.union(leather_strap_external_thread(p))


def leather_strap_screw_printable(p: StationParameters = DEFAULT) -> cq.Workplane:
    """One local strap screw; print two identical copies."""

    return _leather_strap_screw_local(p)


def leather_strap_screw(side: str, p: StationParameters = DEFAULT) -> cq.Workplane:
    """One installed strap screw; left and right share the same right-hand thread."""

    if side not in {"left", "right"}:
        raise ValueError("side must be 'left' or 'right'")
    e = p.enclosure
    s = p.leather_strap
    screw = _leather_strap_screw_local(p)
    if side == "left":
        screw = screw.rotate((0, 0, 0), (0, 1, 0), 90.0)
        x = -e.width / 2.0 - s.thickness
    else:
        screw = screw.rotate((0, 0, 0), (0, 1, 0), -90.0)
        x = e.width / 2.0 + s.thickness
    return screw.translate((x, s.mount_y, s.mount_z))


def leather_strap_shell_boss_and_cutter(
    side: str,
    p: StationParameters = DEFAULT,
) -> tuple[cq.Workplane, cq.Workplane]:
    """Return a pre-threaded load boss/reinforcement and wall-entry void."""

    if side not in {"left", "right"}:
        raise ValueError("side must be 'left' or 'right'")
    e = p.enclosure
    s = p.leather_strap
    sign = -1.0 if side == "left" else 1.0
    inward = -sign
    surface_x = sign * e.width / 2.0
    local_boss = cylinder_axis(
        s.boss_diameter / 2.0,
        s.boss_depth,
        (0.0, 0.0, 0.0),
        (0, 0, 1),
    )
    local_boss = local_boss.cut(
        leather_strap_female_thread_cutter(s.thread_engagement + 4.0, p).translate((0.0, 0.0, -1.0))
    ).cut(_leather_strap_thread_entry_cutter(p).translate((0.0, 0.0, -1.0)))
    if side == "left":
        boss = local_boss.rotate((0, 0, 0), (0, 1, 0), 90.0).translate((surface_x, s.mount_y, s.mount_z))
    else:
        boss = local_boss.rotate((0, 0, 0), (0, 1, 0), -90.0).translate((surface_x, s.mount_y, s.mount_z))
    load_plate = box_at(
        s.reinforcement_depth,
        s.reinforcement_width_y,
        s.reinforcement_height,
        (
            sign * (e.width / 2.0 - s.reinforcement_depth / 2.0),
            s.mount_y,
            s.mount_z + 4.0,
        ),
    )
    female_major = s.thread_nominal_diameter / 2.0
    plate_clearance = cylinder_axis(
        female_major + 0.8,
        s.boss_depth,
        (surface_x, s.mount_y, s.mount_z),
        (inward, 0, 0),
    )
    load_plate = load_plate.cut(plate_clearance)
    wall_entry_start = surface_x - inward * 1.0
    wall_entry = cylinder_axis(
        female_major + 0.8,
        p.enclosure.wall + 2.0,
        (wall_entry_start, s.mount_y, s.mount_z),
        (inward, 0, 0),
    )
    # Clean this union before it is attached to the shell.  Leaving coincident
    # boss/plate faces in the BRep can still report as one valid OCC solid but
    # tessellate into floating, non-watertight STL face islands.
    return boss.union(load_plate), wall_entry


def leather_strap_thread_coupon(p: StationParameters = DEFAULT) -> cq.Workplane:
    """Small production-orientation female boss and matching knurled screw trial."""

    s = p.leather_strap
    receiver = cylinder_axis(s.boss_diameter / 2.0, s.boss_depth, (-22.0, 0.0, 0.0), (0, 0, 1))
    receiver = receiver.cut(
        leather_strap_female_thread_cutter(s.thread_engagement + 4.0, p).translate((-22.0, 0.0, -1.0))
    ).cut(_leather_strap_thread_entry_cutter(p).translate((-22.0, 0.0, -1.0)))
    screw = _leather_strap_screw_local(p).translate((24.0, 0.0, s.head_thickness))
    return cq.Workplane(obj=cq.Compound.makeCompound(receiver.solids().vals() + screw.solids().vals()))


def handle_mount_coupon(p: StationParameters = DEFAULT) -> cq.Workplane:
    """One-foot underside-screw coupon with production grip and pilot depths."""

    h = p.handle
    f = p.fasteners
    cap_sample = box_at(h.foot_width + 8.0, h.foot_depth + 4.0, 12.0, (0.0, 0.0, 6.0))
    foot_sample = box_at(h.foot_width, h.foot_depth, h.foot_thickness, (54.0, 0.0, 12.0 + h.foot_thickness / 2.0))
    for x in (-h.fastener_offset_x, h.fastener_offset_x):
        insert = cylinder_axis(
            f.m3_insert_hole_diameter / 2.0,
            f.insert_depth + 0.2,
            (54.0 + x, 0.0, 11.9),
            (0, 0, 1),
        )
        clearance = cylinder_axis(
            f.m3_clearance_diameter / 2.0,
            13.0,
            (x, 0.0, -0.5),
            (0, 0, 1),
        )
        cap_sample = cap_sample.cut(clearance)
        foot_sample = foot_sample.cut(insert)
    return cap_sample.union(foot_sample)
