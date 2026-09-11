"""Packaging positions and analytically documented clearance corridors."""

from __future__ import annotations

from dataclasses import dataclass

from .parameters import DEFAULT, StationParameters


@dataclass(frozen=True)
class PackagingLayout:
    mac_center: tuple[float, float, float]
    psu_center: tuple[float, float, float]
    router_center: tuple[float, float, float]
    router_tray_z: float
    mains_center: tuple[float, float, float]
    low_voltage_lane_center_x: float
    handle_anchor_z: float


def packaging_layout(p: StationParameters = DEFAULT) -> PackagingLayout:
    c = p.components
    pw = p.power
    mac_z = c.mac_support_plane_z + c.mac_retained_body_height - c.mac_height / 2.0
    psu_z = pw.bottom_z + pw.bottom + 3.0 + c.psu_case_height / 2.0
    router_z = c.router_tray_z + 3.0 + p.fits.equipment_clearance + c.router_height / 2.0
    return PackagingLayout(
        mac_center=(0.0, c.mac_center_y, mac_z),
        psu_center=(pw.center_x, pw.center_y, psu_z),
        router_center=(c.router_center_x, c.router_center_y, router_z),
        router_tray_z=c.router_tray_z,
        mains_center=(pw.center_x, pw.center_y, pw.bottom_z + pw.outer_height / 2.0),
        low_voltage_lane_center_x=48.0,
        handle_anchor_z=p.enclosure.shell_top - 8.0,
    )
