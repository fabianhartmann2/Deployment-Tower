from dataclasses import replace

import pytest

from deployment_station.assembly import part_definitions, printable_parts
from deployment_station.components import build_reference_model, mac_reference, router_connector_clearances, router_source_kind
from deployment_station.coupons import fit_coupons
from deployment_station.geometry import bbox_dimensions, box_at, cylinder_axis
from deployment_station.mac_mount import (
    mac_cradle,
    mac_release_rail_datums,
    mac_vertical_retainer_centres,
    mac_vertical_retainer_lead_in,
)
from deployment_station.parameters import DEFAULT
from deployment_station.power_compartment import power_compartment, power_compartment_cover
from deployment_station.rear_panel import mac_extension_mount_positions
from deployment_station.router_tray import router_support_pad_positions
from deployment_station.shell import lower_shell
from deployment_station.validation import (
    ASSEMBLY_INTERFERENCE_ALLOWLIST,
    _intersection_volume,
    _sampled_translation_clearance,
    apv_top_service_mount_check,
    c8_terminal_passage_check,
    extension_mount_hole_checks,
    fastener_stack_checks,
    geometry_checks,
    handle_structural_mount_check,
    logo_screw_mount_check,
    mac_base_pad_stack_check,
    mac_ac_corridor_packaging_check,
    mac_ac_gland_passage_check,
    mac_vertical_retention_check,
    power_cover_column_check,
    power_tie_bridge_floor_check,
    router_support_stack_check,
    wifi_dock_capture_geometry_check,
)


@pytest.fixture(scope="module")
def validation_parts():
    return printable_parts()


def test_required_printable_part_breakdown_exists():
    required = {
        "base",
        "mac_cradle",
        "lower_shell",
        "upper_shell",
        "router_tray",
        "power_compartment",
        "power_compartment_cover",
        "rear_panel",
        "router_interface_bezel",
        "upper_cap",
        "removable_handle",
        "wifi_dock_left",
        "wifi_dock_right",
        "logo_panel_left",
        "logo_panel_right",
        "logo_panel_blank_template",
        "logo_panel_example_embossed",
        "compliant_pad_template",
        "router_compliant_pad_template",
    }
    assert required <= set(part_definitions())


def test_all_parts_valid_and_fit_printer():
    for name, obj in printable_parts().items():
        assert obj.val().isValid(), name
        assert max(bbox_dimensions(obj)) <= DEFAULT.printer.build_x, name


def test_assembly_parts_are_connected_solids():
    parts = printable_parts()
    for name, definition in part_definitions().items():
        if definition.assembly_part:
            assert len(parts[name].solids().vals()) == 1, name


def test_all_required_coupons_exist_and_are_valid():
    coupons = fit_coupons()
    assert set(coupons) == {
        "coupon_c8_cutout",
        "coupon_insert_boss",
        "coupon_rear_panel_fit_v2",
        "coupon_logo_mount",
        "coupon_handle_mount",
        "coupon_wifi_dock_v2",
        "coupon_mac_button_recess",
        "coupon_router_rf_access",
    }
    assert all(obj.val().isValid() for obj in coupons.values())


def test_official_router_step_and_connector_count():
    assert router_source_kind() == "official_teltonika_step"
    clearances = router_connector_clearances()
    assert len([name for name in clearances if name.startswith("cellular")]) == 4
    assert len([name for name in clearances if name.startswith("wifi")]) == 2
    assert len([name for name in clearances if name.startswith("router_rj45")]) == 2


def test_collision_check_detects_shallow_broad_intersection():
    first = box_at(20.0, 20.0, 1.0, (0.0, 0.0, 0.0))
    second = box_at(20.0, 20.0, 1.0, (0.0, 0.0, 0.995))
    assert _intersection_volume(first, second) == pytest.approx(2.0, abs=1e-5)


def test_sampled_translation_clearance_detects_an_intermediate_obstacle():
    moving = {"moving": box_at(2.0, 2.0, 2.0, (0.0, 0.0, 0.0))}
    stationary = {"obstacle": box_at(2.0, 2.0, 2.0, (0.0, 5.0, 0.0))}

    clear = _sampled_translation_clearance(
        "clear motion",
        moving,
        stationary,
        ((0.0, 0.0, 0.0), (0.0, 1.0, 0.0)),
        "+Y",
    )
    blocked = _sampled_translation_clearance(
        "blocked motion",
        moving,
        stationary,
        ((0.0, 4.0, 0.0),),
        "+Y",
    )

    assert clear.status == "PASS"
    assert blocked.status == "FAIL"
    assert "moving/obstacle" in blocked.detail


def test_screw_mounted_parts_require_no_interference_allowance():
    assert ASSEMBLY_INTERFERENCE_ALLOWLIST == {}


