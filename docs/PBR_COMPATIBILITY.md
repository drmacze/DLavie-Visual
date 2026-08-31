# PBR compatibility policy

DLavie Visual core intentionally does **not** ship metadata-only per-block `*.texture_set.json` overrides.

Bedrock requires a Texture Set to contain a `color` layer. If that color layer references an image, the image must exist in the same resource pack as the Texture Set. Texture Set definitions also do not merge across the resource stack.

That means a visual-only pack cannot safely attach per-texture MERS values to vanilla or arbitrary third-party albedo textures without bundling its own color images. Doing so either creates invalid Texture Sets (magenta/black checkerboards) or overrides the active texture pack's albedo.

DLavie Visual therefore uses:

- `pbr/global.json` fallback materials for textures that do not provide their own PBR data;
- per-biome lighting, atmosphere, color grading, fog, water and shadows;
- local-light mappings for emissive/light blocks;
- Texture Sets only when DLavie owns/provides the corresponding color asset in the same pack.

This keeps the core pack compatible with vanilla textures and with other Vibrant Visuals/PBR-aware texture packs.
