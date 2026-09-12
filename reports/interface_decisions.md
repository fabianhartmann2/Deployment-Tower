# External-interface decisions

The handoff prefers direct native access when the device orientation, hand clearance, and cable path permit it. It permits a replaceable, mechanically supported extension when direct access produces poor routing, an impractical opening, or insufficient plug access. The decisions below apply to the fixed 165 mm package and remain subject to physical hardware tests.

## Direct versus extension table

| Required interface | Qty | Decision | Current CAD implementation | Rationale | Required physical closure |
| --- | ---: | --- | --- | --- | --- |
| PR1KC540 cellular | 4 | **Direct native** | Four official Mobile SMA centres are reached through one 88 x 30 radiused opening in `router_interface_bezel()` | Avoids internal RF extensions/bulkheads; the leads attach at the router face as required by `NET-12` | Install all four actual coupling bodies; verify finger/tool access, edge liner, first bend, and broad non-crushing support |
| Wi-Fi RF | 2 | **Direct native** | Two official Wi-Fi RP-SMA centres share the same opening | Preserves native RF path and permits the antennas to remain connected | Verify actual plugs, simultaneous six-port access, and connected dock/service behavior |
| RUTM30 LAN and WAN | 2 | **Replaceable rear extensions** | Two 18 x 16 provisional openings at X `-17,+17`, Z `196`, within the replaceable router bezel; each has a provisional two-hole M3 flange pattern at horizontal pitch 27 | The native Ethernet face points toward the enclosure front when the six-port RF face points rearward | Select exact parts and vendor drawings; replace/tune the hole and anti-rotation geometry; verify latches, insertion load, link rate, and replacement |
| Internal Mac-to-router Ethernet | 1 | **Internal patch lead** | Provisional 20 x 34 x 24 plug/service envelope in the low-voltage lane | Required internal link | Select actual lead and verify bend/service path; resolve concurrency warning |
| Mac HDMI | 1 | **Replaceable rear extension** | 16 x 7 provisional rear-panel opening at `(X,Z)=(-20,57)` plus a two-hole M3 flange pattern at vertical pitch 20 and a reference extension body | Exact Mac native-port, vendor flange, and plug-overmould coordinates were not supplied; replaceable geometry avoids freezing a large assumed tunnel | Select required HDMI capability and exact mounting form; update the provisional pattern; verify full seating, strain support, service loop, and function |
| Mac USB-C | 1 | **Replaceable rear extension** | 11 x 5.5 provisional rear-panel opening at `(X,Z)=(16,57)` plus a two-hole M3 flange pattern at vertical pitch 20 and a reference extension body | Same measurement gap as HDMI; required USB capability and vendor flange are not yet defined | Specify data/video/power capability; select the exact part, update the provisional pattern, and physically verify support and end-to-end operation |
| Mac AC | 1 | **Internal only** | Provisional plug clearance, relocated diameter-12 floor gland at `(X,Y)=(-55,-33.5)`, and a continuous stepped 6 mm reserved envelope toward the Mac connector | `MAC-14` prohibits a dedicated external Mac-power opening; the reservation demonstrates only one collision-free packaging route | Complete single-inlet topology, branch/protection hardware, conduit/barrier, conductor restraint, materials, and qualified electrical proof remain PENDING |
| Schurter 6160.0021 C8 | 1 | **Direct mounted component** | 20.6 x 11.8 controlled profile plus 0.20 allowance and two diameter-3.2 holes at 28 pitch, on a fixed 42 x 28 island at `(-38,108)` | One external inlet; the fixed island/tunnel remains with the closed power compartment when the rear panel is removed | Confirm current supplier drawing, lifecycle/availability, actual profile, fasteners, terminal shroud, strain relief, and electrical construction |
| Mac native power button | 1 | **Direct mechanical reach** | Continuous 26 mm-wide lower-rear/underside path; no electrical modification | Concealed native access with desk guarding | Measure actual button/intake/feet; test reach, 20 operations, accidental actuation, and comfort |
| Wi-Fi antenna transport | 2 | **Mechanical docks only** | Vertical recessed body clips, hub shelves, cable notches, and two M3 mounting positions per dock | Supports each antenna body while leaving the connector/cable outside the carrying load path | Caliper data, 30/30.5/31 mm coupon, insertion/carry/shake, cable freedom, and 20-cycle tests |
| PR1KC540 body transport | 0 | **Intentionally omitted** | No body dock | `NET-10` explicitly prohibits an enclosure-mounted dock | Inspection; connected leads still need edge protection and support |

