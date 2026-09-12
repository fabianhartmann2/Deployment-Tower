# Known limitations and release blockers

This is editable concept/prototype CAD. It must not be represented as production-ready, safe to carry, or safe to energize.

## Current limitations

1. **Ethernet concurrency is unresolved.** The two-port RUTM30 cannot simultaneously serve two external wired links and the internal Mac link without an approved topology change.
2. **Exact extensions are not selected.** HDMI, USB-C, and both RJ45 features have generic positions/reference bodies and explicit provisional two-hole M3 flange patterns, not vendor-approved mounts. Capability, exact hole pattern, fasteners, anti-rotation, insertion load, internal leads, and replacement remain unverified.
3. **Only the router has official imported CAD.** `reference/0112_RUTM30AMBKX_02.STEP` is official Teltonika geometry. The Mac, APV, antennas, C8, plugs, extensions, and cables are controlled placeholders.
4. **Physical corrections are not a validated scan.** The full Mac-cradle trial selected rear-left button handedness, 0.30 mm side clearance, an 8 mm lower retained-body/hook datum, and a Ø112 cradle opening. Exact Mac underside surfaces, feet, intake slots, support lands, port centres/overmoulds, antenna bodies, APV production dimensions/lugs/leads, and the inlet still require measured verification.
5. **The specified C8 has procurement risk.** Schurter 6160.0021 availability and phase-out/lifecycle status must be confirmed. Any substitute requires dimensional, mounting, terminal, ratings, and electrical re-review—not a silent part-number swap.
6. **Real cable fit is unknown.** The final plug overmoulds, release tabs, bend limits, service loops, coax liner/support, router DC path, and all simultaneous connections have not been mocked up. The stepped 6 mm Mac-AC solid is only a reserved corridor; it is not a selected protective conduit and does not include branch/protection hardware volume.
7. **RF access is only geometric.** The 88 x 30 opening spans all six official centres, but real coupling nuts, hand/tool access, first bends, edge protection, cable support, and RF performance are pending.
8. **Printed mechanisms are not durability-qualified.** The revised rear-panel coupon and three-marker Ø31.0 mm Wi-Fi capture were reported to fit. The four Mac clip/cams and two linked bottom-release rails, rounded-nose Wi-Fi clips, bezel hooks, router latches, panel fits, and inserts still require material-, orientation-, force-, scratch-, conditioning-, carry-, and cycle-specific tests. The original Wi-Fi coupon was physically impossible for the measured Ø30 mm hub and remains withdrawn. The handle and logo interfaces are screw-mounted but their printed bosses and inserts still require the same physical discipline.
9. **Mating supports exist but lack physical proof.** Paired shell fasteners/supports are modeled for the cradle, power box, router tray, six-point hidden split-shell seam, cap, handle, logo panels, rear panel, and docks. The six seam heads sit in internal diameter-7.6 x 3.2 pockets reached by long drivers from the open top; this requires a verified low-head M4x18 head envelope and assembly before cap/router installation. Current stack labels are M3x14 base, M3x10 cradle/handle, low-head M3x6 router tray, M3x8 logo/service/cover, and M4x18 cap/seam; M4 pilot selection, actual heads, bottoming, insert pull-out/torque, accessibility, wear, and service cycles remain open.
10. **Compliant supports are provisional.** Three 2 mm Mac pads sit in 1 mm seats, and four 1.3 mm router pads sit on printed lands clear of modeled vents and low-head recesses. Actual safe contact regions, material compatibility, compression, rocking, heat, wear, and retention are unverified.
11. **There is no structural rating.** The four-screw handle check verifies geometry and a 4x proof-load target only; it is not FEA or a capacity calculation. Insert pull-out, unequal screw loading, strength, layer adhesion, safe working load, fatigue, creep, impact, and vehicle vibration are untested.
12. **Thermal behavior is unknown.** Passive openings exist, but Mac, router, APV, printed material, pads, cables, and enclosure temperatures; APV derating; throttling; and long-duration/abnormal behavior require component-specific testing.
13. **Electrical construction is unresolved.** Raised tie bridges, blind APV insert pods, upper wall-tied cover bosses, the fixed inlet island, and the closed box are mechanical features—not proof of safe terminals, wiring, branch topology/protection, separation, flammability, touch safety, or compliance.
14. **No ingress or drop rating is intended.** Scope is dry indoor operation and careful hand/vehicle transport only.
15. **Cosmetics and markings are not frozen.** Matte finish, seams, color matching, port/safety labels, logo method, and support-free surface quality need owner and process review.
16. **Non-default scaling is not released.** The API intentionally rejects widths other than 165 because device and hardware interfaces cannot be safely scaled proportionally.
17. **3MF is absent.** STEP and print-oriented STL are authoritative exports; slicer/process settings must be managed separately.
18. **Some parameters remain planning/reserved values.** Cable radii, generic snap allowance, some antenna/handle/logo legacy values, Mac-AC route width, and Wi-Fi mouth-angle target are not all release constraints. Parameter presence is not implementation proof.

