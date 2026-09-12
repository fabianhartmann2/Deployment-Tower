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


def test_service_joint_lengths_are_distinct_by_grip_stack():
    fasteners = DEFAULT.fasteners
    assert (fasteners.base_screw, fasteners.base_screw_length) == ("M3x14", 14.0)
    assert (fasteners.cradle_screw, fasteners.cradle_screw_length) == ("M3x10", 10.0)
    assert (fasteners.router_tray_screw, fasteners.router_tray_screw_length) == ("M3x6", 6.0)
    assert (fasteners.logo_screw, fasteners.logo_screw_length) == ("M3x8", 8.0)
    assert (fasteners.handle_screw, fasteners.handle_screw_length) == ("M3x10", 10.0)
    assert (fasteners.service_screw, fasteners.service_screw_length) == ("M3x8", 8.0)
    assert (fasteners.structural_screw, fasteners.structural_screw_length) == ("M4x18", 18.0)
