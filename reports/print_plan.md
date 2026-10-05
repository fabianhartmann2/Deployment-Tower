# Printing plan and coupon order

The baseline target is a Bambu Lab X1 Carbon with a 0.4 mm nozzle. These are prototype starting points, not validated production settings. Confirm the actual printer, plate, filament lot/conditioning, usable build region, slicer, and support/brim allowances.

## Baseline process

| Setting | Starting point | Boundary |
| --- | --- | --- |
| Layer height | 0.20 mm | Tune flexures and calibrated fits from coupons |
| Nominal line width | 0.45 mm | Main wall 3.2; minimum named wall 2.4 |
| Body walls | 7 | About 3.15 nominal; slicer must show continuous roads |
| Body prototype material | ASA | Dry filament and enclosed profile; final grade depends on thermal results |
| Power compartment/cover | Competently reviewed flame-/temperature-suitable grade | Generic ASA or a marketing “FR” label is not automatic electrical approval; avoid PLA |
| Handle/cap | Candidate ASA or PA-CF | Exact material, conditioning, orientation, insert pull-out, creep, and proof-load test govern |
| Supports | Only where preview requires | Keep away from calibrated fit/flexure and visible surfaces where possible |
| Brim/adhesion | Part/process dependent | Shells and large flat parts require warp control |
| Infill | Part specific | Ensure boss/top-skin support; infill percentage does not prove strength |
| Cosmetic seam | Rear or deliberate shadow line | Confirm in slicer and owner review |

Record material manufacturer/grade/color/lot, drying, nozzle, plate, chamber, slicer/profile, orientation, support interface, and post-conditioning for every fit or structural test article.

## Exported STL orientations

STEP remains in assembly coordinates. `export.py` applies these transformations before placing STL geometry on `Z=0`:

| Group | Export transform | Critical slicer review |
| --- | --- | --- |
| Base | Rotate 180 degrees about X, then ground | Broad upper skin on the plate instead of suspending it on four feet; inspect intake/button edges and foot overhangs |
| Cradle, shells, router tray, power box/cover, cap, both pad templates, M3/M4 insert coupons, Mac-button coupon, logo-mount coupon, handle-mount coupon, rear-panel-fit-v2 coupon | Modeled orientation, then ground | Warp/adhesion, tie and retention bridges, boss roads, elephant foot, openings, shell stability, pad thickness, vertical insert axes, and the v2 coupon's upright receiver/flat insert |
| Rear panel, both router rear retainers, C8 coupon, RF-access coupon | Rotate 90 degrees about X | Visible face, connector-edge quality, direct SMA-hole roundness/lands, retainer slots, and support scars |
| Left logo panel | Rotate -90 degrees about Y | Handed face/back orientation, reveal, blind 1.5 mm magnet pockets, and flat seating |
| Right logo panel, blank logo template, legacy Wi-Fi coupon | Rotate +90 degrees about Y | Mirrored panel orientation; the Wi-Fi coupon is retained only as historical calibration evidence |
| Example embossed logo panel | No rotation; edge-print the 70 mm face | Face-down would rest on the emboss; use supports/brim only after preview and cosmetic review |
| Handle | Rotate 90 degrees about X | Cylindrical grip and spherical shoulders, round leg/root layer paths, foot flatness, four screw bores, supports, and surface integrity |

After the listed transform, the exporter repacks disconnected solids along X with a 5 mm gap and independently lowers each one to `Z=0`; this prevents a secondary gauge/key body from floating or fusing into its mate. The actual packed orientation is also checked against the 256 mm build cube. Inspect every body in the slicer anyway. The 250 mm rear panel has limited margin; shells need deliberate brim/support planning. A bounding-box PASS does not include purge towers, brims, printer exclusion zones, or printability of every overhang.

## Recommended coupon order

Do not start either large cosmetic shell until the dependent gates pass.

### V4 prototype-change gate

Before regenerating the large v4 shell/cap/rear-panel parts, print these four small articles from the owner-supplied October measurements:

