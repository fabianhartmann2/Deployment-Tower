"""Reference and clearance solids; none of these are printable parts.

The RUTM30 body is the supplier's native STEP model.  Cable overmoulds, panel
extensions, the photo-derived Mac underside, and Wi-Fi antenna geometry remain
controlled reference envelopes until checked against the physical hardware.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

import cadquery as cq

from .geometry import box_at, compound, cylinder_axis, rounded_panel_xz, rounded_rect_prism
from .layout import packaging_layout
from .parameters import DEFAULT, StationParameters


@dataclass(frozen=True)
class ReferenceModel:
    equipment: dict[str, cq.Workplane]
    clearances: dict[str, cq.Workplane]
    interfaces: dict[str, cq.Workplane]
    hardware: dict[str, cq.Workplane]


def mac_reference(p: StationParameters = DEFAULT) -> cq.Workplane:
    c = p.components
    layout = packaging_layout(p)
    z0 = layout.mac_center[2] - c.mac_height / 2.0
    return rounded_rect_prism(c.mac_width, c.mac_depth, c.mac_height, c.mac_corner_radius, z0).translate(
        (layout.mac_center[0], layout.mac_center[1], 0.0)
    )


def mac_intake_exclusion(p: StationParameters = DEFAULT) -> cq.Workplane:
    c = p.components
    z0 = c.mac_support_plane_z - 2.0
    outer = cq.Workplane("XY").circle(c.mac_intake_outer_diameter / 2.0).extrude(4.0).translate((0, 0, z0))
    inner = cq.Workplane("XY").circle(c.mac_intake_inner_diameter / 2.0).extrude(6.0).translate((0, 0, z0 - 1.0))
    return outer.cut(inner).translate((0.0, c.mac_center_y, 0.0))


def mac_button_reference(p: StationParameters = DEFAULT) -> cq.Workplane:
    c = p.components
    x = c.mac_width / 2.0 - c.mac_button_edge_offset_x
    y = c.mac_center_y + c.mac_depth / 2.0 - c.mac_button_edge_offset_y
    return cq.Workplane("XY").center(x, y).circle(c.mac_button_diameter / 2.0).extrude(1.5).translate(
        (0, 0, c.mac_support_plane_z - 1.5)
    )


def router_reference(p: StationParameters = DEFAULT) -> cq.Workplane:
    c = p.components
    layout = packaging_layout(p)
    step_path = Path(__file__).resolve().parents[2] / "reference" / "0112_RUTM30AMBKX_02.STEP"
    if not step_path.exists():
        return box_at(c.router_width, c.router_depth, c.router_height, layout.router_center)
    model = _official_router_model(str(step_path))
    bb = model.val().BoundingBox()
    centre = ((bb.xmin + bb.xmax) / 2.0, (bb.ymin + bb.ymax) / 2.0, (bb.zmin + bb.zmax) / 2.0)
    target = layout.router_center
    return model.translate((target[0] - centre[0], target[1] - centre[1], target[2] - centre[2]))


@lru_cache(maxsize=1)
def _official_router_model(step_path: str) -> cq.Workplane:
    """Import and orient Teltonika's AP214 STEP into station X/Y/Z axes."""

    raw = cq.importers.importStep(step_path)
    # Supplier: X=width, Y=height, Z=depth. Station: X=width, Y=depth,
    # Z=height. +90 degrees around X performs that axis mapping.
    return raw.rotate((0, 0, 0), (1, 0, 0), 90.0)


def router_source_kind() -> str:
    step_path = Path(__file__).resolve().parents[2] / "reference" / "0112_RUTM30AMBKX_02.STEP"
    return "official_teltonika_step" if step_path.exists() else "documented_placeholder"


def router_connector_clearances(p: StationParameters = DEFAULT) -> dict[str, cq.Workplane]:
    c = p.components
    layout = packaging_layout(p)
    x0, y0, z0 = layout.router_center
    rear_y = y0 + c.router_depth / 2.0
    result: dict[str, cq.Workplane] = {}

    # Official rear-panel sequence: Mobile, Wi-Fi, Mobile, Mobile, Wi-Fi, Mobile.
    # The spatial drawing gives 14.8 mm pitch and z=12 mm above the housing base.
    xs = [(i - 2.5) * c.router_sma_pitch + x0 for i in range(6)]
    kinds = ("cellular_1", "wifi_1", "cellular_2", "cellular_3", "wifi_2", "cellular_4")
    for index, x in enumerate(xs):
        name = kinds[index]
        result[name] = cylinder_axis(
            c.router_sma_clearance_diameter / 2.0,
            c.router_connector_depth,
            (x, rear_y, z0 - c.router_height / 2.0 + 12.0),
            (0, 1, 0),
        )

    front_y = y0 - c.router_depth / 2.0
    # Official front centres are x=66.6/83.5 from the left edge, z=18.2.
    for index, x_rel in enumerate((66.6, 83.5), start=1):
        x = x0 - c.router_width / 2.0 + x_rel
        result[f"router_rj45_{index}"] = box_at(
            c.router_rj45_clearance_width,
            c.router_rj45_plug_depth,
            c.router_rj45_clearance_height,
            (x, front_y - c.router_rj45_plug_depth / 2.0, z0 - c.router_height / 2.0 + 18.2),
        )
    return result


