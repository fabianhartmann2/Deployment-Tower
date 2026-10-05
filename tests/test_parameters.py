from dataclasses import replace

import pytest

from deployment_station.parameters import DEFAULT


def test_default_envelope_and_ratio():
    e = DEFAULT.enclosure
    assert e.width == e.depth == 165.0
    assert e.height == 280.0
    assert e.actual_height_ratio == pytest.approx(1.6969697)
    assert abs(e.actual_height_ratio - e.target_height_ratio) < 0.02


def test_partial_proportional_scaling_is_rejected():
    assert DEFAULT.proportionally_scaled(165.0) is DEFAULT
    with pytest.raises(ValueError, match="not released"):
        DEFAULT.proportionally_scaled(180.0)


def test_joint_clearances_are_separate_parameters():
    fits = DEFAULT.fits
    values = {
        fits.sliding_fit_per_side,
        fits.service_panel_per_side,
        fits.rear_panel_x_per_side,
        fits.rear_panel_z_per_side,
        fits.logo_panel_per_side,
        fits.snap_feature_per_side,
        fits.wifi_clip_radial,
    }
    assert len(values) >= 4


def test_non_default_clearance_builds_independent_configuration():
    modified = replace(DEFAULT, fits=replace(DEFAULT.fits, logo_panel_per_side=0.35))
    assert modified.fits.logo_panel_per_side == 0.35
    assert DEFAULT.fits.logo_panel_per_side == 0.25


def test_wifi_hub_clearance_matches_selected_three_marker_coupon():
    cavity_diameter = DEFAULT.wifi.antenna_base_diameter + 2.0 * DEFAULT.fits.wifi_clip_radial
    assert cavity_diameter == pytest.approx(31.0)


def test_mac_cradle_matches_physical_fit_corrections():
    components = DEFAULT.components
    assert components.mac_button_x_side == -1.0
    assert components.mac_underside_drop == 8.0
    assert components.mac_retained_body_height == 42.0
    assert DEFAULT.mac_retention.side_clearance == 0.30
    assert components.mac_intake_outer_diameter == 112.0


def test_m4_insert_pilot_matches_selected_one_notch_coupon():
    assert DEFAULT.fasteners.m4_insert_hole_diameter == 5.4


def test_seam_head_has_physical_trial_clearance():
    enclosure = DEFAULT.enclosure
    assert enclosure.seam_screw_head_diameter == 7.0
    assert enclosure.seam_head_clearance_diameter - enclosure.seam_screw_head_diameter == pytest.approx(1.2)


def test_router_tray_matches_physical_retention_feedback():
    components = DEFAULT.components
    assert components.router_side_guide_inset == 1.0
    assert components.router_top_ledge_inset == 0.6
    assert components.router_rear_retainer_adjustment == 1.0
    assert components.router_tray_screw_head_height == 3.0
    assert DEFAULT.fasteners.m3_low_head_recess_depth == 2.2


def test_v4_measured_interface_inputs_are_recorded():
    v = DEFAULT.prototype_v4
    assert (v.ethernet_cutout_width, v.ethernet_cutout_height, v.ethernet_mount_pitch) == (17.0, 14.0, 27.6)
    assert (v.hdmi_cutout_width, v.hdmi_cutout_height, v.hdmi_mount_pitch) == (16.0, 6.0, 27.0)
    assert (v.usbc_through_width, v.usbc_through_height, v.usbc_mount_pitch) == (10.0, 4.0, 19.0)
    assert (v.c8_cutout_width, v.c8_cutout_height, v.c8_mount_pitch) == (21.0, 12.5, 29.0)
    assert (v.magnet_diameter, v.magnet_thickness) == (6.0, 3.0)
    assert v.dovetail_clearances == (0.25, 0.35, 0.45)
    assert v.panel_magnet_thickness == 1.5
    assert v.rf_bulkhead_hole_selected == 6.6
    assert v.rf_bulkhead_wall_selected == 2.0
    assert v.power_compartment_target_x_sign == 1.0
    assert v.power_compartment_relocation_required is True
    assert v.dovetail_clearances_v2 == (0.05, 0.10, 0.15)
    assert v.dovetail_clearance_selected == 0.10


def test_v4_rear_io_coupon_feedback_is_recorded_without_mutating_v1():
    v = DEFAULT.prototype_v4
    assert v.ethernet_mount_z_offset_selected == -1.0
    assert v.hdmi_mount_hole_diameter == 3.2
    assert v.hdmi_mount_hole_diameter_selected == 4.1
    assert v.hdmi_mount_axis_setback == 8.0
    assert v.hdmi_connector_top_above_board == 8.0
    assert v.hdmi_shelf_drop_selected == 1.0
    assert v.hdmi_mount_axis_setback_selected == 9.0
    assert v.hdmi_shelf_depth_selected == 13.0
    assert v.usbc_coupon_projection_measured == 4.5
    assert v.usbc_mount_axis_setback == 2.5
    assert v.usbc_target_projection == 0.5
    assert v.usbc_board_standoff == 4.0
    assert v.usbc_board_standoff_selected == 6.0
    assert v.usbc_reinforcement_depth_selected == 2.0
    assert v.usbc_reinforcement_pocket_width_selected == 14.0
    assert v.usbc_reinforcement_pocket_height_selected == 6.5
    assert v.usbc_reinforcement_pocket_depth_selected == 2.5
    assert v.usbc_mount_bridge_width == 28.0
    assert v.usbc_mount_bridge_height == 12.0
    assert v.c8_mount_pitch == 29.0
    assert v.c8_mount_pitch_selected == 30.0


def test_service_joint_lengths_are_distinct_by_grip_stack():
    fasteners = DEFAULT.fasteners
    assert (fasteners.base_screw, fasteners.base_screw_length) == ("M3x14", 14.0)
    assert (fasteners.cradle_screw, fasteners.cradle_screw_length) == ("M3x10", 10.0)
    assert (fasteners.router_tray_screw, fasteners.router_tray_screw_length) == ("M3x6", 6.0)
    assert (fasteners.logo_screw, fasteners.logo_screw_length) == ("M3x8", 8.0)
    assert (fasteners.handle_screw, fasteners.handle_screw_length) == ("M3x14", 14.0)
    assert (fasteners.cap_lock_screw, fasteners.cap_lock_screw_length) == ("M4x10", 10.0)
    assert (fasteners.service_screw, fasteners.service_screw_length) == ("M3x8", 8.0)
    assert (fasteners.structural_screw, fasteners.structural_screw_length) == ("M4x18", 18.0)


def test_v4_production_layout_uses_relocated_power_and_full_height_rear_panel():
    assert DEFAULT.power.center_x == 35.0
    assert DEFAULT.interfaces.c8_position_x == 38.0
    assert DEFAULT.enclosure.rear_panel_height == 250.0
    assert DEFAULT.enclosure.rear_opening_top == 268.0
    assert DEFAULT.interfaces.router_bulkhead_pitch == 20.0
