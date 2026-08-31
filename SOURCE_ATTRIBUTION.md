# Source attribution

DLavie Visual is a Bedrock/Vibrant Visuals adaptation informed by the uploaded
**Derivative 25.1.0** shader source and its DERCODE License Agreement 2.5.

Original DC authors required by that license:

- _DureXXX
- M1zore
- Skeeder461
- Frs0n
- _Sone4ka_

Original project: https://www.curseforge.com/minecraft/shaders/derivative-main

DC/Derivative Discord link referenced by the supplied source:
https://discord.gg/VsNs9xP

The original DERCODE 2.5 license is preserved verbatim in
`THIRD_PARTY_LICENSES/DERCODE-License-2.5.txt`.

## What is and is not copied

The Java GLSL programs and Java-only atmosphere/cloud LUT binaries are **not** shipped
inside the Bedrock pack because RenderDragon/Vibrant Visuals cannot execute or sample
them through the retail resource-pack pipeline. DLavie Visual translates Derivative's
profile values and visual systems into Bedrock-supported atmosphere, lighting, fog,
PBR fallback, local lights, shadows, water, color grading, environment textures, and
per-biome bindings.

The runtime water caustics can use the **original Derivative 25.1.0 60-frame 128×128 atlas**
from the supplied source. When the supplied source asset is present, the build copies it
byte-for-byte into `textures/dlavie/derivative_caustics.png`; public CI falls back to a
deterministic 60-frame atlas if that private build input is absent. The cirrus texture
itself is a deterministic Bedrock reconstruction because Derivative's Java cloud
LUT/noise pipeline cannot be executed by retail RenderDragon.

## Runtime source asset

A local `third_party_runtime/Derivative_Caustics.png` can hold the original Derivative
25.1.0 caustics atlas from the supplied source. If distributed, that asset remains
covered by DERCODE 2.5 plus the author credits above.
