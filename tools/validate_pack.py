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
if m.get('header',{}).get('version')!=[4,1,0]:err('expected version 4.1.0')
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
        if not (ROOT/p).is_file():err('missing '+str(p));continue
        w=load(p).get('minecraft:water_settings',{})
        ca=w.get('caustics',{})
        if ca.get('enabled') and ca.get('texture')!='textures/dlavie/optical_caustics':err(f'{p}: not using optical caustics')
    li=load(Path('subpacks')/pre/'lighting/default.json').get('minecraft:lighting_settings',{})
    sun=li.get('directional_lights',{}).get('orbital',{}).get('sun',{}).get('illuminance',{})
    vals=[float(x) for x in sun.values()] if isinstance(sun,dict) else [float(sun or 0)]
    if max(vals or [0])>110:err(f'{pre}: sun exceeds calibrated range')
    if max(vals or [0])<60:err(f'{pre}: daylight too dim')
    amb=li.get('ambient',{}).get('illuminance',{})
    if isinstance(amb,dict) and max((float(x) for x in amb.values()),default=0)>0.08:err(f'{pre}: ambient too flat/bright for visual-core target')
    ll=load(Path('subpacks')/pre/'local_lighting/local_lighting.json').get('minecraft:local_light_settings',{})
    if len(ll)<12:err(f'{pre}: local-light coverage too small')
    if len(list((ROOT/'subpacks'/pre/'biomes').glob('*.client_biome.json')))<87:err(f'{pre}: missing theme-specific biome bindings')

# This repository is shader/visual only. Block textures and per-block Texture Sets
# belong to the separate DLavie texture project and must never enter this pack.
block_dir=ROOT/'textures'/'blocks'
if block_dir.exists() and any(block_dir.iterdir()):err('visual project contains custom block textures')
sets=list(ROOT.rglob('*.texture_set.json'))
if sets:err(f'visual project contains {len(sets)} Texture Sets; move them to the texture project')
if (ROOT/'tools'/'generate_material_suite.py').exists():err('block material generator still exists in visual project')

# Environment assets are allowed because they are part of the visual renderer path.
ca=ROOT/'textures/dlavie/optical_caustics.png'
if not ca.is_file():err('missing optical caustics')
elif Image.open(ca).size!=(128,7680):err(f'optical caustics must be 128x7680, got {Image.open(ca).size}')
for env in ('sun.png','moon_phases.png','clouds.png','rain.png','snow.png'):
    if not (ROOT/'textures'/'environment'/env).is_file():err('missing visual environment asset '+env)
if len(list((ROOT/'biomes').glob('*.client_biome.json')))<87:err('expected >=87 base biome bindings')
for rel in ('ui/_ui_defs.json','ui/dlavie_ui.json','ui/start_screen.json','branding/cover.svg','THIRD_PARTY_LICENSES/DERCODE-License-2.5.txt'):
    if not (ROOT/rel).is_file():err('missing '+rel)
if errors:
    print('VALIDATION FAILED');[print(' -',e) for e in errors];sys.exit(1)
print('Validation OK: DLavie Visual 4.1 visual core, 9 presets, zero block textures, per-biome/per-dimension lighting, optical caustics')
