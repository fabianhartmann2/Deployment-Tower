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
| Cradle, shells, router tray, power box/cover, cap, both pad templates, insert coupon, Mac-button coupon, logo-mount coupon, handle-mount coupon, rear-panel-fit-v2 coupon | Modeled orientation, then ground | Warp/adhesion, tie and retention bridges, boss roads, elephant foot, openings, shell stability, pad thickness, representative insert axes, and the v2 coupon's upright receiver/flat insert |
| Rear panel, router bezel, C8 coupon, RF-access coupon | Rotate 90 degrees about X | Visible face, connector-edge quality, hook/flexure layers, hole roundness, support scars |
| Left logo panel and left Wi-Fi dock | Rotate -90 degrees about Y | Handed face/back orientation, reveal, logo screw holes, dock clip layers, and cable notch |
| Right logo panel, blank logo template, right Wi-Fi dock, Wi-Fi coupon | Rotate +90 degrees about Y | Mirrored handed orientation and the same critical features |
| Example embossed logo panel | No rotation; edge-print the 70 mm face | Face-down would rest on the emboss; use supports/brim only after preview and cosmetic review |
| Handle | Rotate 90 degrees about X | Grip/leg layer paths, foot flatness, four screw bores, gussets, supports, and surface integrity |

After the listed transform, the exporter repacks disconnected solids along X with a 5 mm gap and independently lowers each one to `Z=0`; this prevents a secondary gauge/key body from floating or fusing into its mate. The actual packed orientation is also checked against the 256 mm build cube. Inspect every body in the slicer anyway. The 236 mm rear panel has limited margin; shells need deliberate brim/support planning. A bounding-box PASS does not include purge towers, brims, printer exclusion zones, or printability of every overhang.

## Recommended coupon order

Do not start either large cosmetic shell until the dependent gates pass.

1. **Insert-boss coupon.** Establish M3 pilot in every intended material/orientation; inspect insertion, perpendicularity, torque, pull-out, cracking, and breakthrough. Create equivalent M4 trials if the selected insert supplier needs them.
2. **C8 cutout coupon.** First reconfirm the specified part's availability/phase-out status and current drawing. Fit the exact inlet and fixing hardware; inspect flange seating, tolerance, panel thickness, rear access, and shroud envelope. This never authorizes wiring or energization.
3. **Rear-panel fit coupon v2.** Print `coupon_rear_panel_fit_v2`: its receiver stands upright like the shell while its separate insert prints flat like the rear panel. Verify the calibrated 0.15 mm/side X and 0.05 mm/side Z nominal allowances, corner seating, insertion, rattle, conditioning change, and repeated removal.
4. **Mac button/recess and Mac-pad trials.** Update from measured Mac data, then test intentional finger reach, guarding, and comfort. Print three 2 mm base pads for the 1 mm seats plus representative clip-cam wear pads; verify contact map, finish protection, compression, four-cam insertion, both linked bottom releases, shake behavior, and at least 20 cycles.
5. **Wi-Fi dock coupon v2.** The owner physically selected the three-marker 31.0 mm cavity for the measured Ø30.0 mm hub; one/two/three small marker holes identify the 30.0/30.5/31.0 mm alternatives. The production cavity is therefore Ø31.0 mm, with a 29.5 mm rounded mouth requiring 0.25 mm nominal motion per arm. Confirm both actual antennas, no marks, free cable exit, carry/shake behavior, and 20 insertion/removal cycles before release.
6. **Router RF-access coupon.** Use `coupon_router_rf_access` with all six actual couplings simultaneously. Verify hand/tool access, first bends, selected liner, nearby broad cable support, and repeat service.
7. **Logo-mount coupon.** Test `coupon_logo_mount` in the actual shell/panel materials for insert installation, M3x8 seating, proven torque, panel clamp-up/reveal, rattle/carry behavior, sharp edges, and at least 20 screw/removal cycles.
8. **Router pad/fastener trial.** Print four 8 x 16 x 1.3 pad candidates and a representative low-head M3x6 tray joint. Verify the actual router has safe lands, nominal 0.4 compression is appropriate, all four contacts share load without rocking, the recess seats the selected diameter-6.2-or-smaller head without contact or blind-pilot bottoming, vents remain open, and repeated -Y insertion/+Y removal is smooth.
9. **Handle-mount coupon.** Test `coupon_handle_mount` with the final cap/handle materials and print settings. Install both inserts, use the selected low-head M3x10 screws on the unrecessed 5 mm foot, verify 5.0 mm engagement/no bottoming, then test torque, pull-out, cracking, section quality, conditioning, and service cycling. This coupon is not the complete carrying test.
10. **Structural cap/handle test assembly.** After coupon closure, use all four handle M3x10 joints, representative M4x18 cap/seam joints, shell supports, inserts, and a guarded fixture. Weigh the complete prototype, calculate `4 x measured mass x 9.80665`, then apply only the competently approved proof-load/dwell protocol before any carry trial. Reject permanent deformation, loosened/spun inserts, cracks, layer separation, cap gaps, or measurable creep outside the approved limit.

After coupon closure, a risk-efficient print order is router bezel, rear panel, power box/cover, cradle/base, docks/logo panels, router tray, cap/handle, lower shell, then upper shell. This discovers interface and mechanism issues before the longest visible prints.

## Part-specific attention

| Part | Review |
| --- | --- |
| Lower/upper shell | Warp, shadow seam, three keys/pockets, rear seat, insert bosses, router/power rails, dock/logo receivers, cap/seam load spines |
| Base | Broad skin printed down after 180-degree flip, feet/contact, diameter-116 intake, four M3x14 clearances, continuous button path |
| Mac cradle | Three 1 mm pad seats with 2 mm pads, diameter-112 exclusion, keepers, four clip/cams and wear pockets, two bottom release rails, four ears, button corridor |
| Router tray | Four compliant lands/pads, guide spacing, top ledges, latch-flexure layers, front stop, vents, four low-head M3x6 recesses, -Y insertion/+Y removal |
| Rear panel/bezel | Flatness, eight counterbores, fixed-island clearance, extension openings and provisional two-hole M3 flange patterns, four bezel hooks, smooth RF edge |
| Power box/cover | Only reviewed material/process; APV/cable clearance, sealed-floor raised tie bridges, blind top-service APV pilots, four shell mounts, four full-height cover columns/M3x8 joints, C8 tunnel/island, gland/exit edges; stepped Mac-AC envelope is not a printable conduit |
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
