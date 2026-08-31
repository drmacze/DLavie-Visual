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
if m.get('header',{}).get('version')!=[4,4,0]:err('expected version 4.4.0')
if m.get('header',{}).get('min_engine_version',[])<[1,26,40]:err('min engine must be >=1.26.40')
if 'pbr' not in m.get('capabilities',[]):err('pbr capability missing')
expected=[f'{t}_{q}' for t in ('natural','cozy','gloomy') for q in ('low','medium','high')]
folders=[x.get('folder_name') for x in m.get('subpacks',[])]
if folders!=expected:err(f'expected nine mood/quality subpacks, got {folders}')
for sp in m.get('subpacks',[]):
    if sp.get('memory_tier',99)>1:err(f"{sp.get('folder_name')}: memory_tier would lock mobile selection")

profiles=('default','forest','dense','dry','cold','swamp','cave','ocean')
ore_hooks={
 'minecraft:coal_ore','minecraft:deepslate_coal_ore','minecraft:iron_ore','minecraft:deepslate_iron_ore',
 'minecraft:copper_ore','minecraft:deepslate_copper_ore','minecraft:gold_ore','minecraft:deepslate_gold_ore',
 'minecraft:redstone_ore','minecraft:deepslate_redstone_ore','minecraft:lapis_ore','minecraft:deepslate_lapis_ore',
 'minecraft:diamond_ore','minecraft:deepslate_diamond_ore','minecraft:emerald_ore','minecraft:deepslate_emerald_ore',
 'minecraft:nether_gold_ore','minecraft:nether_quartz_ore','minecraft:ancient_debris'
}
for pre in expected:
    theme,quality=pre.rsplit('_',1)
    for v in profiles:
        for folder in ('atmospherics','lighting','color_grading','fogs'):
            p=Path('subpacks')/pre/folder/f'{v}.json'
            if not (ROOT/p).is_file():err('missing '+str(p))
            else:load(p)
    for rel in ('pbr/global.json','local_lighting/local_lighting.json','shadows/global.json','fogs/nether.json','fogs/end.json'):
        p=Path('subpacks')/pre/rel
        if not (ROOT/p).is_file():err('missing '+str(p))
        else:load(p)

    # Overworld lighting uses schema 1.26.0 so ambient/sky time keyframes are formally supported.
    for lp in (ROOT/'subpacks'/pre/'lighting').glob('*.json'):
        if lp.stem in ('nether','end'): continue
        rel=lp.relative_to(ROOT); lo=load(rel)
        if lo.get('format_version')!='1.26.0':err(f'{rel}: expected lighting schema 1.26.0')
        ls=lo.get('minecraft:lighting_settings',{})
        amb=ls.get('ambient',{}).get('illuminance',{})
        sky=ls.get('sky',{}).get('intensity',{})
        if not isinstance(amb,dict) or '0.50' not in amb:err(f'{rel}: missing midnight ambient keyframe')
        elif float(amb['0.50'])>0.012:err(f'{rel}: midnight ambient too bright')
        if not isinstance(sky,dict) or '0.50' not in sky:err(f'{rel}: missing midnight sky keyframe')
        elif float(sky['0.50'])>0.20:err(f'{rel}: midnight sky too bright')

    for ap in (ROOT/'subpacks'/pre/'atmospherics').glob('*.json'):
        if ap.stem in ('nether','end'): continue
        rel=ap.relative_to(ROOT); at=load(rel).get('minecraft:atmosphere_settings',{})
        zen=at.get('sky_zenith_color',{}); hor=at.get('sky_horizon_color',{})
        if not all(k in zen for k in ('0.315','0.50','0.685')):err(f'{rel}: incomplete twilight/midnight zenith keys')
        if not all(k in hor for k in ('0.315','0.50','0.685')):err(f'{rel}: incomplete twilight/midnight horizon keys')

    for fp in (ROOT/'subpacks'/pre/'fogs').glob('*.json'):
        rel=fp.relative_to(ROOT); fo=load(rel)
        if fo.get('format_version')!='1.21.90':err(f'{rel}: fog format must be 1.21.90')
        fg=fo.get('minecraft:fog_settings',{}); vol=fg.get('volumetric',{}); den=vol.get('density',{})
        if 'air' not in den or 'water' not in den:err(f'{rel}: missing air/water volumetric density')
        air=den.get('air',{})
        if not air.get('uniform') and fp.stem not in ('cave','nether','end'):
            if 'zero_density_height' not in air or 'max_density_height' not in air:err(f'{rel}: missing height-shaped air fog')
            elif float(air['zero_density_height'])<=float(air['max_density_height']):err(f'{rel}: invalid vertical fog gradient')
        if fp.stem not in ('cave','nether','end') and 'weather' not in den:err(f'{rel}: missing active-weather volumetric density')
        media=vol.get('media_coefficients',{})
        if not all(x in media for x in ('air','water','cloud')):err(f'{rel}: missing air/water/cloud media coefficients')
        hg=vol.get('henyey_greenstein_g',{})
        for medium in ('air','water'):
            g=hg.get(medium,{}).get('henyey_greenstein_g')
            if g is None:err(f'{rel}: missing {medium} Henyey-Greenstein phase value')
            elif not -1<=float(g)<=1:err(f'{rel}: {medium} phase value out of range')
        dist=fg.get('distance',{})
        if 'air' not in dist:err(f'{rel}: missing far-distance haze')
        water_dist=dist.get('water',{})
        if not water_dist:err(f'{rel}: missing underwater depth fog')
        elif 'transition_fog' not in water_dist:err(f'{rel}: missing smooth underwater transition fog')
        if fp.stem not in ('cave','nether','end') and 'weather' not in dist:err(f'{rel}: missing active-weather distance haze')

    min_oct={'low':7,'medium':14,'high':20}[quality]
    for wk in ('default','river','ocean','swamp','frozen'):
        p=Path('subpacks')/pre/f'water/{wk}.json'
        if not (ROOT/p).is_file():err('missing '+str(p));continue
        w=load(p).get('minecraft:water_settings',{})
        pc=w.get('particle_concentrations',{})
        if not all(x in pc for x in ('chlorophyll','suspended_sediment','cdom')):err(f'{p}: missing depth-absorption particle concentrations')
        waves=w.get('waves',{})
        if not waves.get('enabled'):err(f'{p}: waves disabled')
        if int(waves.get('octaves',0))<min_oct:err(f'{p}: expected at least {min_oct} wave octaves')
        ca=w.get('caustics',{})
        if not ca.get('enabled'):err(f'{p}: caustics disabled')
        elif ca.get('texture')!='textures/dlavie/optical_caustics':err(f'{p}: not using optical caustics')
        if float(ca.get('power',0))<1:err(f'{p}: caustics power invalid')

    li=load(Path('subpacks')/pre/'lighting/default.json').get('minecraft:lighting_settings',{})
    sun=li.get('directional_lights',{}).get('orbital',{}).get('sun',{}).get('illuminance',{})
    vals=[float(x) for x in sun.values()] if isinstance(sun,dict) else [float(sun or 0)]
    if max(vals or [0])>110:err(f'{pre}: sun exceeds calibrated range')
    if max(vals or [0])<60:err(f'{pre}: daylight too dim')
    amb=li.get('ambient',{}).get('illuminance',{})
    if isinstance(amb,dict) and max((float(x) for x in amb.values()),default=0)>0.08:err(f'{pre}: ambient too flat/bright for visual-core target')
    ll=load(Path('subpacks')/pre/'local_lighting/local_lighting.json').get('minecraft:local_light_settings',{})
    if len(ll)<12:err(f'{pre}: local-light coverage too small')
    missing_ore=sorted(ore_hooks-set(ll))
    if missing_ore:err(f'{pre}: missing ore local-light hooks: {missing_ore[:4]}')
    if quality=='high':
        for b in ore_hooks:
            if ll.get(b,{}).get('light_type')!='point_light':err(f'{pre}: high ore hook {b} must be point_light')
    if len(list((ROOT/'subpacks'/pre/'biomes').glob('*.client_biome.json')))<87:err(f'{pre}: missing theme-specific biome bindings')

# Shader/visual-only project boundary.
block_dir=ROOT/'textures'/'blocks'
if block_dir.exists() and any(block_dir.iterdir()):err('visual project contains custom block textures')
sets=list(ROOT.rglob('*.texture_set.json'))
if sets:err(f'visual project contains {len(sets)} Texture Sets; move them to the texture project')
if (ROOT/'tools'/'generate_material_suite.py').exists():err('block material generator still exists in visual project')
for tool in ('enhance_weather_water.py','enhance_underwater_night.py'):
    if not (ROOT/'tools'/tool).is_file():err('missing '+tool)

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
print('Validation OK: DLavie Visual 4.4 visual core, advanced underwater shafts/caustics + 1.26.0 cinematic night keyframes + ore light hooks, 9 presets, zero block textures')