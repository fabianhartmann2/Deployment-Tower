# Integrated Deployment Station CAD

Parametric CadQuery concept for an FDM-printed station containing a Mac mini M4, a Teltonika RUTM30, and a Mean Well APV-35-36. The modeled default is a **165 x 165 x 280 mm fixed enclosure** (base, panels, and cap included; removable handle and antennas excluded), with a **1:1:1.697** width:depth:height ratio.

> **Prototype status and safety boundary:** this package is editable concept/prototype mechanical CAD. It is not a production release, an electrical design, a safe-working-load rating, or evidence of regulatory compliance. Computational PASS results prove only the checks named in the generated report. Actual hardware fit, cables and overmoulds, printing tolerances, thermal behavior, carrying load/cycles, and qualified 230 V electrical review and tests are still pending. Do not energize a built unit until a competent electrical designer has completed the architecture and a qualified person has inspected and tested the complete assembly.

## Architecture

The stack from bottom to top is:

1. a removable dark base with 5 mm feet, a 116 mm intake opening, and a continuous lower-rear Mac-button path;
2. a horizontal Mac mini on a physically calibrated Ø112 open-ring, three-pad cradle with 0.30 mm side clearance, four lowered positive-Z clip/cam retainers, and two bottom-operated release rails;
3. a shell-supported, separately covered APV/mains compartment, a distinct low-voltage/data lane, and a provisional reserved Mac-AC route;
4. a horizontal RUTM30 on four replaceable compliant support pads and a shell-supported removable tray at `Z=151`, retained at the rear corners by two adjustable M3-screwed stops rather than brittle flexure clips; and
5. a reinforced upper shell and laterally sliding cap with a removable handle fastened from the cap underside by four hidden M3 screws, broad feet, full-depth handle inserts, two selected dovetail rails, and shell-tied load paths.

The lower and upper shell modules fit the Bambu Lab X1 Carbon's 256 mm build cube. Their load-bearing split uses six hidden M4 joints, an internal U-shaped belt in each shell, and three locating keys; all screw heads, tool corridors, and insert openings remain inside the closed exterior skin. A physical v3 assembly found the original Ø7.6 head pockets tight for measured Ø7.0 heads, so the current source uses Ø8.2 pockets plus 8.4 mm internal-only entry slots. The formerly unsupported 4 mm rear sill is tied into the lower shell by an internal angle beam. The upper shell carries two recessed 70 x 70 mm logo panels using concealed 6 x 3 mm shell magnets opposed by 6 x 1.5 mm panel magnets. The former side antenna docks and their shell bosses are removed; four cellular and two Wi-Fi antennas now mount on six screw-clamped rear bulkheads. The C8 island and closed terminal tunnel move with the complete power compartment to +X; the full-height rear service panel removes around the island. Raised cable-tie bridges preserve a solid box floor, the two APV axes use top-service blind insert pilots, and four wall-tied bosses support the cover. These are mechanical provisions only and do not authorize wiring or energization.

The current joint labels deliberately distinguish **M3x14 base**, **M3x10 Mac-cradle**, hidden underside **M3x14 handle**, recessed low-head **M3x6 router-tray**, **M3x8 service/cover**, hidden **M4x10 cap locks**, and **M4x18 shell-seam** stacks. Physical coupons selected Ø4.2 M3 and Ø5.4 M4 insert pilots. The handle screws pass upward through the detached cap into the full 8 mm feet; the selected dovetails carry vertical cap load while two M4 locks prevent sideways motion. Exact screw heads, engagement, torque, pull-out, and final lengths remain provisional until joint-stack tests pass.

The official router geometry is imported from `reference/0112_RUTM30AMBKX_02.STEP`. The Mac, APV, antennas, C8, extensions, plugs, and cable paths are controlled placeholders; see [assumptions.md](reports/assumptions.md).

## Coordinate system

All dimensions are millimetres.

