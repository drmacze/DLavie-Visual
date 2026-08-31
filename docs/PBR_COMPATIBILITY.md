# PBR compatibility policy

DLavie Visual is a **visual/shader core only** and intentionally ships **zero block `*.texture_set.json` files**.

Bedrock requires a Texture Set to contain a `color` layer, and referenced images must exist in the same resource pack as the Texture Set. Texture Set definitions also do not merge across the resource stack.

Therefore the visual project does not attempt to attach per-block normal/AO/MERS data to vanilla or third-party textures. Those assets belong in a separate DLavie texture/PBR project that owns its own albedo and material maps correctly.

DLavie Visual uses only renderer-facing systems:

- `pbr/global.json` fallback behavior for textures without their own PBR data;
- per-biome and per-dimension lighting;
- atmosphere and color grading;
- volumetric fog;
- water waves/optics/caustics;
- shadow settings;
- local-light mappings;
- visual environment assets such as sun, moon, cirrus and precipitation.

The validator fails the build if block textures or block Texture Sets are accidentally added to this repository. This keeps the shader project independent and allows a future DLavie texture project to be stacked separately.
