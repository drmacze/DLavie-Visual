# DLavie Visual

![DLavie Visual cover](branding/cover.svg)

**DLavie Visual** is a Minecraft Bedrock **Vibrant Visuals shader/visual core** for the 26.x renderer line, with **Bedrock 26.45** as the primary target and **1.26.40** as the compatibility floor.

## 4.3 visual-only architecture

DLavie Visual is deliberately separated from the future DLavie texture project. This repository **does not ship custom block albedo, normal, AO or MERS Texture Sets**. Block/material textures belong in a separate project so shader development and texture development can evolve independently.

The visual pack focuses on renderer-facing systems only:

- custom sun/moon lighting and time-of-day response,
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
- shadow quality scaling,
- visual environment assets such as sun, moon, cirrus, rain and snow.

## Three visual moods × three quality levels

The pack exposes **nine selectable visual subpacks**:

| Mood | Character |
|---|---|
| **Natural** | realistic neutral daylight, balanced atmosphere, cleaner water and natural night |
| **Cozy** | warmer low sun and interiors, amber local lights, softer golden haze |
| **Gloomy** | cooler/desaturated daylight, darker ambient fill, denser eerie fog and stronger night mood |

Each mood has **Low / Medium / High**. Quality changes renderer cost and visual depth, not block textures. High uses deeper shadow/ambient separation, stronger atmosphere, richer fog/water scattering, more water octaves and broader point-light use; Medium is the mobile baseline; Low is the performance path.

## Interactive weather

4.3 adds a dedicated weather pass using the supported Vibrant Visuals weather fog/media path.

- Active rain/snow receives its own `weather` volumetric density instead of permanently thickening clear-air fog.
- Weather distance haze begins earlier during storms to create a darker overcast horizon and hide hard render-distance transitions.
- Cloud media now has independent scattering and absorption values. Dense/humid biomes and Gloomy presets absorb more light in cloud volumes, while dry biomes remain clearer.
- Forest, jungle, swamp, cold, ocean and dry profiles react differently to storm haze.
- Clear weather retains the existing height-shaped air fog and is not forced into a permanent grey veil.

**Wet blocks and reflective puddles are intentionally not faked in this repository.** The public visual-only Vibrant Visuals resource-pack interfaces do not expose a dynamic per-block rain wetness/puddle mask. Correct wet-surface materials belong in the separate DLavie texture/material project (or would require a non-standard renderer hook). DLavie Visual remains texture-independent.

## Advanced water

4.3 deepens water rendering without adding block textures.

- Default, river, ocean, swamp and frozen water use different optical particle concentrations (chlorophyll, suspended sediment and CDOM), affecting how light is absorbed with depth.
- Underwater fog now has water-specific scattering and absorption instead of inheriting generic air values.
- Water has a forward-scattering Henyey-Greenstein phase value; High presets push it further to make sunlight shafts through the surface more visible.
- Underwater distance fog includes a smooth transition profile so entering water does not instantly snap to a flat color.
- Ocean water stays clearer and carries light farther; rivers are slightly sediment-rich; swamp water is intentionally murkier; frozen water stays clean/cold.
- Low / Medium / High use 6 / 12 / 18 water-wave octaves with different depth, speed and frequency.
- Optical caustics use the 60-frame 128px atlas, with stronger/faster projection at higher quality.

## Lighting architecture

Eight Overworld visual profiles are generated: default, forest, dense forest/jungle, dry/desert, cold/snow, swamp, cave/deep-dark and ocean. Each can have separate lighting, atmosphere, fog and color grading. Nether and End also receive their own visual treatment.

The visual-core pass deepens the difference between direct sunlight, sky fill and ambient light. This is specifically intended to avoid the flat "vanilla Vibrant Visuals with different values" look from earlier DLavie versions.

## Volumetric fog realism

Clear-air fog uses a vertical density gradient: strongest near terrain/low altitude and fading toward the upper atmosphere. Rain/snow use a separate weather volume. Air, water and cloud media use separate scattering/absorption coefficients and directional phase values, allowing sunlight shafts to read differently in humid air, caves and underwater.

## Atmosphere and grading

Sun Mie scattering and glare are strengthened mainly around sunrise/sunset while noon stays in the calibrated Bedrock brightness range. Natural stays neutral, Cozy shifts toward warm gold, and Gloomy shifts toward cool/desaturated atmospheric scattering.

Color grading uses ACES with theme-specific white balance, contrast and saturation. High presets intentionally keep stronger shadow separation than Low.

## Texture-pack compatibility

DLavie Visual intentionally contains **zero block Texture Sets**. A separate texture/PBR project can be stacked with DLavie later and own its albedo/normal/MERS/wetness data correctly. Textures without their own Texture Sets continue to use the safe global PBR fallback supplied by the renderer config.

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

The build regenerates renderer configs, visual environment assets and optical caustics, expands all nine visual subpacks, runs the visual-core, volumetric-fog and weather/water enhancement passes, verifies that **no block textures/Texture Sets exist**, then writes `dist/DLavie-Visual.mcpack`.

## Derivative source / license

The supplied Derivative 25.1.0 Java shader remains an art-direction/reference source for parts of DLavie's atmosphere, water and lighting work. A literal Iris/OptiFine GLSL port is not possible on retail Bedrock because those shader entry points are not exposed by RenderDragon. The supplied Derivative source is covered by **DERCODE License Agreement 2.5**; its license and required author attribution are preserved in this repository.

## Compatibility statement

DLavie uses supported Bedrock/Vibrant Visuals resource-pack interfaces rather than patched APK/IPAs or private RenderDragon injection. CI verifies pack structure and visual resources; final visual calibration, thermals and FPS still require physical Android/iPhone testing.
