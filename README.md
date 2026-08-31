# DLavie Visual

![DLavie Visual cover](branding/cover.svg)

**DLavie Visual** is a Minecraft Bedrock **Vibrant Visuals shader/visual core** for the 26.x renderer line, with **Bedrock 26.45** as the primary target and **1.26.40** as the compatibility floor.

## 4.5 visual-only architecture

DLavie Visual is deliberately separated from the future DLavie texture project. This repository **does not ship custom block albedo, normal, AO or MERS Texture Sets**. Block/material textures belong in a separate project so shader development and texture development can evolve independently.

The visual pack focuses on renderer-facing systems only:

- PBR-friendly global fallback behavior and stronger sky IBL/specular support for external realistic texture packs,
- custom sun/moon lighting and time-of-day response,
- violet twilight and very dark midnight transitions,
- atmosphere scattering and low-sun glare/godray character,
- realistic height/weather volumetric fog,
- Henyey-Greenstein directional scattering for light shafts,
- interactive storm haze and cloud optical media,
- ACES color grading,
- biome-specific lighting/fog/grading,
- Nether and End lighting/fog/grading,
- dynamic/local light color and quality control,
- advanced water waves, depth absorption, underwater scattering and optical caustics,
- smooth underwater transition fog,
- ore local-light color/type hooks without changing vanilla gameplay emission,
- shadow quality scaling,
- visual environment assets such as sun, moon, cirrus, rain and snow.

## PBR compatibility / realistic resource packs

4.5 is tuned specifically so DLavie can sit on top of a separate realistic Bedrock PBR resource pack without replacing that pack's material data.

- DLavie keeps the `pbr` capability enabled.
- It ships **zero block Texture Sets**, so a realistic pack remains the owner of its albedo, normal/height and MERS material maps.
- `pbr/global.json` is now a conservative fallback only: non-PBR blocks remain rough, non-metallic and non-emissive instead of being forced into a shiny plastic look.
- Daytime **sky intensity/IBL is raised** relative to 4.4 so authored metallic and low-roughness materials receive stronger sky reflections and specular response.
- Ambient illuminance stays low, preserving directional-light contrast so normal maps read as real surface depth instead of being washed out by fill lighting.
- Night keeps a smaller sky IBL contribution so PBR materials can still catch moon/sky reflections without making midnight bright.
- Emissive desaturation is reduced so emissive maps from external PBR packs keep their authored color more faithfully.

For a typical resource stack, put **DLavie Visual above the realistic PBR texture pack**. DLavie then owns lighting/atmosphere/fog/water/grading while the lower pack owns its block textures and Texture Sets. If the other pack also ships its own renderer JSON files, normal resource-stack priority applies to those overlapping files.

See [`docs/PBR_COMPATIBILITY.md`](docs/PBR_COMPATIBILITY.md) for the full compatibility policy and test scenes.

## Three visual moods × three quality levels

The pack exposes **nine selectable visual subpacks**:

| Mood | Character |
|---|---|
| **Natural** | realistic neutral daylight, purple-blue dusk, balanced atmosphere, clean water and dark natural night |
| **Cozy** | warmer low sun and interiors, amber local lights, rose-violet twilight and softer golden haze |
| **Gloomy** | cooler/desaturated daylight, deeper violet dusk, darker ambient fill, denser eerie fog and near-black midnight |

Each mood has **Low / Medium / High**. Quality changes renderer cost and visual depth, not block textures. High uses richer sky IBL, deeper shadow/ambient separation, stronger atmosphere, richer fog/water scattering, more water octaves and broader point-light use; Medium is the mobile baseline; Low is the performance path.

## Advanced underwater lighting

- Separate chlorophyll, suspended sediment and CDOM values are kept for default, river, ocean, swamp and frozen profiles.
- High-quality water pushes strong forward-scattering so surface sunlight reads as directional underwater shafts instead of uniform haze.
- Absorption remains depth dependent: blue/green wavelengths travel farther in clean ocean water while swamp water loses visibility much sooner.
- Entering water uses a smooth transition profile instead of snapping immediately to a flat fog color.
- Optical caustics remain a 60-frame 128px atlas and scale to 7 / 14 / 20 wave octaves for Low / Medium / High.

## Cinematic twilight and midnight

Generated Overworld lighting uses **lighting schema `1.26.0`**, allowing time-keyframed ambient light and sky intensity.

- Sunset passes through rose/violet and then deep indigo instead of jumping directly from orange to generic blue.
- Midnight has its own dark navy/near-black sky.
- Ambient illumination and sky contribution decrease after twilight, while 4.5 retains enough night IBL for physically based specular response.
- Natural remains readable, Cozy keeps a warmer violet transition, and Gloomy becomes the darkest at midnight.

## Ore lighting hooks

`local_lighting/local_lighting.json` contains color/type hooks for common Overworld and Nether ores. High uses point-light type hooks; Low/Medium use cheaper static-light types.

This is deliberately **not advertised as fake full emissive ore texturing**. Visible emissive ore pixels/bloom still require emissive material data, and vanilla ore blocks do not emit gameplay light by default. Those material assets belong in the separate texture/material project.

## Interactive weather

Active rain/snow receives its own `weather` volumetric density instead of permanently thickening clear-air fog. Weather distance haze begins earlier during storms, cloud media has independent scattering/absorption, and forest/jungle/swamp/ocean/dry profiles respond differently to overcast conditions.

**Wet blocks and reflective puddles are intentionally not faked in this repository.** Correct wet-surface material masks belong in the separate DLavie texture/material project or would require a non-standard renderer hook.

## Lighting architecture

Eight Overworld visual profiles are generated: default, forest, dense forest/jungle, dry/desert, cold/snow, swamp, cave/deep-dark and ocean. Each can have separate lighting, atmosphere, fog and color grading. Nether and End also receive their own visual treatment.

## Installation

1. Import `DLavie-Visual.mcpack` into Minecraft.
2. Remove/disable older DLavie builds to avoid cached resources.
3. If using a realistic PBR pack, enable that pack and place **DLavie Visual above it** in the world resource stack.
4. Use the pack gear icon to select Natural/Cozy/Gloomy plus Low/Medium/High.
5. Enable **Vibrant Visuals** in Settings → Video on supported hardware.

For iPhone 11, start with **Natural • Medium** around 8–12 chunks. High is intended for stronger IBL/reflection depth but costs more GPU time.

## Build

Requirements: Python 3, Pillow and NumPy.

```bash
python3 -m pip install Pillow numpy
./tools/build.sh
```

The build regenerates renderer configs, visual environment assets and optical caustics, expands all nine visual subpacks, then runs visual-core, volumetric-fog, weather/water, underwater/night and PBR-compatibility passes before validation. Validation enforces **zero block textures/Texture Sets**, checks 1.26.0 time keyframes, verifies conservative global PBR fallbacks and confirms the PBR-friendly sky IBL targets.

## Derivative source / license

The supplied Derivative 25.1.0 Java shader remains an art-direction/reference source for parts of DLavie's atmosphere, water and lighting work. A literal Iris/OptiFine GLSL port is not possible on retail Bedrock because those shader entry points are not exposed by RenderDragon. The supplied Derivative source is covered by **DERCODE License Agreement 2.5**; its license and required author attribution are preserved in this repository.

## Compatibility statement

DLavie uses supported Bedrock/Vibrant Visuals resource-pack interfaces rather than patched APK/IPAs or private RenderDragon injection. CI verifies pack structure and visual resources; final visual calibration, thermals and FPS still require physical Android/iPhone testing.
