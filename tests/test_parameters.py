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
        fits.logo_panel_per_side,
        fits.snap_feature_per_side,
        fits.wifi_clip_radial,
    }
    assert len(values) >= 4


def test_non_default_clearance_builds_independent_configuration():
    modified = replace(DEFAULT, fits=replace(DEFAULT.fits, logo_panel_per_side=0.35))
    assert modified.fits.logo_panel_per_side == 0.35
    assert DEFAULT.fits.logo_panel_per_side == 0.25


def test_service_joint_lengths_are_distinct_by_grip_stack():
    fasteners = DEFAULT.fasteners
    assert (fasteners.base_screw, fasteners.base_screw_length) == ("M3x14", 14.0)
    assert (fasteners.cradle_screw, fasteners.cradle_screw_length) == ("M3x10", 10.0)
    assert (fasteners.router_tray_screw, fasteners.router_tray_screw_length) == ("M3x6", 6.0)
    assert (fasteners.logo_screw, fasteners.logo_screw_length) == ("M3x8", 8.0)
    assert (fasteners.handle_screw, fasteners.handle_screw_length) == ("M3x10", 10.0)
    assert (fasteners.service_screw, fasteners.service_screw_length) == ("M3x8", 8.0)
    assert (fasteners.structural_screw, fasteners.structural_screw_length) == ("M4x18", 18.0)
