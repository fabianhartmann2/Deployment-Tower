# Dimensions and parameter reference

All dimensions are millimetres unless stated otherwise. `src/deployment_station/parameters.py` is the executable source of truth; this report records its current `DEFAULT` configuration. After regeneration, exact exported hashes and design-space bounding boxes are in `export_manifest.json`; do not use a pre-regeneration manifest for the current source.

## Coordinate system and datums

- Origin: centre of the enclosure footprint at the desk-contact plane.
- +X: right when looking at the front.
- +Y: toward the rear/service face.
- +Z: upward.
- Centre planes: `X=0`, `Y=0`; desk plane: `Z=0`.
- Front/rear exterior planes: `Y=-82.5` / `Y=+82.5`.
- Fixed-body top: `Z=280`.
- Equipment locations are reference-envelope centres, not guaranteed physical datums.

## Selected exterior and print package

| Item | Default | Boundary |
| --- | ---: | --- |
| Fixed enclosure | 165 x 165 x 280 | Base, shells, cap, panels, bezel, and recessed dock material included; removable handle and antennas excluded |
| Width:depth:height | 1:1:1.69697 | Target 1:1:1.70; absolute height-ratio error 0.00303 |
| Main radii | 24 outer / 20.8 inner | Rounded-square shell |
| Main / minimum named wall | 3.2 / 2.4 | Minimum check covers controlled wall parameters, not every local tessellated section |
| Desk air gap | 5 | Nominal printed-foot height; pad compression is not included |
| Installed handle range | approximately `Z=274..356` | Handle design bbox is 82 high and is excluded from fixed envelope |
| Printer build cube | 256 x 256 x 256 | Every individual printable bbox fits after permitted orientation; slicer confirmation remains required |

The generated fixed-envelope result is `165.00 x 165.00 x 280.00`. Non-default proportional scaling is intentionally rejected: changing width requires a coordinated repack of absolute hardware, interface, seam, and load-path datums.

## Packaging centres and ranges

| Item | Centre `(X,Y,Z)` / datum | Controlled envelope | Approximate range |
| --- | ---: | ---: | --- |
| Mac mini placeholder | `(0,-8,49)` | 127 x 127 x 50 | X `-63.5..63.5`; Y `-71.5..55.5`; Z `24..74` |
| Mac support plane | `Z=24` | — | 10 above nominal base top `Z=14` |
| APV case placeholder | `(-35,8,103.55)` | 57 X x 84 Y x 29.5 Z | X `-63.5..-6.5`; Y `-34..50`; Z `88.8..118.3` |
| APV/mains box | centre `(-35,8,105)` | nominal 72 x 120 x 44 | X `-71..1`; Y `-52..68`; Z `83..127`; fixed rear island/tunnel extends overall design bbox depth to 134.5 |
| Low-voltage lane | `(48,0,116)` | 34 x 122 x 76 | X `31..65`; Y `-61..61`; Z `78..154` |
| Mac-AC reserved corridor | gland datum `(-55,-33.5,83)` toward provisional Mac AC | stepped 6 wide packaging solid | Approximate bbox X `-75.3..42`; Y `-36.5..68.5`; Z `46..83`; no physical conduit or electrical release implied |
| Router tray datum | `Z=151` | 3 thick plate | Shell-supported fasteners; guide/retainer geometry extends above the plate |
| RUTM30 official STEP | `(0,28,170.5)` | 100 x 93.7 x 30 | X `-50..50`; Y `-18.85..74.85`; Z `155.5..185.5` |
| Handle anchor reference | `Z=260` | centres at X `+/-54`, Y `-42` | Cap lock geometry near fixed-body top |

The Mac, APV, antennas, C8, extensions, plugs, and cable ranges are controlled placeholders. Only the RUTM30 body is imported from official STEP.

## Shell, panels, and interfaces

