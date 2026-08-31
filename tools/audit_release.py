#!/usr/bin/env python3
"""Cross-system audit for DLavie Visual source, generated runtime, and final mcpack."""
from __future__ import annotations

from collections import Counter
from io import BytesIO
from pathlib import Path, PurePosixPath
import hashlib
import json
import math
import sys
import zipfile

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
THEMES = ("natural", "cozy", "gloomy")
QUALITIES = ("low", "medium", "high")
SUBPACKS = tuple(f"{theme}_{quality}" for theme in THEMES for quality in QUALITIES)
PROFILES = ("default", "forest", "dense", "dry", "cold", "swamp", "cave", "ocean")
DIMENSIONS = ("nether", "end")
WATER_KINDS = ("default", "river", "ocean", "swamp", "frozen")
ORE_HOOKS = {
    "minecraft:coal_ore", "minecraft:deepslate_coal_ore",
    "minecraft:iron_ore", "minecraft:deepslate_iron_ore",
    "minecraft:copper_ore", "minecraft:deepslate_copper_ore",
    "minecraft:gold_ore", "minecraft:deepslate_gold_ore",
    "minecraft:redstone_ore", "minecraft:deepslate_redstone_ore",
    "minecraft:lapis_ore", "minecraft:deepslate_lapis_ore",
    "minecraft:diamond_ore", "minecraft:deepslate_diamond_ore",
    "minecraft:emerald_ore", "minecraft:deepslate_emerald_ore",
    "minecraft:nether_gold_ore", "minecraft:nether_quartz_ore", "minecraft:ancient_debris",
}
FORBIDDEN_LEGACY = (
    "tools/generate_materials.py",
    "tools/generate_material_suite.py",
    "ui/title_screen.json",
)
ACTIVE_TOOLS = {
    "audit_release.py", "sync_release.py", "package_mcpack.py", "validate_pack.py",
    "generate_configs.py", "generate_assets.py", "generate_optical_caustics.py", "generate_themes.py",
    "enhance_visual_core.py", "enhance_volumetric_fog.py", "enhance_weather_water.py",
    "enhance_underwater_night.py", "enhance_pbr_compat.py",
}
BUILD_STAGES = (
    "audit_release.py source",
    "sync_release.py",
    "generate_configs.py",
    "generate_assets.py",
    "generate_optical_caustics.py",
    "generate_themes.py",
    "enhance_visual_core.py",
    "enhance_volumetric_fog.py",
    "enhance_weather_water.py",
    "enhance_underwater_night.py",
    "enhance_pbr_compat.py",
    "validate_pack.py",
    "audit_release.py generated",
    "package_mcpack.py",
    "audit_release.py mcpack",
)
PACKAGE_EXCLUDE_TOP = {
    "dist", ".git", "__pycache__", "docs", "THIRD_PARTY_LICENSES", "branding",
    "tools", ".github", "config", "third_party_runtime",
}
FIXED_ZIP_TIME = (2026, 1, 1, 0, 0, 0)

errors: list[str] = []
warnings: list[str] = []


def err(message: str) -> None:
    errors.append(message)


def warn(message: str) -> None:
    warnings.append(message)


def load_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        err(f"{path.relative_to(ROOT)}: invalid JSON: {exc}")
        return {}


def release_data():
    return load_json(ROOT / "config" / "release.json")


def check_finite(value, where: str) -> None:
    if isinstance(value, bool) or value is None or isinstance(value, str):
        return
    if isinstance(value, (int, float)):
        if isinstance(value, float) and not math.isfinite(value):
            err(f"{where}: non-finite numeric value {value!r}")
        return
    if isinstance(value, list):
        for i, item in enumerate(value):
            check_finite(item, f"{where}[{i}]")
    elif isinstance(value, dict):
        for key, item in value.items():
            check_finite(item, f"{where}.{key}")