def test_c8_terminal_tunnel_opens_into_main_compartment():
    result = c8_terminal_passage_check(DEFAULT, power_compartment())
    assert result.status == "PASS", result.detail


def test_power_compartment_has_sealed_ties_top_service_mounts_and_cover_columns():
    compartment = power_compartment()
    cover = power_compartment_cover()
    checks = (
        power_tie_bridge_floor_check(DEFAULT, compartment),
        mac_ac_gland_passage_check(DEFAULT, compartment),
        apv_top_service_mount_check(DEFAULT, compartment),
        power_cover_column_check(DEFAULT, compartment, cover),
    )
    assert all(result.status == "PASS" for result in checks), "\n".join(
        f"{result.name}: {result.detail}" for result in checks
    )


def test_mac_ac_reserved_corridor_is_continuous_but_not_a_release_claim():
    parts = {"mac_cradle": mac_cradle(), "lower_shell": lower_shell()}
    model = build_reference_model()
    result = mac_ac_corridor_packaging_check(DEFAULT, parts, model)
    assert result.status == "PASS", result.detail
    assert "packaging envelope" in result.detail


def test_mac_cradle_has_clear_positive_vertical_retention():
    cradle = mac_cradle()
    result = mac_vertical_retention_check(DEFAULT, cradle, mac_reference(), lower_shell())
    assert result.status == "PASS", result.detail

    # Removing all material above the Mac recreates the former unretained
    # condition.  This guards against a clearance-only test becoming tautological.
    mac_top_z = DEFAULT.components.mac_support_plane_z + DEFAULT.components.mac_height
    top_cut = box_at(180.0, 180.0, 20.0, (0.0, DEFAULT.components.mac_center_y, mac_top_z + 10.0))
    assert mac_vertical_retention_check(DEFAULT, cradle.cut(top_cut), mac_reference()).status == "FAIL"

    flat_hooks = cradle
    for side, _stem_x, clip_y in mac_vertical_retainer_centres(DEFAULT):
        flat_hooks = flat_hooks.union(mac_vertical_retainer_lead_in(DEFAULT, side, clip_y))
    assert mac_vertical_retention_check(DEFAULT, flat_hooks, mac_reference()).status == "FAIL"

    retention = DEFAULT.mac_retention
    release_bridge_depth = max(retention.y_offsets) - min(retention.y_offsets) - retention.clip_depth - 1.0
    unlinked_releases = cradle
    for _side, rail_x, rail_y, rail_width, _rail_depth, rail_bottom_z in mac_release_rail_datums(DEFAULT):
        bridge_cut = box_at(
            rail_width + 0.4,
            release_bridge_depth,
            retention.release_rail_height + 0.4,
            (rail_x, rail_y, rail_bottom_z + retention.release_rail_height / 2.0),
        )
        unlinked_releases = unlinked_releases.cut(bridge_cut)
    assert mac_vertical_retention_check(DEFAULT, unlinked_releases, mac_reference()).status == "FAIL"


def test_handle_mount_check_is_not_satisfied_by_two_unmated_solids():
    disconnected_interface = {
        "removable_handle": box_at(128.0, 20.0, 18.0, (0.0, 0.0, 340.0)),
        "upper_cap": box_at(165.0, 165.0, 12.0, (0.0, 0.0, 274.0)),
    }
    assert all(len(part.solids().vals()) == 1 for part in disconnected_interface.values())
    assert handle_structural_mount_check(DEFAULT, disconnected_interface).status == "FAIL"


def test_logo_mount_check_rejects_a_blocked_panel_hole(validation_parts):
    assert logo_screw_mount_check(DEFAULT, validation_parts).status == "PASS"
    panel = validation_parts["logo_panel_right"]
    blocked = cylinder_axis(
        DEFAULT.fasteners.m3_clearance_diameter / 2.0 - 0.1,
        DEFAULT.logo.thickness + 0.2,
        (DEFAULT.enclosure.width / 2.0 + 0.1, -DEFAULT.logo.fastener_offset_y, DEFAULT.logo.center_z),
        (-1.0, 0.0, 0.0),
    )
    damaged = dict(validation_parts)
    damaged["logo_panel_right"] = panel.union(blocked)
    assert logo_screw_mount_check(DEFAULT, damaged).status == "FAIL"


def test_wifi_dock_capture_requires_small_bounded_arm_movement():
    result = wifi_dock_capture_geometry_check(DEFAULT)
    assert result.status == "PASS", result.detail
    impossible_lips = replace(DEFAULT.wifi, clip_lip_intrusion=4.0)
    assert wifi_dock_capture_geometry_check(replace(DEFAULT, wifi=impossible_lips)).status == "FAIL"