- Origin: centre of the external footprint on the desk-contact plane.
- +X: right when looking at the front.
- +Y: toward the rear service face.
- +Z: upward.
- Fixed body: approximately `X=-82.5..82.5`, `Y=-82.5..82.5`, `Z=0..280`.
- Equipment positions in `layout.py` are reference-envelope centres.

The principal centres are Mac `(0,-8,41)`, APV `(35,5,103.55)`, and RUTM30 `(0,28,170.5)`. The Mac reference preserves 50 mm overall height while representing the physically observed 8 mm underside drop below its retained square body. Full datums, packaging ranges, and parameter defaults are in [dimensions.md](reports/dimensions.md).

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

The current source registry expects **18 printable definitions**: 14 installed assembly parts plus four reusable/non-installed templates. Regeneration writes:

- one printable-part STEP and one print-oriented STL for each registered definition;
- 21 coupon STEP files and 21 coupon STL files, including retained historical fit articles;
- `complete_assembly.step`, `exploded_assembly.step`, and `packaging_study.step`;
- `component_envelopes.step`, containing non-printable references and keep-outs;
- four deterministic PNG renders; and
- `reports/export_manifest.json`, with the authoritative regenerated paths, sizes, SHA-256 hashes, and design-space STEP bounding boxes.

STEP files remain in assembly coordinates. STL files receive the documented print-orientation transform and are placed on `Z=0`. No 3MF is generated because this export path cannot preserve dependable slicer/process settings.

### macOS Finder model

`exports/interactive/complete_assembly_finder.usdz` is a color, interactive Quick Look model containing all 14 installed printed parts plus equipment and interface-hardware references. Select it in Finder and press Space, or open it directly, to orbit, pan, and zoom. It uses metres-per-unit metadata corresponding to the millimetre CAD model and passes Apple's strict RealityKit USDZ validation.

On macOS with the Apple USD command-line tools available, regenerate it with:

```sh
.venv/bin/python -m deployment_station.quicklook
```

This convenience visualization is generated separately from the fail-gated STEP/STL manifest and is not a manufacturing export.

## Direct versus extended interfaces

| Interface | Decision | CAD implementation | Verification boundary |
| --- | --- | --- | --- |
| Four cellular SMA connections | Rear bulkhead extensions | Four of six Ø6.6 rear holes with thinned 2.0 mm clamping lands; row sequence Mobile / Wi-Fi / Mobile / Mobile / Wi-Fi / Mobile | Exact pigtails, nut torque, strain relief, first bends, and antenna load test pending |
| Two Wi-Fi RP-SMA connections | Rear bulkhead extensions | Two of the same six screw-clamped rear positions; former side docks removed | Exact RP-SMA gender, coax routing, antenna spacing, RF performance, and load test pending |
| External Ethernet | One replaceable extension | One accepted 17 x 14 opening with 27.6 mm mounting pitch directly in the rear panel | Exact screws/locking, latch access, bend space, strain support, and link performance pending |
| Internal Mac Ethernet | Internal patch lead | Placeholder plug volume in low-voltage lane | Consumes one native router port; actual lead fit pending |
| Mac HDMI | Replaceable extension | Accepted V7 mount relocated to `(-6,108)`—60 mm from the right and 90 mm from the bottom when viewed from behind—with a 13 mm shelf and two top-down blind M3 mounts | Cable bend, strain support, access, and functional test pending |
| Two Mac USB-C | Replaceable extensions | Accepted V7 mounts relocated to `(-24,68)` and `(-41,78)`—rear-view right/bottom offsets `(42,50)` and `(25,60)`—mounted from inside to 6 mm blind-boss bridges with sharp 14 x 6.5 x 2.5 mm reliefs | Cable bend, strain support, access, and functional test pending |
| Mac AC | Internal only | Diameter-12 gland and continuous stepped 6 mm reserved envelope from the covered zone toward the provisional Mac connector | This is packaging space, not a selected conduit or completed branch architecture; qualified design remains PENDING |
| Candidate measured C8 | Direct component | Accepted 21 x 12.5 opening on the fixed inlet island at `(38,116)` with two full-depth Ø4.2 M3 insert pockets, integral with the relocated closed compartment | Insert installation, shroud, wiring, and electrical review pending |
| Mac power button | Direct mechanical reach | Continuous rear-left/underside finger path; no Mac modification | Handedness corrected by full-cradle trial; physical ergonomics/guarding cycles pending |

