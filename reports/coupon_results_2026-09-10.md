# Physical coupon observations — 2026-09-10

These are owner-reported prototype observations. Filament grade/lot, drying, slicer profile, orientation confirmation, insert series, screw head/grade, torque, conditioning, cycle count, and photographs were not supplied, so these results guide CAD revision but are not a production release or structural/electrical qualification.

| Coupon/interface | Reported result | Disposition |
| --- | --- | --- |
| M3 insert boss | Ø4.2 mm selected | Retain the 4.2 mm M3 pilot default; repeat in every final structural material/orientation. |
| Handle mount | Pass | Geometry retained. Complete torque, pull-out, 24-hour clamp/creep, full load-path, and 4x measured-weight proof tests remain required. |
| Logo mount | Pass | Geometry retained. Confirm documented torque and 20 service cycles on final material. |
| Rear-panel fit | Loose; opening measured 42.5 x 22.9 mm, insert measured 41.9 x 22.0 mm | Original coupon withdrawn. Separate X/Z allowances changed to 0.15/0.05 mm per side. `coupon_rear_panel_fit_v2` reproduces upright-shell and flat-panel print orientations and must pass before either shell is printed. |
| Wi-Fi dock | Fail; measured antenna hub is Ø30.0 mm and cannot enter any original clip | Original rectangular lips narrowed the nominal mouth to about 22.8-23.8 mm and are withdrawn. V2 uses rounded 1.0 mm noses with 0.75 mm intrusion per side; production cavity/mouth are 30.9/29.4 mm, demanding 0.30 mm nominal movement per arm. Reprint and cycle-test `coupon_wifi_dock_v2`. |
| C8 cutout | Pass | Mechanical fit observation only; electrical design, procurement status, shroud, fixing, wiring, inspection, and energized tests remain outside this result. |
| RF access | Pass | Retain geometry; fully dressed cable support, abrasion, bend, and signal tests remain required. |
| Mac button access | Pass | Retain geometry; intake/feet map and fully assembled guarding/ergonomics remain separate checks. |

Do not print the Wi-Fi docks or either large shell from an earlier export. Regenerate/use the v2 artifacts and physically pass both revised coupons first.
