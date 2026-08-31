# DLavie Visual

![DLavie Visual cover](branding/cover.svg)

**DLavie Visual** is a Minecraft Bedrock **Vibrant Visuals + PBR** resource pack for the 26.x renderer line, with **Bedrock 26.45** as the primary target and **1.26.40** as the compatibility floor. iPhone 11 (A13) remains the minimum iPhone performance baseline.

## 4.0 visual architecture

DLavie Visual 4.0 is a material + lighting upgrade rather than another global-value-only pass. It combines custom biome/dimension lighting, atmosphere, volumetric fog, ACES grading, local lights, water optics and a DLavie-owned 128x PBR material suite.

### Three distinct visual moods × three quality levels

The pack exposes **nine selectable subpacks** so visual style and performance are both preserved:

| Mood | Character |
|---|---|
| **Natural** | neutral daylight, realistic blue atmosphere, balanced saturation and water |
| **Cozy** | warmer sun/interiors, amber local lights, softer warm haze and golden highlights |
| **Gloomy** | cooler/desaturated daylight, darker ambient light, denser eerie fog and stronger atmosphere |

Each mood is available in **Low, Medium and High**. Low reduces water/shadow cost, Medium is the iPhone 11 baseline, and High enables the strongest water/local-light/shadow settings.

## Per-biome and per-dimension lighting

Eight Overworld render profiles are retained: default, forest, dense forest/jungle, dry/desert, cold/snow, swamp, cave/deep-dark and ocean. Each can use separate lighting, atmosphere, fog and color grading. Nether and End have their own lighting/fog/grading behavior and are additionally shifted by the selected Natural/Cozy/Gloomy mood.

The daylight scale remains calibrated to the Bedrock Vibrant Visuals resource-pack range instead of the erroneous extreme values from older DLavie builds.

## 128x material detail

DLavie 4.0 authors **117 common terrain/building materials** directly in the pack. Each authored material contains:

- a DLavie-owned color/albedo texture with a Minecraft-like pixel language,
- a genuine **128x normal map**,
- a **128x ambient-occlusion source**,
- a 128x MERS/subsurface map for metallic, emissive, roughness and foliage response.

Bedrock Texture Sets do **not** expose a dedicated AO slot. Therefore the authored 128x AO is baked into DLavie's color layer, while normal and MERS/subsurface maps are consumed directly by Vibrant Visuals. Every Texture Set references color/normal/MERS assets that exist in this same pack, preventing the magenta checkerboard regression from 3.0.0.

Materials currently cover core stone/deepslate, dirt/grass, sand/sandstone, major woods/logs/leaves, glass, ice/snow, common ores, iron/gold/copper/gem blocks, quartz, Nether/End surfaces and major emissive blocks.

## Optical water caustics

4.0 replaces the old caustics path with a new **60-frame 128x optical caustics atlas** generated offline from a simulated multi-wave ocean surface. The generator traces refracted light using Snell's law, intersects the refracted rays with an underwater floor and accumulates photon density into the caustics texture. This is a physically based offline optical simulation; it is not a fake noise overlay.

Low/Medium/High adjust wave octaves, frequency and caustics strength independently. River, ocean, swamp, frozen water and default water profiles remain separate.

## PBR compatibility

A Texture Set must own its color image and all referenced PBR images in the same resource pack. DLavie therefore only defines per-texture PBR data for textures it actually owns. Unauthored/third-party textures fall back to `pbr/global.json` rather than receiving invalid cross-pack Texture Sets.

## Installation

1. Import `DLavie-Visual.mcpack` into Minecraft.
2. Remove/disable older DLavie builds to avoid cached assets.
3. Enable **DLavie Visual** in Global Resources or the world resource stack.
4. Open the pack gear icon and choose Natural/Cozy/Gloomy plus Low/Medium/High.
5. Enable **Vibrant Visuals** in Settings → Video on supported hardware.

For iPhone 11, start with **Natural • Medium** or **Cozy • Medium** around 8–12 chunks. Use a Low preset while recording or if the device thermally throttles.

## Build

Requirements: Python 3, Pillow and NumPy.

```bash
python3 -m pip install Pillow numpy
./tools/build.sh
```

The build regenerates all runtime resources, produces the 128x material maps and optical caustics, expands the nine subpacks, validates every same-pack Texture Set reference and writes `dist/DLavie-Visual.mcpack`.

## Derivative source / license

The supplied Derivative 25.1.0 Java shader remains an art-direction/reference source for parts of DLavie's atmosphere, water and lighting work. A literal Iris/OptiFine GLSL port is not possible on retail Bedrock because those shader entry points are not exposed by RenderDragon. The supplied Derivative source is covered by **DERCODE License Agreement 2.5**; its license and required author attribution are preserved in this repository.

## Compatibility statement

DLavie uses supported Bedrock/Vibrant Visuals resource-pack interfaces rather than patched APK/IPAs or private RenderDragon injection. CI can verify structure and generated assets; final visual calibration, thermals and FPS still require physical Android/iPhone testing.