def manifest_checks(manifest: dict, release: dict, where: str = "manifest.json") -> None:
    version = release.get("version")
    if release.get("version_string") != ".".join(map(str, version or [])):
        err("config/release.json: version_string does not match version")
    if manifest.get("format_version") != 2:
        err(f"{where}: format_version must be 2")
    header = manifest.get("header", {})
    if header.get("name") != release.get("name"):
        err(f"{where}: header.name is not synchronized with config/release.json")
    if header.get("version") != version:
        err(f"{where}: header.version {header.get('version')} != release version {version}")
    if header.get("min_engine_version") != release.get("min_engine_version"):
        err(f"{where}: min_engine_version is not synchronized")
    if release.get("version_string") not in str(header.get("description", "")):
        err(f"{where}: description does not contain current release version")
    modules = manifest.get("modules", [])
    if not modules:
        err(f"{where}: modules missing")
    for i, module in enumerate(modules):
        if module.get("version") != version:
            err(f"{where}: modules[{i}].version is stale")
    if "pbr" not in manifest.get("capabilities", []):
        err(f"{where}: pbr capability missing")
    subpacks = manifest.get("subpacks", [])
    folders = tuple(item.get("folder_name") for item in subpacks)
    if folders != SUBPACKS:
        err(f"{where}: subpack order/list mismatch: {folders}")
    if len(folders) != len(set(folders)):
        err(f"{where}: duplicate subpack folder names")
    for item in subpacks:
        if int(item.get("memory_tier", 999)) > 1:
            err(f"{where}: {item.get('folder_name')} memory_tier would lock mobile selection")


def source_audit() -> None:
    release = release_data()
    manifest = load_json(ROOT / "manifest.json")
    manifest_checks(manifest, release)

    for rel in FORBIDDEN_LEGACY:
        if (ROOT / rel).exists():
            err(f"legacy/forbidden system still present: {rel}")

    tools = {p.name for p in (ROOT / "tools").glob("*.py")}
    extra = sorted(tools - ACTIVE_TOOLS)
    missing = sorted(ACTIVE_TOOLS - tools)
    if extra:
        err(f"orphan Python tools not part of current build pipeline: {extra}")
    if missing:
        err(f"required pipeline tools missing: {missing}")

    build = (ROOT / "tools" / "build.sh").read_text(encoding="utf-8")
    positions = []
    for stage in BUILD_STAGES:
        count = build.count(stage)
        if count != 1:
            err(f"tools/build.sh: stage {stage!r} occurs {count} times; expected exactly once")
        positions.append(build.find(stage))
    if any(x < 0 for x in positions) or positions != sorted(positions):
        err("tools/build.sh: generation/enhancement/audit stages are out of order")

    workflow = (ROOT / ".github" / "workflows" / "build.yml").read_text(encoding="utf-8")
    for required in ("py_compile", "bash -n tools/build.sh", "cmp", "sha256sum"):
        if required not in workflow:
            err(f"CI workflow missing hardening check: {required}")

    for lang in ("texts/en_US.lang", "texts/id_ID.lang"):
        text = (ROOT / lang).read_text(encoding="utf-8")
        if "pack.name=DLavie Visual" not in text or "Natural / Cozy / Gloomy" not in text:
            err(f"{lang}: stale/incomplete pack metadata")

    ui_defs = load_json(ROOT / "ui" / "_ui_defs.json")
    refs = ui_defs.get("ui_defs", []) if isinstance(ui_defs, dict) else []
    for ref in refs:
        if not (ROOT / ref).is_file():
            err(f"ui/_ui_defs.json references missing file: {ref}")
    start_ui = (ROOT / "ui" / "start_screen.json").read_text(encoding="utf-8")
    if "dlavie.home_brand" not in start_ui:
        err("ui/start_screen.json: DLavie home brand injection missing")

    print("Source audit complete")


def identifier_from(obj: dict, component: str):
    section = obj.get(component, {})
    return section.get("description", {}).get("identifier") if isinstance(section, dict) else None


def load_registry(folder: Path, component: str) -> set[str]:
    out: set[str] = set()
    for path in sorted(folder.glob("*.json")):
        obj = load_json(path)
        ident = identifier_from(obj, component)
        if not ident:
            err(f"{path.relative_to(ROOT)}: missing description.identifier")
            continue
        if ident in out:
            err(f"{folder.relative_to(ROOT)}: duplicate identifier {ident}")
        out.add(ident)
    return out


def check_texture_reference(value, where: str) -> None:
    if not isinstance(value, str) or not value.startswith("textures/dlavie/"):
        return
    candidates = [ROOT / value, ROOT / f"{value}.png"]
    if not any(path.is_file() for path in candidates):
        err(f"{where}: missing referenced visual texture {value}")


