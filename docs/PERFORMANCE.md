# Performance design

## iPhone 11 target

The iPhone 11 uses A13-class hardware and is inside the supported iOS generation for
Vibrant Visuals. Medium is the baseline preset, but thermal headroom varies strongly
with render distance, screen brightness, recording, world complexity, entities, and
other packs.

### Low
- blocky shadows
- water waves: 8 octaves
- caustics disabled
- smaller environment textures
- narrower custom point-light palette
- rougher global fallback materials to reduce visually noisy highlights

### Medium
- balanced soft shadows
- water waves: 16 octaves
- caustics enabled with moderate power
- 128px environment assets
- core warm/cool point lights
- moderate PBR roughness

### High
- soft shadows
- 28-octave water
- stronger caustics
- 256px environment assets
- broad point-light palette
- lower roughness / stronger highlight response

## Runtime guidance

For iPhone 11 start at 8–12 chunks. Low should be used while recording or during
thermal throttling. On Android, use Low/Medium unless the GPU is comfortably above
the official Vibrant Visuals support floor.
