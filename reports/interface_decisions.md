# External-interface decisions

The handoff prefers direct native access when the device orientation, hand clearance, and cable path permit it. It permits a replaceable, mechanically supported extension when direct access produces poor routing, an impractical opening, or insufficient plug access. The decisions below apply to the fixed 165 mm package and remain subject to physical hardware tests.

## Direct versus extension table

| Required interface | Qty | Decision | Current CAD implementation | Rationale | Required physical closure |
| --- | ---: | --- | --- | --- | --- |
| Cellular RF | 4 | **Rear SMA bulkhead extensions** | Four Ø6.6 positions in a six-port rear row with 2.0 mm clamping lands | Allows standard screw-on enclosure antennas while short pigtails connect to the four native Mobile ports | Select exact SMA pigtails/bulkheads; verify gender, torque, strain relief, bends, antenna load, spacing, and RF performance |
| Wi-Fi RF | 2 | **Rear RP-SMA bulkhead extensions** | Two Ø6.6 positions in the same row accept the Type-15 screw-on antennas; side docks are removed | Avoids the failed/obsolete body-dock concept and provides standard external antenna mounting | Verify exact RP-SMA gender, pigtails, hinge clearance, torque, spacing, handling load, and RF performance |
| External Ethernet from RUTM30 | 1 | **Replaceable rear extension** | One accepted 17 x 14 opening at `(-38,108)` with 27.6 mm two-hole pitch and corrected vertical hole offset, directly in the rear panel | One native router port remains externally usable while the other serves the internal Mac | Verify the measured adapter, latch access, 42 mm inner depth, angled plug, 20 mm cable bend, insertion load, link rate, screws, and replacement |
| Internal Mac-to-router Ethernet | 1 | **Internal patch lead** | Provisional 20 x 34 x 24 plug/service envelope in the low-voltage lane | Uses the router's second native Ethernet port | Select actual lead and verify bend/service path and link performance |
| Mac HDMI | 1 | **Replaceable rear extension on horizontal internal shelf** | V7 geometry is transferred into the full rear panel: 13 mm shelf, top-down M3 mounts, axes 9 mm behind the connector datum | The HDMI lead route is fixed by the Mac mini; the power compartment moved instead | Verify strain support, 45 mm bend/service loop, tool access, Mac removal, and function |
| Mac USB-C | 2 | **Replaceable rear extensions mounted behind rear panel** | V7 geometry is transferred twice: 6 mm boss bridges, inside screws, and sharp 14 x 6.5 x 2.5 mm reinforcement pockets; no exterior screw heads | Both fixed Mac cable routes stay in the low-voltage side while the power compartment moves to +X | Verify ribbon exits, strain support, removal access, Mac removal, and end-to-end operation |
| Mac AC | 1 | **Internal only** | Provisional plug clearance, relocated diameter-12 floor gland at `(X,Y)=(55,-33.5)`, and a continuous stepped 6 mm reserved envelope toward the Mac connector | `MAC-14` prohibits a dedicated external Mac-power opening; the reservation demonstrates only one collision-free packaging route | Complete single-inlet topology, branch/protection hardware, conduit/barrier, conductor restraint, materials, and qualified electrical proof remain PENDING |
| Candidate measured C8 inlet | 1 | **Direct mounted component** | V7 21 x 12.5 opening is transferred to the island at `(38,116)` on the relocated +X compartment; two Ø4.2 full-depth pockets accept M3 heat-set inserts and the island/tunnel remains covered when the rear panel is removed | Raising the inlet 8 mm and moving the box 3 mm forward clears the user-positioned HDMI shelf while retaining the mains service boundary | Reprint and revalidate insert installation and assembled access, then complete terminal shroud, strain relief, touch-safety, material, thermal, and qualified electrical validation; coupon fit is not electrical approval |
| Mac native power button | 1 | **Direct mechanical reach** | Continuous 26 mm-wide lower-rear/underside path; no electrical modification | Concealed native access with desk guarding | Measure actual button/intake/feet; test reach, 20 operations, accidental actuation, and comfort |
| Wi-Fi antenna mounting | 2 | **Screw-on rear bulkheads** | Type-15 antennas attach directly to the two RP-SMA bulkheads; no side body docks remain | Standardized removable mounting with no separate printed flexure | Verify tightening, hinge sweep, spacing, carry/shake load, bulkhead anti-rotation, cable strain relief, and 20 cycles |
| PR1KC540 body transport | 0 | **Intentionally omitted** | No body dock | `NET-10` explicitly prohibits an enclosure-mounted dock | Inspection; connected leads still need edge protection and support |

