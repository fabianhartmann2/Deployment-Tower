# Integrated Deployment Station CAD

Parametric CadQuery concept for an FDM-printed station containing a Mac mini M4, a Teltonika RUTM30, and a Mean Well APV-35-36. The modeled default is a **165 x 165 x 280 mm fixed enclosure** (base and recessed dock material included; removable handle and antennas excluded), with a **1:1:1.697** width:depth:height ratio.

> **Prototype status and safety boundary:** this package is editable concept/prototype mechanical CAD. It is not a production release, an electrical design, a safe-working-load rating, or evidence of regulatory compliance. Computational PASS results prove only the checks named in the generated report. Actual hardware fit, cables and overmoulds, printing tolerances, thermal behavior, carrying load/cycles, and qualified 230 V electrical review and tests are still pending. Do not energize a built unit until a competent electrical designer has completed the architecture and a qualified person has inspected and tested the complete assembly.

## Architecture

The stack from bottom to top is:

1. a removable dark base with 5 mm feet, a 116 mm intake opening, and a continuous lower-rear Mac-button path;
2. a horizontal Mac mini on an open-ring, three-pad cradle with four positive-Z clip/cam retainers and two bottom-operated release rails;
3. a shell-supported, separately covered APV/mains compartment, a distinct low-voltage/data lane, and a provisional reserved Mac-AC route;
4. a horizontal RUTM30 on four replaceable compliant support pads and a shell-supported removable tray at `Z=151`; and
5. a reinforced upper shell and cap with a removable handle carried by four externally accessible M3 screws, broad feet, full-depth cap bosses, and shell-tied load paths.

The lower and upper shell modules fit the Bambu Lab X1 Carbon's 256 mm build cube. The upper shell also carries two 70 x 70 mm logo panels retained by two outward-accessible M3 screws each and two screw-fastened, vertically oriented recessed Wi-Fi antenna transport docks. The C8 inlet island and closed terminal tunnel are integral to the power compartment: the surrounding rear service panel removes around the island, leaving that mechanical mains boundary in place. Inside the box, raised cable-tie bridges preserve a solid floor, the two APV fixing axes use top-service blind insert pilots, and four wall-tied columns reach the removable cover. These are mechanical provisions only and do not authorize wiring or energization.

The current joint labels deliberately distinguish **M3x14 base**, **M3x10 Mac-cradle**, **M3x10 handle**, recessed low-head **M3x6 router-tray**, **M3x8 logo/service/cover**, and **M4x18 cap/seam** stacks. The handle screws seat on the full 5 mm feet rather than in deep counterbores. All screw heads, inserts, engagement, torque, and final lengths remain provisional until coupon and joint-stack tests pass.

The official router geometry is imported from `reference/0112_RUTM30AMBKX_02.STEP`. The Mac, APV, antennas, C8, extensions, plugs, and cable paths are controlled placeholders; see [assumptions.md](reports/assumptions.md).

## Coordinate system

All dimensions are millimetres.

- Origin: centre of the external footprint on the desk-contact plane.
- +X: right when looking at the front.
- +Y: toward the rear service face.
- +Z: upward.
- Fixed body: approximately `X=-82.5..82.5`, `Y=-82.5..82.5`, `Z=0..280`.
- Equipment positions in `layout.py` are reference-envelope centres.

The principal centres are Mac `(0,-8,49)`, APV `(-35,8,103.55)`, and RUTM30 `(0,28,170.5)`. Full datums, packaging ranges, and parameter defaults are in [dimensions.md](reports/dimensions.md).

## Build, test, and export