1. **Rear-I/O gate passed on `coupon_rear_io_mount_v7`.** Ethernet, HDMI, USB-C, and C8 all fit their physical hardware. Freeze the V7 geometry: accepted HDMI height, 13 mm shelf depth and M3 axes; 6.0 mm USB boss bridge with a sharp-cornered 14 x 6.5 x 2.5 mm PCB-facing pocket; and 30.0 mm C8 pitch. No further rear-I/O coupon is required unless the hardware, material, printer, or print settings change. The C8 result is mechanical fit only; it does not authorize wiring or energization.
2. `coupon_rf_bulkhead_v1`: columns left-to-right are diameter 6.6/6.8/7.0 mm; the upper row retains the full 3.2 mm wall and the lower row has a 2.0 mm local land. Select both the smallest smooth hole and the thickest wall that permit full washer/nut thread engagement. Test RP-SMA mechanically for Wi-Fi and the separately sourced SMA mobile bulkhead before freezing a shared geometry.
3. Both Ø6.2 pockets in `coupon_logo_magnet_v2` passed for the Ø6 x 3 mm shell magnet and Ø6 x 1.5 mm logo-panel magnet. Mark polarity before bonding; the magnets must attract. Pull-off force, rattle, adhesive retention, and repeated removal still need to be assessed before applying the arrangement to full panels. The final recessed logo receiver provides position; no extra locating ledge or finger notch is planned.
4. `coupon_cap_dovetail_v1` was too loose at its tightest 0.25 mm pair. On `coupon_cap_dovetail_v2`, the owner selected the two-notch 0.10 mm-per-side pair; the one-notch 0.05 mm pair was already too tight and is rejected for the longer production rail. Apply 0.10 mm per side, then verify the complete cap slides through its full engagement after cooling/conditioning and still uses a separate positive end lock.

All four coupon selections are now recorded and transferred into the production-named parts. The regenerated `upper_shell`, one-piece `rear_panel`, `upper_cap`, ergonomic `removable_handle`, relocated `power_compartment`, `power_compartment_cover`, `lower_shell`, and magnetic logo panels are the current set; do not mix them with earlier printed mating parts. The 71 x 36 x 25 mm DC/DC converter is only a reserved envelope until connector locations, mounting method, heat behavior, and electrical role are supplied. The marketplace C8 coupon is a mechanical fit test only and does not approve the inlet, wiring, insulation, protection, materials, or mains use.

1. **Insert-boss coupon.** Establish M3 pilot in every intended material/orientation; inspect insertion, perpendicularity, torque, pull-out, cracking, and breakthrough.
2. **Hidden-seam M4 insert coupon.** `coupon_m4_seam_insert` was printed in the production orientation; the owner selected the one-notch Ø5.4 mm boss over the Ø5.6 and Ø5.8 alternatives. All M4 insert pilots now use Ø5.4. Repeat only if the insert, material, layer height, wall settings, or conditioning changes; torque/pull-out checks still apply.
3. **C8 cutout coupon.** First reconfirm the specified part's availability/phase-out status and current drawing. Fit the exact inlet and fixing hardware; inspect flange seating, tolerance, panel thickness, rear access, and shroud envelope. This never authorizes wiring or energization.
4. **Rear-panel fit coupon v2.** Print `coupon_rear_panel_fit_v2`: its receiver stands upright like the shell while its separate insert prints flat like the rear panel. Verify the calibrated 0.15 mm/side X and 0.05 mm/side Z nominal allowances, corner seating, insertion, rattle, conditioning change, and repeated removal.
5. **Mac cradle v2 trial.** The original full cradle is withdrawn after physical testing. Print the regenerated `mac_cradle` with its rear-left button path, 0.30 mm side clearance, Ø112 opening, and 8 mm-lowered hooks. Fit three 2 mm base pads into the 1 mm seats plus representative clip-cam wear pads; verify the corrected button corner, full contact map, intake clearance, finish protection, four-cam insertion, both extended bottom releases, shake behavior, and at least 20 cycles.
6. **Legacy Wi-Fi dock coupon v2.** Retain the recorded Ø31.0 result only as revision history. Do not print production docks; the new design uses two screw-on Wi-Fi antennas on rear RP-SMA bulkheads.
7. **RF bulkhead coupon.** The selected production geometry is Ø6.6 with a 2.0 mm thinned clamping land. Reprint `coupon_rf_bulkhead_v1` only if connector hardware, printer, material, or settings change; then confirm washer/nut thread engagement and torque without crushing.
8. **Logo magnet coupon.** The Ø6.2 pockets passed for 6 x 3 mm shell magnets and 6 x 1.5 mm panel magnets. Use `coupon_logo_magnet_v2` for any process change and verify polarity, bonding, pull-off force, rattle, and at least 20 removal cycles.
9. **Revised router tray and stops.** Retire the loose tray with the broken flexure. Print `router_tray`, `router_rear_retainer_left`, and `router_rear_retainer_right`; reuse or print four 8 x 16 x 1.3 pad candidates. Install two Ø4.2-pilot M3 inserts in the rear towers. Verify the four Ø6.2 x 2.2 tray recesses fully contain the selected Ø6.2-or-smaller, 3.0-mm-high M3x6 heads below the router support plane; then check the inward-shifted guides, lowered ledges, common pad loading, no scratch/rock, both M3x8 adjustable stops, and repeated -Y insertion/+Y removal with the stops removed.
10. **Handle-mount coupon.** Test `coupon_handle_mount` with the final cap/handle materials and print settings. Install both foot inserts, use the selected low-head M3x14 screws upward through the cap sample into the 8 mm foot, verify 5.0 mm engagement/no bottoming, then test torque, pull-out, cracking, section quality, conditioning, and service cycling. This coupon is not the complete carrying test.
11. **Structural cap/handle test assembly.** After coupon closure, use all four underside handle M3x14 joints, both selected cap dovetails, both concealed M4x10 locks, all six hidden M4x18 seam joints, shell supports, inserts, and a guarded fixture. Weigh the complete prototype, calculate `4 x measured mass x 9.80665`, then apply only the competently approved proof-load/dwell protocol before any carry trial. Reject permanent deformation, loosened/spun inserts, cracks, layer separation, cap/seam gaps, or measurable creep outside the approved limit.

