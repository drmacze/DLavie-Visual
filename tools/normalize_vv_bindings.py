#!/usr/bin/env python3
"""Normalize DLavie client-biome bindings to the current vanilla Bedrock schema.

The vanilla resource pack uses namespaced identifiers such as `minecraft:plains`
and client-biome schema 1.21.120. Bare identifiers make the resource pack appear
active while its Vibrant Visuals renderer bindings may not override vanilla.
"""
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
CLIENT_BIOME_VERSION = "1.21.120"
CAVE_BINDINGS = {
    "minecraft:fog_appearance": ("fog_identifier", "dlavie:cave_fog"),
    "minecraft:atmosphere_identifier": ("atmosphere_identifier", "dlavie:cave_atmospherics"),
    "minecraft:color_grading_identifier": ("color_grading_identifier", "dlavie:cave_color_grading"),
    "minecraft:lighting_identifier": ("lighting_identifier", "dlavie:cave_lighting"),
}


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def save(path: Path, obj):
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def normalize(path: Path) -> bool:
    obj = load(path)
    cb = obj.get("minecraft:client_biome")
    if not isinstance(cb, dict):
        raise SystemExit(f"{path}: missing minecraft:client_biome")
    desc = cb.get("description")
    if not isinstance(desc, dict) or not isinstance(desc.get("identifier"), str):
        raise SystemExit(f"{path}: missing client biome identifier")

    stem = path.name.removesuffix(".client_biome.json")
    expected = f"minecraft:{stem}"
    obj["format_version"] = CLIENT_BIOME_VERSION
    desc["identifier"] = expected

    # Bedrock 26.x includes sulfur_caves in the vanilla client-biome set. Treat it
    # like the other cave biomes so it does not silently fall back to outdoor light.
    if stem == "sulfur_caves":
        comps = cb.setdefault("components", {})
        for component, (field, identifier) in CAVE_BINDINGS.items():
            comps.setdefault(component, {})[field] = identifier

    save(path, obj)
    return True


def main():
    roots = [ROOT / "biomes"]
    subpacks = ROOT / "subpacks"
    if subpacks.is_dir():
        roots.extend(sorted(p / "biomes" for p in subpacks.iterdir() if p.is_dir()))

    changed = 0
    for directory in roots:
        if not directory.is_dir():
            continue
        for path in sorted(directory.glob("*.client_biome.json")):
            changed += int(normalize(path))

    if changed == 0:
        raise SystemExit("No client-biome files found to normalize")
    print(f"Normalized {changed} Vibrant Visuals client-biome bindings to {CLIENT_BIOME_VERSION} with minecraft: namespace")


if __name__ == "__main__":
    main()
