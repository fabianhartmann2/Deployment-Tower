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
| Mac mini placeholder | `(0,-8,41)` | 127 x 127 x 50 overall | X `-63.5..63.5`; Y `-71.5..55.5`; Z `16..66`; 42 mm retained square body above support plane plus 8 mm central underside drop |
| Mac support plane | `Z=24` | — | 10 above nominal base top `Z=14` |
| APV case placeholder | `(-35,8,103.55)` | 57 X x 84 Y x 29.5 Z | X `-63.5..-6.5`; Y `-34..50`; Z `88.8..118.3` |
| APV/mains box | centre `(-35,8,105)` | nominal 72 x 120 x 44 | X `-71..1`; Y `-52..68`; Z `83..127`; fixed rear island/tunnel extends overall design bbox depth to 134.5 |
| Low-voltage lane | `(48,0,116)` | 34 x 122 x 76 | X `31..65`; Y `-61..61`; Z `78..154` |
| Mac-AC reserved corridor | gland datum `(-55,-33.5,83)` toward provisional Mac AC | stepped 6 wide packaging solid | Approximate bbox X `-75.3..42`; Y `-36.5..68.5`; Z `38..83`; side run remains above the extended cradle-release rail; no physical conduit or electrical release implied |
| Router tray datum | `Z=151` | 3 thick plate | Shell-supported fasteners; guide/retainer geometry extends above the plate |
| RUTM30 official STEP | `(0,28,170.5)` | 100 x 93.7 x 30 | X `-50..50`; Y `-18.85..74.85`; Z `155.5..185.5` |
| Handle anchor reference | `Z=260` | centres at X `+/-54`, Y `-42` | Cap lock geometry near fixed-body top |

The Mac, APV, antennas, C8, extensions, plugs, and cable ranges are controlled placeholders. Only the RUTM30 body is imported from official STEP.

## Shell, panels, and interfaces

| Feature | Current default |
| --- | ---: |
| Base | 14 high total; 5 high feet; visible skin inset 1.5 per side |
| Shell split | lower nominal top `Z=105`; 0.8 shadow gap; upper shell to `Z=268` |
| Structural shell seam | Six hidden vertical M4 axes: X `±76.8`, Y `-50/10/50`; Ø10.4 local bosses/lugs, Ø8.2 x 3.2 internal low-head pockets for measured Ø7.0 heads, 8.4-wide internal entry slots, Ø5.5 top-driver corridors; no exterior openings |
| Rear lower sill | Existing 4 mm sill reinforced internally by a 145 x 11 x 4 flange and 145 x 4 x 10 web; rear-panel seat and Mac-button path recut clear |
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
| Logo faces | 70 x 70 x 2.4, radius 6, centre `Z=156`, 0.8 reveal; two outward-accessible M3 axes each at Y `+/-25` |
| Wi-Fi dock backplates | 36 x 98 x 3, centre `(Y,Z)=(53,216)` on each side; two M3 positions per dock |

`finger_well_reach=38` controls the isolated button coupon. The installed base and cradle derive their longer clearances from the provisional button and rear-face coordinates.

## Exported printable-part bounding boxes

These are assembly-coordinate STEP bounding boxes. Hooks, bosses, clips, and retainers can make them larger than their nominal face/plate values.

| Part | Design bbox X x Y x Z |
| --- | ---: |
| `base` | 162 x 162 x 14 |
| `mac_cradle` | 152 x 137 x 51.2, including four lowered Z-retention clips and two extended release rails |
| `lower_shell` | 165 x 165 x 97 |
| `upper_shell` | 165 x 164.9531 x 162.6 |
| `router_tray` | approximately 120 x 98.9 x 37.5, including the two rear insert towers |
| each `router_rear_retainer_*` | approximately 15 x 8.7 x 10.5; separate slotted rear corner stop |
| `power_compartment` | 72 x 134.5 x 44 |
| `power_compartment_cover` | 72 x 120 x 4.8 |
| `rear_panel` | 132 x 3.2 x 236 |
| `router_interface_bezel` | 119 x 8.8 x 78 |
| `upper_cap` | 165 x 165 x 12 |
| `removable_handle` | 150 x 32 x 76 |
| each `wifi_dock_*` | 17.85 x 36 x 98 |
| each installed/blank logo panel | 2.4 x 70 x 70 |
| example embossed logo panel | 3.2 x 70 x 70 |
| Mac compliant-pad template | 14.6 x 14.6 x 2 |
| router compliant-pad template | 8 x 16 x 1.3 |

