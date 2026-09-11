# Assumptions, unresolved measurements, and deviations

A named CAD parameter is not automatically a verified physical dimension. This report distinguishes imported authority, controlled placeholders, and unresolved hardware.

## Evidence hierarchy

| Item | CAD source | Confidence and boundary |
| --- | --- | --- |
| RUTM30 body | Official Teltonika `reference/0112_RUTM30AMBKX_02.STEP`, AP214, rotated into station axes | **Official imported geometry.** Its station-axis bbox is 100 x 93.7 x 30. Production-unit and connected-hardware checks still apply. |
| RUTM30 connector centres | Official spatial-drawing values encoded analytically | **Controlled reference.** Six RF centres use 14.8 pitch and official ordering; two native Ethernet centres are also represented. Plug/hand/cable envelopes are provisional. |
| Mac mini M4 | 127 x 127 x 50 overall; revised reference separates a 42 mm retained square body from an 8 mm central underside drop | **Physically informed controlled placeholder.** A full-cradle trial selected rear-left button handedness, 0.30 mm side clearance, 8 mm-lower hooks, and a Ø112 opening. No Mac STEP/scan is claimed; exact underside surfaces, contact lands, ports, and overmoulds still require measurement. |
| APV-35-36 | 84 x 57 x 29.5 case plus supplier-drawing lead and lug data | **Controlled placeholder.** Supplied datasheet gives 150 +/-10 mm 18 AWG leads, diameter-3.6 fixing holes, and +/-1 mm case-drawing tolerance. No official APV STEP is claimed. |
| Schurter 6160.0021 | Parametric radiused profile and reference flange from handoff drawing values | **Controlled placeholder.** Actual inlet, current drawing/revision, lifecycle status, mounting method, and terminal envelope are not official imported B-rep data. |
| Two Wi-Fi antennas | 91 length, 30 base, and tapered sections based on owner photographs | **Photo-derived placeholder.** Perspective-limited photographs are not metrology. |
| PR1KC540 leads | Six direct RF access corridors; no antenna-body dock | **System placeholder.** Actual mating bodies, cable construction, bend limit, liner, and support point are not measured. |
| HDMI, USB-C, Ethernet, Mac AC, router DC, and internal power hardware | Simple extension/plug/service volumes; provisional two-hole M3 extension patterns; one stepped Mac-AC reservation | **Controlled placeholders.** Exact part numbers, vendor flange patterns, branch hardware, and tolerance-complete geometry are not selected. |

Reference solids are non-printable. Only the RUTM30 is backed by the supplied official STEP; the Mac, APV, antennas, C8, extensions, plugs, and cable paths must not be described as exact models.

## Unresolved measurement and test register

