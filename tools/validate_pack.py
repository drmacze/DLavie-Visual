#!/usr/bin/env python3
from pathlib import Path
import json,sys
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]; errors=[]
def err(x):errors.append(x)
def load(p):
    try:return json.loads((ROOT/p).read_text(encoding='utf-8'))
    except Exception as e:err(f'{p}: invalid JSON: {e}');return {}
m=load('manifest.json')
if m.get('format_version')!=2:err('manifest format_version must be 2')
if m.get('header',{}).get('version')!=[2,3,0]:err('expected version 2.3.0')
if m.get('header',{}).get('min_engine_version',[])<[1,26,40]:err('min engine must be >=1.26.40')
if 'pbr' not in m.get('capabilities',[]):err('pbr capability missing')
if [x.get('folder_name') for x in m.get('subpacks',[])]!=['low','medium','high']:err('subpacks must be low/medium/high')
for sp in m.get('subpacks',[]):
    if sp.get('memory_tier',99)>1:err(f"{sp.get('folder_name')}: memory_tier would lock mobile selection")
for pre in ('low','medium','high'):
    req=['atmospherics/atmospherics.json','lighting/global.json','lighting/lush.json','color_grading/color_grading.json','color_grading/lush.json','color_grading/dry.json','color_grading/cold.json','color_grading/cave.json','pbr/global.json','local_lighting/local_lighting.json','shadows/global.json']
    req += [f'water/{x}.json' for x in ('default','river','ocean','swamp','frozen')]
    req += [f'fogs/{x}.json' for x in ('default','humid','dry','cold','cave','nether','end')]
    for rel in req:
        p=Path('subpacks')/pre/rel
        if not (ROOT/p).is_file():err('missing '+str(p))
        else:load(p)
    at=load(Path('subpacks')/pre/'atmospherics/atmospherics.json').get('minecraft:atmosphere_settings',{})
    sm=at.get('sun_mie_strength',{}); gl=at.get('sun_glare_shape',{})
    if max(sm.values() or [0])<2.5:err(f'{pre}: godray Mie pass too weak')
    if max(gl.values() or [0])<12:err(f'{pre}: cinematic glare not active')
    li=load(Path('subpacks')/pre/'lighting/global.json').get('minecraft:lighting_settings',{})
    sun=li.get('directional_lights',{}).get('orbital',{}).get('sun',{}).get('illuminance',{})
    if float(sun.get('0.0',0))<100000:err(f'{pre}: physical sun lux missing')
    for n in ('sun.png','moon_phases.png','clouds.png','rain.png','snow.png'):
        if not (ROOT/'subpacks'/pre/'textures/environment'/n).is_file():err(f'{pre}: missing environment {n}')
ca=ROOT/'textures/dlavie/derivative_caustics.png'
if not ca.is_file():err('missing caustics')
else:
    im=Image.open(ca)
    if im.size!=(128,7680):err(f'caustics must be exact 128x7680, got {im.size}')
for n,sz in {'sun.png':(32,32),'moon_phases.png':(128,64),'clouds.png':(256,256),'rain.png':(64,256),'snow.png':(64,256)}.items():
    p=ROOT/'textures/environment'/n
    if not p.is_file():err('missing root '+n)
    elif Image.open(p).size!=sz:err(f'{n} expected {sz}, got {Image.open(p).size}')
if len(list((ROOT/'biomes').glob('*.client_biome.json')))<87:err('expected >=87 biome bindings')
for rel in ('ui/_ui_defs.json','ui/dlavie_ui.json','ui/start_screen.json','branding/cover.svg','THIRD_PARTY_LICENSES/DERCODE-License-2.5.txt'):
    if not (ROOT/rel).is_file():err('missing '+rel)
if errors:
    print('VALIDATION FAILED');[print(' -',e) for e in errors];sys.exit(1)
print('Validation OK: DLavie Visual 2.3 cinematic profile, 5 water profiles, strong Mie/glare, 60-frame caustics')
