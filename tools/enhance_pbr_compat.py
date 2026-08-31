#!/usr/bin/env python3
"""DLavie Visual 4.5 PBR compatibility pass.

This pass is deliberately texture-free. It improves how DLavie's renderer settings
interact with external Bedrock PBR texture packs without creating or overriding any
block Texture Sets. External packs remain the sole owners of albedo/normal/MERS data.
"""
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
THEMES = ("natural", "cozy", "gloomy")
QUALITIES = ("low", "medium", "high")
Q = {"low": 0, "medium": 1, "high": 2}

# Conservative fallbacks for surfaces that do NOT provide their own Texture Set.
# Valid external PBR Texture Sets override these values. Keeping vanilla fallback
# rough prevents non-PBR blocks from becoming plasticky/mirror-like while still
# allowing a small amount of IBL/specular response on higher presets.
FALLBACK_ROUGHNESS = {
    "blocks":    {"low": 248, "medium": 243, "high": 238},
    "actors":    {"low": 248, "medium": 244, "high": 240},
    "particles": {"low": 252, "medium": 250, "high": 248},
    "items":     {"low": 238, "medium": 231, "high": 224},
}

# Sky intensity contributes to BOTH indirect diffuse and specular/IBL in Vibrant
# Visuals. Previous DLavie builds intentionally darkened it heavily for contrast,
# but that also suppressed reflections from realistic PBR packs. These targets
# restore usable IBL while ambient illuminance remains deliberately low.
DAY_SKY = {
    "natural": {"low": .56, "medium": .64, "high": .72},
    "cozy":    {"low": .52, "medium": .60, "high": .68},
    "gloomy":  {"low": .44, "medium": .50, "high": .56},
}
NIGHT_SKY = {
    "natural": {"low": .10, "medium": .12, "high": .14},
    "cozy":    {"low": .10, "medium": .11, "high": .13},
    "gloomy":  {"low": .10, "medium": .10, "high": .11},
}
EMISSIVE_DESAT = {
    "natural": {"low": .020, "medium": .010, "high": .005},
    "cozy":    {"low": .015, "medium": .005, "high": .000},
    "gloomy":  {"low": .030, "medium": .020, "high": .015},
}


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def save(path, obj):
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def patch_pbr(path, quality):
    o = load(path)
    o["format_version"] = "1.21.40"
    pbr = o.setdefault("minecraft:pbr_fallback_settings", {})
    for group in ("blocks", "actors", "particles", "items"):
        rough = FALLBACK_ROUGHNESS[group][quality]
        pbr.setdefault(group, {})["global_metalness_emissive_roughness_subsurface"] = [0, 0, rough, 0]
    save(path, o)


def set_key(d, key, value):
    if isinstance(d, dict):
        d[key] = round(max(.1, min(1.0, float(value))), 6)


def patch_lighting(path, theme, quality):
    o = load(path)
    ls = o.get("minecraft:lighting_settings")
    if not ls:
        return

    # Overworld lighting is already migrated to 1.26.0 by the 4.4 pass.
    # Do not rewrite static Nether/End schemas unless they already use keyframes.
    sky = ls.get("sky", {}).get("intensity")
    if isinstance(sky, dict):
        day = DAY_SKY[theme][quality]
        night = NIGHT_SKY[theme][quality]
        twilight = max(night, day * .62)
        blue_hour = max(night, day * .40)

        for k in ("0.0", "0.18", "0.82", "1.0"):
            set_key(sky, k, day)
        for k in ("0.24", "0.76"):
            set_key(sky, k, twilight)
        for k in ("0.285", "0.715"):
            set_key(sky, k, max(night, day * .48))
        for k in ("0.32", "0.68"):
            set_key(sky, k, blue_hour)
        for k in ("0.34", "0.50", "0.66"):
            set_key(sky, k, night)

    # Preserve emissive texture color fidelity from external PBR packs.
    ls.setdefault("emissive", {})["desaturation"] = EMISSIVE_DESAT[theme][quality]

    # Raising sky IBL can brighten diffuse shadow fill. Counter that with a small
    # ambient reduction while leaving direct sun/moon untouched so normal maps
    # still receive strong directional modeling.
    amb = ls.get("ambient", {}).get("illuminance")
    if isinstance(amb, dict):
        fac = {"low": .97, "medium": .94, "high": .90}[quality]
        for k, v in list(amb.items()):
            amb[k] = round(max(0.0, float(v) * fac), 6)

    save(path, o)


def main():
    pbr_files = lighting_files = 0
    for theme in THEMES:
        for quality in QUALITIES:
            root = ROOT / "subpacks" / f"{theme}_{quality}"
            if not root.is_dir():
                raise SystemExit(f"missing subpack {root.name}")

            pbr = root / "pbr" / "global.json"
            if not pbr.is_file():
                raise SystemExit(f"missing {pbr}")
            patch_pbr(pbr, quality)
            pbr_files += 1

            for lp in (root / "lighting").glob("*.json"):
                patch_lighting(lp, theme, quality)
                lighting_files += 1

    print(
        f"Enhanced PBR compatibility: {pbr_files} fallback profiles, "
        f"{lighting_files} lighting profiles; external Texture Sets remain untouched"
    )


if __name__ == "__main__":
    main()