For this revision, print `lower_shell.stl` and `upper_shell.stl` first to verify the corrected rounded exterior, then `power_compartment.stl` to verify the 3 mm forward shift and both Ø4.2 C8 insert pockets. Print `upper_cap.stl` and `removable_handle.stl` as one mating set, then the one-piece `rear_panel.stl`, followed by both magnetic logo panels. There is no router-bezel part. Dry-assemble the shell seam, cap rails/locks, handle, rear I/O, and all six direct RF bulkheads before installing equipment.

## Part-specific attention

| Part | Review |
| --- | --- |
| Lower/upper shell | Warp, shadow seam, three keys/pockets, rear seat, lower rear-sill angle beam, paired U-belts, six hidden seam bosses/lugs, Ø8.2 head pockets, open driver corridors, relocated +X power rails, magnetic logo receivers, two cap dovetail rails/crossbars, and closed exterior skin |
| Base | Broad skin printed down after 180-degree flip, feet/contact, diameter-116 intake, four M3x14 clearances, continuous button path |
| Mac cradle | Three 1 mm pad seats with 2 mm pads, diameter-112 opening, 0.30 side clearance, four lowered clip/cams and wear pockets, two extended bottom release rails, four ears, rear-left button corridor |
| Router tray and two rear stops | Four compliant lands/pads, inward-shifted guides, lowered top ledges, front stop, vents, four Ø6.2 x 2.2 low-head M3x6 recesses, two webbed Ø4.2 insert towers, two connected slotted M3x8 corner stops, and clear -Y insertion/+Y removal with the stops removed |
| One-piece rear panel | Full 250 mm height, flatness, eight counterbores, +X fixed-island clearance, one Ethernet, user-positioned HDMI/dual USB mounts, six direct Ø6.6 RF holes, and intact 2.0 mm clamping lands |
| Power box/cover | Only reviewed material/process; APV/cable clearance, 3 mm forward position, sealed-floor raised tie bridges, blind top-service APV pilots, four open shell-mount bore/head/driver corridors, four upper wall-tied cover bosses/M3x8 joints, raised C8 tunnel/island with two Ø4.2 insert pockets, gland/exit edges; stepped Mac-AC envelope is not a printable conduit |
| Logo panels | Correct handed transform, matte face, two blind magnet pockets, polarity, reveal, pull-off access, and flat seating; embossed example edge-printed |
| Cap/handle | Continuous perimeter/crossmember, both selected dovetail grooves/rails, two blind M4x10 locks, underside head access, four M3x14 axes, two broad rounded 8 mm feet, insert pockets, cylindrical grip, spherical shoulders, round legs/flared roots, and support removal without damage |

## Print acceptance

A part is eligible for prototype assembly only when:

- the slicer shows intended walls and no omitted thin features;
- no critical face, boss, flexure, rail, hook, or load path is warped, cracked, under-extruded, delaminated, or support-damaged;
- dependent coupons passed in the same material, process, orientation, and conditioning state;
- its current STL mesh check is PASS;
- fit-critical dimensions are measured after cooling/conditioning; and
- structural or electrical suitability has not been inferred from appearance, solid validity, infill, or an “engineering/FR” material name.