Python 3.10-3.12 is supported; CadQuery is pinned to 2.6.1. From `cad/`:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -e ".[test]"
.venv/bin/python -m pytest
.venv/bin/python -m deployment_station.export
```

On Windows, substitute `.venv\Scripts\python.exe` for `.venv/bin/python`. Installed console-script equivalents are `deployment-station-export`, `deployment-station-validate`, and the macOS-only `deployment-station-quicklook`.

The export command rebuilds all parts from `parameters.py`, writes STEP/STL and renders, reopens every STEP, validates every STL, writes the manifest and reports, and exits non-zero if any validation result is `FAIL`. A report-only rerun against the existing STL directory is:

```sh
.venv/bin/python -m deployment_station.validation
```

The complete export command is the authoritative check. The standalone report-only command reruns geometry and whole-file mesh checks; export additionally verifies the actual packed print orientation and independently checks every disconnected mesh component for grounding and manifold integrity.

The non-default proportional-scaling API intentionally raises `ValueError`. Absolute equipment, port, split, and load-path datums cannot be safely scaled as one ratio; a different enclosure width requires a coordinated repack and new verification.

## Computational-result authority

The source checks are fail-gated, but aggregate counts and artifact hashes are intentionally not frozen in this narrative before regeneration. Run the export command after every source change, then use [validation_results.md](reports/validation_results.md), `validation.json`, and `export_manifest.json` as the generated record for that exact build. The checks cover installed-part pairs, selected equipment/mount intersections, print-volume and solid validity, critical mating geometry, STEP reopen, and STL mesh integrity. A zero-FAIL report remains computational evidence only; every physical, thermal, load, signal, cable, and electrical item marked WARN or PENDING remains open.

## Generated outputs

The current source registry expects **19 printable definitions**: 15 installed assembly parts plus four reusable/non-installed templates. Regeneration writes:

- one printable-part STEP and one print-oriented STL for each registered definition;
- 8 coupon STEP files and 8 coupon STL files;
- `complete_assembly.step`, `exploded_assembly.step`, and `packaging_study.step`;
- `component_envelopes.step`, containing non-printable references and keep-outs;
- four deterministic PNG renders; and
- `reports/export_manifest.json`, with the authoritative regenerated paths, sizes, SHA-256 hashes, and design-space STEP bounding boxes.

STEP files remain in assembly coordinates. STL files receive the documented print-orientation transform and are placed on `Z=0`. No 3MF is generated because this export path cannot preserve dependable slicer/process settings.

### macOS Finder model

`exports/interactive/complete_assembly_finder.usdz` is a color, interactive Quick Look model containing all 15 installed printed parts, the three equipment references, and seven interface-hardware references. Select it in Finder and press Space, or open it directly, to orbit, pan, and zoom. It uses metres-per-unit metadata corresponding to the millimetre CAD model and passes Apple's strict RealityKit USDZ validation.

On macOS with the Apple USD command-line tools available, regenerate it with:

```sh
.venv/bin/python -m deployment_station.quicklook
```

This convenience visualization is generated separately from the fail-gated STEP/STL manifest and is not a manufacturing export.

## Direct versus extended interfaces

| Interface | Decision | CAD implementation | Verification boundary |
| --- | --- | --- | --- |
| Four cellular SMA connections | Direct native | Common 88 x 30 radiused RF window at the official RUTM30 row | Actual coupling bodies, hand/tool clearance, first bends, liner, and support pending |
| Two Wi-Fi RP-SMA connections | Direct native | Same common RF window; official sequence is Mobile / Wi-Fi / Mobile / Mobile / Wi-Fi / Mobile | Actual plugs and connected-antenna service pending |
| RUTM30 LAN and WAN | Replaceable extensions | Two supported positions with provisional two-hole M3 flange patterns in the removable router bezel | Exact parts, hole patterns, latch access, link performance, and topology pending |
| Internal Mac Ethernet | Internal patch lead | Placeholder plug volume in low-voltage lane | Consumes one native router port; actual lead fit pending |
| Mac HDMI | Replaceable extension | Rear-panel position at `(-20,57)` with a provisional two-hole M3 flange pattern | Exact native coordinate/overmould, extension capability, and vendor hole pattern pending |
| One Mac USB-C | Replaceable extension | Rear-panel position at `(16,57)` with a provisional two-hole M3 flange pattern | Exact native coordinate/overmould, extension capability, and vendor hole pattern pending |
| Mac AC | Internal only | Diameter-12 gland and continuous stepped 6 mm reserved envelope from the covered zone toward the provisional Mac connector | This is packaging space, not a selected conduit or completed branch architecture; qualified design remains PENDING |
| Schurter 6160.0021 C8 | Direct component | Fixed inlet island at `(-38,108)`, integral with the closed compartment | Actual part, supplier revision/status, mounting, shroud, wiring, and electrical review pending |
| Mac power button | Direct mechanical reach | Continuous lower-rear/underside finger path; no Mac modification | Photo-derived location and physical ergonomics/guarding pending |

The two-port router cannot simultaneously provide both external Ethernet links and the required internal Mac link. Both extension positions exist mechanically, but three simultaneous links require an approved topology change (for example, an appropriately integrated active switch). See [interface_decisions.md](reports/interface_decisions.md).

## Source map

| Module | Responsibility |
| --- | --- |
| `parameters.py`, `layout.py` | Defaults, datums, and packaging locations |
| `components.py` | Official router import; controlled equipment, hardware, cable, and removal placeholders |
| `base.py`, `mac_mount.py` | Base, intake/button path, three 2 mm pad positions in 1 mm seats, four clip/cam retainers, two bottom release rails, and shell-fastened cradle ears |
| `shell.py` | Split shell, rear seat, seam keys/bolts, logo/dock receivers, equipment supports, and cap load path |
| `router_tray.py`, `rear_panel.py` | Router retention, four compliant support lands/pad template, recessed low-head tray screws, rear panel, replaceable bezel, RF window, and provisional two-hole extension flanges |
| `power_compartment.py` | Mechanical APV/mains enclosure, fixed C8 island/tunnel, sealed-floor tie bridges, top-service APV pilots, full-height cover columns, exits, and cover |
| `handle.py` | Six-fastener cap, structural beams, four-screw handle feet/bosses, and mounting coupon |
| `wifi_dock.py`, `logo_panel.py` | Screw-fastened antenna docks and two-screw replaceable logo panels |
| `coupons.py` | Eight high-risk physical-fit articles |
| `assembly.py`, `render.py` | Part registry, assemblies, non-printable references, and views |
| `validation.py`, `export.py` | Fail-closed computational checks and reproducible outputs |

## Documentation

- [dimensions.md](reports/dimensions.md) — envelope, packaging, part envelopes, and parameter reference.
- [interface_decisions.md](reports/interface_decisions.md) — direct/extension decisions and Ethernet warning.
- [bom.md](reports/bom.md) — printed parts, equipment, provisional hardware, screws, and inserts.
- [assembly.md](reports/assembly.md) — de-energized assembly, service, and load-path sequence.
- [print_plan.md](reports/print_plan.md) — orientations, starting process, and coupon order.
- [assumptions.md](reports/assumptions.md) — evidence hierarchy, unresolved measurements, and deviations.
- [requirements_traceability.md](reports/requirements_traceability.md) — handoff IDs mapped to modules, tests, and closure evidence.
- [known_limitations.md](reports/known_limitations.md) — release blockers and explicit electrical boundary.
- [validation_results.md](reports/validation_results.md) — generated computational record.
- [coupon_results_2026-09-10.md](reports/coupon_results_2026-09-10.md) — physical coupon observations, revisions, and selected v2 fits.

## Release boundary

The repository demonstrates a coherent, printable mechanical prototype concept. Before a complete prototype is frozen, it still requires the actual devices, extensions, cables, inserts, pads, and connector hardware to be measured and dry-fitted; physical coupons and service trials to pass; and the Ethernet topology to be resolved. The Mac-AC envelope is only a reserved path, and the branch hardware/topology, APV lead bends, protective separation, restraint, and materials are not released. Before carrying or energizing, it additionally requires load/cycle and thermal tests, a complete competent electrical design, and qualified inspection/testing. Supplier availability and lifecycle status—including the specified C8 inlet—must be reconfirmed before procurement.
