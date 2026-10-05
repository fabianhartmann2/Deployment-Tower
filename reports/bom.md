# Bill of materials

This is a prototype-planning BOM, not a purchasing or production release. Quantities describe current CAD positions; screw length/head, insert series, material grade, and all electrical parts remain subject to physical and competent technical review.

## Printed assembly parts

| Part | Qty | Baseline material | Function / boundary |
| --- | ---: | --- | --- |
| `base` | 1 | Dark ASA | Feet, 116 mm intake, continuous button approach, four screw clearances |
| `mac_cradle` | 1 | ASA | Physically calibrated Ø112 opening, 0.30 mm side gap, three 1 mm pad seats, four 8 mm-lowered positive-Z clip/cams, two extended bottom release rails, four shell-fastened ears |
| `lower_shell` | 1 | Matte white ASA | Base/cradle/power supports, rear bosses, angle-reinforced rear sill, three seam keys, internal U-belt, six hidden structural seam inserts |
| `upper_shell` | 1 | Matte white ASA | Router supports, rear bosses, four blind logo-magnet receivers, two cap dovetail rails/crossbars, internal U-belt, six hidden seam lugs/tool corridors |
| `router_tray` | 1 | ASA | Vented plate, four compliant-pad lands, inward-corrected guides, lowered ledges, front stop, two M3 insert towers, and four deeply recessed shell fasteners; brittle rear clips removed |
| `router_rear_retainer_left`, `router_rear_retainer_right` | 1 each | ASA | Rigid slotted rear-corner stops, installed after the router with one M3x8 screw each; remain outside the SMA envelopes |
| `power_compartment` | 1 | Reviewed flame-/temperature-suitable engineering material | Mechanical APV/mains box, fixed C8 island/tunnel, raised sealed-floor tie bridges, two top-service blind APV pilots, four open lower-shell mounting corridors, four upper wall-tied cover bosses, and exits; not an approved electrical enclosure |
| `power_compartment_cover` | 1 | Same reviewed material | Separate deliberate-access cover with four column-aligned M3 clearance axes |
| `rear_panel` | 1 | Dark ASA | Full-height eight-fastener V7 service face with accepted Ethernet, HDMI, dual USB-C, and relocated C8-island clearance |
| `router_interface_bezel` | 1 | Dark ASA | Replaceable Ethernet/RF insert with six Ø6.6 bulkhead holes, 2.0 mm clamping lands, and four integral hooks |
| `upper_cap` | 1 | Matte white ASA | Selected 0.10 mm/side dovetail grooves, crossmember, bearing pads, underside handle clearances, and two blind M4 lock inserts |
| `removable_handle` | 1 | Candidate ASA/PA-CF after tests | Grip, gusseted legs/ribs, two 42 x 32 x 8 mm feet, four underside M3 insert pockets; no load rating |
| `logo_panel_left`, `logo_panel_right` | 1 each | ASA or approved variant | Recessed 70 mm faces with two blind 6 x 1.5 mm magnet pockets each |

The registry contains **19 printable definitions**: the 15 installed parts above plus `logo_panel_blank_template`, `logo_panel_example_embossed`, `compliant_pad_template`, and `router_compliant_pad_template`. Make three provisional 14.6 x 14.6 x 2 mm Mac pads for the 1 mm seats and four provisional 8 x 16 x 1.3 mm router pads; material, compression, contact compatibility, and release status remain open.

## Fit coupons

| Coupon | Qty / variants | Purpose |
| --- | ---: | --- |
| `coupon_insert_boss` | Per material/orientation | M3 pilot at nominal diameter and +/-0.2 variants |
| `coupon_m4_seam_insert` | Before either revised shell | Three vertical production-orientation M4 seam pilots: Ø5.4/5.6/5.8, marked by one/two/three edge notches |
| `coupon_c8_cutout` | Per inlet/material candidate | Actual inlet profile, panel, and fixing fit |
| `coupon_rear_panel_fit_v2` | Per shell/panel process | Upright shell receiver plus flat panel insert; X/Z allowances 0.15/0.05 mm per side |
| `coupon_mac_button_recess` | After Mac measurement | Finger reach and guarding |
| `coupon_wifi_dock_v2` | Legacy only | Historical coupon for the removed external Wi-Fi dock; not used by the production V4 enclosure |
| `coupon_router_rf_access` | Legacy only | Historical coupon for the former common RF window; the production V4 uses six individual SMA bulkheads |
| `coupon_logo_mount` | Per panel/shell material pair | Two-screw insert fit, seating, torque, service cycling, and rattle |
| `coupon_handle_mount` | Per structural material/orientation | Representative two-screw foot/pad insert stack; torque, pull-out, and section inspection |

## Owner equipment and controlled components

