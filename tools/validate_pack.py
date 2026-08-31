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
if m.get('header',{}).get('version')!=[3,0,0]:err('expected version 3.0.0')
if m.get('header',{}).get('min_engine_version',[])<[1,26,40]:err('min engine must be >=1.26.40')
if 'pbr' not in m.get('capabilities',[]):err('pbr capability missing')
if [x.get('folder_name') for x in m.get('subpacks',[])]!=['low','medium','high']:err('subpacks must be low/medium/high')
for sp in m.get('subpacks',[]):
    if sp.get('memory_tier',99)>1:err(f"{sp.get('folder_name')}: memory_tier would lock mobile selection")
profiles=('default','forest','dense','dry','cold','swamp','cave','ocean')
for pre in ('low','medium','high'):
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
        else:load(p)
    # Regression guard: current official Bedrock sample default sun is ~100. Prevent the previous 1000x exposure bug.
    li=load(Path('subpacks')/pre/'lighting/default.json').get('minecraft:lighting_settings',{})
    sun=li.get('directional_lights',{}).get('orbital',{}).get('sun',{}).get('illuminance',{})
    vals=[float(x) for x in sun.values()] if isinstance(sun,dict) else [float(sun or 0)]
    if max(vals or [0])>120:err(f'{pre}: sun illuminance exceeds mobile/VV calibrated range')
    if max(vals or [0])<70:err(f'{pre}: sun too dim for intended daytime profile')
    at=load(Path('subpacks')/pre/'atmospherics/default.json').get('minecraft:atmosphere_settings',{})
    gl=at.get('sun_glare_shape',{}); gm=max((float(x) for x in gl.values()),default=0)
    if gm>0.20:err(f'{pre}: glare regression (>0.20)')
    if gm<0.08:err(f'{pre}: low-sun glare too weak')
    ll=load(Path('subpacks')/pre/'local_lighting/local_lighting.json').get('minecraft:local_light_settings',{})
    if len(ll)<12:err(f'{pre}: local-light coverage too small')
# Material pass: these are metadata only, no Mojang albedo files copied.
mat=list((ROOT/'textures/blocks').glob('*.texture_set.json'))
if len(mat)<140:err(f'expected >=140 PBR material overrides, got {len(mat)}')
for n in ('grass_top','leaves_oak','planks_oak','stone','glass','ice','iron_block','gold_block','glowstone','sea_lantern'):
    p=ROOT/'textures/blocks'/f'{n}.texture_set.json'
    if not p.is_file():err('missing key material '+n)
    else:
        o=load(p.relative_to(ROOT)).get('minecraft:texture_set',{})
        if 'metalness_emissive_roughness_subsurface' not in o:err('material missing MERS '+n)
ca=ROOT/'textures/dlavie/derivative_caustics.png'
if not ca.is_file():err('missing caustics')
else:
    im=Image.open(ca)
    if im.size!=(128,7680):err(f'caustics must be 128x7680, got {im.size}')
if len(list((ROOT/'biomes').glob('*.client_biome.json')))<87:err('expected >=87 biome bindings')
for rel in ('ui/_ui_defs.json','ui/dlavie_ui.json','ui/start_screen.json','branding/cover.svg','THIRD_PARTY_LICENSES/DERCODE-License-2.5.txt'):
    if not (ROOT/rel).is_file():err('missing '+rel)
if errors:
    print('VALIDATION FAILED');[print(' -',e) for e in errors];sys.exit(1)
print(f'Validation OK: DLavie Visual 3.0, 8 biome render profiles, {len(mat)} PBR materials, calibrated sun, local point lights')
