"""Deterministic off-screen renders from CadQuery tessellations using VTK."""

from __future__ import annotations

from dataclasses import dataclass
from math import cos, radians, sin
from pathlib import Path

import cadquery as cq
import vtk

from .assembly import part_definitions
from .components import build_reference_model
from .parameters import DEFAULT, StationParameters


@dataclass(frozen=True)
class RenderItem:
    obj: cq.Workplane
    color: tuple[float, float, float]
    alpha: float = 1.0


def _polydata(obj: cq.Workplane, tolerance: float = 0.45) -> vtk.vtkPolyData:
    vertices, triangles = obj.val().tessellate(tolerance, 0.20)
    points = vtk.vtkPoints()
    for vertex in vertices:
        points.InsertNextPoint(vertex.x, vertex.y, vertex.z)
    cells = vtk.vtkCellArray()
    for a, b, c in triangles:
        triangle = vtk.vtkTriangle()
        triangle.GetPointIds().SetId(0, a)
        triangle.GetPointIds().SetId(1, b)
        triangle.GetPointIds().SetId(2, c)
        cells.InsertNextCell(triangle)
    poly = vtk.vtkPolyData()
    poly.SetPoints(points)
    poly.SetPolys(cells)
    normals = vtk.vtkPolyDataNormals()
    normals.SetInputData(poly)
    normals.SetFeatureAngle(35.0)
    normals.ConsistencyOn()
    normals.AutoOrientNormalsOn()
    normals.SplittingOn()
    normals.Update()
    return normals.GetOutput()


def _actor(item: RenderItem) -> vtk.vtkActor:
    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputData(_polydata(item.obj))
    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    prop = actor.GetProperty()
    prop.SetColor(*item.color)
    prop.SetOpacity(item.alpha)
    prop.SetAmbient(0.24)
    prop.SetDiffuse(0.72)
    prop.SetSpecular(0.10)
    prop.SetSpecularPower(24.0)
    prop.SetInterpolationToPhong()
    return actor


def _bounds(items: list[RenderItem]) -> tuple[tuple[float, float], tuple[float, float], tuple[float, float]]:
    boxes = [item.obj.val().BoundingBox() for item in items]
    return (
        (min(box.xmin for box in boxes), max(box.xmax for box in boxes)),
        (min(box.ymin for box in boxes), max(box.ymax for box in boxes)),
        (min(box.zmin for box in boxes), max(box.zmax for box in boxes)),
    )


def render_items(
    items: list[RenderItem],
    output: Path,
    elev: float,
    azim: float,
    title: str,
    limits: tuple[tuple[float, float], tuple[float, float], tuple[float, float]] | None = None,
) -> None:
    del title  # Filenames/report captions carry titles without burning text into renders.
    renderer = vtk.vtkRenderer()
    renderer.SetBackground(0.945, 0.94, 0.925)
    renderer.SetUseDepthPeeling(True)
    renderer.SetMaximumNumberOfPeels(100)
    renderer.SetOcclusionRatio(0.05)
    for item in items:
        renderer.AddActor(_actor(item))

    if limits is None:
        limits = _bounds(items)
    centre = tuple((lo + hi) / 2.0 for lo, hi in limits)
    spans = tuple(hi - lo for lo, hi in limits)
    radius = max(spans) * 2.7
    az = radians(azim)
    el = radians(elev)
    direction = (cos(el) * cos(az), cos(el) * sin(az), sin(el))
    camera = vtk.vtkCamera()
    camera.SetFocalPoint(*centre)
    camera.SetPosition(*(centre[i] + radius * direction[i] for i in range(3)))
    camera.SetViewUp(0.0, 0.0, 1.0)
    camera.ParallelProjectionOn()
    camera.SetParallelScale(max(spans[2] * 0.58, spans[0] * 0.64, spans[1] * 0.64))
    renderer.SetActiveCamera(camera)
    renderer.ResetCameraClippingRange()

    key = vtk.vtkLight()
    key.SetLightTypeToSceneLight()
    key.SetPosition(centre[0] - radius, centre[1] - radius, centre[2] + radius)
    key.SetFocalPoint(*centre)
    key.SetColor(1.0, 0.98, 0.94)
    key.SetIntensity(0.82)
    renderer.AddLight(key)
    fill = vtk.vtkLight()
    fill.SetLightTypeToSceneLight()
    fill.SetPosition(centre[0] + radius, centre[1] + radius, centre[2] + radius * 0.4)
    fill.SetFocalPoint(*centre)
    fill.SetColor(0.82, 0.88, 1.0)
    fill.SetIntensity(0.52)
    renderer.AddLight(fill)

    window = vtk.vtkRenderWindow()
    window.SetOffScreenRendering(True)
    window.SetAlphaBitPlanes(True)
    window.SetMultiSamples(0)
    window.SetSize(1800, 1800)
    window.AddRenderer(renderer)
    window.Render()
    capture = vtk.vtkWindowToImageFilter()
    capture.SetInput(window)
    capture.SetScale(1)
    capture.ReadFrontBufferOff()
    capture.Update()
    writer = vtk.vtkPNGWriter()
    output.parent.mkdir(parents=True, exist_ok=True)
    writer.SetFileName(str(output))
    writer.SetInputConnection(capture.GetOutputPort())
    writer.Write()
    window.Finalize()