| Feature | Current default |
| --- | ---: |
| Base | 14 high total; 5 high feet; visible skin inset 1.5 per side |
| Shell split | lower nominal top `Z=105`; 0.8 shadow gap; upper shell to `Z=268` |
| Cap | `Z=268..280`, 12 high; six M4 clearance positions |
| Rear shell opening | 120 wide, `Z=18..252` |
| Rear service panel | 132 x 236 x 3.2; radius 8; eight M3 positions |
| Router bezel face | 118 x 78 x 4.8 nominal; aperture 112 x 72; centre `(X,Z)=(0,178)` |
| RF direct-access window | 88 x 30, radius 5; row centre about `Z=167.5` |
| Router extension centres | X `-17,+17`, Z `196`; provisional cutouts 18 x 16 |
| Router extension flange datums | Two provisional M3 axes per extension, horizontal pitch 27; diameter-3.4 clearances |
| C8 fixed island | 42 x 28 nominal island; inlet centre `(X,Z)=(-38,108)` |
| C8 controlled cutout | 20.6 x 11.8 plus 0.20 profile allowance; radius 3.5; two diameter-3.2 holes at 28 pitch |
| HDMI extension opening | 16 x 7; centre `(X,Z)=(-20,57)` |
| USB-C extension opening | 11 x 5.5; centre `(X,Z)=(16,57)` |
| Mac extension flange datums | Two provisional M3 axes per extension, vertical pitch 20; diameter-3.4 clearances |
| Mac button approach | 26 wide; installed base run follows the button-to-rear distance (42.5 before the rounded end); continuous swept path validated with diameter-11 probe |
| Base intake opening | diameter 116 at Mac Y centre |
| Logo faces | 70 x 70, radius 6, centre `Z=156`, 0.8 reveal; four push-in cantilever studs each |
| Wi-Fi dock backplates | 36 x 98 x 3, centre `(Y,Z)=(53,216)` on each side; two M3 positions per dock |

`finger_well_reach=38` controls the isolated button coupon. The installed base and cradle derive their longer clearances from the provisional button and rear-face coordinates.

## Exported printable-part bounding boxes

These are assembly-coordinate STEP bounding boxes. Hooks, bosses, clips, and retainers can make them larger than their nominal face/plate values.

| Part | Design bbox X x Y x Z |
| --- | ---: |
| `base` | 162 x 162 x 14 |
| `mac_cradle` | 152 x 137 x 59.2, including four Z-retention clips and two release rails |
| `lower_shell` | 165 x 165 x 97 |
| `upper_shell` | 165 x 164.9531 x 162.6 |
| `router_tray` | 120 x 99.1 x 38.1 |
| `power_compartment` | 72 x 134.5 x 44 |
| `power_compartment_cover` | 72 x 120 x 4.8 |
| `rear_panel` | 132 x 3.2 x 236 |
| `router_interface_bezel` | 119 x 8.8 x 78 |
| `upper_cap` | 165 x 165 x 12 |
| `removable_handle` | 130.8 x 26 x 82 |
| each `wifi_dock_*` | 17.85 x 36 x 98 |
| each installed/blank logo panel | 12.9 x 70 x 70 |
| example embossed logo panel | 13.7 x 70 x 70 |
| Mac compliant-pad template | 14.6 x 14.6 x 2 |
| router compliant-pad template | 8 x 16 x 1.3 |

## Exported coupon bounding boxes

| Coupon | Design bbox X x Y x Z |
| --- | ---: |
| `coupon_c8_cutout` | 55 x 3.2 x 35 |
| `coupon_insert_boss` | 46 x 28 x 14 |
| `coupon_rear_panel_fit` | 54 x 9 x 34 |
| `coupon_logo_retention` | 25.2 x 20 x 24 |
| `coupon_handle_lock` | 66.4 x 48 x 23 |
| `coupon_wifi_dock` | 17.9 x 120 x 42 |
| `coupon_mac_button_recess` | 54 x 58 x 12 |
| `coupon_router_rf_access` | 110 x 3.2 x 46 |

