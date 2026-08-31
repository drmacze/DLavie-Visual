#!/usr/bin/env python3
"""DLavie Visual 4.6 deferred-core enhancement pass.

Vibrant Visuals is Bedrock's current deferred PBR renderer. This pass does not
invent a separate manifest capability and does not ship block textures. It tunes
supported renderer-facing controls that materially affect the deferred path:

- broad colored local-light coverage for current vanilla luminous blocks;
- quality-aware point/static light selection;
- water surface sample width for higher fidelity deferred water normals;
- preservation of PBR/IBL compatibility authored by earlier passes.

The user-provided Refined Deferred v3.2 pack was inspected as a behavioral
reference only. No texture, particle, or JSON asset from that pack is copied.
"""
from __future__ import annotations

from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
THEMES = ("natural", "cozy", "gloomy")
QUALITIES = ("low", "medium", "high")

# Vanilla luminous blocks that benefit from an explicit colored-light mapping.
# Colors are DLavie-authored and intentionally distinct from the reference pack.
LIGHTS = {
    # warm combustion / utility
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
    # copper family / 26.x lighting set
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
    # soul / sculk / redstone
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
    # lava / nether
    "minecraft:lava": "#FF612B",
    "minecraft:flowing_lava": "#FF612B",
    "minecraft:magma": "#FF6B32",
    "minecraft:shroomlight": "#FFA45B",
    "minecraft:portal": "#A561FF",
    "minecraft:respawn_anchor": "#9B6BFF",
    "minecraft:crying_obsidian": "#8D58FF",
    # caves / amethyst / vines
    "minecraft:cave_vines_body_with_berries": "#FFC75C",
    "minecraft:cave_vines_head_with_berries": "#FFC75C",
    "minecraft:small_amethyst_bud": "#B48CFF",
    "minecraft:medium_amethyst_bud": "#B48CFF",
    "minecraft:large_amethyst_bud": "#B48CFF",
    "minecraft:amethyst_cluster": "#C29BFF",
    # end / ocean / utility
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
    # education / colored torches
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
    LIGHTS[f"minecraft:{prefix}candle"] = color
    LIGHTS[f"minecraft:{prefix}candle_cake"] = color

# Sources that are worth the more expensive dynamic point-light path on High.
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
HIGH_POINT.update(k for k in LIGHTS if "candle" in k)

MEDIUM_POINT = {
    "minecraft:torch", "minecraft:lantern", "minecraft:soul_torch", "minecraft:soul_lantern",
    "minecraft:campfire", "minecraft:soul_campfire", "minecraft:end_rod", "minecraft:copper_torch",
    "minecraft:copper_lantern",
}

WATER_SAMPLE_WIDTH = {"low": 0.18, "medium": 0.13, "high": 0.09}


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def save(path: Path, obj) -> None:
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def tint(hex_color: str, theme: str) -> str:
    r, g, b = (int(hex_color[i:i+2], 16) for i in (1, 3, 5))
    mul = {
        "natural": (1.00, 1.00, 1.00),
        "cozy": (1.06, 0.95, 0.84),
        "gloomy": (0.86, 0.95, 1.08),
    }[theme]
    vals = [max(0, min(255, round(v * m))) for v, m in zip((r, g, b), mul)]
    return "#%02X%02X%02X" % tuple(vals)


def patch_local_lighting(path: Path, theme: str, quality: str) -> int:
    obj = load(path)
    obj["format_version"] = "1.21.120"
    settings = obj.setdefault("minecraft:local_light_settings", {})
    for block, color in LIGHTS.items():
        current = settings.setdefault(block, {})
        # Preserve deliberately authored ore colors from the night/ore pass.
        if "_ore" not in block and block != "minecraft:ancient_debris":
            current["light_color"] = tint(color, theme)
        if quality == "high" and block in HIGH_POINT:
            current["light_type"] = "point_light"
        elif quality == "medium" and block in MEDIUM_POINT:
            current["light_type"] = "point_light"
        else:
            current["light_type"] = "static_light"
    save(path, obj)
    return len(settings)


def patch_water(path: Path, quality: str) -> None:
    obj = load(path)
    ws = obj.get("minecraft:water_settings")
    if not isinstance(ws, dict):
        return
    waves = ws.setdefault("waves", {})
    if waves.get("enabled", True):
        waves["sampleWidth"] = WATER_SAMPLE_WIDTH[quality]
    save(path, obj)


def patch_tree(base: Path, theme: str, quality: str) -> tuple[int, int]:
    ll = base / "local_lighting" / "local_lighting.json"
    if not ll.is_file():
        raise SystemExit(f"missing deferred local-light config: {ll}")
    count = patch_local_lighting(ll, theme, quality)
    water_count = 0
    for path in sorted((base / "water").glob("*.json")):
        patch_water(path, quality)
        water_count += 1
    return count, water_count


def main() -> None:
    light_counts = []
    water_files = 0
    for theme in THEMES:
        for quality in QUALITIES:
            base = ROOT / "subpacks" / f"{theme}_{quality}"
            if not base.is_dir():
                raise SystemExit(f"missing subpack {base.name}")
            count, waters = patch_tree(base, theme, quality)
            light_counts.append(count)
            water_files += waters

    # Root renderer is Natural-Medium after enhance_pbr_compat.py installs it.
    root_ll = ROOT / "local_lighting" / "local_lighting.json"
    if root_ll.is_file():
        light_counts.append(patch_local_lighting(root_ll, "natural", "medium"))
    for path in sorted((ROOT / "water").glob("*.json")):
        patch_water(path, "medium")
        water_files += 1

    print(
        f"Enhanced deferred core: >= {min(light_counts)} colored local-light mappings per profile, "
        f"{water_files} water profiles with explicit deferred sampleWidth; zero block textures copied"
    )


if __name__ == "__main__":
    main()
