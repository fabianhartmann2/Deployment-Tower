# Assumptions, unresolved measurements, and deviations

A named CAD parameter is not automatically a verified physical dimension. This report distinguishes imported authority, controlled placeholders, and unresolved hardware.

## October v4 measured-interface inputs

Owner-supplied measurements and photographs now define a coupon-stage Ethernet adapter (17 x 14 opening, 27.6 mm two-hole pitch, 22 x 23 x 42 mm inner body), HDMI A6-A8T module (16 x 6 opening, 27 mm pitch, 19 x 13 x 13 mm body and 45 mm bend allowance), two USB-C T9B-T8T-NC 20P modules (10 x 4 visible opening, 12 x 5 x 1.75 mm reinforcement shell, 19 mm oval-slot pitch, 14.2 x 2 mm ribbon), and a candidate marketplace C8 inlet (21 x 12.5 opening, 29 mm pitch, 35.5 x 15.1 mm first inner envelope). These are physical prototype inputs, not supplier-controlled drawings.

The supplied Wi-Fi pigtail is RP-SMA female to RP-SMA male with a nominal 6.5 mm bulkhead hole, 8 mm hex, and 2.1 mm inner bearing depth. The four mobile connections still require mechanically checked SMA—not RP-SMA—bulkheads/pigtails. The coupon therefore explores diameter and local panel thickness without treating the two connector families as electrically interchangeable.

The Type-15 Wi-Fi antennas are recorded as 170 mm long and 90-degree adjustable. Their exact hinge/base sweep remains unverified because the marketplace pages could not be accessed by the available browser tools. The DC/DC converter is recorded only as a 71 x 36 x 25 mm, 24 V/1 A envelope; connector positions, retention, heat dissipation, electrical purpose, and suitability remain unresolved.

The approved v4 logo direction retains the existing recessed 70 mm receiver as the sole positional feature and removes the finger scallop. The original shell-magnet/bonded-steel concept passed pocket fit but is superseded for testing by 3 mm shell magnets opposed by 1.5 mm magnets in the removable panel; pull force, polarity, adhesive, and cycles remain pending. The approved cap/handle direction uses underside handle screws and a concealed sliding dovetail connection with a separate positive lock. The physical v2 coupon selected 0.10 mm clearance per side; 0.05 mm was already too tight over the short coupon and is rejected for the full rail. Full-length fit and the final positive lock/load path remain pending.

## Evidence hierarchy

| Item | CAD source | Confidence and boundary |
| --- | --- | --- |
| RUTM30 body | Official Teltonika `reference/0112_RUTM30AMBKX_02.STEP`, AP214, rotated into station axes | **Official imported geometry.** Its station-axis bbox is 100 x 93.7 x 30. Production-unit and connected-hardware checks still apply. |
| RUTM30 connector centres | Official spatial-drawing values encoded analytically | **Controlled reference.** Six RF centres use 14.8 pitch and official ordering; two native Ethernet centres are also represented. Plug/hand/cable envelopes are provisional. |
| Mac mini M4 | 127 x 127 x 50 overall; revised reference separates a 42 mm retained square body from an 8 mm central underside drop | **Physically informed controlled placeholder.** A full-cradle trial selected rear-left button handedness, 0.30 mm side clearance, 8 mm-lower hooks, and a Ø112 opening. No Mac STEP/scan is claimed; exact underside surfaces, contact lands, ports, and overmoulds still require measurement. |
| APV-35-36 | 84 x 57 x 29.5 case plus supplier-drawing lead and lug data | **Controlled placeholder.** Supplied datasheet gives 150 +/-10 mm 18 AWG leads, diameter-3.6 fixing holes, and +/-1 mm case-drawing tolerance. No official APV STEP is claimed. |
| Schurter 6160.0021 | Parametric radiused profile and reference flange from handoff drawing values | **Controlled placeholder.** Actual inlet, current drawing/revision, lifecycle status, mounting method, and terminal envelope are not official imported B-rep data. |
| Two Type-15 Wi-Fi antennas | Owner-specified 170 mm length and 90-degree hinge | **Controlled marketplace input.** Exact hinge/base sweep, gender, mass, RF data, and bending load remain unverified. |
| RF pigtails/bulkheads | Six Ø6.6 rear bulkhead positions; four SMA mobile and two RP-SMA Wi-Fi | **Measured concept input.** Actual pigtail lengths, connector genders, cable construction, bend limit, torque, and support remain unverified. |
| HDMI, dual USB-C, external Ethernet, C8, Mac AC, router DC, and internal power hardware | Accepted V7 mechanical openings/mounts plus simplified cable/service volumes and one stepped Mac-AC reservation | **Physically informed placeholders.** Coupon fit is recorded; functional capability, full tolerance, cable routing, strain relief, and electrical suitability are not established. |

