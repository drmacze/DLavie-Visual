#!/usr/bin/env python3
"""Authoritative cross-system audit for DLavie Visual.

Modes:
  source     checked-in pipeline/release metadata
  generated  fully generated runtime before packaging
  mcpack     final archive integrity and exact runtime file set
"""
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
SUBPACKS = tuple(f"{t}_{q}" for t in THEMES for q in QUALITIES)
PROFILES = ("default", "forest", "dense", "dry", "cold", "swamp", "cave", "ocean")
DIMENSIONS = ("nether", "end")
WATER_KINDS = ("default", "river", "ocean", "swamp", "frozen")
NO_WEATHER_FOG = {"cave", "nether", "end"}
ORE_HOOKS = {
    "minecraft:coal_ore", "minecraft:deepslate_coal_ore", "minecraft:iron_ore", "minecraft:deepslate_iron_ore",
    "minecraft:copper_ore", "minecraft:deepslate_copper_ore", "minecraft:gold_ore", "minecraft:deepslate_gold_ore",
    "minecraft:redstone_ore", "minecraft:deepslate_redstone_ore", "minecraft:lapis_ore", "minecraft:deepslate_lapis_ore",
    "minecraft:diamond_ore", "minecraft:deepslate_diamond_ore", "minecraft:emerald_ore", "minecraft:deepslate_emerald_ore",
    "minecraft:nether_gold_ore", "minecraft:nether_quartz_ore", "minecraft:ancient_debris",
}
FORBIDDEN = ("tools/generate_materials.py", "tools/generate_material_suite.py", "ui/title_screen.json")
ACTIVE_TOOLS = {
    "audit_release.py", "sync_release.py", "package_mcpack.py", "validate_pack.py",
    "generate_configs.py", "generate_assets.py", "generate_optical_caustics.py", "generate_themes.py",
    "enhance_visual_core.py", "enhance_volumetric_fog.py", "enhance_weather_water.py",
    "enhance_underwater_night.py", "enhance_pbr_compat.py",
}
BUILD_STAGES = (
    "audit_release.py source", "sync_release.py", "generate_configs.py", "generate_assets.py",
    "generate_optical_caustics.py", "generate_themes.py", "enhance_visual_core.py",
    "enhance_volumetric_fog.py", "enhance_weather_water.py", "enhance_underwater_night.py",
    "enhance_pbr_compat.py", "validate_pack.py", "audit_release.py generated",
    "package_mcpack.py", "audit_release.py mcpack",
)
EXCLUDE_TOP = {"dist", ".git", "__pycache__", "docs", "THIRD_PARTY_LICENSES", "branding", "tools", ".github", "config", "third_party_runtime"}
ZIP_TIME = (2026, 1, 1, 0, 0, 0)
errors: list[str] = []


def err(msg: str) -> None:
    errors.append(msg)


