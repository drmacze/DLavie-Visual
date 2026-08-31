#!/usr/bin/env python3
from pathlib import Path
import json,sys
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]; errors=[]
def err(x): errors.append(x)
def load(p):
    try:return json.loads((ROOT/p).read_text(encoding='utf-8'))
    except Exception as e:err(f'{p}: invalid JSON: {e}');return {}

m=load('manifest.json')
if m.get('format_version')!=2:err('manifest format_version must be 2')
if m.get('header',{}).get('version')!=[4,0,0]:err('expected version 4.0.0')
if m.get('header',{}).get('min_engine_version',[])<[1,26,40]:err('min engine must be >=1.26.40')
if 'pbr' not in m.get('capabilities',[]):err('pbr capability missing')
expected=[f'{t}_{q}' for t in ('natural','cozy','gloomy') for q in ('low','medium','high')]
folders=[x.get('folder_name') for x in m.get('subpacks',[])]
if folders!=expected:err(f'expected nine mood/quality subpacks, got {folders}')
for sp in m.get('subpacks',[]):
    if sp.get('memory_tier',99)>1:err(f"{sp.get('folder_name')}: memory_tier would lock mobile selection")

profiles=('default','forest','dense','dry','cold','swamp','cave','ocean')
for pre in expected:
    for v in profiles:
        for folder in ('atmospherics','lighting','color_grading','fogs'):
            p=Path('subpacks')/pre/folder/f'{v}.json'
            if not (ROOT/p).is_file():err('missing '+str(p))
            else:load(p)
    for rel in ('pbr/global.json','local_lighting/local_lighting.json','shadows/global.json'):
        p=Path('subpacks')/pre/rel
        if not (ROOT/p).is_file():err('missing '+str(p))
        else:load(p)
    for wk in ('default','river','ocean','swamp','frozen'):
        p=Path('subpacks')/pre/f'water/{wk}.json'
        if not (ROOT/p).is_file():err('missing '+str(p))
        else:
            w=load(p).get('minecraft:water_settings',{})
            ca=w.get('caustics',{})
            if ca.get('enabled') and ca.get('texture')!='textures/dlavie/optical_caustics':err(f'{p}: not using optical caustics')
    li=load(Path('subpacks')/pre/'lighting/default.json').get('minecraft:lighting_settings',{})
    sun=li.get('directional_lights',{}).get('orbital',{}).get('sun',{}).get('illuminance',{})
    vals=[float(x) for x in sun.values()] if isinstance(sun,dict) else [float(sun or 0)]
    if max(vals or [0])>110:err(f'{pre}: sun exceeds calibrated range')
    if max(vals or [0])<60:err(f'{pre}: daylight too dim')
    ll=load(Path('subpacks')/pre/'local_lighting/local_lighting.json').get('minecraft:local_light_settings',{})
    if len(ll)<12:err(f'{pre}: local-light coverage too small')
    if len(list((ROOT/'subpacks'/pre/'biomes').glob('*.client_biome.json')))<87:err(f'{pre}: missing theme-specific biome bindings')

# PBR texture-set validation. All referenced images must exist in this pack.
sets=list((ROOT/'textures/blocks').glob('*.texture_set.json'))
if len(sets)<100:err(f'expected >=100 authored PBR materials, got {len(sets)}')
for p in sets:
    data=load(p.relative_to(ROOT)).get('minecraft:texture_set',{})
    for key in ('color','normal','metalness_emissive_roughness_subsurface'):
        val=data.get(key)
        if not isinstance(val,str):err(f'{p.name}: missing string {key}');continue
        target=p.parent/(val+'.png')
        if not target.is_file():err(f'{p.name}: unresolved {key} -> {target.name}')
    if 'normal' in data and 'heightmap' in data:err(f'{p.name}: normal and heightmap cannot coexist')
    n=data.get('normal')
    if isinstance(n,str) and (p.parent/(n+'.png')).is_file() and Image.open(p.parent/(n+'.png')).size!=(128,128):err(f'{p.name}: normal map is not 128x128')
    base=p.name.replace('.texture_set.json','')
    ao=p.parent/f'{base}_ao.png'
    if not ao.is_file():err(f'{p.name}: missing 128x AO source')
    elif Image.open(ao).size!=(128,128):err(f'{ao.name}: AO is not 128x128')

ca=ROOT/'textures/dlavie/optical_caustics.png'
if not ca.is_file():err('missing optical caustics')
elif Image.open(ca).size!=(128,7680):err(f'optical caustics must be 128x7680, got {Image.open(ca).size}')
if len(list((ROOT/'biomes').glob('*.client_biome.json')))<87:err('expected >=87 base biome bindings')
for rel in ('ui/_ui_defs.json','ui/dlavie_ui.json','ui/start_screen.json','branding/cover.svg','THIRD_PARTY_LICENSES/DERCODE-License-2.5.txt'):
    if not (ROOT/rel).is_file():err('missing '+rel)
if errors:
    print('VALIDATION FAILED');[print(' -',e) for e in errors];sys.exit(1)
print(f'Validation OK: DLavie Visual 4.0, 9 presets, {len(sets)} 128x PBR materials, optical caustics, per-dimension/biome lighting')
