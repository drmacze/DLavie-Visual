#!/usr/bin/env python3
"""Keep DLavie core PBR-safe with vanilla and third-party texture packs.

Bedrock Texture Sets require a color layer and any referenced image must exist in
the same resource pack. DLavie core does not own/copy Mojang or third-party block
albedo textures, so it must not generate metadata-only per-block Texture Sets.
Per-object fallback material response is handled by pbr/global.json instead.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "textures" / "blocks"
removed = 0

if OUT.exists():
    for path in OUT.glob("*.texture_set.json"):
        path.unlink()
        removed += 1
    try:
        OUT.rmdir()
    except OSError:
        pass

print(
    "PBR compatibility mode: no metadata-only block Texture Sets generated "
    f"({removed} stale overrides removed); using pbr/global.json fallback + "
    "custom lighting/local lights"
)
