# Physical coupon observations — 2026-09-10

These are owner-reported prototype observations. Filament grade/lot, drying, slicer profile, orientation confirmation, insert series, screw head/grade, torque, conditioning, cycle count, and photographs were not supplied, so these results guide CAD revision but are not a production release or structural/electrical qualification.

The Mac-cradle follow-up was reported on 2026-09-11.

| Coupon/interface | Reported result | Disposition |
| --- | --- | --- |
| M3 insert boss | Ø4.2 mm selected | Retain the 4.2 mm M3 pilot default; repeat in every final structural material/orientation. |
| Handle mount | Pass | Geometry retained. Complete torque, pull-out, 24-hour clamp/creep, full load-path, and 4x measured-weight proof tests remain required. |
| Logo mount | Pass | Geometry retained. Confirm documented torque and 20 service cycles on final material. |
| Rear-panel fit | Original loose; opening measured 42.5 x 22.9 mm, insert measured 41.9 x 22.0 mm. Revised coupon subsequently reported **pass**. | Original coupon withdrawn. Retain separate X/Z allowances of 0.15/0.05 mm per side. `coupon_rear_panel_fit_v2` reproduces upright-shell and flat-panel print orientations. Repeated-removal and conditioned-fit observations remain useful. |
| Wi-Fi dock | Original failed completely on the measured Ø30.0 mm hub. Revised three-marker 31.0 mm capture subsequently reported **pass**. | Original rectangular-lip coupon withdrawn. Production hub cavity set to 31.0 mm with rounded 1.0 mm noses, a 29.5 mm mouth, and 0.25 mm nominal movement per arm. Confirm both antennas plus cable, carry/shake, and 20-cycle behavior. |
| C8 cutout | Pass | Mechanical fit observation only; electrical design, procurement status, shroud, fixing, wiring, inspection, and energized tests remain outside this result. |
| RF access | Pass | Retain geometry; fully dressed cable support, abrasion, bend, and signal tests remain required. |
| Mac button coupon | Pass | The isolated access shape passed, but the subsequent full-cradle trial showed its assembled handedness was wrong; the production path is now mirrored to rear-left. |
| Mac cradle | Fail/revise: button access on wrong side; 1.5 mm measured clip gap is too loose; retaining hooks can be 8 mm lower; central ring/opening is 4 mm too large | Original cradle withdrawn. Mirror the button path to rear-left, use 0.30 mm Mac-specific side clearance, lower hooks by 8 mm, reduce the cradle opening from Ø116 to Ø112, shift the omitted support pad to the corrected button corner, and extend the bottom release rails. Reprint and repeat fit/contact/intake/release/shake/cycle checks. |
| Revised power-compartment lower-shell holes | Pass | Corrected four through-bores/head/tool corridors retained. Cover fit remains a separate check. |
| Original two-point lower/upper shell seam | CAD access fail before print | Withdrawn: upper spines blocked the two screw heads and driver paths. Replaced by six hidden internal M4 joints, paired U-belts, and explicit head/tool/exterior-skin checks. Print the new M4 pilot coupon before either revised shell. |
| Original lower-shell rear sill | Printed part visibly flaps | Withdrawn: the one-sided 4 mm strip is now reinforced by an internal angle beam tied across the lower shell; rear-panel seat and button path remain recut clear. Revised lower shell still requires physical verification. |

Use only artifacts regenerated after the two revised coupon results were incorporated. Single-fit coupon closure does not replace the remaining durability, load, cable, thermal, or electrical prototype gates.
