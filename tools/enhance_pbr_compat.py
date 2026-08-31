#!/usr/bin/env python3
"""DLavie Visual 4.6 PBR/deferred compatibility and root-loader failsafe pass.

Vibrant Visuals is Bedrock's current deferred PBR renderer. This pass stays
texture-free while improving how DLavie's renderer settings interact with
external PBR packs and the deferred lighting path:

- conservative fallback PBR values for surfaces without Texture Sets;
- calibrated sky IBL/specular contribution and low ambient fill;
- broad colored local-light coverage with quality-aware point/static lights;
- explicit water sampleWidth for quality-scaled deferred water surface sampling;
- Natural-Medium root renderer failsafe for clients before subpack resolution.

A user-provided Refined Deferred v3.2 pack was inspected as a behavioral
reference only. No texture, particle, or JSON asset from that pack is copied.
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
WATER_SAMPLE_WIDTH = {"low": .18, "medium": .13, "high": .09}

# DLavie-authored colors for current vanilla luminous blocks. Explicit mappings
# are important in deferred rendering because the renderer can preserve the color
# identity of nearby light sources instead of falling back to uniform block light.
DEFERRED_LIGHTS = {
    "minecraft:torch": "#FFC27C",
    "minecraft:lantern": "#FFAA58",
    "minecraft:fire": "#FF7438",
    "minecraft:campfire": "#FF873F",
    "minecraft:glowstone": "#FFC978",
    "minecraft:lit_redstone_lamp": "#FF9C55",
    "minecraft:redstone_lamp": "#FF9C55",
    "minecraft:jack_o_lantern": "#FF9B46",
    "minecraft:lit_pumpkin": "#FF9B46",
    "minecraft:lit_furnace": "#FF7138",
    "minecraft:lit_blast_furnace": "#FF7138",
    "minecraft:lit_smoker": "#FF7138",
    "minecraft:brewing_stand": "#D6A75A",
    "minecraft:firefly_bush": "#FFE86A",
    "minecraft:copper_bulb": "#FFC478",
    "minecraft:waxed_copper_bulb": "#FFC478",
    "minecraft:exposed_copper_bulb": "#D7B475",
    "minecraft:waxed_exposed_copper_bulb": "#D7B475",
    "minecraft:weathered_copper_bulb": "#9DC492",
    "minecraft:waxed_weathered_copper_bulb": "#9DC492",
    "minecraft:oxidized_copper_bulb": "#70BDA0",
    "minecraft:waxed_oxidized_copper_bulb": "#70BDA0",
    "minecraft:copper_torch": "#78D77B",
    "minecraft:copper_lantern": "#66B16F",
    "minecraft:exposed_copper_lantern": "#66B16F",
    "minecraft:weathered_copper_lantern": "#62A97D",
    "minecraft:oxidized_copper_lantern": "#55A88A",
    "minecraft:waxed_copper_lantern": "#66B16F",
    "minecraft:waxed_exposed_copper_lantern": "#66B16F",
    "minecraft:waxed_weathered_copper_lantern": "#62A97D",
    "minecraft:waxed_oxidized_copper_lantern": "#55A88A",
    "minecraft:soul_torch": "#64DCFF",
    "minecraft:soul_lantern": "#64DCFF",
    "minecraft:soul_campfire": "#58CFFF",
    "minecraft:soul_fire": "#58CFFF",
    "minecraft:sculk_catalyst": "#2DAEAE",
    "minecraft:sculk_sensor": "#32B4BA",
    "minecraft:calibrated_sculk_sensor": "#36BEC0",
    "minecraft:sculk_shrieker": "#36A7B7",
    "minecraft:redstone_torch": "#FF443A",
    "minecraft:lit_redstone_ore": "#FF3D34",
    "minecraft:lit_deepslate_redstone_ore": "#FF3D34",
    "minecraft:lava": "#FF612B",
    "minecraft:flowing_lava": "#FF612B",
    "minecraft:magma": "#FF6B32",
    "minecraft:shroomlight": "#FFA45B",
    "minecraft:portal": "#A561FF",
    "minecraft:respawn_anchor": "#9B6BFF",
    "minecraft:crying_obsidian": "#8D58FF",
    "minecraft:cave_vines_body_with_berries": "#FFC75C",
    "minecraft:cave_vines_head_with_berries": "#FFC75C",
    "minecraft:small_amethyst_bud": "#B48CFF",
    "minecraft:medium_amethyst_bud": "#B48CFF",
    "minecraft:large_amethyst_bud": "#B48CFF",
    "minecraft:amethyst_cluster": "#C29BFF",
    "minecraft:enchanting_table": "#B67CFF",
    "minecraft:end_rod": "#DCEBFF",
    "minecraft:end_portal": "#62DBCC",
    "minecraft:end_gateway": "#62DBCC",
    "minecraft:dragon_egg": "#8351D8",
    "minecraft:sea_lantern": "#BDEEFF",
    "minecraft:sea_pickle": "#B6FFD0",
    "minecraft:conduit": "#77F1FF",
    "minecraft:ochre_froglight": "#FFD99B",
    "minecraft:verdant_froglight": "#BFFFD4",
    "minecraft:pearlescent_froglight": "#EBCBFF",
    "minecraft:glow_lichen": "#9ED1A6",
    "minecraft:ender_chest": "#48C8B0",
    "minecraft:beacon": "#75E7FF",
    "minecraft:vault": "#FFB760",
    "minecraft:trial_spawner": "#FFB760",
    "minecraft:creaking_heart": "#E5A45F",
    "minecraft:resin_clump": "#F0A34A",
    "minecraft:colored_torch_blue": "#4AA6FF",
    "minecraft:colored_torch_purple": "#B04DFF",
    "minecraft:colored_torch_red": "#FF4C4C",
    "minecraft:colored_torch_green": "#75D84D",
}
CANDLE_COLORS = {
    "": "#FFD08A", "white_": "#FFF0D8", "orange_": "#FF993D", "magenta_": "#E85AD8",
    "light_blue_": "#67C8FF", "yellow_": "#FFE04A", "lime_": "#A8E84D", "pink_": "#F27DA6",
    "gray_": "#96908E", "light_gray_": "#C0B8B2", "cyan_": "#45D5D0", "purple_": "#A15BE5",
    "blue_": "#5B8EE8", "brown_": "#B27A40", "green_": "#70B53B", "red_": "#E6534C",
    "black_": "#75635D",
}
for prefix, color in CANDLE_COLORS.items():
    DEFERRED_LIGHTS[f"minecraft:{prefix}candle"] = color
    DEFERRED_LIGHTS[f"minecraft:{prefix}candle_cake"] = color

HIGH_POINT = {
    "minecraft:torch", "minecraft:lantern", "minecraft:campfire",
    "minecraft:soul_torch", "minecraft:soul_lantern", "minecraft:soul_campfire",
    "minecraft:redstone_torch", "minecraft:end_rod", "minecraft:sea_pickle",
    "minecraft:beacon", "minecraft:conduit", "minecraft:firefly_bush",
    "minecraft:copper_torch", "minecraft:copper_lantern", "minecraft:exposed_copper_lantern",
    "minecraft:weathered_copper_lantern", "minecraft:oxidized_copper_lantern",
    "minecraft:waxed_copper_lantern", "minecraft:waxed_exposed_copper_lantern",
    "minecraft:waxed_weathered_copper_lantern", "minecraft:waxed_oxidized_copper_lantern",
}
HIGH_POINT.update(k for k in DEFERRED_LIGHTS if "candle" in k)
MEDIUM_POINT = {
    "minecraft:torch", "minecraft:lantern", "minecraft:soul_torch", "minecraft:soul_lantern",
    "minecraft:campfire", "minecraft:soul_campfire", "minecraft:end_rod",
    "minecraft:copper_torch", "minecraft:copper_lantern",
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


def tint(hex_color, theme):
    r, g, b = (int(hex_color[i:i+2], 16) for i in (1, 3, 5))
    mul = {
        "natural": (1.00, 1.00, 1.00),
        "cozy": (1.06, .95, .84),
        "gloomy": (.86, .95, 1.08),
    }[theme]
    vals = [max(0, min(255, round(v * m))) for v, m in zip((r, g, b), mul)]
    return "#%02X%02X%02X" % tuple(vals)


def patch_local_lighting(path, theme, quality):
    o = load(path)
    o["format_version"] = "1.21.120"
    ll = o.setdefault("minecraft:local_light_settings", {})
    for block, color in DEFERRED_LIGHTS.items():
        node = ll.setdefault(block, {})
        node["light_color"] = tint(color, theme)
        if quality == "high" and block in HIGH_POINT:
            node["light_type"] = "point_light"
        elif quality == "medium" and block in MEDIUM_POINT:
            node["light_type"] = "point_light"
        else:
            node["light_type"] = "static_light"
    save(path, o)
    return len(ll)


def patch_water_sampling(path, quality):
    o = load(path)
    ws = o.get("minecraft:water_settings")
    if not isinstance(ws, dict):
        return
    waves = ws.setdefault("waves", {})
    if waves.get("enabled", True):
        waves["sampleWidth"] = WATER_SAMPLE_WIDTH[quality]
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
    """Install a complete Natural-Medium renderer at pack root."""
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
    pbr_files = lighting_files = water_files = 0
    light_counts = []
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
            llp = root / "local_lighting" / "local_lighting.json"
            if not llp.is_file():
                raise SystemExit(f"missing {llp}")
            light_counts.append(patch_local_lighting(llp, theme, quality))
            for wp in (root / "water").glob("*.json"):
                patch_water_sampling(wp, quality)
                water_files += 1

    # Copy after all deferred tuning so the root fallback is byte-consistent with
    # Natural-Medium instead of becoming a separate configuration branch.
    install_root_failsafe()
    print(
        f"Enhanced PBR/deferred core: {pbr_files} PBR profiles, {lighting_files} lighting profiles, "
        f">={min(light_counts)} colored local-light mappings/profile, {water_files} water profiles with sampleWidth; "
        "installed Natural-Medium root renderer failsafe; zero block textures copied"
    )


if __name__ == "__main__":
    main()
