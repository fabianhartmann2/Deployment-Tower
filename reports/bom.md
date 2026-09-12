# Bill of materials

This is a prototype-planning BOM, not a purchasing or production release. Quantities describe current CAD positions; screw length/head, insert series, material grade, and all electrical parts remain subject to physical and competent technical review.

## Printed assembly parts

| Part | Qty | Baseline material | Function / boundary |
| --- | ---: | --- | --- |
| `base` | 1 | Dark ASA | Feet, 116 mm intake, continuous button approach, four screw clearances |
| `mac_cradle` | 1 | ASA | Physically calibrated Ø112 opening, 0.30 mm side gap, three 1 mm pad seats, four 8 mm-lowered positive-Z clip/cams, two extended bottom release rails, four shell-fastened ears |
| `lower_shell` | 1 | Matte white ASA | Base/cradle/power supports, rear bosses, angle-reinforced rear sill, three seam keys, internal U-belt, six hidden structural seam inserts |
| `upper_shell` | 1 | Matte white ASA | Router supports, rear bosses, logo/dock receivers, cap inserts, handle ribs/spines, internal U-belt, six hidden screw lugs/tool corridors |
| `router_tray` | 1 | ASA | Vented plate, four compliant-pad lands, guides, ledges, front stop, rear latch nibs, four recessed low-head shell fasteners |
| `power_compartment` | 1 | Reviewed flame-/temperature-suitable engineering material | Mechanical APV/mains box, fixed C8 island/tunnel, raised sealed-floor tie bridges, two top-service blind APV pilots, four open lower-shell mounting corridors, four upper wall-tied cover bosses, and exits; not an approved electrical enclosure |
| `power_compartment_cover` | 1 | Same reviewed material | Separate deliberate-access cover with four column-aligned M3 clearance axes |
| `rear_panel` | 1 | Dark ASA | Eight-fastener service face; removes around fixed C8 island |
| `router_interface_bezel` | 1 | Dark ASA | Replaceable RF/Ethernet insert with four integral cantilever hooks |
| `upper_cap` | 1 | Matte white ASA | Six-fastener cap, crossmember/ties, two bearing pads, four full-depth M3 handle bosses |
| `removable_handle` | 1 | Candidate ASA/PA-CF after tests | Grip, gusseted legs/full-width ribs, two 42 x 32 x 5 mm feet, four M3 clearance axes; no load rating |
| `wifi_dock_left`, `wifi_dock_right` | 1 each | ASA or PA candidate | Recessed vertical clips, hub shelves, cable notches, two M3 holes each |
| `logo_panel_left`, `logo_panel_right` | 1 each | ASA or approved variant | 70 mm faces with two outward-accessible M3 holes each |

The registry contains **19 printable definitions**: the 15 installed rows above plus `logo_panel_blank_template`, `logo_panel_example_embossed`, `compliant_pad_template`, and `router_compliant_pad_template`. Make three provisional 14.6 x 14.6 x 2 mm Mac pads for the 1 mm seats and four provisional 8 x 16 x 1.3 mm router pads; material, compression, contact compatibility, and release status remain open.

## Fit coupons

| Coupon | Qty / variants | Purpose |
| --- | ---: | --- |
| `coupon_insert_boss` | Per material/orientation | M3 pilot at nominal diameter and +/-0.2 variants |
| `coupon_m4_seam_insert` | Before either revised shell | Three vertical production-orientation M4 seam pilots: Ø5.4/5.6/5.8, marked by one/two/three edge notches |
| `coupon_c8_cutout` | Per inlet/material candidate | Actual inlet profile, panel, and fixing fit |
| `coupon_rear_panel_fit_v2` | Per shell/panel process | Upright shell receiver plus flat panel insert; X/Z allowances 0.15/0.05 mm per side |
| `coupon_mac_button_recess` | After Mac measurement | Finger reach and guarding |
| `coupon_wifi_dock_v2` | 1 minimum | Rounded-mouth 30.0, 30.5, and 31.0 hub-capture variants; replaces impossible rectangular lips |
| `coupon_router_rf_access` | 1 minimum | Full 88 x 30 six-port opening with actual plugs, fingers/tools, liner, and bends |
| `coupon_logo_mount` | Per panel/shell material pair | Two-screw insert fit, seating, torque, service cycling, and rattle |
| `coupon_handle_mount` | Per structural material/orientation | Representative two-screw foot/pad insert stack; torque, pull-out, and section inspection |