def recurse_texture_refs(value, where: str) -> None:
    if isinstance(value, dict):
        for k, v in value.items():
            recurse_texture_refs(v, f"{where}.{k}")
    elif isinstance(value, list):
        for i, v in enumerate(value):
            recurse_texture_refs(v, f"{where}[{i}]")
    else:
        check_texture_reference(value, where)


def generated_audit() -> None:
    release = release_data()
    manifest = load_json(ROOT / "manifest.json")
    manifest_checks(manifest, release)

    # Ensure old build intermediates and old material systems cannot survive a rebuild.
    for rel in ("subpacks/low", "subpacks/medium", "subpacks/high", "_quality_subpacks", "textures/blocks"):
        if (ROOT / rel).exists():
            err(f"stale generated path survived current pipeline: {rel}")
    texture_sets = list(ROOT.rglob("*.texture_set.json"))
    if texture_sets:
        err(f"visual-only project generated {len(texture_sets)} block Texture Sets")

    subpack_root = ROOT / "subpacks"
    actual_subpacks = tuple(sorted(p.name for p in subpack_root.iterdir() if p.is_dir())) if subpack_root.is_dir() else ()
    if actual_subpacks != tuple(sorted(SUBPACKS)):
        err(f"generated subpack directories mismatch: {actual_subpacks}")

    base_biomes = sorted(p.name for p in (ROOT / "biomes").glob("*.client_biome.json"))
    if len(base_biomes) < 87:
        err(f"base biome bindings incomplete: {len(base_biomes)}")

    # Global parse/finite/reference pass across every JSON that will influence runtime.
    json_roots = [ROOT / "biomes", ROOT / "subpacks", ROOT / "ui"]
    for json_root in json_roots:
        for path in json_root.rglob("*.json") if json_root.exists() else ():
            obj = load_json(path)
            check_finite(obj, str(path.relative_to(ROOT)))
            recurse_texture_refs(obj, str(path.relative_to(ROOT)))
            raw = path.read_text(encoding="utf-8")
            if "textures/dlavie/derivative_caustics" in raw:
                err(f"{path.relative_to(ROOT)}: stale Derivative caustics reference survived optical-caustics pass")

    for env in ("sun.png", "moon_phases.png", "clouds.png", "rain.png", "snow.png"):
        path = ROOT / "textures" / "environment" / env
        if not path.is_file():
            err(f"missing environment asset: {path.relative_to(ROOT)}")
    caustics = ROOT / "textures" / "dlavie" / "optical_caustics.png"
    if not caustics.is_file():
        err("missing textures/dlavie/optical_caustics.png")
    else:
        try:
            with Image.open(caustics) as im:
                if im.size != (128, 7680):
                    err(f"optical caustics atlas must be 128x7680, got {im.size}")
                im.verify()
        except Exception as exc:
            err(f"optical caustics PNG invalid: {exc}")

    for path in (ROOT / "textures").rglob("*.png") if (ROOT / "textures").exists() else ():
        try:
            with Image.open(path) as im:
                if im.width <= 0 or im.height <= 0:
                    err(f"{path.relative_to(ROOT)}: zero-sized PNG")
                im.verify()
        except Exception as exc:
            err(f"{path.relative_to(ROOT)}: corrupt PNG: {exc}")

    for sp in SUBPACKS:
        root = subpack_root / sp
        theme, quality = sp.rsplit("_", 1)
        expected_files = {
            "atmospherics": set(PROFILES + DIMENSIONS),
            "lighting": set(PROFILES + DIMENSIONS),
            "color_grading": set(PROFILES + DIMENSIONS),
            "fogs": set(PROFILES + DIMENSIONS),
            "water": set(WATER_KINDS),
        }
        for folder, stems in expected_files.items():
            actual = {p.stem for p in (root / folder).glob("*.json")}
            if actual != stems:
                err(f"subpacks/{sp}/{folder}: files mismatch; missing={sorted(stems-actual)}, extra={sorted(actual-stems)}")

        for rel in ("pbr/global.json", "local_lighting/local_lighting.json", "shadows/global.json"):
            if not (root / rel).is_file():
                err(f"subpacks/{sp}: missing {rel}")

        themed_biomes = sorted(p.name for p in (root / "biomes").glob("*.client_biome.json"))
        if themed_biomes != base_biomes:
            err(f"subpacks/{sp}/biomes: bindings differ from generated base biome set")

        registries = {
            "fog": load_registry(root / "fogs", "minecraft:fog_settings"),
            "atmosphere": load_registry(root / "atmospherics", "minecraft:atmosphere_settings"),
            "color_grading": load_registry(root / "color_grading", "minecraft:color_grading_settings"),
            "lighting": load_registry(root / "lighting", "minecraft:lighting_settings"),
            "water": load_registry(root / "water", "minecraft:water_settings"),
        }
        ref_specs = (
            ("minecraft:fog_appearance", "fog_identifier", "fog"),
            ("minecraft:atmosphere_identifier", "atmosphere_identifier", "atmosphere"),
            ("minecraft:color_grading_identifier", "color_grading_identifier", "color_grading"),
            ("minecraft:lighting_identifier", "lighting_identifier", "lighting"),
            ("minecraft:water_identifier", "water_identifier", "water"),
        )
        for biome_path in (root / "biomes").glob("*.client_biome.json"):
            biome = load_json(biome_path).get("minecraft:client_biome", {})
            comps = biome.get("components", {})
            for comp_name, field, registry_name in ref_specs:
                comp = comps.get(comp_name)
                if not isinstance(comp, dict):
                    continue
                value = comp.get(field)
                if value not in registries[registry_name]:
                    err(f"{biome_path.relative_to(ROOT)}: unresolved {field}={value!r}")

        # Lighting: current Overworld schema, calibrated sun, dark midnight, PBR-friendly sky IBL.
        for profile in PROFILES:
            path = root / "lighting" / f"{profile}.json"
            obj = load_json(path)
            if obj.get("format_version") != "1.26.0":
                err(f"{path.relative_to(ROOT)}: Overworld lighting schema must be 1.26.0")
            ls = obj.get("minecraft:lighting_settings", {})
            sun = ls.get("directional_lights", {}).get("orbital", {}).get("sun", {}).get("illuminance", {})
            sun_values = [float(v) for v in sun.values()] if isinstance(sun, dict) else [float(sun or 0)]
            if max(sun_values or [0]) > 110:
                err(f"{path.relative_to(ROOT)}: sunlight exceeds calibrated range")
            amb = ls.get("ambient", {}).get("illuminance", {})
            sky = ls.get("sky", {}).get("intensity", {})
            if not isinstance(amb, dict) or "0.50" not in amb:
                err(f"{path.relative_to(ROOT)}: midnight ambient keyframe missing")
            elif float(amb["0.50"]) > 0.012:
                err(f"{path.relative_to(ROOT)}: midnight ambient too bright")
            if not isinstance(sky, dict) or "0.50" not in sky:
                err(f"{path.relative_to(ROOT)}: midnight sky keyframe missing")
            elif float(sky["0.50"]) > 0.20:
                err(f"{path.relative_to(ROOT)}: midnight sky too bright")
        default_lighting = load_json(root / "lighting" / "default.json").get("minecraft:lighting_settings", {})
        default_sun = default_lighting.get("directional_lights", {}).get("orbital", {}).get("sun", {}).get("illuminance", {})
        default_sun_values = [float(v) for v in default_sun.values()] if isinstance(default_sun, dict) else [float(default_sun or 0)]
        if max(default_sun_values or [0]) < 60:
            err(f"subpacks/{sp}/lighting/default.json: daylight unexpectedly dim")
        sky_map = default_lighting.get("sky", {}).get("intensity", {})
        if isinstance(sky_map, dict) and float(sky_map.get("0.0", 0)) < {"low":0.38,"medium":0.45,"high":0.52}[quality]:
            err(f"subpacks/{sp}/lighting/default.json: daytime sky IBL below PBR compatibility floor")

        for profile in PROFILES:
            path = root / "atmospherics" / f"{profile}.json"
            obj = load_json(path)
            if obj.get("format_version") != "1.21.40":
                err(f"{path.relative_to(ROOT)}: atmosphere schema changed unexpectedly")
            at = obj.get("minecraft:atmosphere_settings", {})
            for key in ("sky_zenith_color", "sky_horizon_color"):
                cmap = at.get(key, {})
                if not all(k in cmap for k in ("0.315", "0.50", "0.685")):
                    err(f"{path.relative_to(ROOT)}: incomplete cinematic twilight/midnight {key} keys")

        for path in (root / "fogs").glob("*.json"):
            obj = load_json(path)
            if obj.get("format_version") != "1.21.90":
                err(f"{path.relative_to(ROOT)}: fog schema must be 1.21.90 after enhancement pass")
            fg = obj.get("minecraft:fog_settings", {})
            vol = fg.get("volumetric", {})
            density = vol.get("density", {})
            media = vol.get("media_coefficients", {})
            hg = vol.get("henyey_greenstein_g", {})
            if not all(k in density for k in ("air", "water")):
                err(f"{path.relative_to(ROOT)}: air/water volumetric density missing")
            if not all(k in media for k in ("air", "water", "cloud")):
                err(f"{path.relative_to(ROOT)}: air/water/cloud media coefficients missing")
            for medium in ("air", "water"):
                g = hg.get(medium, {}).get("henyey_greenstein_g")
                if g is None or not -1 <= float(g) <= 1:
                    err(f"{path.relative_to(ROOT)}: invalid {medium} Henyey-Greenstein value")
            if path.stem not in DIMENSIONS and "weather" not in density:
                err(f"{path.relative_to(ROOT)}: active-weather volumetric density missing")
            water_dist = fg.get("distance", {}).get("water", {})
            if "transition_fog" not in water_dist:
                err(f"{path.relative_to(ROOT)}: underwater transition fog missing")

        min_octaves = {"low": 7, "medium": 14, "high": 20}[quality]
        for kind in WATER_KINDS:
            path = root / "water" / f"{kind}.json"
            obj = load_json(path)
            if obj.get("format_version") != "1.26.0":
                err(f"{path.relative_to(ROOT)}: water schema must be 1.26.0")
            ws = obj.get("minecraft:water_settings", {})
            particles = ws.get("particle_concentrations", {})
            if not all(k in particles for k in ("chlorophyll", "suspended_sediment", "cdom")):
                err(f"{path.relative_to(ROOT)}: depth-absorption particle concentrations incomplete")
            waves = ws.get("waves", {})
            if not waves.get("enabled") or int(waves.get("octaves", 0)) < min_octaves:
                err(f"{path.relative_to(ROOT)}: water wave quality regressed")
            caustics_cfg = ws.get("caustics", {})
            if not caustics_cfg.get("enabled"):
                err(f"{path.relative_to(ROOT)}: caustics disabled")
            if caustics_cfg.get("texture") != "textures/dlavie/optical_caustics":
                err(f"{path.relative_to(ROOT)}: stale/wrong caustics texture reference")

        ll_path = root / "local_lighting" / "local_lighting.json"
        ll_obj = load_json(ll_path)
        if ll_obj.get("format_version") != "1.21.120":
            err(f"{ll_path.relative_to(ROOT)}: local-light schema changed unexpectedly")
        ll = ll_obj.get("minecraft:local_light_settings", {})
        missing_ores = sorted(ORE_HOOKS - set(ll))
        if missing_ores:
            err(f"{ll_path.relative_to(ROOT)}: ore hooks missing: {missing_ores}")
        if quality == "high":
            wrong = sorted(k for k in ORE_HOOKS if ll.get(k, {}).get("light_type") != "point_light")
            if wrong:
                err(f"{ll_path.relative_to(ROOT)}: High ore hooks not point lights: {wrong}")

        pbr_path = root / "pbr" / "global.json"
        pbr = load_json(pbr_path).get("minecraft:pbr_fallback_settings", {})
        for category in ("blocks", "actors", "particles", "items"):
            mers = pbr.get(category, {}).get("global_metalness_emissive_roughness_subsurface")
            if not (isinstance(mers, list) and len(mers) == 4 and all(isinstance(v, (int, float)) and 0 <= v <= 255 for v in mers)):
                err(f"{pbr_path.relative_to(ROOT)}: invalid {category} fallback MERS")
                continue
            if mers[0] != 0 or mers[1] != 0 or mers[3] != 0:
                err(f"{pbr_path.relative_to(ROOT)}: fallback must remain non-metal/non-emissive/no-subsurface")
            if float(mers[2]) < 200:
                err(f"{pbr_path.relative_to(ROOT)}: fallback roughness too low; may make non-PBR packs look plastic")

    print("Generated runtime audit complete")