| Gate / ID | Required measurement or decision | Current concept value | Closure evidence |
| --- | --- | --- | --- |
| `OPEN-02` | Both Wi-Fi antennas: length, hub/stem/taper, radial exit, surface/compressibility, and safe clip lands | 91 long; 30 base; 12 stem; 0.50 radial allowance selected by the three-marker Ø31 coupon | Confirm both antennas, then cable/carry/shake and 20-cycle test |
| `OPEN-03` | All six installed RF couplings, finger/tool envelope, first bend, liner, and nearby support | diameter-14 x 36 corridors; 88 x 30 opening; provisional 20 bend radius | Fully connected coupon/bezel mock-up and repeated six-port connect/disconnect test |
| `OPEN-04` | Mac button centre/diameter/travel, feet, intake-slot limits, acceptable support lands, clip/cam contact regions, release access, port centres, and actual overmoulds | Rear-left 13.5 edge offsets; diameter-11 button; Ø112 cradle opening; 0.30 side gap; 42 mm retained-body height; three 2 mm pads in 1 mm seats; four Z-clips and two linked release rails | Reprint corrected cradle, then record contact map, fully cabled fit, 20 button operations, and clip/release/shake cycles |
| APV fit | Production case/lugs, supplier coordinate pattern, lead exits, bend space, case-temperature point, and fasteners | 84 x 57 x 29.5; longitudinal hole-coordinate delta 98.6; two diameter-3.6 top-service axes; 3 mm blind insert pilots; 150 +/-10 leads | Actual part inspection, selected insert/fastener stack, and dry assembly in the closed box |
| `PWR-07` | Exact C8 profile/flange, fixing condition, tolerance, allowed panel thickness, screw/nut access, terminals, and shroud | 20.6 x 11.8 +0.20; 28 pitch; diameter-3.2 holes | Current supplier drawing plus coupon with actual part |
| Procurement | Availability and lifecycle status of Schurter 6160.0021 | Handoff-specified part; phase-out risk flagged | Supplier confirmation or approved exact substitute followed by geometry and electrical re-review |
| `MEC-13` | Exact HDMI, USB-C, both Ethernet extensions/patches and flange patterns, Mac AC, router DC, coax, grommets, and liner | Generic bodies; provisional vertical-20 and horizontal-27 two-hole M3 flange patterns; recorded 18 non-coax and 20 coax bend assumptions | Fully wired, unenergized mock-up with accessible releases and no pinching |
| Mac-AC branch | Complete branch topology, junction/protection volume, conduit/barrier, restraint, gland, cable OD, and Mac connector | Diameter-12 floor gland and a continuous stepped 6 mm **reserved envelope** from power box toward the provisional Mac connector | Competent electrical architecture, exact parts, updated CAD, unenergized fit, and qualified inspection/tests before energization |
| Router support | Actual underside safe lands, pad material/compression, fastener-head clearance, and removal force | Four 8 x 16 lands; 1.3 mm pad template with 0.4 mm nominal compression; diameter-6.2 x 1.8 low-head recess | Actual router inspection, four-pad fit/rock/thermal check, fastener coupon, and repeated -Y insertion/+Y removal |
| Insert release | Chosen M3/M4 insert OD/length/process, pull-out, torque, and parent-material compatibility | diameter-4.2/5.6 pilots; 5.5 depth | Supplier data and coupon in every final material/orientation |
| `OPEN-15` | Complete assembled mass and approved transport factor | 1.8 kg provisional; 2x test target | Weighed complete prototype and controlled load/time record |
| `OPEN-16` | Tamper/security policy | Rear/underside tool screws; no lock | Owner/service approval |
| `OPEN-18` | Logo appearance, flexure fit, color/method, rattle, and durability | 70 square; 0.25/side receiver clearance; four cantilever studs | Owner approval and at least 20 install/removal cycles |
| Thermal release | Mac/router/APV temperatures and APV derating under representative loads | Passive intake/high exhaust; no fan | Instrumented comparison to agreed open-air baseline |

## Packaging assumptions

- The selected 165 x 165 x 280 package is fixed. `proportionally_scaled()` rejects any other width because equipment and interface datums are absolute.
- The Mac support plane at `Z=24` is 10 above the nominal base top at `Z=14`.
- Router placement at `(0,28,170.5)` prioritizes direct access to the six native RF connectors; its native Ethernet face is consequently opposite the rear service face.
- The APV/mains box is a mechanical containment concept. Its 4 mm keep-out expansion is not a creepage, clearance, insulation, flame, or certification value.
- Cable radii are recorded planning values; the current model uses simplified straight volumes plus a stepped Mac-AC reserved envelope rather than tolerance-complete cables or a released protective conduit.
- The three 2 mm Mac base pads occupy 1 mm-deep seats and avoid the Ø112 underside ring and corrected rear-left button corner. The first full-cradle trial found the original 1.5 mm side gap loose and the hooks 8 mm high; production geometry now uses 0.30 mm clearance and the physically selected lower elevation. Final material, compression, preload, force, contact map, scratch protection, shake behavior, and fatigue remain open.
- The router rests conceptually on four compliant-pad lands clear of modeled vents and recessed low-head screw heads. Pad material, true safe contact zones, compression, temperature effect, and rocking remain open.
- Wi-Fi dock material is flush/recessed inside the fixed 165 mm envelope. Antennas and their connected cables are excluded from that envelope.
- The 116 mm base opening and rear slots are geometric air paths, not airflow or temperature evidence.

## Deviations and implementation choices

