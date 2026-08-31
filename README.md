# DLavie Visual

![DLavie Visual cover](branding/cover.svg)

**DLavie Visual** is a Minecraft Bedrock **Vibrant Visuals shader/visual core** for the 26.x renderer line, with **Bedrock 26.45** as the primary target and **1.26.40** as the compatibility floor.

## 4.4 visual-only architecture

DLavie Visual is deliberately separated from the future DLavie texture project. This repository **does not ship custom block albedo, normal, AO or MERS Texture Sets**. Block/material textures belong in a separate project so shader development and texture development can evolve independently.

The visual pack focuses on renderer-facing systems only:

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

## Three visual moods × three quality levels

The pack exposes **nine selectable visual subpacks**:

| Mood | Character |
|---|---|
| **Natural** | realistic neutral daylight, purple-blue dusk, balanced atmosphere, clean water and dark natural night |
| **Cozy** | warmer low sun and interiors, amber local lights, rose-violet twilight and softer golden haze |
| **Gloomy** | cooler/desaturated daylight, deeper violet dusk, darker ambient fill, denser eerie fog and near-black midnight |

Each mood has **Low / Medium / High**. Quality changes renderer cost and visual depth, not block textures. High uses deeper shadow/ambient separation, stronger atmosphere, richer fog/water scattering, more water octaves and broader point-light use; Medium is the mobile baseline; Low is the performance path.

## Advanced underwater lighting

4.4 strengthens the underwater path without introducing block textures.

- Water keeps separate chlorophyll, suspended sediment and CDOM values for default, river, ocean, swamp and frozen profiles.
- Water volumetric media now pushes stronger forward-scattering at higher quality, reaching roughly `g=0.9` in clear High ocean water so surface sunlight reads as directional underwater shafts instead of uniform haze.
- Absorption remains depth dependent: blue/green wavelengths travel farther in clean ocean water while swamp water loses visibility much sooner.
- Entering water uses a smooth transition profile instead of snapping immediately to a flat fog color.
- Optical caustics remain a 60-frame 128px atlas and scale to 7 / 14 / 20 wave octaves for Low / Medium / High.
- High caustics use a faster animation and stronger projection so shallow-water refraction is easier to read on terrain.

## Cinematic twilight and midnight

4.4 migrates generated Overworld lighting files to **lighting schema `1.26.0`**, which is the schema where Bedrock officially supports time-keyframed ambient light and sky intensity.

- Sunset no longer jumps from orange directly into generic blue. It passes through rose/violet, then deep indigo.
- Midnight receives a dedicated dark navy/near-black sky instead of reusing the dusk palette.
- Ambient illumination and sky contribution continue decreasing after twilight, giving caves, forests and unlit terrain much stronger separation at midnight.
- Natural remains readable, Cozy keeps a subtle warmer violet transition, and Gloomy becomes the darkest/most threatening at midnight.
- Moonlight remains cool and directional but is intentionally not strong enough to flatten the night scene.

## Ore lighting hooks

`local_lighting/local_lighting.json` now includes color/type hooks for the common Overworld and Nether ores (coal, iron, copper, gold, redstone, lapis, diamond, emerald, quartz, Nether gold and ancient debris). High uses point-light type hooks; Low/Medium use the cheaper static-light type.

This is deliberately **not advertised as fake full emissive ore texturing**. In the public Vibrant Visuals pipeline, local-light strength still comes from the block's `light_emission` component, while visible emissive ore pixels/bloom require emissive material data. Vanilla ore blocks have no gameplay emission, and this shader-only project does not override their textures or behavior. The hooks are present so a separate DLavie material/behavior project can supply emission later without changing this visual core.

## Interactive weather

Active rain/snow receives its own `weather` volumetric density instead of permanently thickening clear-air fog. Weather distance haze begins earlier during storms, cloud media has independent scattering/absorption, and forest/jungle/swamp/ocean/dry profiles respond differently to overcast conditions.

**Wet blocks and reflective puddles are intentionally not faked in this repository.** The public visual-only Vibrant Visuals resource-pack interfaces do not expose a dynamic per-block rain wetness/puddle mask. Correct wet-surface materials belong in the separate DLavie texture/material project (or would require a non-standard renderer hook).

## Lighting architecture

Eight Overworld visual profiles are generated: default, forest, dense forest/jungle, dry/desert, cold/snow, swamp, cave/deep-dark and ocean. Each can have separate lighting, atmosphere, fog and color grading. Nether and End also receive their own visual treatment.

The visual-core pass deepens the difference between direct sunlight, sky fill and ambient light. This is specifically intended to avoid the flat "vanilla Vibrant Visuals with different values" look from earlier DLavie versions.

## Texture-pack compatibility

DLavie Visual intentionally contains **zero block Texture Sets**. A separate texture/PBR project can be stacked with DLavie later and own its albedo/normal/MERS/wetness/emissive data correctly. Textures without their own Texture Sets continue to use the safe global PBR fallback supplied by the renderer config.

## Installation

1. Import `DLavie-Visual.mcpack` into Minecraft.
2. Remove/disable older DLavie builds to avoid cached resources.
3. Enable **DLavie Visual** in Global Resources or the world resource stack.
4. Use the pack gear icon to select Natural/Cozy/Gloomy plus Low/Medium/High.
5. Enable **Vibrant Visuals** in Settings → Video on supported hardware.

For iPhone 11, start with **Natural • Medium** around 8–12 chunks. Use Low while recording or if thermal throttling is noticeable.

## Build

Requirements: Python 3, Pillow and NumPy.

```bash
python3 -m pip install Pillow numpy
./tools/build.sh
```

The build regenerates renderer configs, visual environment assets and optical caustics, expands all nine visual subpacks, then runs visual-core, volumetric-fog, weather/water and underwater/night enhancement passes before validation. Validation enforces **zero block textures/Texture Sets** and checks the 1.26.0 midnight keyframes.

## Derivative source / license

The supplied Derivative 25.1.0 Java shader remains an art-direction/reference source for parts of DLavie's atmosphere, water and lighting work. A literal Iris/OptiFine GLSL port is not possible on retail Bedrock because those shader entry points are not exposed by RenderDragon. The supplied Derivative source is covered by **DERCODE License Agreement 2.5**; its license and required author attribution are preserved in this repository.

## Compatibility statement

DLavie uses supported Bedrock/Vibrant Visuals resource-pack interfaces rather than patched APK/IPAs or private RenderDragon injection. CI verifies pack structure and visual resources; final visual calibration, thermals and FPS still require physical Android/iPhone testing.