## Exported coupon bounding boxes

| Coupon | Design bbox X x Y x Z |
| --- | ---: |
| `coupon_c8_cutout` | 55 x 3.2 x 35 |
| `coupon_insert_boss` | 46 x 28 x 14 |
| `coupon_m4_seam_insert` | 54 x 24 x 16; three vertical Ø5.4/5.6/5.8 pilot bosses |
| `coupon_rear_panel_fit_v2` | 120 x 22.5 x 37; upright receiver plus flat insert |
| `coupon_logo_mount` | 23.2 x 32 x 18 |
| `coupon_handle_mount` | 100 x 36 x 12 |
| `coupon_wifi_dock_v2` | 17.9 x 120 x 42 |
| `coupon_mac_button_recess` | 54 x 58 x 12 |
| `coupon_router_rf_access` | 110 x 3.2 x 46 |
| `coupon_rear_io_v1` | 180 x 3.2 x 45; Ethernet/HDMI/USB-C/candidate-C8 strip |
| `coupon_rear_io_mount_v2` | 180 x 31.2 x 50; corrected Ethernet/C8 plus inside USB bosses and top-down HDMI shelf |
| `coupon_rear_io_mount_v3` | 180 x 31.2 x 50; v2 mounting layout with M3 rather than M4 HDMI insert pilots |
| `coupon_rf_bulkhead_v1` | 78 x 3.2 x 50; six RF trials at two local wall thicknesses |
| `coupon_logo_magnet_v1` | 16.4 x 110 x 35 design compound; separate blind-pocket receiver and steel-recess panel |
| `coupon_logo_magnet_v2` | 16.4 x 110 x 35 design compound; 3 mm shell magnets opposed by 1.5 mm panel magnets |
| `coupon_cap_dovetail_v1` | 56 x 18 x 11 design compound; six separately packed rail/slider bodies |
| `coupon_cap_dovetail_v2` | 56 x 18 x 11 design compound; 0.05/0.10/0.15 mm-per-side rail/slider pairs |

### Pending v4 measured-interface coupon parameters