## Parameter reference

### Enclosure and fit

| Parameter group | Defaults | Meaning |
| --- | --- | --- |
| `width`, `depth`, `height` | 165, 165, 280 | Fixed exterior |
| `target_height_ratio` | 1.70 | Height/width target |
| `wall`, `minimum_wall` | 3.2, 2.4 | Named shell/wall controls |
| `outer_corner_radius`, `inner_corner_radius` | 24, 20.8 | Main radii |
| `base_height`, `foot_height`, `cap_height` | 14, 5, 12 | Vertical modules |
| `lower_shell_top`, `shell_top`, `shadow_gap` | 105, 268, 0.8 | Split/cap datums |
| `rear_opening_width`, `rear_opening_bottom/top` | 120, 18/252 | Shell service opening |
| `rear_panel_width/height/thickness/radius` | 132/236/3.2/8 | Rear service panel |
| `equipment_clearance` | 1.5 | Nominal equipment gap |
| `sliding_fit_per_side` | 0.30 | General sliding/seam-key fit |
| `service_panel_per_side` | 0.35 | Panel/lip coupon fit |
| `logo_panel_per_side` | 0.25 | Logo receiver clearance |
| `handle_lock_per_side` | 0.35 | T-lock clearance |
| `wifi_clip_radial` | 0.45 | Antenna capture allowance |
| `snap_feature_per_side`, `insert_pilot_allowance` | 0.20, -0.15 | Reserved references; actual mechanisms/coupon variants have explicit geometry |

### Equipment and cable references

| Parameter group | Defaults | Meaning / evidence boundary |
| --- | --- | --- |
| Mac `width/depth/height/radius/mass` | 127/127/50/12; 0.67 kg | Controlled placeholder |
| Mac `support_plane_z`, `center_y` | 24, -8 | Placement |
| Mac button edge offsets/diameter/free gap | 13.5/13.5/11/0.75 | Photo-derived |
| Mac intake inner/outer diameters | 100/112 | Photo-derived exclusion annulus |
| Mac plug depth/clearance height | 34/24 | Provisional volumes |
| Mac base pad seat/pad thickness | 1 / 2 | Three active seats; actual pad compression/contact pending |
| Mac Z-retention stations | Y offsets -17/+17 on both X sides | Four clip/cams; 1.2 nominal top gap; two linked bottom-release rails |
| Router `width/depth/height/mass` | 100/93.7/30; 0.319 kg | Official body envelope / published mass |
| Router centre X/Y and tray Z | 0/28; 151 | Rear-biased packaging |
| RF connector depth/pitch/access diameter | 36/14.8/14 | Official centres; provisional connected access volume |
| RJ45 clearance W/H/depth | 18/16/40 | Provisional extension/plug volume |
| Router support pad W/D/T/compression | 8/16/1.3/0.4 | Four provisional compliant pads/lands; underside and preload unverified |
| APV case L/W/H | 84/57/29.5 | Datasheet placeholder |
| APV longitudinal mounting delta / fixing hole | 98.6 / diameter 3.6 | Supplier drawing coordinates; actual unit check required |
| APV leads | 150 +/-10 long; 3.5 controlled diameter | Datasheet length; simplified clearance solids |
| Cable/coax minimum bend radius | 18 / provisional 20 | Recorded assumptions only; builders do not create tolerance-complete swept cables |

### Power compartment

