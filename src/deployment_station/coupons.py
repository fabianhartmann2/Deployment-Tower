"""High-risk interface fit coupons."""

from __future__ import annotations

from collections import OrderedDict

import cadquery as cq

from .base import mac_button_coupon
from .handle import handle_lock_coupon
from .logo_panel import logo_retention_coupon
from .parameters import DEFAULT, StationParameters
from .power_compartment import insert_boss_coupon
from .rear_panel import c8_cutout_coupon, rear_panel_fit_coupon, router_rf_access_coupon
from .wifi_dock import wifi_dock_coupon


def fit_coupons(p: StationParameters = DEFAULT) -> OrderedDict[str, cq.Workplane]:
    return OrderedDict(
        (
            ("coupon_c8_cutout", c8_cutout_coupon(p)),
            ("coupon_insert_boss", insert_boss_coupon(p)),
            ("coupon_rear_panel_fit", rear_panel_fit_coupon(p)),
            ("coupon_logo_retention", logo_retention_coupon(p)),
            ("coupon_handle_lock", handle_lock_coupon(p)),
            ("coupon_wifi_dock", wifi_dock_coupon(p)),
            ("coupon_mac_button_recess", mac_button_coupon(p)),
            ("coupon_router_rf_access", router_rf_access_coupon(p)),
        )
    )