def psu_reference(p: StationParameters = DEFAULT) -> cq.Workplane:
    c = p.components
    layout = packaging_layout(p)
    x, y, z = layout.psu_center
    case = box_at(c.psu_case_width, c.psu_case_length, c.psu_case_height, (x, y, z))
    # Thin mounting-lug envelope from APV-35 mechanical drawing; hole pattern is
    # represented on the PSU cradle rather than subtracted from the equipment.
    lugs = box_at(c.psu_case_width * 0.35, c.psu_mount_length, 1.9, (x, y, z - c.psu_case_height / 2.0 + 0.95))
    return case.union(lugs)


def psu_lead_clearances(p: StationParameters = DEFAULT) -> dict[str, cq.Workplane]:
    c = p.components
    layout = packaging_layout(p)
    x, y, z = layout.psu_center
    rear_y = y + c.psu_case_length / 2.0
    front_y = y - c.psu_case_length / 2.0
    # The attached wires are 150 +/-10 mm.  The solids show only the initial
    # straight run and conservative bend-volume destinations inside the box.
    lead_clearance_radius = c.psu_lead_diameter / 2.0 + p.fits.equipment_clearance
    ac = cylinder_axis(lead_clearance_radius, 30.0, (x, rear_y, z), (0, 1, 0))
    dc = cylinder_axis(lead_clearance_radius, 28.0, (x, front_y, z), (0, -1, 0))
    ac_bend = box_at(20.0, 24.0, 18.0, (x, rear_y + 20.0, z))
    dc_bend = box_at(20.0, 24.0, 18.0, (x, front_y - 18.0, z))
    return {"psu_ac_lead": ac.union(ac_bend), "psu_dc_lead": dc.union(dc_bend)}


def wifi_antenna_reference(side: str, p: StationParameters = DEFAULT) -> cq.Workplane:
    """Photo-derived vertical transport envelope for one connected antenna."""

    if side not in {"left", "right"}:
        raise ValueError("side must be 'left' or 'right'")
    e = p.enclosure
    w = p.wifi
    sign = 1.0 if side == "right" else -1.0
    x = sign * e.width / 2.0
    y = w.dock_center_y
    z0 = w.dock_center_z - w.antenna_length / 2.0
    hub_h = w.antenna_hub_depth
    shoulder_h = 14.0
    stem_h = w.antenna_length - hub_h - shoulder_h
    hub = cylinder_axis(w.antenna_base_diameter / 2.0, hub_h, (x, y, z0), (0, 0, 1))
    shoulder = cq.Workplane(
        obj=cq.Solid.makeCone(
            w.antenna_base_diameter / 2.0,
            w.antenna_proximal_diameter / 2.0,
            shoulder_h,
            cq.Vector(x, y, z0 + hub_h),
            cq.Vector(0, 0, 1),
        )
    )
    stem = cq.Workplane(
        obj=cq.Solid.makeCone(
            w.antenna_stem_diameter / 2.0,
            w.antenna_tip_diameter / 2.0,
            stem_h,
            cq.Vector(x, y, z0 + hub_h + shoulder_h),
            cq.Vector(0, 0, 1),
        )
    )
    radial_lead = cylinder_axis(2.0, 18.0, (x, y + 2.0, z0 + 4.0), (0, 1, 0))
    return hub.union(shoulder).union(stem).union(radial_lead)


def mac_connector_clearances(p: StationParameters = DEFAULT) -> dict[str, cq.Workplane]:
    c = p.components
    layout = packaging_layout(p)
    _, y0, z0 = layout.mac_center
    rear = y0 + c.mac_depth / 2.0
    depth = c.mac_rear_plug_depth
    h = c.mac_connector_clearance_height
    return {
        "mac_internal_ethernet": box_at(20.0, depth, h, (-39.0, rear + depth / 2.0, z0)),
        "mac_internal_ac": box_at(18.0, depth, h, (39.0, rear + depth / 2.0, z0)),
        "mac_hdmi_extension": box_at(20.0, depth, h, (-14.0, rear + depth / 2.0, z0)),
        "mac_usbc_extension": box_at(14.0, depth, h, (10.0, rear + depth / 2.0, z0)),
    }