Reference solids are non-printable. Only the RUTM30 is backed by the supplied official STEP; the Mac, APV, antennas, C8, extensions, plugs, and cable paths must not be described as exact models.

## Unresolved measurement and test register

| Gate / ID | Required measurement or decision | Current concept value | Closure evidence |
| --- | --- | --- | --- |
| `OPEN-02` | Two Type-15 Wi-Fi antennas, RP-SMA gender, hinge sweep, spacing, torque, handling load, and RF performance | 170 long; two rear bulkheads in the six-port row | Confirm exact antennas/pigtails, then torque, shake, interference, RF, and 20-cycle tests |
| `OPEN-03` | All six RF bulkheads/pigtails, washer/nut torque, anti-rotation, strain support, first bend, and service | Direct one-piece-panel Ø6.6 holes at 20 pitch; 2.0 mm clamping lands; provisional 20 bend radius | Fully connected rear-panel mock-up and repeated six-port/antenna service test |
| `OPEN-04` | Mac button centre/diameter/travel, feet, intake-slot limits, acceptable support lands, clip/cam contact regions, release access, port centres, and actual overmoulds | Rear-left 13.5 edge offsets; diameter-11 button; Ø112 cradle opening; 0.30 side gap; 42 mm retained-body height; three 2 mm pads in 1 mm seats; four Z-clips and two linked release rails | Reprint corrected cradle, then record contact map, fully cabled fit, 20 button operations, and clip/release/shake cycles |
| APV fit | Production case/lugs, supplier coordinate pattern, lead exits, bend space, case-temperature point, and fasteners | 84 x 57 x 29.5; longitudinal hole-coordinate delta 98.6; two diameter-3.6 top-service axes; 3 mm blind insert pilots; 150 +/-10 leads | Actual part inspection, selected insert/fastener stack, and dry assembly in the closed box |
| `PWR-07` | Exact C8 profile/flange, fixing condition, tolerance, allowed panel thickness, screw access, terminals, and shroud | Accepted 21 x 12.5 +0.40; 30 pitch; two full-depth Ø4.2 M3 heat-set-insert pockets | V7 mechanical pass, production insert trial, and qualified installation/shroud/electrical review |
| Procurement | Availability and lifecycle status of Schurter 6160.0021 | Handoff-specified part; phase-out risk flagged | Supplier confirmation or approved exact substitute followed by geometry and electrical re-review |
| `MEC-13` | Accepted HDMI, dual USB-C, single external Ethernet, internal Mac Ethernet, Mac AC, router DC, coax, grommets, and strain support | V7-derived rear-I/O mounts; one direct rear-panel Ethernet flange; recorded 18 non-coax and 20 coax bend assumptions | Fully wired, unenergized mock-up with accessible releases and no pinching |
| Mac-AC branch | Complete branch topology, junction/protection volume, conduit/barrier, restraint, gland, cable OD, and Mac connector | Diameter-12 floor gland and a continuous stepped 6 mm **reserved envelope** from power box toward the provisional Mac connector | Competent electrical architecture, exact parts, updated CAD, unenergized fit, and qualified inspection/tests before energization |
| Router support | Actual underside safe lands, pad material/compression, fastener-head clearance, and removal force | Four 8 x 16 lands; 1.3 mm pads with 0.4 mm nominal compression; physical 3.0 mm heads over Ø6.2 x 2.2 recesses; guides inset 1.0; rigid slotted rear stops | Reprint; four-pad fit/rock/scratch/thermal check; adjust and cycle both M3x8 stops; repeated -Y insertion/+Y removal |
| Insert release | Chosen M3/M4 insert OD/length/process, pull-out, torque, and parent-material compatibility | physically selected diameter-4.2/5.4 pilots; 5.5 depth | Supplier data and coupon in every final material/orientation |
| `OPEN-15` | Complete assembled mass and approved transport factor | 1.8 kg provisional; 2x test target | Weighed complete prototype and controlled load/time record |
| `OPEN-16` | Tamper/security policy | Rear/underside tool screws; no lock | Owner/service approval |
| `OPEN-18` | Logo appearance, magnet adhesive/polarity/pull force, color/method, rattle, and durability | 70 square; 0.25/side recess clearance; two 6 x 3 plus two 6 x 1.5 magnets per side | Owner approval and at least 20 install/removal cycles |
| Thermal release | Mac/router/APV temperatures and APV derating under representative loads | Passive intake/high exhaust; no fan | Instrumented comparison to agreed open-air baseline |

