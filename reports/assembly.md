# Assembly and service sequence

This is a **de-energized mechanical prototype sequence**, not an electrical work instruction. Keep the C8 cord disconnected throughout mechanical assembly and service. Only a competent/qualified person may define and perform mains assembly, inspection, energized tests, or work behind the power-compartment cover.

## Preconditions

1. Print and pass the applicable coupons in [print_plan.md](print_plan.md).
2. Confirm the freshly regenerated [validation_results.md](validation_results.md) has no `FAIL`; review every WARN and PENDING item.
3. Measure the actual Mac, APV, antennas, C8, extensions, inserts, plugs, grommets, liner, and cables. Update parameters/retention geometry and regenerate outputs where results differ.
4. Resolve the two-port/three-link Ethernet topology before ordering or wiring extensions.
5. Have a competent electrical designer define the complete single-inlet topology, protection, materials, separation, shrouding, restraint, labels, inspection, and test plan.
6. Select screw heads/lengths and inserts from coupon and joint-stack results. Verify tool access, engagement, torque, pull-out, perpendicularity, and no boss cracking/breakthrough.

## Mechanical assembly order

1. **Inspect prints.** Deburr only non-calibrated edges. Reject warped interfaces, cracked flexures/bosses, incomplete walls, or damaged cable/connector edges.
2. **Install verified inserts.** Fit the M3 and M4 inserts in their paired shell/compartment bosses using the insert maker's process. Include the four full-height power-cover columns and the two short blind APV pilots only after the selected insert is proven compatible with its available depth. The CAD contains 32 M3 and 8 M4 service/structural shell positions, excluding APV/C8 and provisional extension-flange hardware; install only those needed at each dry-fit stage.
3. **Mount the power box mechanically.** Seat `power_compartment` on the two lower-shell rails and fasten its four floor positions from inside the empty box with the provisional M3x8 stack. Confirm the fixed C8 island/tunnel aligns with the rear-panel clearance island, both raised tie bridges are clear, and the nominal diameter-12 Mac-AC gland remains unobstructed.
4. **Dry-fit the unenergized power hardware.** With the compartment already shell-mounted and its cover removed, lower the actual APV onto the two supplier-coordinate axes and install its fixing screws from above into the blind insert/captive concept. Verify the diameter-3.6 lug clearance, washer/head access, insert retention, and no floor breakthrough. Use the raised bridges for a restraint mock-up without drilling the floor. The four wall-tied columns accept a provisional M3x8 cover stack with 5.2 mm nominal engagement. The stepped 6 mm Mac-AC solid is only a reserved routing envelope: branch hardware, conduit/barrier construction, lead bends, topology, and electrical acceptance remain PENDING. Do not wire or energize from this sequence.
5. **Join the body modules.** Engage the three lower-shell alignment keys with the upper-shell pockets across the 0.8 mm shadow seam. Install the two provisional M4x18 seam screws through the upper lugs into the lower front-spine inserts. Confirm no step, rocking, bottoming, or forced fit.
6. **Install the router tray.** Fit four tested 8 x 16 x 1.3 mm compliant pads to the printed lands. Fasten the four top-loaded positions into the two upper-shell cross rails using provisional low-head M3x6 screws seated in the diameter-6.2 x 1.8 recesses while the router is absent. Verify lands, ledges, latch fingers, fasteners, and the +Y withdrawal corridor are clear.
7. **Install the Mac cradle.** Fit three approved 2 mm compliant pads into the 1 mm seats; the intended nominal pad top is the Mac support plane, but compression remains a physical test result. Fasten the four cradle ears from below into the lower-shell bosses with provisional M3x10 hardware. Keep the annular intake and button corridor completely clear.
8. **Load and retain the Mac from below.** With the base removed, use the lead-in cams to deflect the four positive-Z clips as the Mac rises horizontally into the cradle. Confirm all four overhangs have their nominal non-contact top gap, the two linked bottom release rails remain reachable, and no printed feature or provisional wear pad marks the Mac, intake, button, finish, or port/plug keep-outs. Fit, force, preload, scratch, shake, and cycle acceptance remain PENDING.
9. **Dry-fit the button and intake.** Temporarily attach the base with the four provisional M3x14 screws. Operate the native button through the continuous lower-rear path and inspect the diameter-116 opening against the physical intake/feet. Remove the base for cable dress.
10. **Install low-voltage/data hardware.** Mount the exact HDMI and USB-C extensions with positive replaceable support. Route the Mac Ethernet, HDMI, USB-C, router DC, and Ethernet-extension leads in the low-voltage lane with measured service loops and accessible releases. Keep them outside the mains keep-out, Mac air/button/removal paths, and all fastener tips.
11. **Load the RUTM30.** Present the official-orientation router at the open rear (+Y) end, then slide it toward the front (-Y) until the front stop is reached and the two rear latch nibs recover behind it. Confirm the native RF row faces rear, all four compliant lands share support without rocking, and the native Ethernet face has clear internal lead routing toward the extension bezel.
12. **Populate the replaceable interfaces.** Dry-fit the selected RJ45 extensions to the bezel's provisional two-hole M3 flange patterns and the selected HDMI/USB-C extensions to the corresponding two-hole M3 rear-panel patterns. These patterns are placeholders, not vendor-approved mounts. Fit the bezel's four cantilever hooks into the rear-panel aperture. Connect all six native RF couplings through the common 88 x 30 opening and add the tested liner and nearby broad/non-crushing support.
13. **Close the rear service face.** Offer the panel over the fixed C8 island without moving the inlet or inner cover. Install the eight provisional M3x8 rear-panel screws. Confirm rear withdrawal needs neither handle nor dock removal.
14. **Install side features.** Fasten each recessed vertical Wi-Fi dock with two provisional M3x8 outside-accessible screws. Push each logo panel's four cantilever studs into its shell receivers and confirm its lower thumbnail scallop remains usable. Snaps are not structural carrying features.
15. **Attach the cap.** Seat the cap onto the upper-shell load structures and install six provisional M4x18 screws: four perimeter positions plus two directly over the handle spines. There must be no gap or screw bottoming at the bearing/support regions.
16. **Close the base.** Dress cables clear, then install its four provisional M3x14 screws and verify all feet are stable. The base, cradle, recessed router-tray, and general service stacks deliberately use different lengths.
17. **Install the unloaded handle.** Lower both T-keys through the entry pockets, slide them toward the enclosure front into the locked position, and verify both lateral pawls expand into their pockets. For removal, support the handle, squeeze both exposed release pads inward, slide back to the entry position, and lift out. Do not carry equipment until cycle, accidental-release, creep, and controlled load tests pass.