def expected_runtime_paths() -> set[str]:
    paths: set[str] = set()
    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(ROOT)
        if rel.parts[0] in PACKAGE_EXCLUDE_TOP:
            continue
        if rel.name in {".DS_Store", ".gitignore"}:
            continue
        paths.add(rel.as_posix())
    paths.add("THIRD_PARTY_LICENSES/DERCODE-License-2.5.txt")
    return paths


def mcpack_audit(mcpack: Path) -> None:
    if not mcpack.is_file():
        err(f"mcpack missing: {mcpack}")
        return
    release = release_data()
    try:
        with zipfile.ZipFile(mcpack) as zf:
            bad = zf.testzip()
            if bad:
                err(f"mcpack CRC failure: {bad}")
            infos = zf.infolist()
            names = [i.filename for i in infos]
            counts = Counter(names)
            duplicates = sorted(name for name, count in counts.items() if count > 1)
            if duplicates:
                err(f"mcpack contains duplicate paths: {duplicates[:10]}")
            for info in infos:
                pure = PurePosixPath(info.filename)
                if pure.is_absolute() or ".." in pure.parts or "\\" in info.filename:
                    err(f"unsafe archive path: {info.filename}")
                if info.date_time != FIXED_ZIP_TIME:
                    err(f"non-deterministic ZIP timestamp: {info.filename} -> {info.date_time}")
            expected = expected_runtime_paths()
            actual = set(names)
            if actual != expected:
                missing = sorted(expected - actual)
                extra = sorted(actual - expected)
                err(f"mcpack runtime file set mismatch; missing={missing[:12]}, extra={extra[:12]}")
            forbidden_tops = {"tools", "config", "docs", ".github", "branding", "third_party_runtime", "dist"}
            leaked = sorted(name for name in names if name.split("/", 1)[0] in forbidden_tops)
            if leaked:
                err(f"development/source files leaked into mcpack: {leaked[:12]}")
            if any(name.startswith("textures/blocks/") or name.endswith(".texture_set.json") for name in names):
                err("mcpack contains forbidden block texture/material data")
            if "THIRD_PARTY_LICENSES/DERCODE-License-2.5.txt" not in actual:
                err("mcpack missing Derivative third-party license")

            manifest = json.loads(zf.read("manifest.json"))
            manifest_checks(manifest, release, "mcpack:manifest.json")
            for name in names:
                if name.endswith(".json"):
                    try:
                        obj = json.loads(zf.read(name))
                        check_finite(obj, f"mcpack:{name}")
                    except Exception as exc:
                        err(f"mcpack:{name}: invalid JSON: {exc}")
                elif name.endswith(".png"):
                    try:
                        with Image.open(BytesIO(zf.read(name))) as im:
                            if im.width <= 0 or im.height <= 0:
                                err(f"mcpack:{name}: zero-sized PNG")
                            im.verify()
                    except Exception as exc:
                        err(f"mcpack:{name}: invalid PNG: {exc}")
    except zipfile.BadZipFile as exc:
        err(f"invalid mcpack ZIP: {exc}")
        return

    digest = hashlib.sha256(mcpack.read_bytes()).hexdigest()
    print(f"mcpack audit complete: {mcpack.name} sha256={digest}")


def finish() -> None:
    for message in warnings:
        print(f"AUDIT WARNING: {message}")
    if errors:
        print(f"AUDIT FAILED ({len(errors)} issue(s))")
        for message in errors:
            print(f" - {message}")
        raise SystemExit(1)
    print("AUDIT OK: no stale pipeline, unresolved runtime reference, malformed asset, or package-structure error detected")


def main(argv: list[str]) -> None:
    if len(argv) < 2 or argv[1] not in {"source", "generated", "mcpack"}:
        raise SystemExit("usage: audit_release.py source|generated|mcpack [path]")
    mode = argv[1]
    if mode == "source":
        source_audit()
    elif mode == "generated":
        generated_audit()
    else:
        path = Path(argv[2]) if len(argv) > 2 else ROOT / "dist" / "DLavie-Visual.mcpack"
        if not path.is_absolute():
            path = ROOT / path
        mcpack_audit(path)
    finish()


if __name__ == "__main__":
    main(sys.argv)
