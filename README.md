# DLavie Visual

![DLavie Visual cover](branding/cover.svg)

**DLavie Visual** is a Minecraft Bedrock **Vibrant Visuals shader/visual core** for the 26.x renderer line, with **Bedrock 26.45** as the primary target and **1.26.40** as the compatibility floor.

## 4.2 visual-only architecture

DLavie Visual is deliberately separated from the future DLavie texture project. This repository **does not ship custom block albedo, normal, AO or MERS Texture Sets**. Block textures belong in a separate project so shader development and texture development can evolve independently.

The visual pack focuses on renderer-facing systems only:

- custom sun/moon lighting and time-of-day response,
- atmosphere scattering and low-sun glare/godray character,
- realistic height/weather volumetric fog,
- Henyey-Greenstein directional scattering for light shafts,
- ACES color grading,
- biome-specific lighting/fog/grading,
- Nether and End lighting/fog/grading,
- dynamic/local light color and quality control,
- water waves, absorption/scattering and optical caustics,
- shadow quality scaling,
- visual environment assets such as sun, moon, cirrus, rain and snow.

## Three visual moods × three quality levels

The pack exposes **nine selectable visual subpacks**:

| Mood | Character |
|---|---|
| **Natural** | realistic neutral daylight, balanced atmosphere, cleaner water and natural night |
| **Cozy** | warmer low sun and interiors, amber local lights, softer golden haze |
| **Gloomy** | cooler/desaturated daylight, darker ambient fill, denser eerie fog and stronger night mood |

Each mood has **Low / Medium / High**. Quality changes renderer cost and visual depth, not block textures. High uses deeper shadow/ambient separation, stronger atmosphere, richer fog scattering, more water octaves and broader point-light use; Medium is the mobile baseline; Low is the performance path.

## Lighting architecture

Eight Overworld visual profiles are generated: default, forest, dense forest/jungle, dry/desert, cold/snow, swamp, cave/deep-dark and ocean. Each can have separate lighting, atmosphere, fog and color grading. Nether and End also receive their own visual treatment.

The visual-core pass deepens the difference between direct sunlight, sky fill and ambient light. This is specifically intended to avoid the flat "vanilla Vibrant Visuals with different values" look from earlier DLavie versions.

## Volumetric fog realism

4.2 rebuilds the fog treatment around the supported Vibrant Visuals volumetric model instead of relying on a single density multiplier.

- Clear-air fog uses a vertical density gradient: strongest near terrain/low altitude and fading toward the upper atmosphere.
- Forest, dense jungle, swamp, dry, cold, ocean and cave profiles have different fog depth and vertical falloff.
- Rain/snow use a separate `weather` volumetric density so storms gain depth without making clear weather permanently milky.
- `media_coefficients` now define air, water and cloud scattering/absorption separately.
- Fog files use format `1.21.90` and provide **Henyey-Greenstein phase values** for air and water. Positive forward scattering concentrates light around the sun direction and gives more believable shafts through trees, windows and humid air.
- Cave fog uses lower anisotropy so underground dust reads softer and less like outdoor sun haze.
- A subtle far-distance haze is retained only near the render-distance limit to hide hard distance transitions without replacing the terrain-aware volumetric effect.
- Natural / Cozy / Gloomy and Low / Medium / High still alter density and scattering strength independently.

## Atmosphere and grading

Sun Mie scattering and glare are strengthened mainly around sunrise/sunset while noon stays in the calibrated Bedrock brightness range. Natural stays neutral, Cozy shifts toward warm gold, and Gloomy shifts toward cool/desaturated atmospheric scattering.

Color grading uses ACES with theme-specific white balance, contrast and saturation. High presets intentionally keep stronger shadow separation than Low.

## Water

River, ocean, swamp, frozen and default water remain separate profiles. Low/Medium/High use different wave octave counts, frequency, animation speed and caustics strength.

The optical caustics atlas is a **60-frame 128px** visual effect generated offline by tracing refracted rays through a simulated multi-wave water surface using Snell-law refraction. It is a shader/environment asset, not a block texture.

## Texture-pack compatibility

DLavie Visual intentionally contains **zero block Texture Sets**. A separate texture/PBR project can be stacked with DLavie later and own its albedo/normal/MERS data correctly. Textures without their own Texture Sets continue to use the safe global PBR fallback supplied by the renderer config.

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

The build regenerates renderer configs, visual environment assets and optical caustics, expands all nine visual subpacks, runs the visual-core and volumetric-fog enhancement passes, verifies that **no block textures/Texture Sets exist**, then writes `dist/DLavie-Visual.mcpack`.

## Derivative source / license

The supplied Derivative 25.1.0 Java shader remains an art-direction/reference source for parts of DLavie's atmosphere, water and lighting work. A literal Iris/OptiFine GLSL port is not possible on retail Bedrock because those shader entry points are not exposed by RenderDragon. The supplied Derivative source is covered by **DERCODE License Agreement 2.5**; its license and required author attribution are preserved in this repository.

## Compatibility statement

DLavie uses supported Bedrock/Vibrant Visuals resource-pack interfaces rather than patched APK/IPAs or private RenderDragon injection. CI verifies pack structure and visual resources; final visual calibration, thermals and FPS still require physical Android/iPhone testing.