def test_sampled_motion_check_detects_an_intermediate_obstruction():
    moving = {"service_part": box_at(2.0, 2.0, 2.0, (0.0, 0.0, 0.0))}
    stationary = {"obstacle": box_at(2.0, 2.0, 2.0, (0.0, 5.0, 0.0))}
    result = _sampled_translation_clearance(
        "regression motion",
        moving,
        stationary,
        ((0.0, 0.0, 0.0), (0.0, 5.0, 0.0), (0.0, 10.0, 0.0)),
        "+Y regression",
    )
    assert result.status == "FAIL"
    assert "service_part/obstacle" in result.detail


def test_fastener_stack_checks_cover_all_screw_families_and_reject_wrong_lengths(validation_parts):
    results = fastener_stack_checks(DEFAULT, validation_parts)
    assert all(result.status == "PASS" for result in results), "\n".join(
        f"{result.name}: {result.detail}" for result in results
    )
    assert {result.name for result in results} == {
        "fastener stack: removable base M3x14",
        "fastener stack: Mac cradle M3x10",
        "fastener stack: router tray M3x6",
        "fastener stack: reinforced handle M3x10",
        "fastener stack: logo panels M3x8",
        "fastener stack: upper cap M4x18",
        "fastener stack: structural shell seam M4x18",
        "fastener stack: power-compartment cover M3x8",
    }

    wrong_fasteners = replace(
        DEFAULT.fasteners,
        base_screw="M3x8",
        base_screw_length=8.0,
        cradle_screw="M3x8",
        cradle_screw_length=8.0,
        router_tray_screw="M3x8",
        router_tray_screw_length=8.0,
        logo_screw="M3x6",
        logo_screw_length=6.0,
        handle_screw="M3x8",
        handle_screw_length=8.0,
        structural_screw="M4x12",
        structural_screw_length=12.0,
    )
    wrong_results = {
        result.name: result.status
        for result in fastener_stack_checks(replace(DEFAULT, fasteners=wrong_fasteners), validation_parts)
    }
    assert wrong_results["fastener stack: removable base M3x14"] == "FAIL"
    assert wrong_results["fastener stack: Mac cradle M3x10"] == "FAIL"
    assert wrong_results["fastener stack: router tray M3x6"] == "FAIL"
    assert wrong_results["fastener stack: reinforced handle M3x10"] == "FAIL"
    assert wrong_results["fastener stack: logo panels M3x8"] == "FAIL"
    assert wrong_results["fastener stack: upper cap M4x18"] == "FAIL"
    assert wrong_results["fastener stack: structural shell seam M4x18"] == "FAIL"
    assert wrong_results["fastener stack: power-compartment cover M3x8"] == "PASS"


def test_pad_support_and_extension_mount_witnesses_reject_missing_geometry(validation_parts):
    mac_pad = mac_base_pad_stack_check(
        DEFAULT,
        validation_parts["mac_cradle"],
        validation_parts["compliant_pad_template"],
    )
    router_support = router_support_stack_check(
        DEFAULT,
        validation_parts["router_tray"],
        validation_parts["router_compliant_pad_template"],
    )
    extension_mounts = extension_mount_hole_checks(
        DEFAULT,
        validation_parts["rear_panel"],
        validation_parts["router_interface_bezel"],
    )
    assert mac_pad.status == "PASS", mac_pad.detail
    assert router_support.status == "PASS", router_support.detail
    assert all(result.status == "PASS" for result in extension_mounts), "\n".join(
        f"{result.name}: {result.detail}" for result in extension_mounts
    )

    shallow_pad = replace(DEFAULT.mac_retention, base_pad_thickness=1.0)
    assert mac_base_pad_stack_check(
        replace(DEFAULT, mac_retention=shallow_pad),
        validation_parts["mac_cradle"],
        validation_parts["compliant_pad_template"],
    ).status == "FAIL"

    support_x, support_y = router_support_pad_positions(DEFAULT)[0]
    removed_land = box_at(
        DEFAULT.components.router_pad_width,
        DEFAULT.components.router_pad_depth,
        2.0,
        (support_x, support_y, DEFAULT.components.router_tray_z + 4.0),
    )
    damaged_tray = validation_parts["router_tray"].cut(removed_land)
    assert router_support_stack_check(
        DEFAULT,
        damaged_tray,
        validation_parts["router_compliant_pad_template"],
    ).status == "FAIL"

    mount_x, mount_z = mac_extension_mount_positions(DEFAULT)[0]
    panel_y0 = DEFAULT.enclosure.depth / 2.0 - DEFAULT.enclosure.rear_panel_thickness
    blocked_axis = cylinder_axis(
        DEFAULT.fasteners.m3_clearance_diameter / 2.0 - 0.1,
        DEFAULT.enclosure.rear_panel_thickness + 0.2,
        (mount_x, panel_y0 - 0.1, mount_z),
        (0.0, 1.0, 0.0),
    )
    blocked_panel = validation_parts["rear_panel"].union(blocked_axis)
    assert extension_mount_hole_checks(
        DEFAULT,
        blocked_panel,
        validation_parts["router_interface_bezel"],
    )[0].status == "FAIL"


