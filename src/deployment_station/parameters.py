"""Single source of truth for design dimensions, in millimetres.

Coordinate system
-----------------
Origin: centre of the external footprint at the desk-contact datum.
+X: right when looking at the front.
+Y: rear/service face.
+Z: upward.
The enclosure datum planes are X=0, Y=0 and Z=0.  Equipment positions in
``layout.py`` refer to the centre of each documented envelope.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class EnclosureParameters:
    width: float = 165.0
    depth: float = 165.0
    height: float = 280.0
    target_height_ratio: float = 1.70
    wall: float = 3.2
    minimum_wall: float = 2.4
    outer_corner_radius: float = 24.0
    inner_corner_radius: float = 20.8
    base_height: float = 14.0
    foot_height: float = 5.0
    cap_height: float = 12.0
    lower_shell_top: float = 105.0
    shell_top: float = 268.0
    shadow_gap: float = 0.8
    seam_fastener_y: tuple[float, ...] = (-50.0, 10.0, 50.0)
    seam_axis_x: float = 76.8
    seam_boss_diameter: float = 10.4
    seam_lug_height: float = 11.0
    seam_head_clearance_diameter: float = 7.6
    seam_head_clearance_height: float = 3.2
    seam_driver_clearance_diameter: float = 5.5
    rear_opening_width: float = 120.0
    rear_opening_bottom: float = 18.0
    rear_opening_top: float = 252.0
    rear_panel_width: float = 132.0
    rear_panel_height: float = 236.0
    rear_panel_thickness: float = 3.2
    rear_panel_corner_radius: float = 8.0
    underside_intake_opening_diameter: float = 116.0
    desk_air_gap: float = 5.0

    @property
    def lower_shell_height(self) -> float:
        return self.lower_shell_top - self.base_height

    @property
    def upper_shell_height(self) -> float:
        return self.shell_top - self.lower_shell_top

    @property
    def actual_height_ratio(self) -> float:
        return self.height / self.width


@dataclass(frozen=True)
class FitParameters:
    equipment_clearance: float = 1.5
    sliding_fit_per_side: float = 0.30
    service_panel_per_side: float = 0.35
    rear_panel_x_per_side: float = 0.15
    rear_panel_z_per_side: float = 0.05
    logo_panel_per_side: float = 0.25
    snap_feature_per_side: float = 0.20
    # Three-marker physical coupon selected: 31.0 mm cavity for the measured
    # 30.0 mm antenna hub, hence 0.50 mm radial allowance.
    wifi_clip_radial: float = 0.50
    insert_pilot_allowance: float = -0.15


@dataclass(frozen=True)
class ComponentParameters:
    mac_width: float = 127.0
    mac_depth: float = 127.0
    mac_height: float = 50.0
    mac_corner_radius: float = 12.0
    mac_mass_kg: float = 0.67
    mac_support_plane_z: float = 24.0
    # Physical cradle trial: the central underside section hangs below the
    # retained 127 mm square body, placing the body top 8 mm below the earlier
    # full-height rectangular placeholder while preserving 50 mm overall.
    mac_underside_drop: float = 8.0
    mac_center_y: float = -8.0
    mac_button_x_side: float = -1.0
    mac_button_edge_offset_x: float = 13.5
    mac_button_edge_offset_y: float = 13.5
    mac_button_diameter: float = 11.0
    mac_button_free_clearance: float = 0.75
    mac_intake_inner_diameter: float = 100.0
    mac_intake_outer_diameter: float = 112.0
    mac_rear_plug_depth: float = 34.0
    mac_connector_clearance_height: float = 24.0
    router_width: float = 100.0
    router_depth: float = 93.7
    router_height: float = 30.0
    router_mass_kg: float = 0.319
    router_center_x: float = 0.0
    router_center_y: float = 28.0
    router_tray_z: float = 151.0
    router_connector_depth: float = 36.0
    router_sma_pitch: float = 14.8
    router_sma_clearance_diameter: float = 14.0
    router_rj45_clearance_width: float = 18.0
    router_rj45_clearance_height: float = 16.0
    router_rj45_plug_depth: float = 40.0
    router_pad_width: float = 8.0
    router_pad_depth: float = 16.0
    router_pad_thickness: float = 1.3
    router_pad_nominal_compression: float = 0.4
    psu_case_length: float = 84.0
    psu_case_width: float = 57.0
    psu_case_height: float = 29.5
    psu_mount_length: float = 98.6
    psu_lead_length: float = 150.0
    psu_lead_tolerance: float = 10.0
    psu_lead_diameter: float = 3.5
    psu_mount_hole_diameter: float = 3.6
    cable_min_bend_radius: float = 18.0
    coax_min_bend_radius_provisional: float = 20.0

    @property
    def mac_retained_body_height(self) -> float:
        return self.mac_height - self.mac_underside_drop


@dataclass(frozen=True)
class MacRetentionParameters:
    """Provisional printed retainers; pad compression awaits hardware testing."""

    base_pad_seat_depth: float = 1.0
    base_pad_thickness: float = 2.0
    side_clearance: float = 0.30
    y_offsets: tuple[float, float] = (-17.0, 17.0)
    stem_thickness: float = 3.0
    clip_depth: float = 10.0
    top_gap: float = 1.2
    overhang: float = 3.0
    tab_thickness: float = 3.0
    lead_in_height: float = 1.5
    pad_seat_width: float = 2.0
    pad_seat_length: float = 6.0
    pad_seat_recess: float = 0.8
    # Narrowing the Mac fit moves the clip stems inward; the release rails keep
    # enough outward reach to remain accessible beyond the cradle plate.
    release_rail_outreach: float = 7.5
    release_rail_root_overlap: float = 0.6
    release_rail_height: float = 9.0
    release_rail_bottom_offset: float = 14.0


@dataclass(frozen=True)
class InterfaceParameters:
    c8_flange_width: float = 35.0
    c8_flange_height: float = 18.0
    c8_cutout_width: float = 20.6
    c8_cutout_height: float = 11.8
    c8_cutout_corner_radius: float = 3.5
    c8_hole_pitch: float = 28.0
    c8_hole_diameter: float = 3.2
    c8_panel_fit_allowance: float = 0.20
    c8_position_x: float = -38.0
    c8_position_z: float = 108.0
    hdmi_cutout_width: float = 16.0
    hdmi_cutout_height: float = 7.0
    hdmi_position_x: float = -20.0
    hdmi_position_z: float = 57.0
    usbc_cutout_width: float = 11.0
    usbc_cutout_height: float = 5.5
    usbc_position_x: float = 16.0
    usbc_position_z: float = 57.0
    mac_extension_mount_vertical_pitch: float = 20.0
    router_interface_center_x: float = 0.0
    router_interface_center_z: float = 178.0
    router_bezel_center_x: float = 0.0
    router_bezel_width: float = 118.0
    router_bezel_height: float = 78.0
    router_bezel_thickness: float = 4.8
    router_bezel_aperture_width: float = 112.0
    router_bezel_aperture_height: float = 72.0
    router_rf_window_height: float = 30.0
    router_extension_mount_horizontal_pitch: float = 27.0
    rear_panel_screw_x: float = 63.0
    rear_panel_screw_z: tuple[float, ...] = (31.0, 92.0, 218.0, 244.0)
    finger_well_width: float = 26.0
    finger_well_reach: float = 38.0
    finger_well_corner_radius: float = 7.0


@dataclass(frozen=True)
class PowerCompartmentParameters:
    outer_width: float = 72.0
    outer_depth: float = 120.0
    outer_height: float = 44.0
    wall: float = 2.4
    bottom: float = 2.8
    cover_thickness: float = 2.8
    center_x: float = -35.0
    center_y: float = 8.0
    bottom_z: float = 83.0
    grommet_hole_diameter: float = 9.0
    mac_ac_gland_diameter: float = 12.0
    mac_ac_exit_offset_x: float = -20.0
    mac_ac_exit_offset_y: float = -41.5
    tie_bridge_width: float = 14.0
    tie_bridge_depth: float = 7.0
    tie_bridge_height: float = 5.0
    tie_bridge_tunnel_width: float = 8.0
    tie_bridge_tunnel_height: float = 3.0
    apv_mount_boss_diameter: float = 10.0
    apv_insert_pocket_diameter: float = 4.2
    apv_insert_pocket_depth: float = 3.0
    apv_support_clearance: float = 0.10
    cover_screw_length: float = 8.0
    cover_min_thread_engagement: float = 4.5
    mac_ac_corridor_width: float = 6.0
    terminal_tunnel_inner_overlap: float = 1.0
    mains_keepout_extra: float = 4.0


@dataclass(frozen=True)
class HandleParameters:
    grip_span: float = 128.0
    grip_depth: float = 20.0
    grip_height: float = 18.0
    rise: float = 58.0
    leg_width: float = 18.0
    leg_depth: float = 26.0
    anchor_spacing: float = 108.0
    foot_width: float = 42.0
    foot_depth: float = 32.0
    foot_thickness: float = 5.0
    fastener_offset_x: float = 14.0
    reinforcement_rib_thickness: float = 5.0
    design_static_factor: float = 4.0
    provisional_complete_mass_kg: float = 1.8


@dataclass(frozen=True)
class WifiDockParameters:
    antenna_length: float = 91.0
    antenna_base_diameter: float = 30.0
    antenna_stem_diameter: float = 12.0
    antenna_hub_depth: float = 18.0
    antenna_proximal_diameter: float = 15.0
    antenna_tip_diameter: float = 5.0
    cable_exit_width: float = 8.0
    backplate_width: float = 36.0
    backplate_height: float = 98.0
    backplate_thickness: float = 3.0
    clip_width: float = 10.0
    clip_wall: float = 2.4
    clip_lip_radius: float = 1.0
    clip_lip_intrusion: float = 0.75
    dock_center_y: float = 53.0
    dock_center_z: float = 216.0


@dataclass(frozen=True)
class LogoParameters:
    size: float = 70.0
    thickness: float = 2.4
    pocket_depth: float = 1.6
    reveal: float = 0.8
    corner_radius: float = 6.0
    retention_rail_width: float = 5.0
    retention_rail_depth: float = 2.6
    retention_rail_length: float = 54.0
    detent_diameter: float = 2.8
    emboss_height: float = 0.8
    center_z: float = 156.0
    finger_notch_diameter: float = 8.0
    fastener_offset_y: float = 25.0


@dataclass(frozen=True)
class FastenerParameters:
    service_screw: str = "M3x8"
    base_screw: str = "M3x14"
    cradle_screw: str = "M3x10"
    router_tray_screw: str = "M3x6"
    logo_screw: str = "M3x8"
    handle_screw: str = "M3x10"
    structural_screw: str = "M4x18"
    service_screw_length: float = 8.0
    base_screw_length: float = 14.0
    cradle_screw_length: float = 10.0
    router_tray_screw_length: float = 6.0
    logo_screw_length: float = 8.0
    handle_screw_length: float = 10.0
    structural_screw_length: float = 18.0
    minimum_thread_engagement: float = 4.5
    m3_clearance_diameter: float = 3.4
    m4_clearance_diameter: float = 4.5
    m3_insert_hole_diameter: float = 4.2
    m4_insert_hole_diameter: float = 5.6
    m3_boss_diameter: float = 9.0
    m4_boss_diameter: float = 12.0
    insert_depth: float = 5.5
    m3_low_head_recess_diameter: float = 6.2
    m3_low_head_recess_depth: float = 1.8


@dataclass(frozen=True)
class PrintParameters:
    build_x: float = 256.0
    build_y: float = 256.0
    build_z: float = 256.0
    nozzle: float = 0.4
    nominal_line_width: float = 0.45
    layer_height: float = 0.20
    body_wall_lines: int = 7
    prototype_material: str = "ASA"


@dataclass(frozen=True)
class StationParameters:
    enclosure: EnclosureParameters = field(default_factory=EnclosureParameters)
    fits: FitParameters = field(default_factory=FitParameters)
    components: ComponentParameters = field(default_factory=ComponentParameters)
    mac_retention: MacRetentionParameters = field(default_factory=MacRetentionParameters)
    interfaces: InterfaceParameters = field(default_factory=InterfaceParameters)
    power: PowerCompartmentParameters = field(default_factory=PowerCompartmentParameters)
    handle: HandleParameters = field(default_factory=HandleParameters)
    wifi: WifiDockParameters = field(default_factory=WifiDockParameters)
    logo: LogoParameters = field(default_factory=LogoParameters)
    fasteners: FastenerParameters = field(default_factory=FastenerParameters)
    printer: PrintParameters = field(default_factory=PrintParameters)

    def proportionally_scaled(self, width: float) -> "StationParameters":
        """Reject unsafe partial scaling of a hardware-sized assembly.

        The fixed 165 mm package fits the selected equipment and printer.  A new
        width would require a coordinated repack of every absolute equipment,
        interface, split, and load-path datum; returning a partly scaled model is
        more dangerous than making that design decision explicit.
        """

        if abs(width - self.enclosure.width) > 1e-9:
            raise ValueError(
                "proportional scaling is not released: repack all equipment and "
                "interface datums before changing the 165 mm enclosure"
            )
        return self


DEFAULT = StationParameters()