## Packaging assumptions

- The selected 165 x 165 x 280 package is fixed. `proportionally_scaled()` rejects any other width because equipment and interface datums are absolute.
- The Mac support plane at `Z=24` is 10 above the nominal base top at `Z=14`.
- Router placement at `(0,28,170.5)` prioritizes direct access to the six native RF connectors; its native Ethernet face is consequently opposite the rear service face.
- The APV/mains box is a mechanical containment concept. Its 4 mm keep-out expansion is not a creepage, clearance, insulation, flame, or certification value.
- Cable radii are recorded planning values; the current model uses simplified straight volumes plus a stepped Mac-AC reserved envelope rather than tolerance-complete cables or a released protective conduit.
- The three 2 mm Mac base pads occupy 1 mm-deep seats and avoid the Ø112 underside ring and corrected rear-left button corner. The first full-cradle trial found the original 1.5 mm side gap loose and the hooks 8 mm high; production geometry now uses 0.30 mm clearance and the physically selected lower elevation. Final material, compression, preload, force, contact map, scratch protection, shake behavior, and fatigue remain open.
- The router rests conceptually on four compliant-pad lands clear of modeled vents and the revised deeper M3x6 head recesses. A physical trial found the first tray loose, its 3 mm screw heads contacted the router, and a rear flexure broke 5 mm behind the chassis. Current geometry responds with deeper recesses, inward/lowered guides, and two adjustable screw-mounted rear stops; the revision remains physically unverified.
- The old side Wi-Fi docks are removed. Rear-mounted antennas and their connected pigtails are excluded from the fixed 165 mm body envelope.
- The 116 mm base opening and rear slots are geometric air paths, not airflow or temperature evidence.

## Deviations and implementation choices

