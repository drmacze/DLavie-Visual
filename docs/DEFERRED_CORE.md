# DLavie Visual Deferred Core

DLavie Visual 4.6 targets Minecraft Bedrock's current **Vibrant Visuals deferred PBR pipeline**. There is no separate `deferred` manifest capability in the current public resource-pack path; the correct opt-in remains `"pbr"`.

## What 4.6 adds

- Expanded colored local-light mappings for 100+ current vanilla luminous block states and variants.
- Quality-aware lighting cost: High promotes selected small light sources to `point_light`, Medium keeps only the most useful dynamic sources, and Low favors `static_light` for mobile performance.
- Explicit water `sampleWidth` values for Low / Medium / High (`0.18 / 0.13 / 0.09`) while preserving DLavie's existing depth absorption, optical caustics, volumetric underwater scattering and 7 / 14 / 20 minimum wave-octave targets.
- Existing PBR compatibility is preserved: external Texture Sets remain authoritative for metalness, emissive, roughness, subsurface and normal/height data.
- Existing sky IBL remains responsible for indirect diffuse/specular lighting, while SSR behavior remains material-driven by the external PBR resource pack.
- Natural-Medium root failsafe receives the same deferred local-light and water sampling data as the selectable subpack.

## Project boundary

This repository remains a **visual/shader core**. It intentionally contains no block albedo, normal, AO, MERS or block Texture Sets. A separate texture/material project should own those assets.

## Refined Deferred reference pack

The user supplied `Refined Deferred v3.2.0` by **XiaoCraft** as a behavioral reference while designing this pass. The pack was inspected to understand its resource-pack architecture and current vanilla light coverage. DLavie 4.6 does **not** redistribute its block textures, Texture Sets, particle assets, caustics or JSON files; colors and tuning in DLavie are independently authored.

The reference also contains an undocumented `sun_rays` lighting field. DLavie deliberately does not depend on that field because it is not present in the current public Mojang lighting schema. DLavie's light shafts continue to use supported atmosphere + volumetric fog/Henyey-Greenstein controls so the build remains schema-safe on retail Bedrock.
