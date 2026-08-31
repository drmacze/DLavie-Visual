#!/usr/bin/env python3
"""DLavie Visual 4.5+ PBR compatibility and runtime-loader failsafe pass.

This pass stays texture-free. It improves how DLavie's renderer settings interact
with external Bedrock PBR texture packs, then installs a root Natural-Medium
fallback so the visual core still resolves if a subpack has not been selected yet.
"""
from pathlib import Path
import json
import shutil

ROOT = Path(__file__).resolve().parents[1]
THEMES = ("natural", "cozy", "gloomy")
QUALITIES = ("low", "medium", "high")

FALLBACK_ROUGHNESS = {
    "blocks":    {"low": 248, "medium": 243, "high": 238},
    "actors":    {"low": 248, "medium": 244, "high": 240},
    "particles": {"low": 252, "medium": 250, "high": 248},
    "items":     {"low": 238, "medium": 231, "high": 224},
}
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
    path.parent.mkdir(parents=True, exist_ok=True)
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
    ls.setdefault("emissive", {})["desaturation"] = EMISSIVE_DESAT[theme][quality]
    amb = ls.get("ambient", {}).get("illuminance")
    if isinstance(amb, dict):
        fac = {"low": .97, "medium": .94, "high": .90}[quality]
        for k, v in list(amb.items()):
            amb[k] = round(max(0.0, float(v) * fac), 6)
    save(path, o)


def root_identifier(obj):
    for component in (
        "minecraft:atmosphere_settings", "minecraft:lighting_settings",
        "minecraft:color_grading_settings", "minecraft:fog_settings", "minecraft:water_settings",
    ):
        desc = obj.get(component, {}).get("description")
        if isinstance(desc, dict) and isinstance(desc.get("identifier"), str):
            ident = desc["identifier"]
            if ident.startswith("dlavie:"):
                desc["identifier"] = "dlavie_root:" + ident.split(":", 1)[1]
    return obj


def install_root_failsafe():
    """Install a complete Natural-Medium renderer at pack root.

    Subpack files override root files when a subpack is selected. The root copy is
    intentionally namespaced separately so it cannot collide with selected subpack
    identifiers, and it gives vanilla biomes an explicit custom binding even before
    the subpack selector is resolved by the client.
    """
    src = ROOT / "subpacks" / "natural_medium"
    if not src.is_dir():
        raise SystemExit("natural_medium subpack missing for root failsafe")

    reserved_default = {
        "atmospherics": "atmospherics.json",
        "lighting": "global.json",
        "color_grading": "color_grading.json",
        "water": "water.json",
        "fogs": "default.json",
    }
    for folder in ("atmospherics", "lighting", "color_grading", "fogs", "water"):
        outdir = ROOT / folder
        outdir.mkdir(parents=True, exist_ok=True)
        for source in sorted((src / folder).glob("*.json")):
            name = reserved_default[folder] if source.stem == "default" else source.name
            save(outdir / name, root_identifier(load(source)))

    for rel in ("pbr/global.json", "local_lighting/local_lighting.json", "shadows/global.json"):
        source = src / rel
        target = ROOT / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)

    # Root biome files are the safety net. Selected subpacks contain the same biome
    # paths and override these bindings with their mood/quality-specific identifiers.
    for path in sorted((ROOT / "biomes").glob("*.client_biome.json")):
        o = load(path)
        comps = o.get("minecraft:client_biome", {}).get("components", {})
        fields = (
            ("minecraft:fog_appearance", "fog_identifier"),
            ("minecraft:atmosphere_identifier", "atmosphere_identifier"),
            ("minecraft:color_grading_identifier", "color_grading_identifier"),
            ("minecraft:lighting_identifier", "lighting_identifier"),
            ("minecraft:water_identifier", "water_identifier"),
        )
        for comp, field in fields:
            node = comps.get(comp)
            if isinstance(node, dict) and isinstance(node.get(field), str) and node[field].startswith("dlavie:"):
                node[field] = "dlavie_root:" + node[field].split(":", 1)[1]
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

    install_root_failsafe()
    print(
        f"Enhanced PBR compatibility: {pbr_files} fallback profiles, {lighting_files} lighting profiles; "
        "installed Natural-Medium root renderer failsafe; external Texture Sets remain untouched"
    )


if __name__ == "__main__":
    main()