## Owner equipment and controlled components

| Item | Qty | Known nominal data | CAD treatment |
| --- | ---: | --- | --- |
| Apple Mac mini M4 (2024, non-Pro) | 1 | 127 x 127 x 50; about 0.67 kg | Outer dimensions official; cradle datums revised from physical fit, but no validated scan/STEP |
| Teltonika RUTM30 | 1 | 100 x 93.7 x 30; about 0.319 kg | Official AP214 STEP imported from `reference/0112_RUTM30AMBKX_02.STEP` |
| Mean Well APV-35-36 | 1 | 36 V, 1 A, 36 W; 84 x 57 x 29.5; 150 +/-10 mm attached 18 AWG leads | Datasheet-based placeholder; actual fit/temperature/wiring pending |
| Schurter 6160.0021 C8 inlet | 1 | Controlled 28 pitch / diameter-3.2 pattern; exact current drawing governs | Parametric placeholder and coupon; **phase-out/lifecycle and availability risk must be resolved before order** |
| Standard Wi-Fi antennas | 2 | Photo-derived about 91 long x 30 base | Placeholder bodies and three-size dock coupon |
| Teltonika PR1KC540 5G combo antenna | 1 | Four cellular leads used; GNSS unused | No body dock; four direct native connections |

## Data, RF, and cable hardware — exact selection pending

| Item | Provisional qty | Acceptance criteria |
| --- | ---: | --- |
| Panel-supported RJ45 extension/coupler | 2 | Required link category/rate; compact replaceable retention; latch and internal lead access; vendor pattern checked against provisional two-hole M3 flange datums |
| Internal leads for the RJ45 extensions | 2 | Correct orientation/performance, bend radius, and service loop |
| Mac-to-router Ethernet patch lead | 1 | Required rate, compact plugs, low-voltage-lane fit; topology warning resolved |
| Panel-supported HDMI extension | 1 | Required HDMI mode end to end, positive mounting, serviceable internal lead; vendor pattern checked against provisional vertical two-hole M3 flange datums |
| Panel-supported USB-C extension | 1 | Explicit data/video/power capability, orientation, positive mounting, full-feature test; vendor pattern checked against provisional vertical two-hole M3 flange datums |
| Actual Wi-Fi antennas | 2 | Bodies match released dock; cables/connectors carry no dock load |
| PR1KC540 cellular leads | 4 attached | Connector identity, manufacturer bend limit, and support verified |
| RF-window liner / edge protection | TBD | Jacket-compatible, retained, temperature/process compatible |
| Low-voltage cable ties/supports | TBD | Reachable, replaceable, broad/non-crushing for coax |
| DC grommet and Mac-AC gland | 1 each | Exact hardware for diameter-9 and diameter-12 modeled openings after electrical/mechanical review; the stepped 6 mm Mac-AC solid is reserved space, not a selected conduit |

Do not freeze these parts until the actual-cable mock-up and Ethernet-topology decision are complete.

## Mechanical fasteners and inserts

Current joint-stack labels are **M3x14 for the base**, **M3x10 for the Mac cradle and handle**, **low-head M3x6 for the recessed router tray**, **M3x8 for logo/service/cover joints**, and **M4x18 for the cap and shell seam**, with diameter-4.2 M3 pilots, diameter-5.6 M4 pilots, and 5.5 mm general insert depth. Handle screw heads remain above the feet so the full 5 mm thickness is in the grip stack. These are geometry inputs, not released purchase specifications; verify head form, bottoming, engagement, material, torque, and pull-out physically.