An opening, two-hole M3 pattern, or reference body is not a released extension mount. The current vertical-20 and horizontal-27 flange patterns are explicit but provisional. Exact extension part numbers, vendor hole patterns, anti-rotation features, fasteners, and internal cable terminations remain unresolved.

## Router connector row and common opening

The official service-face sequence is:

`Mobile 1 — Wi-Fi 1 — Mobile 2 — Mobile 3 — Wi-Fi 2 — Mobile 4`

The centres are at 14.8 mm pitch and 12 mm above the housing base. With the router centred at `(0,28,170.5)`, the RF row is centred at about `Z=167.5`. Six separate diameter-14 access holes would leave 0.8 mm webs, below the 2.4 mm controlled minimum wall. The chosen direct-access feature is therefore a single `5 x 14.8 + 14 = 88 mm` wide, 30 mm high, radius-5 window.

The generated check proves that the analytic window spans all six official centres. It does not prove clearance for real coupling nuts, fingers or tools, coax bends, an edge liner, or simultaneous cabling. `coupon_router_rf_access` reproduces the full 88 x 30 section and must be tested before the bezel/shell are committed.

The router is installed through the rear opening from +Y toward the front (-Y), where the front stop arrests travel and the rear latches recover. Service removal is the reverse motion along +Y. Direction and removal remain subject to a fully wired physical trial.

## Ethernet concurrency warning

The requirements ask for both native router Ethernet ports to be externally usable and for a simultaneous internal Mac-to-router Ethernet link. The RUTM30 has only two native Ethernet ports, so those requests require three links from two jacks.

The CAD deliberately retains two external extension positions and one internal cable placeholder, but it does not disguise the system conflict. Before wiring or extension procurement, the owner must approve one of these outcomes:

1. only one external port is usable while the internal Mac link is connected;
2. a suitably rated active switch is added and the package is reworked for its volume, heat, power, wiring, service, and compliance; or
3. another documented topology satisfies the operational intent.

Until the approved choice is implemented and functionally tested, combined compliance with `NET-03` and `NET-04` remains unresolved. The generated report records this as a WARN; other WARN/PENDING rows may also remain and must be reviewed from the regenerated report.

## Fixed C8 service boundary

The inlet is not mounted to the routine rear service panel. `power_compartment.py` creates the inlet island and a closed tunnel back to the separately covered power box; `rear_panel.py` removes a clearance island around that fixed structure. Removing the eight rear-panel screws therefore leaves the inlet and its mechanical terminal boundary in place. The compartment also has two raised tie bridges over a continuous nominal floor, two blind top-service APV insert pilots, four wall-tied upper cover bosses, and four unobstructed lower-shell fastening corridors.

This is a mechanical service concept only. The stepped Mac-AC solid is a reserved envelope rather than a selected protective conduit. None of these features establishes touch safety, required clearances, insulating properties, terminal coverage, branch topology, conductor restraint, protection, temperature rating, or regulatory compliance. Rear-panel service is de-energized work, opening the inner power cover is a separate qualified operation, and no built unit may be energized before competent architecture and qualified inspection/tests are complete.

## Interfaces intentionally not exposed

No dedicated external openings are modeled for router LEDs, SIM slots, reset, USB, GNSS, other Mac ports, the headphone jack, Mac status LED, an external power switch, or an externally accessible fuse holder. The high rear slots are general enclosure exhaust openings, not device-interface access.

## Extension acceptance criteria

Before an HDMI, USB-C, or Ethernet extension is accepted, record its exact manufacturer and part number and verify that it:

- supports the required signal/performance mode end to end;
- has positive, replaceable panel/bezel retention and anti-rotation where needed;
- replaces or explicitly approves the provisional two-hole M3 flange datums against the vendor drawing and real part;
- does not transfer plug forces to a native device port;
- allows full insertion and latch/release operation with the intended cable overmould;
- fits its internal lead, bend radius, and service loop without pinching or blocking removal;
- survives the defined service cycles; and
- remains outside the mains boundary and Mac intake/button/removal paths.