| Item | Qty | Known nominal data | CAD treatment |
| --- | ---: | --- | --- |
| Apple Mac mini M4 (2024, non-Pro) | 1 | 127 x 127 x 50; about 0.67 kg | Outer dimensions official; cradle datums revised from physical fit, but no validated scan/STEP |
| Teltonika RUTM30 | 1 | 100 x 93.7 x 30; about 0.319 kg | Official AP214 STEP imported from `reference/0112_RUTM30AMBKX_02.STEP` |
| Mean Well APV-35-36 | 1 | 36 V, 1 A, 36 W; 84 x 57 x 29.5; 150 +/-10 mm attached 18 AWG leads | Datasheet-based placeholder; actual fit/temperature/wiring pending |
| Schurter 6160.0021 C8 inlet | 1 | Controlled 28 pitch / diameter-3.2 pattern; exact current drawing governs | Parametric placeholder and coupon; **phase-out/lifecycle and availability risk must be resolved before order** |
| Type-15 Wi-Fi antennas | 2 | 170 mm long, 90-degree hinge, screw-on RP-SMA | Rear bulkhead reference envelopes; no side docks |
| Teltonika PR1KC540 5G combo antenna | 1 | Four cellular leads used; GNSS unused | Four cellular pigtail/bulkhead extensions |

## Data, RF, and cable hardware — exact selection pending

| Item | Provisional qty | Acceptance criteria |
| --- | ---: | --- |
| Panel-supported RJ45 extension/coupler | 2 | Required link category/rate; compact replaceable retention; latch and internal lead access; vendor pattern checked against provisional two-hole M3 flange datums |
| Internal leads for the RJ45 extensions | 2 | Correct orientation/performance, bend radius, and service loop |
| Mac-to-router Ethernet patch lead | 1 | Required rate, compact plugs, low-voltage-lane fit; topology warning resolved |
| Panel-supported HDMI extension | 1 | Required HDMI mode end to end, positive mounting, serviceable internal lead; vendor pattern checked against provisional vertical two-hole M3 flange datums |
| Panel-supported USB-C extension | 1 | Explicit data/video/power capability, orientation, positive mounting, full-feature test; vendor pattern checked against provisional vertical two-hole M3 flange datums |
| SMA/RP-SMA panel bulkheads and short coax pigtails | 6 total | Four cellular plus two Wi-Fi positions; correct gender, Ø6.6 fit, nut torque, bend radius, strain relief, and router-port compatibility |
| Type-15 Wi-Fi antennas | 2 | Screw securely to the two Wi-Fi bulkheads; spacing, hinge clearance, RF performance, handling load, and loosening resistance verified |
| PR1KC540 cellular leads | 4 attached | Connector identity, manufacturer bend limit, and support verified |
| RF bulkhead washers/nuts | 6 sets | Compatible with 2.0 mm printed clamping lands; controlled torque without crushing or rotation |
| Low-voltage cable ties/supports | TBD | Reachable, replaceable, broad/non-crushing for coax |
| DC grommet and Mac-AC gland | 1 each | Exact hardware for diameter-9 and diameter-12 modeled openings after electrical/mechanical review; the stepped 6 mm Mac-AC solid is reserved space, not a selected conduit |

Do not freeze these parts until the actual-cable mock-up and Ethernet-topology decision are complete.

## Mechanical fasteners and inserts

Current joint-stack labels are **M3x14 for the base and underside-mounted handle**, **M3x10 for the Mac cradle**, **low-head M3x6 for the recessed router tray**, **M3x8 for service/cover joints**, **M4x10 for the two hidden cap locks**, and **M4x18 for the shell seam**, with the physically selected diameter-4.2 M3 and diameter-5.4 M4 pilots and 5.5 mm general insert depth. Handle screw heads remain hidden inside the detached cap and engage 5.0 mm into the 8 mm handle feet. These are geometry inputs, not released purchase specifications; verify head form, bottoming, engagement, material, torque, and pull-out physically.