def load(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        err(f"{path.relative_to(ROOT)}: invalid JSON: {exc}")
        return {}


def finite(value, where: str) -> None:
    if isinstance(value, bool) or value is None or isinstance(value, str):
        return
    if isinstance(value, (int, float)):
        if isinstance(value, float) and not math.isfinite(value):
            err(f"{where}: non-finite number")
    elif isinstance(value, list):
        for i, item in enumerate(value): finite(item, f"{where}[{i}]")
    elif isinstance(value, dict):
        for key, item in value.items(): finite(item, f"{where}.{key}")


def release():
    return load(ROOT / "config" / "release.json")


def check_manifest(manifest: dict, rel: dict, where="manifest.json") -> None:
    ver = rel.get("version")
    if rel.get("version_string") != ".".join(map(str, ver or [])):
        err("config/release.json: version_string mismatch")
    if manifest.get("format_version") != 2: err(f"{where}: format_version != 2")
    h = manifest.get("header", {})
    if h.get("name") != rel.get("name"): err(f"{where}: stale name")
    if h.get("version") != ver: err(f"{where}: stale header version {h.get('version')}")
    if h.get("min_engine_version") != rel.get("min_engine_version"): err(f"{where}: min engine mismatch")
    if rel.get("version_string") not in str(h.get("description", "")): err(f"{where}: description version stale")
    for i, mod in enumerate(manifest.get("modules", [])):
        if mod.get("version") != ver: err(f"{where}: module {i} version stale")
    if "pbr" not in manifest.get("capabilities", []): err(f"{where}: pbr capability missing")
    folders = tuple(x.get("folder_name") for x in manifest.get("subpacks", []))
    if folders != SUBPACKS: err(f"{where}: subpack list/order mismatch")
    if len(folders) != len(set(folders)): err(f"{where}: duplicate subpack folders")
    for sp in manifest.get("subpacks", []):
        if int(sp.get("memory_tier", 999)) > 1: err(f"{where}: {sp.get('folder_name')} mobile memory_tier regression")


def source_audit() -> None:
    rel = release(); check_manifest(load(ROOT / "manifest.json"), rel)
    for path in FORBIDDEN:
        if (ROOT / path).exists(): err(f"legacy system still present: {path}")
    tools = {p.name for p in (ROOT / "tools").glob("*.py")}
    if tools != ACTIVE_TOOLS:
        err(f"active Python tool set mismatch; missing={sorted(ACTIVE_TOOLS-tools)}, orphan={sorted(tools-ACTIVE_TOOLS)}")
    build = (ROOT / "tools" / "build.sh").read_text(encoding="utf-8")
    positions = []
    for stage in BUILD_STAGES:
        if build.count(stage) != 1: err(f"build.sh: {stage!r} must occur exactly once")
        positions.append(build.find(stage))
    if any(p < 0 for p in positions) or positions != sorted(positions): err("build.sh: stage order is invalid")
    workflow = (ROOT / ".github/workflows/build.yml").read_text(encoding="utf-8")
    for token in ("py_compile", "bash -n tools/build.sh", "cmp", "sha256sum"):
        if token not in workflow: err(f"CI hardening missing: {token}")
    for lang in ("texts/en_US.lang", "texts/id_ID.lang"):
        text = (ROOT / lang).read_text(encoding="utf-8")
        if "pack.name=DLavie Visual" not in text or "Natural / Cozy / Gloomy" not in text: err(f"{lang}: stale metadata")
    defs = load(ROOT / "ui/_ui_defs.json")
    for ref in defs.get("ui_defs", []) if isinstance(defs, dict) else []:
        if not (ROOT / ref).is_file(): err(f"ui definition missing: {ref}")
    if "dlavie.home_brand" not in (ROOT / "ui/start_screen.json").read_text(encoding="utf-8"):
        err("start-screen brand injection missing")
    print("Source audit complete")


def registry(folder: Path, component: str) -> set[str]:
    found: set[str] = set()
    for path in sorted(folder.glob("*.json")):
        ident = load(path).get(component, {}).get("description", {}).get("identifier")
        if not ident: err(f"{path.relative_to(ROOT)}: description.identifier missing")
        elif ident in found: err(f"{folder.relative_to(ROOT)}: duplicate identifier {ident}")
        else: found.add(ident)
    return found


def visual_refs(value, where: str) -> None:
    if isinstance(value, dict):
        for k, v in value.items(): visual_refs(v, f"{where}.{k}")
    elif isinstance(value, list):
        for i, v in enumerate(value): visual_refs(v, f"{where}[{i}]")
    elif isinstance(value, str) and value.startswith("textures/dlavie/"):
        if not (ROOT / value).is_file() and not (ROOT / f"{value}.png").is_file(): err(f"{where}: missing texture {value}")


def generated_audit() -> None:
    rel = release(); check_manifest(load(ROOT / "manifest.json"), rel)
    for path in ("subpacks/low", "subpacks/medium", "subpacks/high", "_quality_subpacks", "textures/blocks"):
        if (ROOT / path).exists(): err(f"stale generated path: {path}")
    if list(ROOT.rglob("*.texture_set.json")): err("visual core generated Texture Sets")
    actual = tuple(sorted(p.name for p in (ROOT / "subpacks").iterdir() if p.is_dir()))
    if actual != tuple(sorted(SUBPACKS)): err(f"generated subpacks mismatch: {actual}")
    base_biomes = sorted(p.name for p in (ROOT / "biomes").glob("*.client_biome.json"))
    if len(base_biomes) < 87: err(f"base biome binding count too small: {len(base_biomes)}")

    for base in (ROOT / "biomes", ROOT / "subpacks", ROOT / "ui"):
        for path in base.rglob("*.json") if base.exists() else ():
            obj = load(path); finite(obj, str(path.relative_to(ROOT))); visual_refs(obj, str(path.relative_to(ROOT)))
            if "textures/dlavie/derivative_caustics" in path.read_text(encoding="utf-8"):
                err(f"{path.relative_to(ROOT)}: old caustics reference survived final pass")

    required_env = ("sun.png", "moon_phases.png", "clouds.png", "rain.png", "snow.png")
    for name in required_env:
        if not (ROOT / "textures/environment" / name).is_file(): err(f"missing environment asset {name}")
    ca = ROOT / "textures/dlavie/optical_caustics.png"
    if not ca.is_file(): err("optical caustics missing")
    for path in (ROOT / "textures").rglob("*.png") if (ROOT / "textures").exists() else ():
        try:
            with Image.open(path) as im:
                if im.width <= 0 or im.height <= 0: err(f"{path.relative_to(ROOT)}: invalid dimensions")
                if path == ca and im.size != (128, 7680): err(f"optical caustics size {im.size}, expected 128x7680")
                im.verify()
        except Exception as exc: err(f"{path.relative_to(ROOT)}: invalid PNG: {exc}")

    expected_sets = {
        "atmospherics": set(PROFILES + DIMENSIONS), "lighting": set(PROFILES + DIMENSIONS),
        "color_grading": set(PROFILES + DIMENSIONS), "fogs": set(PROFILES + DIMENSIONS), "water": set(WATER_KINDS),
    }
    for sp in SUBPACKS:
        root = ROOT / "subpacks" / sp; theme, quality = sp.rsplit("_", 1)
        for folder, stems in expected_sets.items():
            got = {p.stem for p in (root / folder).glob("*.json")}
            if got != stems: err(f"{sp}/{folder}: missing={sorted(stems-got)}, extra={sorted(got-stems)}")
        for relpath in ("pbr/global.json", "local_lighting/local_lighting.json", "shadows/global.json"):
            if not (root / relpath).is_file(): err(f"{sp}: missing {relpath}")
        if sorted(p.name for p in (root / "biomes").glob("*.client_biome.json")) != base_biomes: err(f"{sp}: biome set diverged")

        regs = {
            "fog": registry(root / "fogs", "minecraft:fog_settings"),
            "atmosphere": registry(root / "atmospherics", "minecraft:atmosphere_settings"),
            "grading": registry(root / "color_grading", "minecraft:color_grading_settings"),
            "lighting": registry(root / "lighting", "minecraft:lighting_settings"),
            "water": registry(root / "water", "minecraft:water_settings"),
        }
        specs = (
            ("minecraft:fog_appearance", "fog_identifier", "fog"),
            ("minecraft:atmosphere_identifier", "atmosphere_identifier", "atmosphere"),
            ("minecraft:color_grading_identifier", "color_grading_identifier", "grading"),
            ("minecraft:lighting_identifier", "lighting_identifier", "lighting"),
            ("minecraft:water_identifier", "water_identifier", "water"),
        )
        for path in (root / "biomes").glob("*.client_biome.json"):
            comps = load(path).get("minecraft:client_biome", {}).get("components", {})
            for comp, field, reg in specs:
                if isinstance(comps.get(comp), dict):
                    value = comps[comp].get(field)
                    if value not in regs[reg]: err(f"{path.relative_to(ROOT)}: unresolved {field}={value!r}")

        for profile in PROFILES:
            lp = root / "lighting" / f"{profile}.json"; obj = load(lp)
            if obj.get("format_version") != "1.26.0": err(f"{lp.relative_to(ROOT)}: lighting schema != 1.26.0")
            ls = obj.get("minecraft:lighting_settings", {}); amb = ls.get("ambient", {}).get("illuminance", {}); sky = ls.get("sky", {}).get("intensity", {})
            if not isinstance(amb, dict) or "0.50" not in amb or float(amb.get("0.50", 1)) > .012: err(f"{lp.relative_to(ROOT)}: midnight ambient invalid")
            if not isinstance(sky, dict) or "0.50" not in sky or float(sky.get("0.50", 1)) > .20: err(f"{lp.relative_to(ROOT)}: midnight sky invalid")
            sun = ls.get("directional_lights", {}).get("orbital", {}).get("sun", {}).get("illuminance", {})
            vals = [float(v) for v in sun.values()] if isinstance(sun, dict) else [float(sun or 0)]
            if max(vals or [0]) > 110: err(f"{lp.relative_to(ROOT)}: sunlight too high")
        dls = load(root / "lighting/default.json").get("minecraft:lighting_settings", {}); sun = dls.get("directional_lights", {}).get("orbital", {}).get("sun", {}).get("illuminance", {})
        vals = [float(v) for v in sun.values()] if isinstance(sun, dict) else [float(sun or 0)]
        if max(vals or [0]) < 60: err(f"{sp}: default daylight too dim")
        sky = dls.get("sky", {}).get("intensity", {})
        if isinstance(sky, dict) and float(sky.get("0.0", 0)) < {"low":.38, "medium":.45, "high":.52}[quality]: err(f"{sp}: PBR sky IBL below floor")

        for profile in PROFILES:
            ap = root / "atmospherics" / f"{profile}.json"; obj = load(ap)
            if obj.get("format_version") != "1.21.40": err(f"{ap.relative_to(ROOT)}: atmosphere schema changed")
            at = obj.get("minecraft:atmosphere_settings", {})
            for key in ("sky_zenith_color", "sky_horizon_color"):
                cmap = at.get(key, {})
                if not all(k in cmap for k in ("0.315", "0.50", "0.685")): err(f"{ap.relative_to(ROOT)}: twilight keys incomplete")

        for fp in (root / "fogs").glob("*.json"):
            obj = load(fp); fg = obj.get("minecraft:fog_settings", {}); vol = fg.get("volumetric", {}); den = vol.get("density", {}); media = vol.get("media_coefficients", {}); hg = vol.get("henyey_greenstein_g", {})
            if obj.get("format_version") != "1.21.90": err(f"{fp.relative_to(ROOT)}: fog schema != 1.21.90")
            if not all(k in den for k in ("air", "water")): err(f"{fp.relative_to(ROOT)}: fog density incomplete")
            if not all(k in media for k in ("air", "water", "cloud")): err(f"{fp.relative_to(ROOT)}: fog media incomplete")
            for medium in ("air", "water"):
                g = hg.get(medium, {}).get("henyey_greenstein_g")
                if g is None or not -1 <= float(g) <= 1: err(f"{fp.relative_to(ROOT)}: invalid {medium} HG")
            if fp.stem not in NO_WEATHER_FOG and "weather" not in den: err(f"{fp.relative_to(ROOT)}: weather volume missing")
            if "transition_fog" not in fg.get("distance", {}).get("water", {}): err(f"{fp.relative_to(ROOT)}: underwater transition missing")

        min_oct = {"low": 7, "medium": 14, "high": 20}[quality]
        for kind in WATER_KINDS:
            wp = root / "water" / f"{kind}.json"; obj = load(wp); ws = obj.get("minecraft:water_settings", {})
            if obj.get("format_version") != "1.26.0": err(f"{wp.relative_to(ROOT)}: water schema != 1.26.0")
            if not all(k in ws.get("particle_concentrations", {}) for k in ("chlorophyll", "suspended_sediment", "cdom")): err(f"{wp.relative_to(ROOT)}: absorption particles incomplete")
            waves = ws.get("waves", {}); caustics = ws.get("caustics", {})
            if not waves.get("enabled") or int(waves.get("octaves", 0)) < min_oct: err(f"{wp.relative_to(ROOT)}: wave quality regressed")
            if not caustics.get("enabled") or caustics.get("texture") != "textures/dlavie/optical_caustics": err(f"{wp.relative_to(ROOT)}: caustics regression")

        llp = root / "local_lighting/local_lighting.json"; llobj = load(llp); ll = llobj.get("minecraft:local_light_settings", {})
        if llobj.get("format_version") != "1.21.120": err(f"{llp.relative_to(ROOT)}: local-light schema changed")
        if ORE_HOOKS - set(ll): err(f"{llp.relative_to(ROOT)}: ore hooks missing")
        if quality == "high" and any(ll.get(k, {}).get("light_type") != "point_light" for k in ORE_HOOKS): err(f"{llp.relative_to(ROOT)}: High ore point-light hook regression")

        pbrp = root / "pbr/global.json"; pbr = load(pbrp).get("minecraft:pbr_fallback_settings", {})
        for cat in ("blocks", "actors", "particles", "items"):
            mers = pbr.get(cat, {}).get("global_metalness_emissive_roughness_subsurface")
            if not (isinstance(mers, list) and len(mers) == 4 and all(isinstance(v, (int, float)) and 0 <= v <= 255 for v in mers)): err(f"{pbrp.relative_to(ROOT)}: invalid {cat} MERS")
            elif mers[0] != 0 or mers[1] != 0 or mers[3] != 0 or float(mers[2]) < 200: err(f"{pbrp.relative_to(ROOT)}: unsafe {cat} fallback")
    print("Generated runtime audit complete")


def expected_runtime() -> set[str]:
    result: set[str] = set()
    for path in ROOT.rglob("*"):
        if not path.is_file(): continue
        rel = path.relative_to(ROOT)
        if rel.parts[0] in EXCLUDE_TOP or rel.name in {".DS_Store", ".gitignore"}: continue
        result.add(rel.as_posix())
    result.add("THIRD_PARTY_LICENSES/DERCODE-License-2.5.txt")
    return result


def mcpack_audit(path: Path) -> None:
    if not path.is_file(): err(f"mcpack missing: {path}"); return
    rel = release()
    try:
        with zipfile.ZipFile(path) as zf:
            if zf.testzip(): err("mcpack CRC test failed")
            infos = zf.infolist(); names = [i.filename for i in infos]; counts = Counter(names)
            if any(v > 1 for v in counts.values()): err("mcpack contains duplicate paths")
            for info in infos:
                pure = PurePosixPath(info.filename)
                if pure.is_absolute() or ".." in pure.parts or "\\" in info.filename: err(f"unsafe archive path {info.filename}")
                if info.date_time != ZIP_TIME: err(f"non-deterministic timestamp {info.filename}: {info.date_time}")
            actual = set(names); expected = expected_runtime()
            if actual != expected: err(f"mcpack file-set mismatch; missing={sorted(expected-actual)[:10]}, extra={sorted(actual-expected)[:10]}")
            if any(n.startswith("textures/blocks/") or n.endswith(".texture_set.json") for n in names): err("mcpack leaked block material data")
            for top in ("tools/", "config/", "docs/", ".github/", "branding/", "third_party_runtime/", "dist/"):
                if any(n.startswith(top) for n in names): err(f"mcpack leaked development path {top}")
            if "THIRD_PARTY_LICENSES/DERCODE-License-2.5.txt" not in actual: err("third-party license missing from mcpack")
            check_manifest(json.loads(zf.read("manifest.json")), rel, "mcpack:manifest.json")
            for name in names:
                if name.endswith(".json"):
                    try:
                        obj = json.loads(zf.read(name)); finite(obj, f"mcpack:{name}")
                    except Exception as exc: err(f"mcpack:{name}: invalid JSON: {exc}")
                elif name.endswith(".png"):
                    try:
                        with Image.open(BytesIO(zf.read(name))) as im: im.verify()
                    except Exception as exc: err(f"mcpack:{name}: invalid PNG: {exc}")
    except zipfile.BadZipFile as exc: err(f"invalid mcpack ZIP: {exc}")
    print(f"mcpack audit complete: {path.name} sha256={hashlib.sha256(path.read_bytes()).hexdigest()}")


def finish() -> None:
    if errors:
        print(f"AUDIT FAILED ({len(errors)} issue(s))")
        for message in errors: print(" -", message)
        raise SystemExit(1)
    print("AUDIT OK: no stale pipeline, unresolved runtime reference, malformed asset, or package-structure error detected")


def main() -> None:
    if len(sys.argv) < 2 or sys.argv[1] not in {"source", "generated", "mcpack"}: raise SystemExit("usage: audit_release.py source|generated|mcpack [path]")
    if sys.argv[1] == "source": source_audit()
    elif sys.argv[1] == "generated": generated_audit()
    else:
        path = Path(sys.argv[2]) if len(sys.argv) > 2 else ROOT / "dist/DLavie-Visual.mcpack"
        if not path.is_absolute(): path = ROOT / path
        mcpack_audit(path)
    finish()


if __name__ == "__main__": main()