| Parameter group | Defaults | Meaning |
| --- | --- | --- |
| Ethernet opening / pitch / inner body | 17 x 14 / 27.6 / 22 x 23 x 42 | Owner-measured downward-cable adapter; coupon adds 0.20 mm per cutout side and 0.20 mm diametral hole allowance |
| HDMI opening / pitch / inner body / bend space | 16 x 6 / 27 / 19 x 13 x 13 / 45 | A6-A8T owner measurement; final inner support awaits coupon result |
| USB-C opening / shell rebate / oval pitch | 10 x 4 / 12 x 5 x 1.75 / 19 | T9B-T8T-NC 20P; two identical production interfaces intended |
| Candidate C8 opening / pitch / first envelope | 21 x 12.5 / 29 / 35.5 x 15.1 x 3 | Mechanical coupon only; no mains approval implied |
| RF bulkhead trials | diameter 6.6/6.8/7.0; wall 3.2/2.0 | Select actual SMA-mobile and RP-SMA-Wi-Fi fit/thread stack physically |
| Logo magnet pocket / skins | shell Ø6.2 x 3.2 behind 0.6; panel Ø6.2 x 1.7 leaving about 0.7 | Magnet-to-magnet v2 trial; recessed panel positions itself; no finger notch |
| Cap dovetail clearances | v1 0.25/0.35/0.45; v2 0.05/0.10/0.15 per side | One/two/three-notch coupon pairs; final positive lock and load path not yet modeled |
| DC/DC reserved envelope | 71 x 36 x 25 | 24 V/1 A owner-supplied module; mount, terminals, thermal and electrical role unresolved |

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
| Seam axes / boss / lug | X ±76.8; Y -50/10/50; Ø10.4; 11 high | Six hidden internal M4 joints distributed along the side walls |
| Seam head / pocket / entry / driver | measured Ø7.0 / Ø8.2 x 3.2 / 8.4 wide / Ø5.5 | 0.6 radial head relief plus explicit lateral insertion and top tool access; 1.6 mm local closed exterior skin remains behind the pocket |
| `rear_opening_width`, `rear_opening_bottom/top` | 120, 18/252 | Shell service opening |
| `rear_panel_width/height/thickness/radius` | 132/236/3.2/8 | Rear service panel |
| `equipment_clearance` | 1.5 | Nominal equipment gap |
| `sliding_fit_per_side` | 0.30 | General sliding/seam-key fit |
| `service_panel_per_side` | 0.35 | Power-cover internal relief; independent of calibrated rear-panel seat |
| `rear_panel_x_per_side`, `rear_panel_z_per_side` | 0.15, 0.05 | Calibrated rear-panel seat allowances; v2 physical fit reported passed |
| `logo_panel_per_side` | 0.25 | Logo receiver clearance |
| `wifi_clip_radial` | 0.50 | Antenna capture allowance selected by the three-marker physical coupon |
| `snap_feature_per_side`, `insert_pilot_allowance` | 0.20, -0.15 | Reserved references; actual mechanisms/coupon variants have explicit geometry |

### Equipment and cable references

| Parameter group | Defaults | Meaning / evidence boundary |
| --- | --- | --- |
| Mac `width/depth/height/radius/mass` | 127/127/50/12; 0.67 kg | Controlled placeholder |
| Mac `support_plane_z`, `center_y`, underside drop/retained-body height | 24, -8, 8/42 | Placement revised from the full-cradle physical trial while preserving 50 mm overall height |
| Mac button side/edge offsets/diameter/free gap | rear-left; 13.5/13.5/11/0.75 | Handedness physically corrected; exact centre remains photo-derived |
| Mac intake inner/outer diameters | 100/112 | Photo-derived exclusion annulus |
| Mac cradle side clearance / central opening | 0.30 per side / diameter 112 | Selected from the first full-cradle physical trial; opening reduced 4 mm |
| Mac plug depth/clearance height | 34/24 | Provisional volumes |
| Mac base pad seat/pad thickness | 1 / 2 | Three active seats; actual pad compression/contact pending |
| Mac Z-retention stations | Y offsets -17/+17 on both X sides | Four clip/cams lowered 8 mm to the 42 mm retained body; 1.2 nominal top gap; two linked bottom-release rails with 7.5 mm outreach |
| Router `width/depth/height/mass` | 100/93.7/30; 0.319 kg | Official body envelope / published mass |
| Router centre X/Y and tray Z | 0/28; 151 | Rear-biased packaging |
| RF connector depth/pitch/access diameter | 36/14.8/14 | Official centres; provisional connected access volume |
| RJ45 clearance W/H/depth | 18/16/40 | Provisional extension/plug volume |
| Router support pad W/D/T/compression | 8/16/1.3/0.4 | Four provisional compliant pads/lands; underside and preload unverified |
| Router physical fit corrections | side guides inward 1.0; top ledges down 0.6 | Responds to measured 1.3 mm side play per side and 1.0 mm top play; predicts about 0.3 mm physical side clearance |
| Router rear stops | two separate 4 mm-thick corner stops; ±1.0 adjustment | Screw-retained after router insertion; rear contact datum corrected about 4.2 mm forward from the broken flexure centre while preserving 0.3 mm clearance to the official chassis |
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
| Cover bosses / screw | 4 wall-tied upper bosses, 12.0 high; M3x8 provisional | Diameter-4.2 x 5.5 pilots; 5.2 nominal engagement through 2.8 cover |
| Lower-shell mounting access | 4 floor bores at the unchanged lower-shell axes | Diameter-3.4 through bores; diameter-6.2 screw-head and diameter-4.5 driver corridors verified open |
| `mains_keepout_extra` | 4 | Packaging keep-out expansion, not an electrical clearance |

