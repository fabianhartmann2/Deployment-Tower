"""Part registry and complete/packaging/exploded assemblies."""

from __future__ import annotations

from collections import OrderedDict
from dataclasses import dataclass
from typing import Callable

import cadquery as cq

from .base import base
from .components import build_reference_model
from .handle import removable_handle, upper_cap
from .logo_panel import blank_logo_panel, example_embossed_logo_panel, logo_panel
from .mac_mount import compliant_pad_template, mac_cradle
from .parameters import DEFAULT, StationParameters
from .power_compartment import power_compartment, power_compartment_cover
from .rear_panel import rear_panel, router_interface_bezel
from .router_tray import router_compliant_pad_template, router_tray
from .shell import lower_shell, upper_shell
from .wifi_dock import wifi_dock


Builder = Callable[[StationParameters], cq.Workplane]


@dataclass(frozen=True)
class PartDefinition:
    name: str
    builder: Builder
    material: str
    color: tuple[float, float, float]
    assembly_part: bool = True
    note: str = ""


def part_definitions() -> OrderedDict[str, PartDefinition]:
    white = (0.90, 0.90, 0.87)
    dark = (0.08, 0.09, 0.10)
    internal = (0.30, 0.34, 0.38)
    return OrderedDict(
        (
            d.name,
            d,
        )
        for d in (
            PartDefinition("base", base, "ASA, dark", dark),
            PartDefinition("mac_cradle", mac_cradle, "ASA + separate TPU/silicone pads", internal),
            PartDefinition("lower_shell", lower_shell, "ASA, matte white", white),
            PartDefinition("upper_shell", upper_shell, "ASA, matte white", white),
            PartDefinition("router_tray", router_tray, "ASA", internal),
            PartDefinition("power_compartment", power_compartment, "FR engineering filament after review", (0.40, 0.42, 0.44)),
            PartDefinition("power_compartment_cover", power_compartment_cover, "FR engineering filament after review", (0.28, 0.30, 0.32)),
            PartDefinition("rear_panel", rear_panel, "ASA, dark", dark),
            PartDefinition("router_interface_bezel", router_interface_bezel, "ASA, dark", (0.12, 0.13, 0.14)),
            PartDefinition("upper_cap", upper_cap, "ASA, matte white", white),
            PartDefinition("removable_handle", removable_handle, "ASA/PA-CF after load test", dark),
            PartDefinition("wifi_dock_left", lambda p: wifi_dock("left", p), "ASA or PA", dark),
            PartDefinition("wifi_dock_right", lambda p: wifi_dock("right", p), "ASA or PA", dark),
            PartDefinition("logo_panel_left", lambda p: logo_panel("left", p), "ASA, matte white", white),
            PartDefinition("logo_panel_right", lambda p: logo_panel("right", p), "ASA, matte white", white),
            PartDefinition("logo_panel_blank_template", blank_logo_panel, "ASA", white, False, "Reusable panel template"),
            PartDefinition("logo_panel_example_embossed", example_embossed_logo_panel, "ASA/multicolor", (0.75, 0.77, 0.80), False),
            PartDefinition("compliant_pad_template", compliant_pad_template, "TPU 95A or laser-cut silicone", (0.22, 0.22, 0.22), False),
            PartDefinition("router_compliant_pad_template", router_compliant_pad_template, "TPU 95A or laser-cut silicone", (0.22, 0.22, 0.22), False),
        )
    )


def printable_parts(p: StationParameters = DEFAULT) -> OrderedDict[str, cq.Workplane]:
    return OrderedDict((name, definition.builder(p)) for name, definition in part_definitions().items())


def build_assembly(
    p: StationParameters = DEFAULT,
    include_references: bool = True,
    include_handle: bool = True,
) -> cq.Assembly:
    assembly = cq.Assembly(name="Integrated Deployment Station v0.9")
    for name, definition in part_definitions().items():
        if not definition.assembly_part:
            continue
        if name == "removable_handle" and not include_handle:
            continue
        assembly.add(definition.builder(p), name=name, color=cq.Color(*definition.color))

    if include_references:
        model = build_reference_model(p)
        equipment_colors = {
            "mac_mini_m4": (0.64, 0.67, 0.69),
            "rutm30": (0.12, 0.38, 0.42),
            "apv_35_36": (0.84, 0.84, 0.78),
        }
        for name, obj in model.equipment.items():
            assembly.add(obj, name=f"reference_{name}", color=cq.Color(*equipment_colors[name]))
        for name, obj in model.hardware.items():
            assembly.add(obj, name=f"reference_{name}", color=cq.Color(0.34, 0.36, 0.38))
    return assembly


def packaging_assembly(p: StationParameters = DEFAULT) -> cq.Assembly:
    assembly = cq.Assembly(name="Phase 1 packaging study")
    model = build_reference_model(p)
    colors = {
        "mac_mini_m4": (0.64, 0.67, 0.69),
        "rutm30": (0.10, 0.40, 0.46),
        "apv_35_36": (0.85, 0.82, 0.68),
    }
    for name, obj in model.equipment.items():
        assembly.add(obj, name=name, color=cq.Color(*colors[name]))
    for name, obj in model.clearances.items():
        assembly.add(obj, name=f"clearance_{name}", color=cq.Color(0.85, 0.30, 0.20, 0.35))
    for name, obj in model.interfaces.items():
        assembly.add(obj, name=f"zone_{name}", color=cq.Color(0.35, 0.45, 0.85, 0.25))
    for name, obj in model.hardware.items():
        assembly.add(obj, name=f"hardware_{name}", color=cq.Color(0.34, 0.36, 0.38))
    return assembly


def exploded_assembly(p: StationParameters = DEFAULT) -> cq.Assembly:
    offsets = {
        "base": (0.0, 0.0, -38.0),
        "mac_cradle": (0.0, 0.0, -18.0),
        "lower_shell": (0.0, 0.0, 0.0),
        "power_compartment": (-88.0, 0.0, 10.0),
        "power_compartment_cover": (-88.0, 0.0, 32.0),
        "router_tray": (0.0, 0.0, 28.0),
        "upper_shell": (0.0, 0.0, 36.0),
        "rear_panel": (0.0, 90.0, 0.0),
        "router_interface_bezel": (0.0, 116.0, 0.0),
        "upper_cap": (0.0, 0.0, 78.0),
        "removable_handle": (0.0, 0.0, 118.0),
        "wifi_dock_left": (-42.0, 0.0, 18.0),
        "wifi_dock_right": (42.0, 0.0, 18.0),
        "logo_panel_left": (-48.0, 0.0, 0.0),
        "logo_panel_right": (48.0, 0.0, 0.0),
    }
    assembly = cq.Assembly(name="Exploded Integrated Deployment Station")
    for name, definition in part_definitions().items():
        if not definition.assembly_part:
            continue
        assembly.add(definition.builder(p).translate(offsets.get(name, (0.0, 0.0, 0.0))), name=name, color=cq.Color(*definition.color))
    return assembly
