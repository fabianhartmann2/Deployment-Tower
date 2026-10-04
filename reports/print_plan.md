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
| Rear panel, router bezel, both router rear retainers, C8 coupon, RF-access coupon | Rotate 90 degrees about X | Visible face, connector-edge quality, hook/stop layers, retainer slots, hole roundness, support scars |
| Left logo panel and left Wi-Fi dock | Rotate -90 degrees about Y | Handed face/back orientation, reveal, logo screw holes, dock clip layers, and cable notch |
| Right logo panel, blank logo template, right Wi-Fi dock, Wi-Fi coupon | Rotate +90 degrees about Y | Mirrored handed orientation and the same critical features |
| Example embossed logo panel | No rotation; edge-print the 70 mm face | Face-down would rest on the emboss; use supports/brim only after preview and cosmetic review |
| Handle | Rotate 90 degrees about X | Grip/leg layer paths, foot flatness, four screw bores, gussets, supports, and surface integrity |

After the listed transform, the exporter repacks disconnected solids along X with a 5 mm gap and independently lowers each one to `Z=0`; this prevents a secondary gauge/key body from floating or fusing into its mate. The actual packed orientation is also checked against the 256 mm build cube. Inspect every body in the slicer anyway. The 236 mm rear panel has limited margin; shells need deliberate brim/support planning. A bounding-box PASS does not include purge towers, brims, printer exclusion zones, or printability of every overhang.

## Recommended coupon order

Do not start either large cosmetic shell until the dependent gates pass.

### V4 prototype-change gate

Before regenerating the large v4 shell/cap/rear-panel parts, print these four small articles from the owner-supplied October measurements:

1. `coupon_rear_io_v1`: left-to-right Ethernet, HDMI, USB-C, and the new C8 inlet. Confirm the physical connector nose enters without force, both mounting axes align, the visible face seats flat, and the PCB/flange does not rock.
   V5 confirmed the corrected Ethernet and HDMI geometry. Its USB reinforcement pocket at the boss plane was still too small; the subsequent 13 x 6 x 2.2 mm rounded V6 pocket was also rejected before printing. Do not reprint v2-v6; print `coupon_rear_io_mount_v7`. V7 keeps the accepted HDMI height, 13 mm shelf depth, and M3 axes. USB-C still mounts from inside on the 6.0 mm-deep common boss bridge; its PCB-facing pocket is now a sharp-cornered 14 x 6.5 x 2.5 mm rectangle and the smaller connector channel continues to the exterior. C8 pitch remains 30.0 mm. Print v7 with the flat outer face on the bed as exported, install only the intended low-voltage hardware for the fit check, and do not wire or energize the C8 inlet.
2. `coupon_rf_bulkhead_v1`: columns left-to-right are diameter 6.6/6.8/7.0 mm; the upper row retains the full 3.2 mm wall and the lower row has a 2.0 mm local land. Select both the smallest smooth hole and the thickest wall that permit full washer/nut thread engagement. Test RP-SMA mechanically for Wi-Fi and the separately sourced SMA mobile bulkhead before freezing a shared geometry.
3. Both Ø6.2 pockets in `coupon_logo_magnet_v2` passed for the Ø6 x 3 mm shell magnet and Ø6 x 1.5 mm logo-panel magnet. Mark polarity before bonding; the magnets must attract. Pull-off force, rattle, adhesive retention, and repeated removal still need to be assessed before applying the arrangement to full panels. The final recessed logo receiver provides position; no extra locating ledge or finger notch is planned.
4. `coupon_cap_dovetail_v1` was too loose at its tightest 0.25 mm pair. On `coupon_cap_dovetail_v2`, the owner selected the two-notch 0.10 mm-per-side pair; the one-notch 0.05 mm pair was already too tight and is rejected for the longer production rail. Apply 0.10 mm per side, then verify the complete cap slides through its full engagement after cooling/conditioning and still uses a separate positive end lock.

Do not print `upper_shell_v4`, `rear_panel_v4`, `upper_cap_v4`, the new handle, or the repacked router tray until these four results are recorded. The 71 x 36 x 25 mm DC/DC converter is only a reserved envelope until connector locations, mounting method, heat behavior, and electrical role are supplied. The marketplace C8 coupon is a mechanical fit test only and does not approve the inlet, wiring, insulation, protection, materials, or mains use.

