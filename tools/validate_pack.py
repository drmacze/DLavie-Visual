#!/usr/bin/env python3
from pathlib import Path
import json, sys
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]; errors=[]
def err(x): errors.append(x)
def load(p):
    try:return json.loads((ROOT/p).read_text(encoding='utf-8'))
    except Exception as e:err(f'{p}: invalid JSON: {e}');return {}
m=load('manifest.json')
if m.get('format_version')!=2:err('manifest format_version must be 2')
if m.get('header',{}).get('min_engine_version',[])<[1,26,40]:err('min_engine_version must be >= 1.26.40')
if 'pbr' not in m.get('capabilities',[]):err('manifest must include pbr')
if [x.get('folder_name') for x in m.get('subpacks',[])]!=['low','medium','high']:err('subpacks must be low/medium/high')
req=['atmospherics/atmospherics.json','atmospherics/nether.json','atmospherics/end.json','lighting/global.json','lighting/nether.json','lighting/end.json','color_grading/color_grading.json','color_grading/nether.json','color_grading/end.json','pbr/global.json','water/water.json','fogs/dlavie_overworld.json','fogs/dlavie_nether.json','fogs/dlavie_end.json','local_lighting/local_lighting.json','shadows/global.json']
for pre in ('low','medium','high'):
  for rel in req:
    p=Path('subpacks')/pre/rel
    if not (ROOT/p).is_file():err(f'missing {p}')
    else:load(p)
  w=load(Path('subpacks')/pre/'water/water.json').get('minecraft:water_settings',{})
  ca=w.get('caustics',{})
  if not isinstance(ca.get('power'),int):err(f'{pre}: caustics power must be integer')
  if pre!='low' and ca.get('texture')!='textures/dlavie/derivative_caustics':err(f'{pre}: custom Derivative caustics not wired')
  for rel in ['textures/environment/clouds.png','textures/environment/sun.png','textures/environment/moon_phases.png']:
    p=ROOT/'subpacks'/pre/rel
    if not p.is_file():err(f'missing {p.relative_to(ROOT)}')
    elif p.read_bytes()[:8]!=b'\x89PNG\r\n\x1a\n':err(f'not PNG: {p.relative_to(ROOT)}')
# Catch the old implementation regressions.
for pre in ('low','medium','high'):
  l=load(Path('subpacks')/pre/'lighting/global.json').get('minecraft:lighting_settings',{})
  sun=l.get('directional_lights',{}).get('orbital',{}).get('sun',{}).get('illuminance',{})
  if isinstance(sun,dict) and float(sun.get('0.0',0))<50000:err(f'{pre}: sun illuminance is not physical-lux scale')
  at=load(Path('subpacks')/pre/'atmospherics/atmospherics.json').get('minecraft:atmosphere_settings',{})
  glare=at.get('sun_glare_shape',{})
  if isinstance(glare,dict) and not (0.04 <= max(glare.values() or [0]) <= 0.12):err(f'{pre}: sun glare outside sane VV range')
caustic=ROOT/'textures/dlavie/derivative_caustics.png'
if not caustic.is_file():err('missing root custom caustics texture')
else:
  im=Image.open(caustic)
  if im.height%im.width:err('caustics sprite sheet must use square vertical frames')
  if im.width!=128 or im.height//im.width!=60:err('runtime Derivative caustics must be 60 vertical 128px frames')
if not (ROOT/'textures/textures_list.json').is_file():err('missing textures/textures_list.json')
for b in ['plains','hell','crimson_forest','warped_forest','soulsand_valley','basalt_deltas','the_end']:
  if not (ROOT/'biomes'/(b+'.client_biome.json')).is_file():err(f'missing dimension biome binding {b}')
if not (ROOT/'branding/cover.svg').is_file():err('missing manual SVG cover')
lic=ROOT/'THIRD_PARTY_LICENSES/DERCODE-License-2.5.txt'
if not lic.is_file() or 'DERCODE License Agreement 2.5' not in lic.read_text(encoding='utf-8'):err('DERCODE license missing')
attr=(ROOT/'SOURCE_ATTRIBUTION.md').read_text(encoding='utf-8')
for n in ['_DureXXX','M1zore','Skeeder461','Frs0n','_Sone4ka_']:
  if n not in attr:err('missing source credit '+n)
for rel in ['textures/environment/clouds.png','textures/environment/sun.png','textures/environment/moon_phases.png','ui/_ui_defs.json','ui/dlavie_ui.json','ui/start_screen.json']:
  if not (ROOT/rel).is_file():err('missing '+rel)
if errors:
  print('VALIDATION FAILED');[print(' -',x) for x in errors];sys.exit(1)
print(f'Validation OK: {len(list((ROOT/"biomes").glob("*.json")))} biome bindings, 3 presets, physical sun, custom caustics, modern local lighting')