| Joint | Modeled positions | Provisional hardware | Current mating geometry |
| --- | ---: | --- | --- |
| Base to lower shell | 4 M3 | 4 provisional M3x14 screws + 4 M3 inserts | Paired through-holes and webbed shell bosses; longer stack is distinct from service screws |
| Mac cradle to lower shell | 4 M3 | 4 provisional M3x10 screws + 4 M3 inserts | Downward-access holes and shell-tied bosses; nominal stack avoids marginal M3x8 engagement |
| Power compartment to lower shell | 4 M3 | 4 provisional low-head M3x8 screws + 4 M3 inserts | Unchanged lower-shell axes; diameter-3.4 floor bores with verified diameter-6.2 head and diameter-4.5 driver access, two support rails, four shell bosses |
| Power-compartment cover | 4 M3 | 4 provisional M3x8 screws + 4 M3 inserts | Short upper wall-tied bosses and aligned cover clearances; 5.2 mm nominal engagement into 5.5 mm pilots |
| Router tray to upper shell | 4 M3 | 4 M3x6 screws, measured heads no larger than Ø6.2 x 3.0, + 4 M3 inserts | Diameter-6.2 x 2.2 recesses leave 0.8 mm floor and about 0.7 mm nominal router clearance; accessible after +Y router removal |
| Router rear corner stops to tray | 2 M3 | 2 M3x8 screws + washers + 2 M3 inserts | Two top-access adjustable slots into rigid tray towers; replaces broken rear flexures and stays outside SMA envelopes |
| Rear panel to shells | 8 M3 | 8 provisional M3x8 screws + 8 M3 inserts | Counterbores and paired lower/upper rear bosses |
| Logo panels to upper shell | 4 magnet pairs | 4 shell magnets 6 x 3 mm + 4 panel magnets 6 x 1.5 mm + suitable adhesive | Two blind pockets per side; recessed face provides location; polarity and pull-off validation required |
| Removable handle to upper cap | 4 M3 | 4 provisional low-head M3x14 screws + 4 M3 inserts | Screws enter upward from cap underside into two broad 8 mm feet; 5.0 mm nominal engagement |
| Lower-to-upper shell structural seam | 6 M4 | 6 provisional low-head M4x18 screws with measured Ø7.0 heads + 6 M4 inserts | Three per side at X ±76.8 and Y -50/10/50; Ø8.2 internal pockets, 8.4-wide entry slots and top tool corridors, paired U-belts, no exterior openings |
| Upper cap to upper shell | 2 M4 | 2 provisional M4x10 screws + 2 M4 inserts | Selected dual dovetails carry vertical load; two concealed internal locks prevent lateral escape |
| APV fixing | 2 diameter-3.6 axes | Exact screw/insert/washer or approved alternative TBD | Supplier-coordinate axes over 3 mm blind diameter-4.2 pilots with 2.7 mm sealed floor; top service after shell mounting |
| C8 fixing | 2 diameter-3.2 positions | Supplier-approved screws/nuts/locking TBD | Fixed island pattern; terminal access/shroud review required |
| Router bezel | 4 integral hooks | No normal fasteners | Replaceable cantilever retention; cycle test pending |
| External Ethernet flange | 2 M3 through positions | Vendor-specific screws/nuts/locking TBD | Accepted 27.6 mm pitch with the vertical offset physically corrected |
| Mac HDMI PCB | 2 M3 blind positions | 2 screws + 2 M3 inserts | Accepted top-down mounting on 13 mm shelf, 9 mm axis setback |
| Two Mac USB-C PCBs | 4 M3 blind positions | 4 screws + 4 M3 inserts | Accepted inside mounting on 6 mm bosses with sharp reinforcement pockets |
| Router LAN/WAN flanges | 2 M3 holes per extension | Vendor-specific screws/nuts/locking TBD | Provisional horizontal-27 pattern in replaceable bezel; exact extension governs |

The modeled printed-part joints total **34 general M3 insert positions** and **8 M4 insert positions**, excluding the two APV axes and all connector-specific Ethernet/HDMI/USB/C8 hardware. The six seam screws use physically measured Ø7.0 heads in Ø8.2 x 3.2 pockets and require a long hex driver through the open top. Do not purchase by aggregate count alone: select head type, grade, washer, insert series, length, engagement, torque, access tool, and spare quantity after coupon and joint-stack review.

## Compliant and finishing items

| Item | Provisional qty | Requirement |
| --- | ---: | --- |
| Mac support pads | 3 | Nominal 14.6 x 14.6 x 2 mm TPU/silicone candidate in 1 mm seats; non-marking, replaceable, outside intake/button; compression TBD |
| Mac clip-cam wear pads | 4 | Tiny replaceable candidate pads for the modeled cam pockets; material, adhesion, force, wear, and thickness TBD |
| Router support pads | 4 | Nominal 8 x 16 x 1.3 mm candidate; 0.4 mm compression is provisional; verify safe underside lands, vent clearance, rocking, heat, and retention |
| Non-slip foot pads | 4 if used | Preserve approximately 5 mm loaded air gap; material/adhesive TBD |
| Discreet rear labels | 1 set | LAN/WAN and extended Mac ports; method and durable wording TBD |

## Mains and power-distribution items — competent design required

The following are deliberately **not specified for purchase** while `OPEN-13` remains open:

- single-inlet distribution topology, branch connection/protection hardware, and its required packaging volume;
- Mac and APV mains conductors/connectors/terminations;
- any required internal service-only fuse/protection;
- ferrules, sleeving, barriers, splice enclosure, insulating hardware, and approved electrical fasteners;
- inlet terminal shroud, cord anchorage, glands/grommets, protective conduit/barriers, conductor restraint, strain relief, and required markings; and
- exact flame-/temperature-rated compartment material and process.

A competent electrical designer must select these against the actual voltage, load, fault conditions, temperature, construction, and applicable requirements. APV or inlet component ratings do not qualify the integrated assembly.