1. **Insert-boss coupon.** Establish M3 pilot in every intended material/orientation; inspect insertion, perpendicularity, torque, pull-out, cracking, and breakthrough.
2. **Hidden-seam M4 insert coupon.** `coupon_m4_seam_insert` was printed in the production orientation; the owner selected the one-notch Ø5.4 mm boss over the Ø5.6 and Ø5.8 alternatives. All M4 insert pilots now use Ø5.4. Repeat only if the insert, material, layer height, wall settings, or conditioning changes; torque/pull-out checks still apply.
3. **C8 cutout coupon.** First reconfirm the specified part's availability/phase-out status and current drawing. Fit the exact inlet and fixing hardware; inspect flange seating, tolerance, panel thickness, rear access, and shroud envelope. This never authorizes wiring or energization.
4. **Rear-panel fit coupon v2.** Print `coupon_rear_panel_fit_v2`: its receiver stands upright like the shell while its separate insert prints flat like the rear panel. Verify the calibrated 0.15 mm/side X and 0.05 mm/side Z nominal allowances, corner seating, insertion, rattle, conditioning change, and repeated removal.
5. **Mac cradle v2 trial.** The original full cradle is withdrawn after physical testing. Print the regenerated `mac_cradle` with its rear-left button path, 0.30 mm side clearance, Ø112 opening, and 8 mm-lowered hooks. Fit three 2 mm base pads into the 1 mm seats plus representative clip-cam wear pads; verify the corrected button corner, full contact map, intake clearance, finish protection, four-cam insertion, both extended bottom releases, shake behavior, and at least 20 cycles.
6. **Wi-Fi dock coupon v2.** The owner physically selected the three-marker 31.0 mm cavity for the measured Ø30.0 mm hub; one/two/three small marker holes identify the 30.0/30.5/31.0 mm alternatives. The production cavity is therefore Ø31.0 mm, with a 29.5 mm rounded mouth requiring 0.25 mm nominal motion per arm. Confirm both actual antennas, no marks, free cable exit, carry/shake behavior, and 20 insertion/removal cycles before release.
7. **Router RF-access coupon.** Use `coupon_router_rf_access` with all six actual couplings simultaneously. Verify hand/tool access, first bends, selected liner, nearby broad cable support, and repeat service.
8. **Logo-mount coupon.** Test `coupon_logo_mount` in the actual shell/panel materials for insert installation, M3x8 seating, proven torque, panel clamp-up/reveal, rattle/carry behavior, sharp edges, and at least 20 screw/removal cycles.
9. **Revised router tray and stops.** Retire the loose tray with the broken flexure. Print `router_tray`, `router_rear_retainer_left`, and `router_rear_retainer_right`; reuse or print four 8 x 16 x 1.3 pad candidates. Install two Ø4.2-pilot M3 inserts in the rear towers. Verify the four Ø6.2 x 2.2 tray recesses fully contain the selected Ø6.2-or-smaller, 3.0-mm-high M3x6 heads below the router support plane; then check the inward-shifted guides, lowered ledges, common pad loading, no scratch/rock, both M3x8 adjustable stops, and repeated -Y insertion/+Y removal with the stops removed.
10. **Handle-mount coupon.** Test `coupon_handle_mount` with the final cap/handle materials and print settings. Install both inserts, use the selected low-head M3x10 screws on the unrecessed 5 mm foot, verify 5.0 mm engagement/no bottoming, then test torque, pull-out, cracking, section quality, conditioning, and service cycling. This coupon is not the complete carrying test.
11. **Structural cap/handle test assembly.** After coupon closure, use all four handle M3x10 joints, all six hidden M4x18 seam joints, the six M4x18 cap joints, shell supports, inserts, and a guarded fixture. Weigh the complete prototype, calculate `4 x measured mass x 9.80665`, then apply only the competently approved proof-load/dwell protocol before any carry trial. Reject permanent deformation, loosened/spun inserts, cracks, layer separation, cap/seam gaps, or measurable creep outside the approved limit.

With the selected Ø5.4 M4 pilot regenerated, print `lower_shell_v3` first and inspect the six insert bosses plus the new rear angle beam. Then print `upper_shell_v3` and perform a dry six-screw seam assembly before installing the router tray or cap. Other already-passed or already-printed parts do not need reprinting unless their interface changed.

## Part-specific attention

| Part | Review |
| --- | --- |
| Lower/upper shell | Warp, shadow seam, three keys/pockets, rear seat, lower rear-sill angle beam, paired U-belts, six hidden seam bosses/lugs, Ø8.2 head pockets for measured Ø7.0 heads, 8.4-wide internal entry slots, open top-driver corridors, router/power rails, dock/logo receivers, cap/handle load spines, and completely closed exterior skin |
| Base | Broad skin printed down after 180-degree flip, feet/contact, diameter-116 intake, four M3x14 clearances, continuous button path |
| Mac cradle | Three 1 mm pad seats with 2 mm pads, diameter-112 opening, 0.30 side clearance, four lowered clip/cams and wear pockets, two extended bottom release rails, four ears, rear-left button corridor |
| Router tray and two rear stops | Four compliant lands/pads, inward-shifted guides, lowered top ledges, front stop, vents, four Ø6.2 x 2.2 low-head M3x6 recesses, two webbed Ø4.2 insert towers, two connected slotted M3x8 corner stops, and clear -Y insertion/+Y removal with the stops removed |
| Rear panel/bezel | Flatness, eight counterbores, fixed-island clearance, extension openings and provisional two-hole M3 flange patterns, four bezel hooks, smooth RF edge |
| Power box/cover | Only reviewed material/process; APV/cable clearance, sealed-floor raised tie bridges, blind top-service APV pilots, four open shell-mount bore/head/driver corridors, four upper wall-tied cover bosses/M3x8 joints, C8 tunnel/island, gland/exit edges; stepped Mac-AC envelope is not a printable conduit |
| Wi-Fi docks | Vertical clip axes, hub shelf, cable notch, flexure layers, two screw holes each |
| Logo panels | Correct handed transform, matte face, two clean M3 bores, thumbnail scallop, reveal, and flat seating; embossed example edge-printed |
| Cap/handle | Continuous perimeter/crossmember/tie paths, six provisional M4x18 cap joints, four full-depth M3 bosses/pads, two broad feet, four screw bores, gussets, and support removal without damage |

## Print acceptance

A part is eligible for prototype assembly only when:

- the slicer shows intended walls and no omitted thin features;
- no critical face, boss, flexure, rail, hook, or load path is warped, cracked, under-extruded, delaminated, or support-damaged;
- dependent coupons passed in the same material, process, orientation, and conditioning state;
- its current STL mesh check is PASS;
- fit-critical dimensions are measured after cooling/conditioning; and
- structural or electrical suitability has not been inferred from appearance, solid validity, infill, or an “engineering/FR” material name.
