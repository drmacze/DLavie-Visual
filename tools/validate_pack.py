#!/usr/bin/env python3
from pathlib import Path
import json, struct, sys
ROOT=Path(__file__).resolve().parents[1]
errors=[]
def err(x): errors.append(x)
def load(p):
    try: return json.loads((ROOT/p).read_text(encoding="utf-8"))
    except Exception as e: err(f"{p}: invalid JSON: {e}"); return {}
manifest=load("manifest.json")
if manifest.get("format_version")!=2: err("manifest format_version must be 2")
if manifest.get("header",{}).get("min_engine_version",[]) < [1,26,40]: err("min_engine_version must be >= 1.26.40")
if "pbr" not in manifest.get("capabilities",[]): err("manifest must include pbr capability")
sp=manifest.get("subpacks",[])
if [x.get("folder_name") for x in sp] != ["low","medium","high"]: err("subpacks must be low/medium/high")
if [x.get("memory_tier") for x in sp] != [8,12,20]: err("unexpected memory tiers")
req=["atmospherics/atmospherics.json","lighting/global.json","color_grading/color_grading.json","pbr/global.json","water/water.json","fogs/dlavie_overworld.json","point_lights/global.json","shadows/shadows.json"]
for pre in ("low","medium","high"):
    for rel in req:
        p=Path("subpacks")/pre/rel
        if not (ROOT/p).is_file(): err(f"missing {p}")
        else: load(p)
    for rel in ["textures/environment/clouds.png","textures/environment/sun.png","textures/environment/moon_phases.png","textures/colormap/grass.png","textures/colormap/foliage.png"]:
        p=ROOT/"subpacks"/pre/rel
        if not p.is_file(): err(f"missing {p.relative_to(ROOT)}"); continue
        data=p.read_bytes()
        if data[:8]!=b"\x89PNG\r\n\x1a\n": err(f"not PNG: {p.relative_to(ROOT)}")
for p in (ROOT/"biomes").glob("*.json"):
    o=load(p.relative_to(ROOT)); comp=o.get("minecraft:client_biome",{}).get("components",{})
    for k in ["minecraft:atmosphere_identifier","minecraft:color_grading_identifier","minecraft:lighting_identifier","minecraft:water_identifier"]:
        if k not in comp: err(f"{p.name}: missing {k}")
for p in [ROOT/"pack_icon.png",ROOT/"branding"/"cover.svg"]:
    if not p.is_file(): err(f"missing {p.relative_to(ROOT)}")
lic=(ROOT/"THIRD_PARTY_LICENSES"/"DERCODE-License-2.5.txt")
if not lic.is_file() or "DERCODE License Agreement 2.5" not in lic.read_text(encoding="utf-8"): err("DERCODE 2.5 license missing")
attr=(ROOT/"SOURCE_ATTRIBUTION.md").read_text(encoding="utf-8")
for name in ["_DureXXX","M1zore","Skeeder461","Frs0n","_Sone4ka_"]:
    if name not in attr: err(f"missing source credit: {name}")
if errors:
    print("VALIDATION FAILED")
    for x in errors: print(" -",x)
    sys.exit(1)
print(f"Validation OK: {len(list((ROOT/'biomes').glob('*.json')))} biome bindings, 3 presets, PBR enabled")