| Joint | Modeled positions | Provisional hardware | Current mating geometry |
| --- | ---: | --- | --- |
| Base to lower shell | 4 M3 | 4 provisional M3x14 screws + 4 M3 inserts | Paired through-holes and webbed shell bosses; longer stack is distinct from service screws |
| Mac cradle to lower shell | 4 M3 | 4 provisional M3x10 screws + 4 M3 inserts | Downward-access holes and shell-tied bosses; nominal stack avoids marginal M3x8 engagement |
| Power compartment to lower shell | 4 M3 | 4 provisional low-head M3x8 screws + 4 M3 inserts | Unchanged lower-shell axes; diameter-3.4 floor bores with verified diameter-6.2 head and diameter-4.5 driver access, two support rails, four shell bosses |
| Power-compartment cover | 4 M3 | 4 provisional M3x8 screws + 4 M3 inserts | Short upper wall-tied bosses and aligned cover clearances; 5.2 mm nominal engagement into 5.5 mm pilots |
| Router tray to upper shell | 4 M3 | 4 provisional low-head M3x6 screws + 4 M3 inserts | Diameter-6.2 x 1.8 head recesses; shorter stack avoids blind-pilot bottoming; accessible after +Y router removal |
| Rear panel to shells | 8 M3 | 8 provisional M3x8 screws + 8 M3 inserts | Counterbores and paired lower/upper rear bosses |
| Wi-Fi docks to upper shell | 4 M3 total | 4 provisional M3x8 screws + 4 M3 inserts | Two outside-accessible positions per dock; webbed pocket bosses |
| Logo panels to upper shell | 4 M3 total | 4 provisional M3x8 screws + 4 M3 inserts | Two outward-accessible positions per panel; shell-webbed blind bosses; 5.5 mm nominal insert overlap |
| Removable handle to upper cap | 4 M3 | 4 provisional low-head M3x10 screws + 4 M3 inserts | Two screws per broad 5 mm foot into full-depth cap bosses/pads; 5.0 mm nominal engagement |
| Lower-to-upper shell structural seam | 6 M4 | 6 provisional low-head M4x18 screws + 6 M4 inserts | Three per side at X ±76.8 and Y -50/10/50; internal heads and top tool corridors, paired U-belts, no exterior openings |
| Upper cap to upper shell | 6 M4 | 6 provisional M4x18 screws + 6 M4 inserts | Four perimeter plus two handle-spine positions |
| APV fixing | 2 diameter-3.6 axes | Exact screw/insert/washer or approved alternative TBD | Supplier-coordinate axes over 3 mm blind diameter-4.2 pilots with 2.7 mm sealed floor; top service after shell mounting |
| C8 fixing | 2 diameter-3.2 positions | Supplier-approved screws/nuts/locking TBD | Fixed island pattern; terminal access/shroud review required |
| Router bezel | 4 integral hooks | No normal fasteners | Replaceable cantilever retention; cycle test pending |
| Mac HDMI/USB-C flanges | 2 M3 holes per extension | Vendor-specific screws/nuts/locking TBD | Provisional vertical-20 pattern in removable rear panel; exact extension governs |
| Router LAN/WAN flanges | 2 M3 holes per extension | Vendor-specific screws/nuts/locking TBD | Provisional horizontal-27 pattern in replaceable bezel; exact extension governs |

The modeled shell service/structural patterns total **40 M3 screw/insert positions** and **12 M4 screw/insert positions**, excluding the two APV axes, two C8 points, and provisional extension-flange through-holes. The six seam screws specifically require a low head no larger than the provisional Ø7.6 x 3.2 envelope and a long hex driver through the open top. Do not purchase by aggregate count alone: select head type, grade, washer, insert series, length, engagement, torque, access tool, and spare quantity after coupon and joint-stack review.

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