| Requirement / target | Decision | Rationale | State |
| --- | --- | --- | --- |
| Direct ports preferred (`MAC-13`, `NET-03`, section 6.1) | HDMI, both USB-C connections, and one external Ethernet use replaceable extensions; the Mac uses the router's other Ethernet port internally | Mac port/plug data are unverified; router Ethernet is opposite the directly exposed RF face | Two router ports now have a resolved one-to-one allocation; exact hardware and functional tests pending |
| Six RF connections (`NET-06`, `NET-12`) | Six panel bulkheads at 20 mm pitch instead of the former common window | Permits standard screw-on external antennas and serviceable short internal pigtails while retaining 2.0 mm clamping lands | Ø6.6/2.0 geometry checked; exact connectors, torque, strain relief, routing, and RF tests pending |
| One external Ethernet plus internal link (`NET-03`, `NET-04`) | One external rear-panel extension and one internal Mac patch lead use the two native router ports | Matches the available two-port router without assuming a switch or third link | Allocation resolved in CAD; actual leads, bends, latch access, and link tests pending |
| Resizing (`ENV-03`) | Non-165 requests are rejected rather than partially scaled | Hardware, ports, splits, clearances, and load paths need coordinated repack, not geometric multiplication | Safer tool behavior; a new size is a new verified configuration |
| Logo retaining concept (`LOGO-06`) | Two concealed magnet pairs per recessed panel; 3 mm shell magnets oppose 1.5 mm panel magnets | Clean exterior with the recess providing position and no doubled 3 mm magnet stack | Pocket/skin/interference checks pass; polarity, adhesive, pull force, cycle/rattle tests pending |
| Handle (`HDL-07`, `HDL-08`) | Continuous Ø22 rounded grip, spherical shoulders, Ø24 round legs, Ø32 flared roots, and radiused 8 mm feet; four underside M3x14 screws; detached cap slides onto two selected dovetails and uses two hidden M4x10 locks | Ergonomic external contact surfaces, clean top face, and a direct load path into shell crossbars; dovetails carry vertical load | Geometry/length/dovetail checks and 4x target pass computationally; insert/material/full-length fit/creep/proof tests pending |
| Routine rear service (`SVC-03`) | Fixed C8 island/tunnel belongs to power box; panel removes around it | Keeps mechanical mains boundary in place during cable service | Geometry implemented; touch-safe/electrical proof pending |
| APV and cover service | Two blind top-service insert pilots and four wall-tied 12 mm upper cover bosses | APV/cover screws are accessible from above after routine shell mounting; the upper bosses do not obstruct the four floor fasteners | Geometry implemented; exact insert, screw, washer, torque, pull-out, material, and electrical acceptance pending |
| Power-cable restraint | Two raised internal bridges replace floor-through tie slots | Preserves a continuous nominal floor beneath the strap tunnels | Geometry implemented; final conductor restraint, abrasion, spacing, and electrical suitability pending |
| Mac-AC routing | Continuous stepped 6 mm reserved envelope from the relocated diameter-12 gland toward the provisional Mac connector | Records a collision-free packaging route without pretending the branch architecture is solved | Geometry-only reservation; conduit/barrier, branch hardware/topology, protection, and qualified proof pending |
| Refined exterior and labels | White/dark palette and restrained openings modeled; final labels absent | Functional packaging precedes graphic/process freeze | Owner appearance and labeling review pending |
| Optional 3MF | STEP and print-oriented STL only | Toolchain does not reliably preserve slicer process settings | 3MF was optional; no functional requirement lost |

No departure from the square 165 x 165 footprint or approximately 1:1:1.70 fixed-envelope ratio has been taken.

## Explicit 230 V review boundary

The CAD creates a closed mechanical box/cover, fixed inlet island/tunnel, raised tie bridges over a nominally sealed floor, top-service APV pilots, wall-tied upper cover bosses, open shell-mount screw corridors, nominal openings, and modeled routing reservations. It does **not** define or validate:

- the complete single-inlet branch topology to the Mac and APV, or the junction/protection volume needed to implement it;
- over-current/branch protection, fuse selection/location, switching, or fault behavior;
- conductors, connectors, terminations, splices, ferrules, insulation, sleeving, or color coding;
- creepage, clearance, protective separation, reinforced/double insulation, fire enclosure, material flammability, or touch-safe probe performance;
- inlet installation/rating, cord anchorage, terminal shrouding, conductor restraint, protective conduit/barriers, strain relief, bushings, or abrasion protection;
- temperature rise, derating, abnormal operation, EMC, dielectric strength, insulation resistance, earth arrangements, or Swiss/EU conformity; or
- an authorized assembly, inspection, test, or service procedure.

The APV datasheet and its component approvals do not certify the integrated station. Before any energization, a competent electrical designer must define the architecture and applicable requirements, and a qualified person must build, inspect, and test the complete unit. Any required fuse remains internal and service-only; no external switch or external fuse holder is modeled.
