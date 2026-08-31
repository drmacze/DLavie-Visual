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

The runtime 60-frame caustics atlas can use the supplied Derivative source when it is
available to the build; public CI has a deterministic low-contrast fallback with the
same 60x128 frame layout. The cirrus density map is a deterministic Bedrock
reconstruction following Derivative's Profile.Derivative cirrus mode rather than a
copy of Java-only cloud LUT data.
