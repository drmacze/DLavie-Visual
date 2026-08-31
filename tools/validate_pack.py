#!/usr/bin/env python3
"""Feature-level validation for the generated DLavie Visual runtime.

Release/package/reference integrity is handled by audit_release.py. This validator
stays focused on required renderer features and the runtime loader safety net.
"""
from __future__ import annotations

from pathlib import Path
import json
import sys

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
THEMES = ("natural", "cozy", "gloomy")
QUALITIES = ("low", "medium", "high")
SUBPACKS = tuple(f"{t}_{q}" for t in THEMES for q in QUALITIES)
PROFILES = ("default", "forest", "dense", "dry", "cold", "swamp", "cave", "ocean")
WATER_KINDS = ("default", "river", "ocean", "swamp", "frozen")
errors: list[str] = []


def err(message: str) -> None:
    errors.append(message)


def load(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        err(f"{path.relative_to(ROOT)}: invalid JSON: {exc}")
        return {}


def collect_ids(folder: Path, component: str) -> set[str]:
    ids: set[str] = set()
    for path in folder.glob("*.json"):
        ident = load(path).get(component, {}).get("description", {}).get("identifier")
        if isinstance(ident, str):
            if ident in ids:
                err(f"{folder.relative_to(ROOT)}: duplicate identifier {ident}")
            ids.add(ident)
    return ids


def main() -> None:
    release = load(ROOT / "config" / "release.json")
    manifest = load(ROOT / "manifest.json")
    version = release.get("version")
    if manifest.get("header", {}).get("version") != version:
        err("manifest header version is not synchronized with config/release.json")
    for module in manifest.get("modules", []):
        if module.get("version") != version:
            err("manifest module version is stale")
    if "pbr" not in manifest.get("capabilities", []):
        err("manifest pbr capability missing")

    folders = tuple(item.get("folder_name") for item in manifest.get("subpacks", []))
    if folders != SUBPACKS:
        err(f"manifest subpack list mismatch: {folders}")

    for sp in SUBPACKS:
        root = ROOT / "subpacks" / sp
        _, quality = sp.rsplit("_", 1)
        if not root.is_dir():
            err(f"missing subpack {sp}")
            continue

        for profile in PROFILES:
            for folder in ("atmospherics", "lighting", "color_grading", "fogs"):
                path = root / folder / f"{profile}.json"
                if not path.is_file():
                    err(f"missing {path.relative_to(ROOT)}")
        for dimension in ("nether", "end"):
            for folder in ("atmospherics", "lighting", "color_grading", "fogs"):
                path = root / folder / f"{dimension}.json"
                if not path.is_file():
                    err(f"missing {path.relative_to(ROOT)}")

        for profile in PROFILES:
            path = root / "lighting" / f"{profile}.json"
            obj = load(path)
            if obj.get("format_version") != "1.26.0":
                err(f"{path.relative_to(ROOT)}: Overworld lighting must use schema 1.26.0")
            ls = obj.get("minecraft:lighting_settings", {})
            amb = ls.get("ambient", {}).get("illuminance", {})
            sky = ls.get("sky", {}).get("intensity", {})
            if not isinstance(amb, dict) or "0.50" not in amb:
                err(f"{path.relative_to(ROOT)}: midnight ambient key missing")
            if not isinstance(sky, dict) or "0.50" not in sky:
                err(f"{path.relative_to(ROOT)}: midnight sky key missing")
            sun = ls.get("directional_lights", {}).get("orbital", {}).get("sun", {}).get("illuminance", {})
            vals = [float(v) for v in sun.values()] if isinstance(sun, dict) else [float(sun or 0)]
            if max(vals or [0]) > 110:
                err(f"{path.relative_to(ROOT)}: sunlight exceeds calibrated range")

        for path in (root / "fogs").glob("*.json"):
            obj = load(path)
            if obj.get("format_version") != "1.21.90":
                err(f"{path.relative_to(ROOT)}: enhanced fog schema must be 1.21.90")
            fg = obj.get("minecraft:fog_settings", {})
            vol = fg.get("volumetric", {})
            if not all(k in vol.get("density", {}) for k in ("air", "water")):
                err(f"{path.relative_to(ROOT)}: volumetric air/water density missing")
            if not all(k in vol.get("media_coefficients", {}) for k in ("air", "water", "cloud")):
                err(f"{path.relative_to(ROOT)}: air/water/cloud media coefficients missing")
            if "transition_fog" not in fg.get("distance", {}).get("water", {}):
                err(f"{path.relative_to(ROOT)}: underwater transition fog missing")

        min_octaves = {"low": 7, "medium": 14, "high": 20}[quality]
        for kind in WATER_KINDS:
            path = root / "water" / f"{kind}.json"
            obj = load(path)
            ws = obj.get("minecraft:water_settings", {})
            if obj.get("format_version") != "1.26.0":
                err(f"{path.relative_to(ROOT)}: water schema must be 1.26.0")
            pc = ws.get("particle_concentrations", {})
            if not all(k in pc for k in ("chlorophyll", "suspended_sediment", "cdom")):
                err(f"{path.relative_to(ROOT)}: depth absorption values incomplete")
            waves = ws.get("waves", {})
            if not waves.get("enabled") or int(waves.get("octaves", 0)) < min_octaves:
                err(f"{path.relative_to(ROOT)}: wave quality regressed")
            caustics = ws.get("caustics", {})
            if not caustics.get("enabled") or caustics.get("texture") != "textures/dlavie/optical_caustics":
                err(f"{path.relative_to(ROOT)}: optical caustics not active")

        pbr_path = root / "pbr" / "global.json"
        pbr = load(pbr_path).get("minecraft:pbr_fallback_settings", {})
        for category in ("blocks", "actors", "particles", "items"):
            mers = pbr.get(category, {}).get("global_metalness_emissive_roughness_subsurface")
            if not (isinstance(mers, list) and len(mers) == 4):
                err(f"{pbr_path.relative_to(ROOT)}: {category} fallback MERS missing")

        ll_path = root / "local_lighting" / "local_lighting.json"
        if not ll_path.is_file():
            err(f"missing {ll_path.relative_to(ROOT)}")
        shadow_path = root / "shadows" / "global.json"
        if not shadow_path.is_file():
            err(f"missing {shadow_path.relative_to(ROOT)}")
        if len(list((root / "biomes").glob("*.client_biome.json"))) < 87:
            err(f"subpacks/{sp}: biome bindings incomplete")

    # 4.5.2 loader safety net. The root pack must be usable even if the client has
    # not resolved a subpack yet. Reserved filenames follow Mojang's VV layout.
    root_required = (
        "atmospherics/atmospherics.json", "lighting/global.json",
        "color_grading/color_grading.json", "fogs/default.json", "water/water.json",
        "pbr/global.json", "local_lighting/local_lighting.json", "shadows/global.json",
    )
    for rel in root_required:
        if not (ROOT / rel).is_file():
            err(f"runtime loader failsafe missing {rel}")

    root_regs = {
        "fog": collect_ids(ROOT / "fogs", "minecraft:fog_settings"),
        "atmosphere": collect_ids(ROOT / "atmospherics", "minecraft:atmosphere_settings"),
        "grading": collect_ids(ROOT / "color_grading", "minecraft:color_grading_settings"),
        "lighting": collect_ids(ROOT / "lighting", "minecraft:lighting_settings"),
        "water": collect_ids(ROOT / "water", "minecraft:water_settings"),
    }
    specs = (
        ("minecraft:fog_appearance", "fog_identifier", "fog"),
        ("minecraft:atmosphere_identifier", "atmosphere_identifier", "atmosphere"),
        ("minecraft:color_grading_identifier", "color_grading_identifier", "grading"),
        ("minecraft:lighting_identifier", "lighting_identifier", "lighting"),
        ("minecraft:water_identifier", "water_identifier", "water"),
    )
    base_biomes = list((ROOT / "biomes").glob("*.client_biome.json"))
    if len(base_biomes) < 87:
        err("root biome loader safety net is incomplete")
    for path in base_biomes:
        comps = load(path).get("minecraft:client_biome", {}).get("components", {})
        for comp, field, registry in specs:
            node = comps.get(comp)
            if isinstance(node, dict):
                ident = node.get(field)
                if not isinstance(ident, str) or not ident.startswith("dlavie_root:"):
                    err(f"{path.relative_to(ROOT)}: root failsafe {field} not namespaced")
                elif ident not in root_regs[registry]:
                    err(f"{path.relative_to(ROOT)}: unresolved root failsafe {field}={ident}")

    # Visual project boundary: material textures belong to the separate texture project.
    block_dir = ROOT / "textures" / "blocks"
    if block_dir.exists() and any(block_dir.iterdir()):
        err("visual project contains block textures")
    if list(ROOT.rglob("*.texture_set.json")):
        err("visual project contains block Texture Sets")
    if (ROOT / "tools" / "generate_materials.py").exists() or (ROOT / "tools" / "generate_material_suite.py").exists():
        err("obsolete block-material generator still exists")

    legacy_caustics = ROOT / "textures" / "dlavie" / "derivative_caustics.png"
    if legacy_caustics.exists():
        err("obsolete derivative_caustics.png survived runtime generation")
    textures_list = ROOT / "textures" / "textures_list.json"
    if not textures_list.is_file():
        err("textures_list.json missing")
    else:
        listed = load(textures_list)
        if listed != ["textures/dlavie/optical_caustics"]:
            err(f"textures_list.json contains stale runtime assets: {listed}")

    caustics_path = ROOT / "textures" / "dlavie" / "optical_caustics.png"
    if not caustics_path.is_file():
        err("optical caustics atlas missing")
    else:
        try:
            with Image.open(caustics_path) as im:
                if im.size != (128, 7680):
                    err(f"optical caustics must be 128x7680, got {im.size}")
        except Exception as exc:
            err(f"optical caustics invalid: {exc}")

    if errors:
        print(f"VALIDATION FAILED ({len(errors)} issue(s))")
        for message in errors:
            print(" -", message)
        raise SystemExit(1)
    print(f"Validation OK: DLavie Visual {release.get('version_string')} renderer, root loader failsafe and texture-project boundaries are clean")


if __name__ == "__main__":
    main()
