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

The Java GLSL programs are **not** shipped inside the Bedrock pack because
RenderDragon/Vibrant Visuals does not execute Iris/OptiFine GLSL. DLavie Visual
translates the source shader's visual intent and default values into Bedrock's
supported data-driven systems: atmospheric scattering, global/directional
lighting, volumetric fog, PBR fallback materials, point lights, shadows, water,
color grading, environment textures, and per-biome bindings.