def _assembled_items(p: StationParameters, exploded: bool = False) -> list[RenderItem]:
    offsets = {
        "base": (0.0, 0.0, -38.0),
        "mac_cradle": (0.0, 0.0, -18.0),
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
    items: list[RenderItem] = []
    for name, definition in part_definitions().items():
        if not definition.assembly_part:
            continue
        obj = definition.builder(p)
        if exploded:
            obj = obj.translate(offsets.get(name, (0.0, 0.0, 0.0)))
        items.append(RenderItem(obj, definition.color, 1.0))
    return items


def render_all(output_dir: Path, p: StationParameters = DEFAULT) -> list[Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    paths: list[Path] = []
    assembled = output_dir / "assembled_three_quarter.png"
    render_items(_assembled_items(p), assembled, 20.0, -136.0, "Integrated Deployment Station - assembled")
    paths.append(assembled)

    model = build_reference_model(p)
    rear_items = _assembled_items(p)
    rear_items.extend(RenderItem(obj, (0.10, 0.28, 0.31), 1.0) for obj in model.equipment.values())
    rear_items.extend(RenderItem(obj, (0.33, 0.35, 0.38), 1.0) for obj in model.hardware.values())
    rear = output_dir / "rear_interface.png"
    render_items(rear_items, rear, 7.0, 90.0, "Rear service interfaces")
    paths.append(rear)

    exploded = output_dir / "exploded_view.png"
    render_items(_assembled_items(p, exploded=True), exploded, 18.0, -128.0, "Exploded printable assembly")
    paths.append(exploded)

    packaging_items = [
        RenderItem(model.equipment["mac_mini_m4"], (0.65, 0.67, 0.70), 0.95),
        RenderItem(model.equipment["rutm30"], (0.10, 0.42, 0.48), 0.95),
        RenderItem(model.equipment["apv_35_36"], (0.88, 0.76, 0.38), 0.95),
    ]
    for obj in model.clearances.values():
        packaging_items.append(RenderItem(obj, (0.88, 0.28, 0.18), 0.10))
    for obj in model.interfaces.values():
        packaging_items.append(RenderItem(obj, (0.26, 0.40, 0.88), 0.10))
    packaging = output_dir / "packaging_study.png"
    render_items(
        packaging_items,
        packaging,
        18.0,
        -128.0,
        "Phase 1 packaging and clearance study",
        ((-90.0, 100.0), (-105.0, 105.0), (-30.0, 285.0)),
    )
    paths.append(packaging)
    return paths