def test_full_geometry_validation_has_no_failures():
    results = geometry_checks()
    result_names = {result.name for result in results}
    installed_count = sum(definition.assembly_part for definition in part_definitions().values())
    pairwise_results = [result for result in results if result.name.startswith("assembly interference: ")]
    assert len(pairwise_results) == installed_count * (installed_count - 1) // 2
    assert "Mac power-button continuous swept path" in result_names
    assert "handle four-screw reinforced mounting stack" in result_names
    assert "logo panels four-screw replaceable mounting stack" in result_names
    assert "Wi-Fi dock rounded-lip insertion geometry" in result_names
    assert "C8 terminal tunnel/main-compartment passage" in result_names
    assert "sealed-floor raised power tie bridges" in result_names
    assert "Mac AC nominal gland aperture" in result_names
    assert "APV top-service blind insert mounts" in result_names
    assert "power-cover full-height insert columns" in result_names
    assert "Mac AC reserved corridor continuity" in result_names
    assert "mains/SELV modeled keep-out non-overlap" in result_names
    assert "Mac AC branch hardware, protected conduit/restraint, and qualified separation proof" in result_names
    assert "APV lead bends and internal branch-hardware packaging" in result_names
    assert "Mac positive-Z clip retention" in result_names
    assert "Mac vertical-retainer pad/preload, release-force, and shake-cycle test" in result_names
    assert {
        "Mac three-pad pocket/support-plane stack",
        "RUTM30 four-pad support/counterbore stack",
        "fastener stack: removable base M3x14",
        "fastener stack: Mac cradle M3x10",
        "fastener stack: router tray M3x6",
        "fastener stack: reinforced handle M3x10",
        "fastener stack: logo panels M3x8",
        "fastener stack: upper cap M4x18",
        "fastener stack: structural shell seam M4x18",
        "fastener stack: power-compartment cover M3x8",
        "provisional HDMI/USB-C two-fastener extension holes",
        "provisional dual-RJ45 two-fastener extension holes",
        "rear panel+bezel sampled +Y service sweep",
        "Mac+cradle sampled downward service sweep",
        "RUTM30 sampled rearward service sweep (retainers released)",
        "RF aperture analytic connector-centre span",
        "as-built cable/forbidden-geometry routing and bend mock-up",
        "physical RF plug/finger/tool access",
        "local minimum-wall scan of all generated geometry",
    } <= result_names
    assert "Mac three-pad pocket/support-plane stack" in result_names
    assert "RUTM30 four-pad support/counterbore stack" in result_names
    assert {
        "fastener stack: removable base M3x14",
        "fastener stack: Mac cradle M3x10",
        "fastener stack: router tray M3x6",
        "fastener stack: reinforced handle M3x10",
        "fastener stack: logo panels M3x8",
        "fastener stack: upper cap M4x18",
        "fastener stack: structural shell seam M4x18",
        "fastener stack: power-compartment cover M3x8",
    } <= result_names
    assert {
        "provisional HDMI/USB-C two-fastener extension holes",
        "provisional dual-RJ45 two-fastener extension holes",
    } <= result_names
    assert "rear panel+bezel sampled +Y service sweep" in result_names
    assert "Mac+cradle sampled downward service sweep" in result_names
    assert "RUTM30 sampled rearward service sweep (retainers released)" in result_names
    assert "RF aperture analytic connector-centre span" in result_names
    assert "physical RF plug/finger/tool access" in result_names
    assert "local minimum-wall scan of all generated geometry" in result_names
    assert "as-built cable/forbidden-geometry routing and bend mock-up" in result_names
    assert {
        "equipment/mount interference: mac_mini_m4 / mac_cradle",
        "equipment/mount interference: rutm30 / router_tray",
        "equipment/mount interference: apv_35_36 / power_compartment",
        "equipment/mount interference: apv_35_36 / power_compartment_cover",
    } <= result_names
    pending_names = {result.name for result in results if result.status == "PENDING"}
    assert {
        "physical RF plug/finger/tool access",
        "local minimum-wall scan of all generated geometry",
        "as-built cable/forbidden-geometry routing and bend mock-up",
    } <= pending_names
    failures = [result for result in results if result.status == "FAIL"]
    assert failures == [], "\n".join(f"{item.name}: {item.detail}" for item in failures)
