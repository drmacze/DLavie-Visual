#!/usr/bin/env python3
from pathlib import Path
import json, sys

ROOT=Path(__file__).resolve().parents[1]
errors=[]
def err(x): errors.append(x)
def load(p):
    try: return json.loads(p.read_text(encoding='utf-8'))
    except Exception as e: err(f'{p}: {e}'); return {}

def check_dir(d,prefix,expected=None):
    files=sorted(d.glob('*.client_biome.json')) if d.is_dir() else []
    names={p.name for p in files}
    if not files: err(f'{d}: no client biomes')
    if expected is not None and names!=expected: err(f'{d}: biome file set differs from root')
    for p in files:
        o=load(p); cb=o.get('minecraft:client_biome',{}); stem=p.name.removesuffix('.client_biome.json')
        if o.get('format_version')!='1.21.120': err(f'{p}: wrong client-biome schema')
        if cb.get('description',{}).get('identifier')!=f'minecraft:{stem}': err(f'{p}: vanilla identifier is not namespaced')
        comps=cb.get('components',{})
        for comp,field in (("minecraft:fog_appearance","fog_identifier"),("minecraft:atmosphere_identifier","atmosphere_identifier"),("minecraft:color_grading_identifier","color_grading_identifier"),("minecraft:lighting_identifier","lighting_identifier"),("minecraft:water_identifier","water_identifier")):
            node=comps.get(comp)
            if isinstance(node,dict) and field in node and not str(node[field]).startswith(prefix): err(f'{p}: {field} does not bind DLavie renderer')
    return names

m=load(ROOT/'manifest.json'); subs=[x['folder_name'] for x in m.get('subpacks',[]) if 'folder_name' in x]
root=check_dir(ROOT/'biomes','dlavie_root:')
for req in ('plains.client_biome.json','ocean.client_biome.json','hell.client_biome.json','the_end.client_biome.json','sulfur_caves.client_biome.json'):
    if req not in root: err(f'missing required biome {req}')
for sp in subs: check_dir(ROOT/'subpacks'/sp/'biomes','dlavie:',root)

plains=load(ROOT/'biomes/plains.client_biome.json').get('minecraft:client_biome',{})
if plains.get('components',{}).get('minecraft:lighting_identifier',{}).get('lighting_identifier')!='dlavie_root:default_lighting': err('root plains is not using DLavie lighting')
sulfur=load(ROOT/'biomes/sulfur_caves.client_biome.json').get('minecraft:client_biome',{})
if sulfur.get('components',{}).get('minecraft:lighting_identifier',{}).get('lighting_identifier')!='dlavie_root:cave_lighting': err('sulfur_caves is not using cave lighting')
for rel in ('atmospherics/atmospherics.json','lighting/global.json','color_grading/color_grading.json','fogs/default.json','water/water.json','pbr/global.json','local_lighting/local_lighting.json','shadows/global.json'):
    if not (ROOT/rel).is_file(): err(f'missing root failsafe {rel}')
if errors:
    print('VV BINDING VALIDATION FAILED'); [print(' -',e) for e in errors]; sys.exit(1)
print(f'VV binding validation OK: {len(root)} vanilla biome bindings across root + {len(subs)} subpacks')
