# DLavie Visual

![DLavie Visual cover](branding/cover.svg)

**DLavie Visual** is a Minecraft Bedrock **Vibrant Visuals + PBR** resource pack for the 26.x renderer line, with **Bedrock 26.45** as the primary target and **1.26.40** as the manifest compatibility floor. It targets supported iPhone/iPad and Android hardware, with iPhone 11 (A13) as the minimum iPhone performance baseline.

## Rendering approach

The supplied Derivative 25.1.0 Java shader was audited and its visual priorities were mapped to Bedrock-supported systems: atmosphere scattering, keyframed sun/moon lighting, volumetric fog media, biome-specific grading, local lights, PBR fallback response, water waves/absorption and a 60-frame Derivative caustics atlas when the source asset is present.

A literal Iris/OptiFine GLSL port is not possible on retail Bedrock because those shader entry points are not exposed by RenderDragon. DLavie therefore targets visual reconstruction through the supported Vibrant Visuals/deferred pipeline.

## 3.0.1 PBR compatibility hotfix

3.0.0 introduced metadata-only per-block `*.texture_set.json` files. That was incorrect for Bedrock: every Texture Set requires a `color` layer, and referenced texture images must exist in the same resource pack as the Texture Set definition. On device this produced the magenta/black missing-texture checkerboard.

3.0.1 removes those invalid block Texture Sets completely. DLavie core now leaves block albedo and per-texture PBR ownership to vanilla or the active texture pack and applies its art direction through `pbr/global.json`, biome lighting, atmosphere, fog, water, shadows and local lights. The validator now rejects Texture Sets without a valid same-pack color layer so this regression cannot pass CI again.

See [docs/PBR_COMPATIBILITY.md](docs/PBR_COMPATIBILITY.md) for the resource-stack policy.

## Custom lighting architecture

DLavie uses eight Overworld render profiles: default, forest, dense forest/jungle, dry/desert, cold/snow, swamp, cave/deep-dark and ocean. Each profile can use its own lighting, atmosphere, color grading and fog. The 3.x lighting scale is calibrated to the current Bedrock Vibrant Visuals resource-pack scale rather than the incorrect 1000x values used in the earlier pass.

Medium and High also expand local-light mappings for torches, lanterns, glowstone, sea lanterns, froglights, redstone lamps, campfires, soul lights and other light-emitting blocks. Low keeps the cheaper path for mobile performance.

## Presets

| Preset | Intended device | Main cost controls |
|---|---|---|
| **Low** | iPhone 11 while recording / supported lower-end Android | blocky shadows, 6 water octaves, restrained fog, caustics off |
| **Medium** | **iPhone 11 recommended** | soft shadows, 10 water octaves + caustics, balanced fog/local lights |
| **High** | newer iPhone/iPad / stronger Android | soft 8-texel shadows, 14 water octaves, strongest atmosphere/local-light pass |

All three subpacks remain manually selectable on supported mobile hardware.

## PBR + other texture packs

DLavie Visual does not redistribute Mojang block albedo textures and does not attempt to attach metadata-only Texture Sets to textures owned by another pack. This is intentional: Bedrock Texture Sets do not merge across the resource stack and their referenced images must live in the same resource pack.

A Vibrant-Visuals/PBR-aware texture pack can therefore supply its own valid Texture Sets, while textures with no specific PBR data receive DLavie's global fallback material response. This is the safe path for vanilla/third-party texture compatibility.

## Installation

1. Build or download `DLavie-Visual.mcpack`.
2. Open it with Minecraft.
3. Enable **DLavie Visual** in Global Resources or the world resource packs.
4. Use the pack gear icon to select Low, Medium or High.
5. In **Settings → Video**, select **Vibrant Visuals** on supported hardware.

For iPhone 11, start with Medium and roughly 8–12 chunks. Use Low while screen recording or if thermal throttling becomes noticeable.

## Build

Requirements: Python 3 + Pillow.

```bash
python3 -m pip install Pillow
./tools/build.sh
```

The output is `dist/DLavie-Visual.mcpack`. The build regenerates configs/assets, clears unsafe stale block Texture Sets and runs structural/regression validation.

## Source / license compliance

The supplied Derivative source is licensed under **DERCODE License Agreement 2.5**. The license is preserved verbatim and required original authors are credited in [SOURCE_ATTRIBUTION.md](SOURCE_ATTRIBUTION.md).

## Compatibility statement

DLavie uses official Bedrock resource-pack/Vibrant Visuals interfaces rather than injectors, patched APK/IPAs or RenderDragon hacks. Repository validation can verify pack structure and data, but physical device testing is still required for final visual calibration, thermals and FPS claims.