An opening, two-hole M3 pattern, or reference body is not a released extension mount. Exact extension part numbers, vendor hole patterns, anti-rotation features, fasteners, and internal cable terminations remain subject to the physical parts.

## Router connector row and rear bulkheads

The official service-face sequence is:

`Mobile 1 — Wi-Fi 1 — Mobile 2 — Mobile 3 — Wi-Fi 2 — Mobile 4`

The native router centres remain at 14.8 mm pitch, but the rear bulkheads are redistributed to 20 mm pitch at `Z=158` for washer/nut and antenna clearance. The sequence is preserved through six short internal pigtails. Every rear hole is Ø6.6 and the inner rebate leaves a 2.0 mm exterior clamping land.

The generated check proves six open axes, 20 mm pitch, and surrounding clamping material. It does not prove connector gender, nut torque, anti-rotation, coax routing, strain relief, antenna loads, spacing, detuning, or RF performance. The selected Ø6.6/2.0 coupon geometry must be repeated if hardware or print process changes.

The router is installed through the rear opening from +Y toward the front (-Y), where the front stop arrests travel. The original printed rear flexures broke and sat about 5 mm behind the physical chassis, so they are withdrawn. Two rigid slotted corner stops are fitted afterward and secured to tray insert towers with M3x8 screws. Service removal is the reverse motion along +Y after both stops are unscrewed. Direction and removal remain subject to a fully wired physical trial.

## Ethernet allocation

The owner selected exactly one external Ethernet connection. The two native RUTM30 ports are therefore allocated one-to-one: one internal Mac-to-router patch lead and one rear-panel Ethernet extension. The former two-port bezel and its second external Ethernet opening are removed, so no active switch or three-link topology is assumed by the CAD. Actual cable routing, link performance, strain support, and latch/service access remain physical checks.

## Fixed C8 service boundary

The inlet is not mounted to the routine rear service panel. `power_compartment.py` creates the inlet island and a closed tunnel back to the separately covered power box; `rear_panel.py` removes a clearance island around that fixed structure. Removing the eight rear-panel screws therefore leaves the inlet and its mechanical terminal boundary in place. The compartment also has two raised tie bridges over a continuous nominal floor, two blind top-service APV insert pilots, four wall-tied upper cover bosses, and four unobstructed lower-shell fastening corridors.

This is a mechanical service concept only. The stepped Mac-AC solid is a reserved envelope rather than a selected protective conduit. None of these features establishes touch safety, required clearances, insulating properties, terminal coverage, branch topology, conductor restraint, protection, temperature rating, or regulatory compliance. Rear-panel service is de-energized work, opening the inner power cover is a separate qualified operation, and no built unit may be energized before competent architecture and qualified inspection/tests are complete.

## Interfaces intentionally not exposed

No dedicated external openings are modeled for router LEDs, SIM slots, reset, USB, GNSS, other Mac ports, the headphone jack, Mac status LED, an external power switch, or an externally accessible fuse holder. The high rear slots are general enclosure exhaust openings, not device-interface access.

## Extension acceptance criteria

Before an HDMI, USB-C, or Ethernet extension is accepted, record its exact manufacturer and part number and verify that it:

- supports the required signal/performance mode end to end;
- has positive, replaceable panel retention and anti-rotation where needed;
- replaces or explicitly approves the provisional two-hole M3 flange datums against the vendor drawing and real part;
- does not transfer plug forces to a native device port;
- allows full insertion and latch/release operation with the intended cable overmould;
- fits its internal lead, bend radius, and service loop without pinching or blocking removal;
- survives the defined service cycles; and
- remains outside the mains boundary and Mac intake/button/removal paths.