### Handle, Wi-Fi docks, and logo panels

| Parameter group | Defaults | Meaning |
| --- | --- | --- |
| Handle grip span/depth/height | 128/20/18 | Nominal grip |
| Rise; leg width/depth | 58; 18/26 | Printed handle |
| Anchor spacing | 108 | Leg/foot centres at X `+/-54` |
| Foot W/D/T | 42/32/5 | Broad cap bearing area; screw heads seat on the unrecessed top surface; 7 mm screw-centre edge distance |
| Fastener offset | `+/-14` from each anchor | Four M3 axes at X `-68,-40,+40,+68`, Y `-42` |
| Rib thickness | 5 | Structural geometry |
| Complete mass / proof-load factor | 1.8 kg provisional / 4.0 | 70.6 N provisional test target; not a rating |
| Antenna length/base/stem | 91/30/12 | Photo-derived placeholder |
| Antenna hub/proximal/tip | 18/15/5 | Placeholder reference-solid sections |
| Dock backplate W/H/T | 36/98/3 | Recessed removable dock |
| Dock clip width/wall | 10/2.4 | Vertical-axis half-annulus clips |
| Dock rounded lip radius/intrusion | 1.0 / 0.75 per side | Selected production cavity/mouth 31.0/29.5 for measured Ø30.0 hub; 0.25 nominal arm movement per side |
| Logo size/thickness/radius | 70/2.4/6 | Face geometry |
| Logo pocket depth/reveal/emboss | 1.6/0.8/0.8 | Appearance parameters |
| Logo centre Z / finger notch | 156 / diameter 8 | Placement/removal |
| Logo fastener offset | Y `+/-25` | Two outward-accessible M3 screws per panel into shell-webbed blind inserts |

### Fasteners, inserts, and print

| Parameter group | Defaults | Meaning |
| --- | --- | --- |
| M3 screw stacks | M3x14 base; M3x10 cradle/handle; low-head M3x6 router tray; M3x8 router stops/logo/service/cover | Separate lengths prevent marginal engagement or blind-pilot bottoming; all provisional pending joint tests |
| Structural screw stack | M4x18 | Cap and shell-seam joints; provisional pending joint tests |
| M3/M4 clearance holes | diameter 3.4 / 4.5 | Modeled clearances |
| M3/M4 insert pilots | diameter 4.2 / 5.4 | Physically selected heat-set holes; M4 one-notch vertical coupon reported best fit |
| M3/M4 bosses | diameter 9 / 12 general; seam M4 diameter 10.4 | Modeled support values; seam rings are integrated into paired U-belts |
| Insert depth | 5.5 | Provisional; supplier and coupon govern |
| Low-head M3 recess | diameter 6.2 x 2.2 deep | Four router-tray positions; leaves 0.8 mm floor and about 0.7 mm under-router clearance for the measured 3.0 mm-high heads |
| Printer build X/Y/Z | 256/256/256 | Bounding-cube check |
| Nozzle / line width / layer | 0.4/0.45/0.20 | Starting process |
| Body wall lines / prototype material | 7 / ASA | Starting point only; thermal/electrical review governs final materials |

The parameter file centralizes intended design inputs, but a field can be a reserved design value or placeholder. Only geometry actually consumed by builders and the exact validations reported in [validation_results.md](validation_results.md) should be treated as computationally checked.