| Requirement / target | Decision | Rationale | State |
| --- | --- | --- | --- |
| Direct ports preferred (`MAC-13`, `NET-03`, section 6.1) | HDMI, USB-C, and both Ethernet connections use replaceable extension positions | Mac port/plug data are unverified; router Ethernet is opposite the directly exposed RF face | Permitted by handoff rule; exact hardware and functional tests pending |
| Six direct RF connections (`NET-06`, `NET-12`) | One common 88 x 30 radiused opening instead of six diameter-14 holes | At 14.8 pitch, separate holes leave only 0.8 webs, below the 2.4 controlled wall | Computational span check passes; physical access/liner/support pending; dedicated coupon now exported |
| Two external Ethernet links plus internal link (`NET-03`, `NET-04`) | Two external positions are retained, but no third native link exists | Two-port router cannot supply three simultaneous connections | **Unresolved warning; owner-approved topology required** |
| Resizing (`ENV-03`) | Non-165 requests are rejected rather than partially scaled | Hardware, ports, splits, clearances, and load paths need coordinated repack, not geometric multiplication | Safer tool behavior; a new size is a new verified configuration |
| Logo retaining concept (`LOGO-06`) | Two outward-accessible M3x8 screws and webbed blind inserts per panel | Unambiguous assembly path and independently replaceable panels | Geometry/length stack pass computationally; torque/insert/cycle/rattle tests pending |
| Handle (`HDL-07`, `HDL-08`) | Four externally accessible low-head M3x10 screws, two per 5 mm foot, into full-depth cap bosses/pads | Direct redundant load path with no unreachable snap motion; screw heads retain full foot bearing thickness | Geometry/length stack and 4x target pass computationally; insert/material/creep/proof tests pending |
| Routine rear service (`SVC-03`) | Fixed C8 island/tunnel belongs to power box; panel removes around it | Keeps mechanical mains boundary in place during cable service | Geometry implemented; touch-safe/electrical proof pending |
| APV and cover service | Two blind top-service insert pilots and four wall-tied full-height cover columns | APV/cover screws are accessible from above after routine shell mounting; no dependence on lower-shell rail access | Geometry implemented; exact insert, screw, washer, torque, pull-out, material, and electrical acceptance pending |
| Power-cable restraint | Two raised internal bridges replace floor-through tie slots | Preserves a continuous nominal floor beneath the strap tunnels | Geometry implemented; final conductor restraint, abrasion, spacing, and electrical suitability pending |
| Mac-AC routing | Continuous stepped 6 mm reserved envelope from the relocated diameter-12 gland toward the provisional Mac connector | Records a collision-free packaging route without pretending the branch architecture is solved | Geometry-only reservation; conduit/barrier, branch hardware/topology, protection, and qualified proof pending |
| Refined exterior and labels | White/dark palette and restrained openings modeled; final labels absent | Functional packaging precedes graphic/process freeze | Owner appearance and labeling review pending |
| Optional 3MF | STEP and print-oriented STL only | Toolchain does not reliably preserve slicer process settings | 3MF was optional; no functional requirement lost |

No departure from the square 165 x 165 footprint or approximately 1:1:1.70 fixed-envelope ratio has been taken.

## Explicit 230 V review boundary

The CAD creates a closed mechanical box/cover, fixed inlet island/tunnel, raised tie bridges over a nominally sealed floor, top-service APV pilots, full-height cover columns, nominal openings, and modeled routing reservations. It does **not** define or validate:

- the complete single-inlet branch topology to the Mac and APV, or the junction/protection volume needed to implement it;
- over-current/branch protection, fuse selection/location, switching, or fault behavior;
- conductors, connectors, terminations, splices, ferrules, insulation, sleeving, or color coding;
- creepage, clearance, protective separation, reinforced/double insulation, fire enclosure, material flammability, or touch-safe probe performance;
- inlet installation/rating, cord anchorage, terminal shrouding, conductor restraint, protective conduit/barriers, strain relief, bushings, or abrasion protection;
- temperature rise, derating, abnormal operation, EMC, dielectric strength, insulation resistance, earth arrangements, or Swiss/EU conformity; or
- an authorized assembly, inspection, test, or service procedure.

The APV datasheet and its component approvals do not certify the integrated station. Before any energization, a competent electrical designer must define the architecture and applicable requirements, and a qualified person must build, inspect, and test the complete unit. Any required fuse remains internal and service-only; no external switch or external fuse holder is modeled.