def mac_ac_branch_corridor(p: StationParameters = DEFAULT) -> cq.Workplane:
    """Continuous reserved envelope from the power-box gland to Mac AC.

    The route passes above the Mac only long enough to reach the left-side lane,
    descends outside the Mac plan, then approaches the provisional connector in
    the rear service volume.  It is packaging evidence, not a printable conduit
    or a claim that branch hardware, insulation, restraint, or separation has
    been selected.
    """

    e = p.enclosure
    c = p.components
    pw = p.power
    layout = packaging_layout(p)
    width = pw.mac_ac_corridor_width
    exit_x = pw.center_x + pw.mac_ac_exit_offset_x
    exit_y = pw.center_y + pw.mac_ac_exit_offset_y
    overhead_z = pw.bottom_z - width / 2.0
    side_x = -e.width / 2.0 + e.wall + width + 1.0
    target_x = 39.0
    target_y = c.mac_center_y + c.mac_depth / 2.0 + 10.0
    target_z = layout.mac_center[2]
    # Run just above the linked Mac-retainer release rail and the shell's rear
    # cradle boss; the half-width clearance is explicit in this datum.
    side_run_z = target_z + width / 4.0
    points = (
        (exit_x, exit_y, overhead_z),
        (side_x, exit_y, overhead_z),
        (side_x, exit_y, side_run_z),
        (side_x, target_y, side_run_z),
        (side_x, target_y, target_z),
        (target_x, target_y, target_z),
    )

    def run(start: tuple[float, float, float], end: tuple[float, float, float]) -> cq.Workplane:
        lengths = tuple(abs(end[index] - start[index]) + width for index in range(3))
        centre = tuple((start[index] + end[index]) / 2.0 for index in range(3))
        return box_at(lengths[0], lengths[1], lengths[2], centre)

    corridor = run(points[0], points[1])
    for start, end in zip(points[1:-1], points[2:]):
        corridor = corridor.union(run(start, end))
    return corridor


def service_removal_envelopes(p: StationParameters = DEFAULT) -> dict[str, cq.Workplane]:
    c = p.components
    layout = packaging_layout(p)
    e = p.enclosure
    mac_down = box_at(c.mac_width + 2.0, c.mac_depth + 2.0, c.mac_height + 80.0, (0, 0, -16.0))
    router_rear = box_at(
        c.router_width + 6.0,
        e.depth,
        c.router_height + 8.0,
        (layout.router_center[0], e.depth / 2.0, layout.router_center[2]),
    )
    panel_rear = box_at(e.rear_panel_width + 4.0, 80.0, e.rear_panel_height + 4.0, (0, e.depth / 2.0 + 40.0, 135.0))
    return {"mac_downward_removal": mac_down, "router_rear_removal": router_rear, "rear_panel_removal": panel_rear}


def build_reference_model(p: StationParameters = DEFAULT) -> ReferenceModel:
    equipment = {
        "mac_mini_m4": mac_reference(p),
        "rutm30": router_reference(p),
        "apv_35_36": psu_reference(p),
    }
    clearances = {
        "mac_intake_exclusion": mac_intake_exclusion(p),
        "mac_button": mac_button_reference(p),
        **mac_connector_clearances(p),
        **router_connector_clearances(p),
        **psu_lead_clearances(p),
        **service_removal_envelopes(p),
    }
    interfaces = {
        "low_voltage_lane": box_at(34.0, 122.0, 76.0, (packaging_layout(p).low_voltage_lane_center_x, 0.0, 116.0)),
        "mains_keepout": box_at(
            p.power.outer_width + 2.0 * p.power.mains_keepout_extra,
            p.power.outer_depth + 2.0 * p.power.mains_keepout_extra,
            p.power.outer_height + 2.0 * p.power.mains_keepout_extra,
            packaging_layout(p).mains_center,
        ),
        "mac_ac_branch_corridor": mac_ac_branch_corridor(p),
    }
    e = p.enclosure
    i = p.interfaces
    y0 = e.depth / 2.0
    hardware = {
        "c8_inlet": rounded_panel_xz(i.c8_flange_width, i.c8_flange_height, 4.0, 2.0, y0, i.c8_position_x, i.c8_position_z, 1),
        "mac_hdmi_panel_extension": rounded_panel_xz(24.0, 26.0, 4.0, 2.5, y0, i.hdmi_position_x, i.hdmi_position_z, 1),
        "mac_usbc_panel_extension": rounded_panel_xz(21.0, 26.0, 4.0, 2.5, y0, i.usbc_position_x, i.usbc_position_z, 1),
        "router_lan_panel_extension": rounded_panel_xz(34.0, 22.0, 4.0, 2.0, y0, i.router_interface_center_x - 17.0, i.router_interface_center_z + 18.0, 1),
        "router_wan_panel_extension": rounded_panel_xz(34.0, 22.0, 4.0, 2.0, y0, i.router_interface_center_x + 17.0, i.router_interface_center_z + 18.0, 1),
        "wifi_antenna_left": wifi_antenna_reference("left", p),
        "wifi_antenna_right": wifi_antenna_reference("right", p),
    }
    return ReferenceModel(equipment=equipment, clearances=clearances, interfaces=interfaces, hardware=hardware)


def component_envelope_compound(p: StationParameters = DEFAULT) -> cq.Workplane:
    model = build_reference_model(p)
    return compound(
        list(model.equipment.values())
        + list(model.clearances.values())
        + list(model.interfaces.values())
        + list(model.hardware.values())
    )
