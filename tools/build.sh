#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

# Fail early on stale/orphan source systems before generating runtime content.
python3 -B tools/audit_release.py source
python3 -B tools/sync_release.py

# Visual-only build: no block albedo/normal/AO/MERS generation in this project.
# Root renderer folders are regenerated too; selected subpacks override root files normally.
rm -rf biomes subpacks textures pack_icon.png _quality_subpacks \
  atmospherics lighting color_grading fogs water pbr local_lighting shadows
python3 -B tools/generate_configs.py >/dev/null
echo "Generated base renderer configs"
python3 -B tools/generate_assets.py >/dev/null
echo "Generated visual environment assets"
python3 -B tools/generate_optical_caustics.py
python3 -B tools/generate_themes.py

# Bind to the actual vanilla biome identifiers used by current Bedrock resource packs.
python3 -B - <<'PY'
from pathlib import Path
import json
root=Path('.')
dirs=[root/'biomes']+[p/'biomes' for p in sorted((root/'subpacks').iterdir()) if p.is_dir()]
count=0
for directory in dirs:
    for path in sorted(directory.glob('*.client_biome.json')):
        obj=json.loads(path.read_text(encoding='utf-8'))
        cb=obj.get('minecraft:client_biome')
        if not isinstance(cb,dict): raise SystemExit(f'{path}: missing minecraft:client_biome')
        stem=path.name.removesuffix('.client_biome.json')
        desc=cb.setdefault('description',{})
        obj['format_version']='1.21.120'
        desc['identifier']=f'minecraft:{stem}'
        if stem=='sulfur_caves':
            comps=cb.setdefault('components',{})
            for component,field,value in (
                ('minecraft:fog_appearance','fog_identifier','dlavie:cave_fog'),
                ('minecraft:atmosphere_identifier','atmosphere_identifier','dlavie:cave_atmospherics'),
                ('minecraft:color_grading_identifier','color_grading_identifier','dlavie:cave_color_grading'),
                ('minecraft:lighting_identifier','lighting_identifier','dlavie:cave_lighting'),
            ):
                comps.setdefault(component,{})[field]=value
        path.write_text(json.dumps(obj,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
        count+=1
if not count: raise SystemExit('no client-biome bindings were generated')
print(f'Normalized {count} vanilla client-biome bindings to schema 1.21.120 + minecraft namespace')
PY

python3 -B tools/enhance_visual_core.py
python3 -B tools/enhance_volumetric_fog.py
python3 -B tools/enhance_weather_water.py
python3 -B tools/enhance_underwater_night.py
python3 -B tools/enhance_pbr_compat.py
# Deferred pass runs after PBR compatibility so it can patch both selectable
# subpacks and the Natural-Medium root renderer failsafe installed above.
python3 -B tools/enhance_deferred_core.py

# Runtime canary: prove that pack-active actually means vanilla biomes resolve DLavie renderer IDs.
python3 -B - <<'PY'
from pathlib import Path
import json
root=Path('.')
errors=[]
def load(p):
    try:return json.loads(p.read_text(encoding='utf-8'))
    except Exception as e: errors.append(f'{p}: invalid JSON: {e}'); return {}
def check(directory,prefix,expected=None):
    paths=sorted(directory.glob('*.client_biome.json')) if directory.is_dir() else []
    names={p.name for p in paths}
    if not paths: errors.append(f'{directory}: no client biome files')
    if expected is not None and names!=expected: errors.append(f'{directory}: biome set differs from root')
    for p in paths:
        o=load(p); cb=o.get('minecraft:client_biome',{}); stem=p.name.removesuffix('.client_biome.json')
        if o.get('format_version')!='1.21.120': errors.append(f'{p}: wrong schema')
        if cb.get('description',{}).get('identifier')!=f'minecraft:{stem}': errors.append(f'{p}: does not override minecraft:{stem}')
        comps=cb.get('components',{})
        for comp,field in (
            ('minecraft:fog_appearance','fog_identifier'),
            ('minecraft:atmosphere_identifier','atmosphere_identifier'),
            ('minecraft:color_grading_identifier','color_grading_identifier'),
            ('minecraft:lighting_identifier','lighting_identifier'),
            ('minecraft:water_identifier','water_identifier'),
        ):
            node=comps.get(comp)
            if isinstance(node,dict) and field in node and not str(node[field]).startswith(prefix):
                errors.append(f'{p}: {field}={node[field]!r} does not start with {prefix}')
    return names
manifest=load(root/'manifest.json')
subs=[x.get('folder_name') for x in manifest.get('subpacks',[]) if x.get('folder_name')]
root_names=check(root/'biomes','dlavie_root:')
for required in ('plains.client_biome.json','ocean.client_biome.json','hell.client_biome.json','the_end.client_biome.json','sulfur_caves.client_biome.json'):
    if required not in root_names: errors.append(f'missing required current vanilla binding {required}')
for sp in subs: check(root/'subpacks'/sp/'biomes','dlavie:',root_names)
plains=load(root/'biomes/plains.client_biome.json').get('minecraft:client_biome',{})
if plains.get('components',{}).get('minecraft:lighting_identifier',{}).get('lighting_identifier')!='dlavie_root:default_lighting':
    errors.append('root minecraft:plains does not resolve DLavie root lighting')
sulfur=load(root/'biomes/sulfur_caves.client_biome.json').get('minecraft:client_biome',{})
if sulfur.get('components',{}).get('minecraft:lighting_identifier',{}).get('lighting_identifier')!='dlavie_root:cave_lighting':
    errors.append('minecraft:sulfur_caves does not resolve cave lighting')
for rel in ('atmospherics/atmospherics.json','lighting/global.json','color_grading/color_grading.json','fogs/default.json','water/water.json','pbr/global.json','local_lighting/local_lighting.json','shadows/global.json'):
    if not (root/rel).is_file(): errors.append(f'missing root renderer failsafe {rel}')
if errors:
    print(f'VV RUNTIME BINDING CHECK FAILED ({len(errors)})')
    for e in errors: print(' -',e)
    raise SystemExit(1)
print(f'VV runtime binding OK: {len(root_names)} vanilla biomes × root + {len(subs)} selectable subpacks')
PY

# Feature-level validator + cross-system runtime audit.
python3 -B tools/validate_pack.py
python3 -B tools/audit_release.py generated

rm -rf dist
mkdir -p dist
python3 -B tools/package_mcpack.py
python3 -B tools/audit_release.py mcpack dist/DLavie-Visual.mcpack