## Intended handle load path

`grip -> two legs -> two T-keys/cap undercuts and pawls -> integral cap cross members -> six M4 cap joints (including two over spines) -> upper-shell ribs/ties/spines -> two M4 shell-seam joints -> lower-shell structure/equipment supports`

Computational validation checks the installed pawl preload (`2.484 mm3` total, below a `4.0 mm3` allowlist) and confirms that a `+0.50 mm` virtual lift intersects each cap bearing undercut by `10.440 mm3`. It does not perform FEA or establish material strength, layer adhesion, safe working load, fatigue, impact, creep, or accidental-release safety. Replace the provisional 1.8 kg mass with the measured complete mass before a controlled test at the approved factor.

## Routine service sequence

1. Shut down equipment as required; disconnect the external C8 cord, data cables, and antenna connections needed for access; follow the approved electrical procedure; verify de-energization.
2. For cable/interface service, remove the eight rear-panel screws and withdraw the panel along +Y. It moves around the fixed inlet island; leave the separate power cover closed.
3. Replace an extension, patch lead, liner, or low-voltage support without opening the mains compartment. Recheck releases, bends, service loops, and pinch points.
4. For router service, disconnect its RF, Ethernet, and DC connections, spread the two rear latch fingers, and withdraw the router along +Y through the rear opening. The four recessed low-head tray screws then become accessible if the tray itself must be removed. Reinstallation proceeds from +Y toward -Y.
5. For Mac service, remove the four M3x14 base screws and lower the base. Disconnect the internal Mac leads, use the two bottom-access release rails to deflect the four Z-retention clips outward, and lower the Mac. Release/remove the four cradle screws only if the cradle also needs service. Validate force, hand access, and the fully wired downward-removal sequence on hardware.
6. Wi-Fi docks are removed using their two external screws. Logo panels start at the thumbnail scallop and release by flexing their four receiver hooks; neither operation should expose the power cover.
7. Open the power-compartment cover only as a separate deliberate operation by an authorized person under the reviewed electrical procedure.
8. Reassemble in reverse order and inspect every cable, flexure, insert, and joint for wear or damage.

## Physical post-assembly checks

- Stable four-foot support and retained measured air gap.
- Twenty intentional Mac-button operations from desk and handled positions, with no accidental actuation.
- Unobstructed Mac intake/exhaust and instrumented temperature comparison under representative load.
- Fully wired Mac downward removal using both release rails and router removal along +Y without cable/structure interference.
- Four Mac clip/cam engagements, wear pads, two linked release rails, three 2 mm base pads in 1 mm seats, and at least 20 insert/release/shake cycles without damage or unintended release.
- Four router compliant pads share load without rocking, excessive compression, vent obstruction, or low-head screw contact; rear-to-front (-Y) insertion and +Y removal remain smooth after cycling.
- Full seating, latch/release access, retention, and functional test for HDMI, USB-C, and both Ethernet extensions.
- Concurrent six-port RF connection/disconnection with no edge abrasion, connector load, or tight coax bend.
- Both connected Wi-Fi antennas dock/carry/shake/release without cable or connector structural load; at least 20 cycles.
- Logo panels remain flush, non-rattling, and removable after at least 20 cycles.
- Insert/screw joints survive defined torque and repeated service without spin-out or cracked bosses.
- Handle lock survives cycle/accidental-release evaluation and the complete load path passes the documented controlled test before carrying.
- Qualified electrical inspection and applicable tests pass before any routine energized use.
