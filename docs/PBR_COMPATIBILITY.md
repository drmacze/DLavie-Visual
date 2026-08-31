# DLavie Visual 4.5 — PBR Compatibility

DLavie Visual is a **renderer/visual core**, not a block texture pack. It intentionally ships no `textures/blocks/*` assets and no `*.texture_set.json` files.

## What 4.5 changes

- keeps the `pbr` capability active on the visual pack;
- raises calibrated daytime sky intensity so external PBR materials receive stronger image-based lighting (IBL) and specular reflections;
- keeps ambient illuminance low so normal-map depth and directional sunlight remain visible instead of being flattened by fill light;
- preserves a small night-sky IBL contribution so metallic/wet materials can still catch moon/sky reflections without making midnight bright;
- lowers emissive desaturation so emissive maps from external packs keep their authored color;
- changes global PBR fallback values to deliberately rough, non-metallic, non-emissive defaults so vanilla/non-PBR surfaces do not become fake mirrors;
- does not generate, merge, replace or reference external Texture Sets.

## External PBR pack behavior

A compatible Bedrock PBR texture pack should own its own color/albedo and Texture Set resources, including normal or height data plus MERS material data. Those material values take precedence for textures that actually provide a Texture Set; DLavie's `pbr/global.json` is only the fallback for surfaces that do not provide one.

For a typical setup, place **DLavie Visual above the PBR texture pack** in the resource stack. DLavie then keeps control of lighting, atmosphere, fog, water and grading while the lower texture pack owns block textures and their PBR Texture Sets. If another pack also ships its own `lighting/`, `fogs/`, `water/` or `atmospherics/` files, normal resource-stack priority rules apply to those overlapping files.

## Reflection behavior

Vibrant Visuals uses sky/image-based lighting and screen-space reflections. Roughness and metalness authored by the texture pack determine how strongly a surface reflects. DLavie 4.5 intentionally avoids forcing those values globally when a valid Texture Set is present.

Very rough materials should remain matte. Smooth non-metals can show dielectric reflections. Metallic materials can use their authored metalness and roughness values. Transparent geometry still follows Bedrock renderer limitations; glass does not gain full SSR behavior simply because DLavie is active.

## Recommended test scenes

1. polished/metallic blocks outdoors at noon to verify sky IBL and SSR;
2. rough stone next to polished stone to verify roughness separation;
3. walls with strong normal maps under low-angle sunlight to verify depth response;
4. emissive blocks at night to verify authored emissive colors are preserved;
5. wet-looking PBR materials near water to check reflection balance;
6. cave scenes with local lights to confirm normals remain readable without excessive ambient fill.

## Project boundary

If a future DLavie texture/material project is enabled, it may provide its own albedo, normals, MERS, emissive and wet-surface material data. This repository will remain the visual/shader side so PBR texture development can evolve independently.
