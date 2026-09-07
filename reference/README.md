# External CAD reference

`0112_RUTM30AMBKX_02.STEP` is the native AP214 model supplied by Teltonika in
the official RUTM30 spatial-measurement archive:

https://wiki.teltonika-networks.com/images/d/d4/Networking_rutm30_manual_spatial_measurements_3d.zip

The archive was retrieved on 2026-09-07.  The model identifies itself as a
SolidWorks 2024 export and contains 37 solids.  Its measured bounding box is
100.0000 x 30.0000 x 93.6999 mm in supplier X/Y/Z axes, matching the published
100 x 30 x 93.7 mm housing dimensions.  `components.py` rotates it into station
X=width, Y=depth, Z=height coordinates and retains it as non-printable reference
geometry.

No official STEP was supplied for the Mac mini, APV-35-36, antennas, or cable
overmoulds.  Their controlled envelopes and uncertainty are documented in
`reports/assumptions.md`.