## Computational-validation boundary

Use the freshly regenerated [validation_results.md](validation_results.md) and `validation.json` for authoritative counts. This narrative intentionally does not repeat pre-regeneration totals. The automated suite is designed to check:

- square footprint, ratio, and fixed external bbox;
- validity, connected-solid state, and orientable 256 mm bbox for every printable part;
- every pair among the 15 installed printed parts using bounding-box screening and OpenCascade intersection volume, failing closed if an intersection is indeterminate;
- zero unallowlisted installed-part interference; the current screw-mounted design has no intentional overlap allowlist;
- selected equipment-to-shell and equipment-to-mount intersections;
- the Mac intake exclusion and a continuous diameter-11 button-probe swept path through base, cradle, lower shell, and rear panel;
- a continuous reserved Mac-AC packaging corridor and non-overlap of modeled power/low-voltage keep-outs, reported narrowly as packaging evidence rather than electrical-separation proof;
- sealed-floor raised power tie bridges, the full nominal Mac-AC gland aperture, two top-service blind APV pilots, four wall-tied upper cover bosses, and four open shell-mount screw corridors;
- four Mac positive-Z clip/cam interfaces and linked release-rail geometry, plus router support-land/pad and low-head screw clearances;
- rear-panel corridor, rear-sill angle reinforcement, RF-window span, logo face/four screw axes, router provenance, six hidden seam screw/head/driver corridors with closed exterior skin, and the four-screw handle boss/bearing/engagement stack;
- STEP reopen during export; and
- STL watertightness and winding consistency.

These computations do **not** prove:

- physical dimensions after FDM shrinkage, warp, aging, or conditioning;
- fit force, rattle, retention, latch access, cable dress, or real removal paths under wiring/gravity;
- absence of every cable/device collision or minimum thickness at every local section;
- mechanical strength, safe load, fatigue, impact, creep, vibration, or accidental release;
- airflow, component temperatures, material temperature/flame behavior, or APV derating;
- HDMI/USB-C/Ethernet function, signal integrity, RF performance/detuning, or EMC; or
- electrical safety, regulatory compliance, or authorization to energize.

A PASS must be read with its exact check description. The Ethernet topology warning, packaging-only power-route warning, and every PENDING physical/safety item remain open.

## Explicit mains/electrical boundary

The fixed C8 island and tunnel remain attached to the covered power compartment when the routine rear panel is removed. Raised tie bridges preserve the nominal floor, top-service APV pilots avoid lower-rail access, and upper wall-tied bosses mate to the cover without blocking the four shell-mount screws. These improve mechanical service geometry but do not validate a 230 V assembly.

The CAD does not specify or approve topology, branch/over-current protection, fuse selection, conductor sizing/type, connectors, splices, terminations, protective conduit/barriers, insulation systems, creepage/clearance, reinforced/double insulation, flammability/fire containment, temperature class, cord/inlet anchorage, shrouding, strain relief, touch safety, dielectric/insulation tests, EMC, or Swiss/EU conformity. The APV and inlet component ratings cannot be transferred to the integrated product.

Before any energization, a competent electrical designer must define the complete architecture and applicable requirements; a qualified person must assemble, inspect, and test the actual unit. Rear service is de-energized. The inner cover is opened only under that approved procedure. Any required fuse is internal/service-only; no external switch or fuse holder is modeled.

## Release gates

Before freezing a complete mechanical prototype:

- close `OPEN-02`, `OPEN-03`, and `OPEN-04` with measured hardware and the exported coupons;
- confirm APV/C8 production geometry and C8 supplier status;
- select and physically retain exact HDMI, USB-C, Ethernet, grommet, liner, and cable hardware, replacing/approving the provisional flange patterns;
- prove the three Mac base pads, four clip/cams, two bottom release rails, four router pads/lands, and low-head tray screws on actual devices;
- complete the Mac-AC branch architecture, reserve all hardware volume, and replace the route envelope with reviewed conduit/barrier/restraint geometry where required;
- complete a fully wired unenergized fit/service mock-up;
- resolve and implement the Ethernet topology;
- pass insert, panel, button, antenna, RF, logo, bezel, tray, cradle, and handle-mount fit/cycle checks; and
- retain zero computational FAIL results after every parameter change/export.

Before carrying or routine energized use:

- weigh the complete assembly and pass approved handle/anchor load, cycle, creep, and accidental-release tests;
- pass representative and abnormal component-specific thermal tests;
- pass service/removal, cable-abrasion/strain, rattle, and transport checks;
- close `OPEN-13`, `OPEN-15`, `OPEN-16`, and `OPEN-18`; and
- complete documented competent electrical review and qualified inspection/tests on the finished hardware.
