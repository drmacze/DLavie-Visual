#!/usr/bin/env python3
"""Generate DLavie Visual 2.3 cinematic Vibrant Visuals configurations."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]
PRESETS=json.loads((ROOT/'config/presets.json').read_text(encoding='utf-8'))
BIOME_CFG=json.loads((ROOT/'config/biomes.json').read_text(encoding='utf-8'))

def dump(path,obj):
    p=ROOT/path; p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(obj,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')

def atmosphere(identifier='dlavie:default_atmospherics', dimension='overworld'):
    if dimension=='nether':
        return {"format_version":"1.21.40","minecraft:atmosphere_settings":{
          "description":{"identifier":identifier},
          "horizon_blend_stops":{"min":{"0":0.0,"1":0.0},"start":{"0":0.32,"1":0.32},"mie_start":{"0":0.46,"1":0.46},"max":{"0":0.28,"1":0.28}},
          "rayleigh_strength":{"0":0.8,"1":0.8},"sun_mie_strength":{"0":0.75,"1":0.75},"moon_mie_strength":{"0":0.0,"1":0.0},"sun_glare_shape":{"0":4.0,"1":4.0},
          "sky_zenith_color":{"0":[19,2,4],"1":[19,2,4]},"sky_horizon_color":{"0":[118,25,11],"1":[118,25,11]}}}
    if dimension=='end':
        return {"format_version":"1.21.40","minecraft:atmosphere_settings":{
          "description":{"identifier":identifier},
          "horizon_blend_stops":{"min":{"0":0.0,"1":0.0},"start":{"0":0.40,"1":0.40},"mie_start":{"0":0.42,"1":0.42},"max":{"0":0.30,"1":0.30}},
          "rayleigh_strength":{"0":1.2,"1":1.2},"sun_mie_strength":{"0":0.35,"1":0.35},"moon_mie_strength":{"0":0.6,"1":0.6},"sun_glare_shape":{"0":5.5,"1":5.5},
          "sky_zenith_color":{"0":[8,4,23],"1":[8,4,23]},"sky_horizon_color":{"0":[65,42,103],"1":[65,42,103]}}}
    # Cinematic Overworld. This intentionally uses the same strong ranges demonstrated in Mojang's
    # current Atmospherics customization example (Mie up to ~3, glare shape in the ~4-16 range).
    zen={
      "0.0":[49,116,170],"0.145":[60,130,184],"0.195":[67,126,176],
      "0.225":[39,77,121],"0.25":[18,38,72],"0.305":[8,17,39],
      "0.40":[4,8,24],"0.50":[2,5,16],"0.60":[4,8,24],"0.695":[8,17,39],
      "0.75":[20,43,80],"0.78":[46,91,139],"0.82":[63,132,184],"1.0":[49,116,170]
    }
    hor={
      "0.0":[190,214,229],"0.15":[202,219,231],"0.19":[244,220,181],
      "0.215":[255,199,145],"0.235":[255,153,91],"0.25":[255,112,68],
      "0.29":[182,73,87],"0.35":[87,65,113],"0.42":[34,43,83],"0.50":[16,25,55],
      "0.58":[34,43,83],"0.65":[87,65,113],"0.71":[207,88,103],"0.75":[255,124,76],
      "0.775":[255,174,111],"0.805":[255,207,158],"0.85":[202,219,231],"1.0":[190,214,229]
    }
    ray={"0.0":10.5,"0.15":10.0,"0.20":7.0,"0.25":4.7,"0.32":3.1,"0.50":2.2,"0.68":3.1,"0.75":4.7,"0.80":7.0,"0.85":10.0,"1.0":10.5}
    sm={"0.0":0.8,"0.14":1.0,"0.18":1.6,"0.205":2.4,"0.225":3.0,"0.25":3.2,"0.285":2.5,"0.33":1.15,"0.40":0.42,"0.50":0.12,"0.60":0.42,"0.67":1.15,"0.715":2.5,"0.75":3.2,"0.775":3.0,"0.795":2.4,"0.82":1.6,"0.86":1.0,"1.0":0.8}
    mm={"0.0":0.0,"0.29":0.15,"0.35":0.7,"0.42":1.1,"0.50":1.35,"0.58":1.1,"0.65":0.7,"0.71":0.15,"1.0":0.0}
    glare={"0.0":10.0,"0.14":12.5,"0.18":14.2,"0.205":15.3,"0.225":15.9,"0.25":15.9,"0.285":15.2,"0.33":12.0,"0.40":7.0,"0.50":4.0,"0.60":7.0,"0.67":12.0,"0.715":15.2,"0.75":15.9,"0.775":15.9,"0.795":15.3,"0.82":14.2,"0.86":12.5,"1.0":10.0}
    return {"format_version":"1.21.40","minecraft:atmosphere_settings":{
      "description":{"identifier":identifier},
      "horizon_blend_stops":{
        "min":{"0.0":0.0,"0.19":0.006,"0.25":0.0,"0.34":0.055,"0.50":0.025,"0.66":0.055,"0.75":0.0,"0.81":0.006,"1.0":0.0},
        "start":{"0.0":0.31,"0.19":0.42,"0.25":0.19,"0.34":0.34,"0.50":0.26,"0.66":0.34,"0.75":0.19,"0.81":0.42,"1.0":0.31},
        "mie_start":{"0.0":0.50,"0.19":1.05,"0.25":0.50,"0.34":0.46,"0.50":0.20,"0.66":0.46,"0.75":0.50,"0.81":1.05,"1.0":0.50},
        "max":{"0.0":0.25,"0.19":0.13,"0.25":0.02,"0.34":0.42,"0.50":0.22,"0.66":0.42,"0.75":0.02,"0.81":0.13,"1.0":0.25}},
      "rayleigh_strength":ray,"sun_mie_strength":sm,"moon_mie_strength":mm,"sun_glare_shape":glare,
      "sky_zenith_color":zen,"sky_horizon_color":hor}}

def lighting(c,identifier='dlavie:default_lighting',dimension='overworld',variant='default'):
    if dimension=='nether':
        return {"format_version":"1.26.0","minecraft:lighting_settings":{"description":{"identifier":identifier},"directional_lights":{"orbital":{"sun":{"illuminance":{"0":20,"1":20},"color":[255,78,42]},"moon":{"illuminance":{"0":0,"1":0},"color":[120,65,90]},"orbital_offset_degrees":0.0},"flash":{"illuminance":3.0,"color":[255,190,160]}},"emissive":{"desaturation":0.08},"ambient":{"color":[255,94,62],"illuminance":{"0":0.025,"1":0.025}},"sky":{"intensity":{"0":0.18,"1":0.18}}}}
    if dimension=='end':
        return {"format_version":"1.26.0","minecraft:lighting_settings":{"description":{"identifier":identifier},"directional_lights":{"orbital":{"sun":{"illuminance":{"0":10,"1":10},"color":[171,150,255]},"moon":{"illuminance":{"0":0.10,"1":0.10},"color":[190,202,255]},"orbital_offset_degrees":0.0},"flash":{"illuminance":10.0,"color":[220,225,255]}},"emissive":{"desaturation":0.05},"ambient":{"color":[134,118,194],"illuminance":{"0":0.022,"1":0.022}},"sky":{"intensity":{"0":0.22,"1":0.22}}}}
    s=c['sun_illuminance']; m=c['moon_illuminance']; ad=c['ambient_day']; an=c['ambient_night']; sd=c['sky_day']; sn=c['sky_night']
    # Keep direct light dominant to recreate bright windows / deep interiors from Derivative.
    sun_i={"0.0":s,"0.14":s,"0.18":s*0.91,"0.205":s*0.68,"0.225":s*0.42,"0.25":s*0.105,"0.285":2800,"0.32":80,"0.35":0,"0.65":0,"0.68":80,"0.715":2800,"0.75":s*0.105,"0.775":s*0.42,"0.795":s*0.68,"0.82":s*0.91,"0.86":s,"1.0":s}
    sun_c={"0.0":[255,249,239],"0.18":[255,239,215],"0.205":[255,215,171],"0.225":[255,182,115],"0.25":[255,132,67],"0.29":[255,110,61],"0.50":[255,238,224],"0.71":[255,116,68],"0.75":[255,140,76],"0.775":[255,188,124],"0.795":[255,218,175],"0.82":[255,239,215],"1.0":[255,249,239]}
    moon_i={"0.0":0.0,"0.25":0.0,"0.30":m*0.25,"0.36":m*0.72,"0.44":m,"0.56":m,"0.64":m*0.72,"0.70":m*0.25,"0.75":0.0,"1.0":0.0}
    moon_c={"0.0":[154,178,255],"0.50":[171,195,255],"1.0":[154,178,255]}
    amb_i={"0.0":ad,"0.16":ad,"0.205":ad*0.68,"0.25":ad*0.36,"0.32":an*1.15,"0.40":an,"0.50":an,"0.60":an,"0.68":an*1.15,"0.75":ad*0.36,"0.795":ad*0.68,"0.84":ad,"1.0":ad}
    amb_c={"0.0":[222,234,249],"0.205":[255,220,181],"0.25":[255,165,118],"0.34":[112,128,178],"0.50":[77,99,151],"0.66":[112,128,178],"0.75":[255,171,124],"0.795":[255,223,185],"1.0":[222,234,249]}
    sky_i={"0.0":sd,"0.16":sd,"0.205":sd*0.80,"0.25":sd*0.48,"0.34":sn,"0.50":sn,"0.66":sn,"0.75":sd*0.48,"0.795":sd*0.80,"0.84":sd,"1.0":sd}
    if variant=='lush':
        amb_c={k:([max(0,v[0]-10),min(255,v[1]+6),min(255,v[2]+4)] if isinstance(v,list) else v) for k,v in amb_c.items()}
    return {"format_version":"1.26.0","minecraft:lighting_settings":{
      "description":{"identifier":identifier},
      "directional_lights":{"orbital":{"sun":{"illuminance":sun_i,"color":sun_c},"moon":{"illuminance":moon_i,"color":moon_c},"orbital_offset_degrees":3.0},"flash":{"illuminance":14.0,"color":[229,237,255]}},
      "emissive":{"desaturation":0.12},"ambient":{"color":amb_c,"illuminance":amb_i},"sky":{"intensity":sky_i}}}

def grading(c,identifier='dlavie:default_color_grading',dimension='overworld',variant='default'):
    if dimension=='nether': contrast=1.16; sat=0.96; temp=6100
    elif dimension=='end': contrast=1.18; sat=0.90; temp=7800
    else: contrast=c['contrast']; sat=c['saturation']; temp=c['temperature']
    if variant=='lush':
        gain_mid=[0.97,1.025,0.965]; sat*=1.035
    elif variant=='dry':
        gain_mid=[1.03,1.0,0.94]; sat*=0.98
    elif variant=='cold':
        gain_mid=[0.96,1.0,1.055]; sat*=0.95
    elif variant=='cave':
        gain_mid=[0.86,0.92,1.02]; contrast*=1.05; sat*=0.88
    else:
        gain_mid=[0.985,1.0,1.0]
    grade={
      "shadows":{"enabled":True,"contrast":[contrast*1.03]*3,"gain":[0.86,0.92,1.01],"gamma":[2.22,2.22,2.27],"offset":[-0.006,-0.004,0.0],"saturation":[sat*0.84]*3,"shadowsMax":0.72},
      "midtones":{"contrast":[contrast]*3,"gain":gain_mid,"gamma":[2.18,2.20,2.22],"offset":[0,0,0],"saturation":[sat]*3},
      "highlights":{"enabled":True,"contrast":[contrast*0.90]*3,"gain":[1.10,1.035,0.94],"gamma":[2.12,2.16,2.22],"offset":[0.004,0.002,0.0],"saturation":[sat*0.88]*3,"highlightsMin":1.18},
      "temperature":{"enabled":True,"temperature":temp,"type":"white_balance"}}
    return {"format_version":"1.21.90","minecraft:color_grading_settings":{"description":{"identifier":identifier},"color_grading":grade,"tone_mapping":{"operator":"aces"}}}

def pbr(c):
    return {"format_version":"1.21.40","minecraft:pbr_fallback_settings":{
      "blocks":{"global_metalness_emissive_roughness_subsurface":[0,0,c['roughness'],0]},
      "actors":{"global_metalness_emissive_roughness_subsurface":[0,0,c['actor_roughness'],0]},
      "particles":{"global_metalness_emissive_roughness_subsurface":[0,0,225,0]},
      "items":{"global_metalness_emissive_roughness_subsurface":[0,0,202,0]}}}

def water(c,identifier,kind='default'):
    profiles={
      'default':dict(ch=0.16,sed=0.025,cdom=0.055,freq=0.024,depth=0.46,shape=3.4,pull=0.22,mix=0.58,scale=0.62,speedscale=0.22,color=0.46),
      'river':dict(ch=0.20,sed=0.035,cdom=0.070,freq=0.018,depth=0.38,shape=3.8,pull=0.20,mix=0.62,scale=0.58,speedscale=0.20,color=0.62),
      'ocean':dict(ch=0.10,sed=0.015,cdom=0.025,freq=0.028,depth=0.56,shape=3.2,pull=0.25,mix=0.54,scale=0.64,speedscale=0.24,color=0.58),
      'swamp':dict(ch=0.72,sed=0.20,cdom=0.58,freq=0.012,depth=0.22,shape=4.4,pull=0.16,mix=0.70,scale=0.54,speedscale=0.16,color=0.72),
      'frozen':dict(ch=0.05,sed=0.010,cdom=0.015,freq=0.016,depth=0.28,shape=4.0,pull=0.16,mix=0.66,scale=0.56,speedscale=0.18,color=0.64)}
    p=profiles[kind]
    ca={"enabled":bool(c['caustics']),"frame_length":0.05,"scale":0.62 if kind!='swamp' else 0.85,"power":int(c['caustics_power'])}
    if c['caustics']: ca['texture']='textures/dlavie/derivative_caustics'
    return {"format_version":"1.26.0","minecraft:water_settings":{
      "description":{"identifier":identifier},
      "particle_concentrations":{"chlorophyll":p['ch'],"suspended_sediment":p['sed'],"cdom":p['cdom']},
      "caustics":ca,
      "waves":{"enabled":True,"frequency":p['freq'],"octaves":c['water_octaves'],"depth":p['depth'],"direction_increment":73.0,"speed":0.92,"shape":p['shape'],"pull":p['pull'],"mix":p['mix'],"frequency_scaling":p['scale'],"speed_scaling":p['speedscale']},
      "biome_water_color_contribution":p['color']}}

def fog(c,identifier,dimension='overworld',kind='default'):
    if dimension=='nether':
        air={"max_density":0.042,"uniform":True}; wd=0.48; asc=[0.030,0.012,0.008]; aab=[0.021,0.017,0.016]
    elif dimension=='end':
        air={"max_density":0.021,"uniform":True}; wd=0.44; asc=[0.021,0.018,0.034]; aab=[0.006,0.005,0.009]
    else:
        factor={'default':1.0,'humid':1.48,'dry':0.58,'cold':0.78,'cave':1.75}.get(kind,1.0)
        if kind=='cave': air={"max_density":min(0.035,c['fog_density']*factor),"uniform":True}
        else: air={"max_density":c['fog_density']*factor,"zero_density_height":160.0 if kind!='humid' else 172.0,"max_density_height":51.0 if kind!='humid' else 58.0}
        wd=c['water_fog_density'] * ({'swamp':1.25}.get(kind,1.0))
        if kind=='humid': asc=[0.038,0.046,0.060]
        elif kind=='dry': asc=[0.022,0.025,0.030]
        elif kind=='cold': asc=[0.025,0.032,0.044]
        elif kind=='cave': asc=[0.018,0.024,0.035]
        else: asc=[0.030,0.038,0.052]
        aab=[0.0007,0.0009,0.0013]
    return {"format_version":"1.16.100","minecraft:fog_settings":{"description":{"identifier":identifier},"volumetric":{"density":{"water":{"max_density":wd,"uniform":True},"air":air},"media_coefficients":{"water":{"scattering":[0.030,0.068,0.082],"absorption":[0.40,0.14,0.08]},"air":{"scattering":asc,"absorption":aab}}}}}

LIGHTS={
 "minecraft:torch":{"light_color":"#FFD0A0","light_type":"point_light"},
 "minecraft:lantern":{"light_color":"#FFB16A","light_type":"point_light"},
 "minecraft:soul_torch":{"light_color":"#62D7FF","light_type":"point_light"},
 "minecraft:soul_lantern":{"light_color":"#62D7FF","light_type":"point_light"},
 "minecraft:end_rod":{"light_color":"#DFEAFF","light_type":"point_light"},
 "minecraft:redstone_torch":{"light_color":"#FF3D2D","light_type":"point_light"},
 "minecraft:candle":{"light_color":"#FFD19A","light_type":"point_light"},
 "minecraft:sea_pickle":{"light_color":"#B5FFD0","light_type":"point_light"},
 "minecraft:glowstone":{"light_color":"#FFD096","light_type":"static_light"},
 "minecraft:sea_lantern":{"light_color":"#C7EDFF","light_type":"static_light"},
 "minecraft:redstone_lamp":{"light_color":"#FFB36F","light_type":"static_light"},
 "minecraft:shroomlight":{"light_color":"#FFB06B","light_type":"static_light"},
 "minecraft:ochre_froglight":{"light_color":"#FFD89C","light_type":"static_light"},
 "minecraft:verdant_froglight":{"light_color":"#C2FFD2","light_type":"static_light"},
 "minecraft:pearlescent_froglight":{"light_color":"#E9CBFF","light_type":"static_light"},
 "minecraft:campfire":{"light_color":"#FFAA62","light_type":"static_light"},
 "minecraft:soul_campfire":{"light_color":"#61D2FF","light_type":"static_light"}
}

for name,c in PRESETS.items():
    base=Path('subpacks')/name
    dump(base/'atmospherics/atmospherics.json',atmosphere())
    dump(base/'atmospherics/nether.json',atmosphere('dlavie:nether_atmospherics','nether'))
    dump(base/'atmospherics/end.json',atmosphere('dlavie:end_atmospherics','end'))
    dump(base/'lighting/global.json',lighting(c))
    dump(base/'lighting/lush.json',lighting(c,'dlavie:lush_lighting','overworld','lush'))
    dump(base/'lighting/nether.json',lighting(c,'dlavie:nether_lighting','nether'))
    dump(base/'lighting/end.json',lighting(c,'dlavie:end_lighting','end'))
    dump(base/'color_grading/color_grading.json',grading(c))
    for v in ('lush','dry','cold','cave'): dump(base/f'color_grading/{v}.json',grading(c,f'dlavie:{v}_color_grading','overworld',v))
    dump(base/'color_grading/nether.json',grading(c,'dlavie:nether_color_grading','nether'))
    dump(base/'color_grading/end.json',grading(c,'dlavie:end_color_grading','end'))
    dump(base/'pbr/global.json',pbr(c))
    for kind in ('default','river','ocean','swamp','frozen'):
        ident='dlavie:default_water' if kind=='default' else f'dlavie:{kind}_water'
        dump(base/f'water/{kind}.json',water(c,ident,kind))
    for kind in ('default','humid','dry','cold','cave'):
        ident='dlavie:overworld_fog' if kind=='default' else f'dlavie:{kind}_fog'
        dump(base/f'fogs/{kind}.json',fog(c,ident,'overworld',kind))
    dump(base/'fogs/nether.json',fog(c,'dlavie:nether_fog','nether'))
    dump(base/'fogs/end.json',fog(c,'dlavie:end_fog','end'))
    dump(base/'local_lighting/local_lighting.json',{"format_version":"1.21.120","minecraft:local_light_settings":LIGHTS})
    dump(base/'shadows/global.json',{"format_version":"1.21.80","minecraft:shadow_settings":{"shadow_style":c['shadow_style'],"texel_size":c['shadow_texel_size']}})

COLD=('cold','frozen','ice_','snowy','peaks','grove')
DRY=('desert','mesa','savanna','badlands')
LUSH=('forest','jungle','bamboo','meadow','lush','taiga','cherry','mushroom')
CAVE=('deep_dark','dripstone_caves','lush_caves')
SWAMP=('swampland','mangrove_swamp')

def group_for(b):
    if b in CAVE:return 'cave'
    if any(x in b for x in SWAMP):return 'humid'
    if any(x in b for x in DRY):return 'dry'
    if any(x in b for x in COLD):return 'cold'
    if any(x in b for x in LUSH):return 'lush'
    return 'default'

def water_kind(b):
    if any(x in b for x in SWAMP):return 'swamp'
    if 'ocean' in b:
        return 'frozen' if any(x in b for x in ('cold','frozen')) else 'ocean'
    if 'river' in b or 'beach' in b:return 'frozen' if 'frozen' in b or 'cold' in b else 'river'
    return 'default'

def water_color(b,k):
    if k=='swamp': return '#48664F'
    if k=='frozen': return '#326B86'
    if k=='ocean':
        if 'warm' in b:return '#20829A'
        if 'lukewarm' in b:return '#20778F'
        return '#1C6785'
    if k=='river':return '#2A8496'
    return '#287A91'

for b in BIOME_CFG['biomes']:
    g=group_for(b); wk=water_kind(b)
    fog_id='dlavie:overworld_fog' if g in ('default','lush') else f'dlavie:{g}_fog'
    if g=='lush': fog_id='dlavie:humid_fog'
    grade_id='dlavie:default_color_grading' if g=='default' else f'dlavie:{g}_color_grading'
    light_id='dlavie:lush_lighting' if g=='lush' else 'dlavie:default_lighting'
    water_id='dlavie:default_water' if wk=='default' else f'dlavie:{wk}_water'
    opacity={'swamp':0.90,'frozen':0.84,'ocean':0.80,'river':0.76,'default':0.80}[wk]
    comps={
      "minecraft:fog_appearance":{"fog_identifier":fog_id},
      "minecraft:water_appearance":{"surface_color":water_color(b,wk),"surface_opacity":opacity},
      "minecraft:atmosphere_identifier":{"atmosphere_identifier":"dlavie:default_atmospherics"},
      "minecraft:color_grading_identifier":{"color_grading_identifier":grade_id},
      "minecraft:lighting_identifier":{"lighting_identifier":light_id},
      "minecraft:water_identifier":{"water_identifier":water_id}}
    dump(Path('biomes')/(b+'.client_biome.json'),{"format_version":"1.21.130","minecraft:client_biome":{"description":{"identifier":b},"components":comps}})
for b in ['hell','crimson_forest','warped_forest','soulsand_valley','basalt_deltas']:
    dump(Path('biomes')/(b+'.client_biome.json'),{"format_version":"1.21.130","minecraft:client_biome":{"description":{"identifier":b},"components":{"minecraft:fog_appearance":{"fog_identifier":"dlavie:nether_fog"},"minecraft:atmosphere_identifier":{"atmosphere_identifier":"dlavie:nether_atmospherics"},"minecraft:color_grading_identifier":{"color_grading_identifier":"dlavie:nether_color_grading"},"minecraft:lighting_identifier":{"lighting_identifier":"dlavie:nether_lighting"}}}})
dump(Path('biomes/the_end.client_biome.json'),{"format_version":"1.21.130","minecraft:client_biome":{"description":{"identifier":"the_end"},"components":{"minecraft:fog_appearance":{"fog_identifier":"dlavie:end_fog"},"minecraft:atmosphere_identifier":{"atmosphere_identifier":"dlavie:end_atmospherics"},"minecraft:color_grading_identifier":{"color_grading_identifier":"dlavie:end_color_grading"},"minecraft:lighting_identifier":{"lighting_identifier":"dlavie:end_lighting"}}}})
print(f"Generated DLavie Visual 2.3: {len(PRESETS)} presets, cinematic biome groups, 5 water profiles")
