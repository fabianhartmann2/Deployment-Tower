"""Small reusable geometry helpers."""

from __future__ import annotations

import cadquery as cq


def box_at(width: float, depth: float, height: float, center: tuple[float, float, float]) -> cq.Workplane:
    return cq.Workplane("XY").box(width, depth, height).translate(center)


def rounded_rect_prism(
    width: float,
    depth: float,
    height: float,
    radius: float,
    z0: float = 0.0,
) -> cq.Workplane:
    """Create a robust rounded-square prism without sketch fillet edge cases."""

    if min(width, depth) <= 2.0 * radius:
        raise ValueError("corner radius is too large")
    a = cq.Workplane("XY").box(width - 2.0 * radius, depth, height, centered=(True, True, False))
    b = cq.Workplane("XY").box(width, depth - 2.0 * radius, height, centered=(True, True, False))
    result = a.union(b)
    for x in (-width / 2.0 + radius, width / 2.0 - radius):
        for y in (-depth / 2.0 + radius, depth / 2.0 - radius):
            result = result.union(cq.Workplane("XY").center(x, y).circle(radius).extrude(height))
    return result.translate((0, 0, z0))


def rounded_rect_ring(
    width: float,
    depth: float,
    height: float,
    radius: float,
    wall: float,
    z0: float = 0.0,
) -> cq.Workplane:
    outer = rounded_rect_prism(width, depth, height, radius, z0)
    inner = rounded_rect_prism(
        width - 2.0 * wall,
        depth - 2.0 * wall,
        height + 2.0,
        max(0.5, radius - wall),
        z0 - 1.0,
    )
    return outer.cut(inner)


def cylinder_axis(
    radius: float,
    length: float,
    start: tuple[float, float, float],
    direction: tuple[float, float, float],
) -> cq.Workplane:
    solid = cq.Solid.makeCylinder(radius, length, cq.Vector(*start), cq.Vector(*direction))
    return cq.Workplane(obj=solid)


def rounded_panel_xz(
    width: float,
    height: float,
    thickness: float,
    radius: float,
    y0: float,
    center_x: float = 0.0,
    center_z: float = 0.0,
    direction: int = 1,
) -> cq.Workplane:
    """Rounded rectangle in X/Z, extruded along Y."""

    if direction not in (-1, 1):
        raise ValueError("direction must be -1 or +1")
    y_center = y0 + direction * thickness / 2.0
    a = box_at(width - 2.0 * radius, thickness, height, (center_x, y_center, center_z))
    b = box_at(width, thickness, height - 2.0 * radius, (center_x, y_center, center_z))
    result = a.union(b)
    for x in (center_x - width / 2.0 + radius, center_x + width / 2.0 - radius):
        for z in (center_z - height / 2.0 + radius, center_z + height / 2.0 - radius):
            start_y = y0 if direction > 0 else y0
            result = result.union(cylinder_axis(radius, thickness, (x, start_y, z), (0, direction, 0)))
    return result


def rounded_panel_yz(
    width: float,
    height: float,
    thickness: float,
    radius: float,
    x0: float,
    center_y: float = 0.0,
    center_z: float = 0.0,
    direction: int = 1,
) -> cq.Workplane:
    """Rounded rectangle in Y/Z, extruded along X."""

    if direction not in (-1, 1):
        raise ValueError("direction must be -1 or +1")
    x_center = x0 + direction * thickness / 2.0
    a = box_at(thickness, width - 2.0 * radius, height, (x_center, center_y, center_z))
    b = box_at(thickness, width, height - 2.0 * radius, (x_center, center_y, center_z))
    result = a.union(b)
    for y in (center_y - width / 2.0 + radius, center_y + width / 2.0 - radius):
        for z in (center_z - height / 2.0 + radius, center_z + height / 2.0 - radius):
            result = result.union(cylinder_axis(radius, thickness, (x0, y, z), (direction, 0, 0)))
    return result


def compound(parts: list[cq.Workplane]) -> cq.Workplane:
    shapes = []
    for part in parts:
        shapes.extend(part.vals())
    return cq.Workplane(obj=cq.Compound.makeCompound(shapes))


def bbox_dimensions(obj: cq.Workplane | cq.Shape) -> tuple[float, float, float]:
    shape = obj.val() if isinstance(obj, cq.Workplane) else obj
    bb = shape.BoundingBox()
    return bb.xlen, bb.ylen, bb.zlen


def placed_on_bed(obj: cq.Workplane) -> cq.Workplane:
    """Centre an object in X/Y and put its minimum Z on the build plate."""

    bb = obj.val().BoundingBox()
    return obj.translate((-(bb.xmin + bb.xmax) / 2.0, -(bb.ymin + bb.ymax) / 2.0, -bb.zmin))


def placed_solids_on_bed(obj: cq.Workplane) -> cq.Workplane:
    """Preserve XY layout while putting every disconnected solid on Z=0.

    Fit coupons often contain a separate gauge/key next to a receiver.  Moving a
    compound by only its global minimum Z can leave that second body suspended
    in the STL even though each mesh is individually watertight.
    """

    bb = obj.val().BoundingBox()
    dx = -(bb.xmin + bb.xmax) / 2.0
    dy = -(bb.ymin + bb.ymax) / 2.0
    solids = obj.solids().vals()
    if not solids:
        raise ValueError("cannot place an object with no solids on the bed")
    grounded = [solid.translate(cq.Vector(dx, dy, -solid.BoundingBox().zmin)) for solid in solids]
    return cq.Workplane(obj=cq.Compound.makeCompound(grounded))