The two native router ports now have a defined one-to-one allocation: one internal Mac link and one external Ethernet extension. No second external Ethernet opening is modeled.

## Source map

| Module | Responsibility |
| --- | --- |
| `parameters.py`, `layout.py` | Defaults, datums, and packaging locations |
| `components.py` | Official router import; controlled equipment, hardware, cable, and removal placeholders |
| `base.py`, `mac_mount.py` | Base, intake/button path, three 2 mm pad positions in 1 mm seats, four clip/cam retainers, two bottom release rails, and shell-fastened cradle ears |
| `shell.py` | Split shell, reinforced rear sill, three seam keys, six hidden internal seam joints/belts, magnetic logo receivers, dovetail cap rails, equipment supports, and handle load path |
| `router_tray.py`, `rear_panel.py` | Router support, physically corrected side/top fit, four compliant pads, adjustable screw-mounted rear stops, and a full-height one-piece rear panel with six direct RF bulkheads and the measured extension mounts |
| `power_compartment.py` | Mechanical APV/mains enclosure, fixed C8 island/tunnel, sealed-floor tie bridges, top-service APV pilots, wall-tied upper cover bosses, four verified shell-mount access corridors, exits, and cover |
| `handle.py` | Sliding dovetail cap, two concealed anti-slide locks, structural beams, underside four-screw handle feet, and mounting coupon |
| `wifi_dock.py`, `logo_panel.py` | Legacy dock coupon source retained for traceability; production magnet-retained logo panels |
| `coupons.py` | High-risk physical-fit articles, including the original calibration set and four measured v4 interface coupons |
| `prototype_v4.py` | Coupon-stage measured Ethernet/HDMI/USB-C/C8 interfaces, RF bulkhead wall trials, blind logo magnets, and concealed cap dovetails for the pending v4 redesign |
| `assembly.py`, `render.py` | Part registry, assemblies, non-printable references, and views |
| `validation.py`, `export.py` | Fail-closed computational checks and reproducible outputs |

## Documentation

- [dimensions.md](reports/dimensions.md) — envelope, packaging, part envelopes, and parameter reference.
- [interface_decisions.md](reports/interface_decisions.md) — direct/extension decisions and the one-internal/one-external Ethernet allocation.
- [bom.md](reports/bom.md) — printed parts, equipment, provisional hardware, screws, and inserts.
- [assembly.md](reports/assembly.md) — de-energized assembly, service, and load-path sequence.
- [print_plan.md](reports/print_plan.md) — orientations, starting process, and coupon order.
- [assumptions.md](reports/assumptions.md) — evidence hierarchy, unresolved measurements, and deviations.
- [requirements_traceability.md](reports/requirements_traceability.md) — handoff IDs mapped to modules, tests, and closure evidence.
- [known_limitations.md](reports/known_limitations.md) — release blockers and explicit electrical boundary.
- [validation_results.md](reports/validation_results.md) — generated computational record.
- [coupon_results_2026-09-10.md](reports/coupon_results_2026-09-10.md) — physical coupon observations, revisions, and selected v2 fits.

## Release boundary

The repository demonstrates a coherent, printable mechanical prototype concept. Before a complete prototype is frozen, it still requires the actual devices, extensions, cables, inserts, pads, and connector hardware to be measured and dry-fitted and physical coupons and service trials to pass. The Mac-AC envelope is only a reserved path, and the branch hardware/topology, APV lead bends, protective separation, restraint, and materials are not released. Before carrying or energizing, it additionally requires load/cycle and thermal tests, a complete competent electrical design, and qualified inspection/testing. Supplier availability and lifecycle status—including the specified C8 inlet—must be reconfirmed before procurement.