| Parameter group | Defaults | Meaning |
| --- | --- | --- |
| Outer W/D/H | 72/120/44 | Nominal closed box; rear island/tunnel adds depth to bbox |
| Wall/bottom/cover | 2.4/2.8/2.8 | Mechanical containment geometry only |
| Centre X/Y; bottom Z | -35/8; 83 | Placement |
| DC grommet / Mac AC gland openings | diameter 9 / 12 | Hardware selection pending |
| Mac AC gland datum / reserved route | X -55, Y -33.5 / 6 wide stepped solid | Packaging reservation only; no selected conduit, branch hardware, protection, or electrical acceptance |
| Raised tie bridges | 14 x 7 x 5 outer; 8 x 3 strap tunnel | Two internal bridges over continuous nominal floor; physical restraint/electrical suitability pending |
| APV blind mounting pilots | 2 axes; diameter 4.2 x 3 deep | Aligned to supplier diameter-3.6 lug axes; 2.7 residual sealed floor; exact insert/fastener pending |
| Cover columns / screw | 4 full-height wall-tied columns; M3x8 provisional | Diameter-4.2 x 5.5 pilots; 5.2 nominal engagement through 2.8 cover |
| `mains_keepout_extra` | 4 | Packaging keep-out expansion, not an electrical clearance |

### Handle, Wi-Fi docks, and logo panels

| Parameter group | Defaults | Meaning |
| --- | --- | --- |
| Handle grip span/depth/height | 128/20/18 | Nominal grip |
| Rise; leg width/depth | 58; 18/26 | Printed handle |
| Anchor spacing | 108 | Lock centres at X `+/-54` |
| Tongue W/L/H; neck width | 15/24/6; 11 | Dual T-lock geometry |
| Socket length/depth | 30/6.4 | Cap interface |
| Rib thickness / lock boss diameter | 5/10 | Structural geometry |
| Complete mass / static factor | 1.8 kg provisional / 2.0 | Inputs for future test, not a rating |
| Handle detent diameter/deflection | 3.2/0.8 | Legacy/reserved values; current positive lock uses explicit lateral pawl geometry |
| Antenna length/base/stem | 91/30/12 | Photo-derived placeholder |
| Antenna hub/proximal/tip | 18/15/5 | Placeholder reference-solid sections |
| Dock backplate W/H/T | 36/98/3 | Recessed removable dock |
| Dock clip width/wall | 10/2.4 | Vertical-axis half-annulus clips |
| Dock opening angle | 74 degrees | Reserved target; explicit mouth geometry governs current model |
| Logo size/thickness/radius | 70/2.4/6 | Face geometry |
| Logo pocket depth/reveal/emboss | 1.6/0.8/0.8 | Appearance parameters |
| Logo centre Z / finger notch | 156 / diameter 8 | Placement/removal |
| Logo rail and detent fields | 5/2.6/54; diameter 2.8 | Legacy/reserved; current panels use four explicit push-in cantilever studs/hooks |

### Fasteners, inserts, and print

| Parameter group | Defaults | Meaning |
| --- | --- | --- |
| M3 screw stacks | M3x14 base; M3x10 cradle; low-head M3x6 router tray; M3x8 service/cover | Separate lengths prevent marginal engagement or blind-pilot bottoming; all provisional pending joint tests |
| Structural screw stack | M4x18 | Cap and shell-seam joints; provisional pending joint tests |
| M3/M4 clearance holes | diameter 3.4 / 4.5 | Modeled clearances |
| M3/M4 insert pilots | diameter 4.2 / 5.6 | Provisional heat-set holes |
| M3/M4 bosses | diameter 9 / 12 | Modeled support values |
| Insert depth | 5.5 | Provisional; supplier and coupon govern |
| Low-head M3 recess | diameter 6.2 x 1.8 deep | Four router-tray positions; exact screw head and seating pending |
| Printer build X/Y/Z | 256/256/256 | Bounding-cube check |
| Nozzle / line width / layer | 0.4/0.45/0.20 | Starting process |
| Body wall lines / prototype material | 7 / ASA | Starting point only; thermal/electrical review governs final materials |

The parameter file centralizes intended design inputs, but a field can be a reserved design value or placeholder. Only geometry actually consumed by builders and the exact validations reported in [validation_results.md](validation_results.md) should be treated as computationally checked.
