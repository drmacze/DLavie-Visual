#!/usr/bin/env python3
"""Generate DLavie Visual 3.0: biome lighting + atmosphere + water + fog profiles."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]
PRESETS=json.loads((ROOT/'config/presets.json').read_text(encoding='utf-8'))
BIOME_CFG=json.loads((ROOT/'config/biomes.json').read_text(encoding='utf-8'))

def dump(path,obj):
    p=ROOT/path; p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(obj,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')

def scale_color(c, mul=(1,1,1), add=(0,0,0)):
    return [max(0,min(255,int(c[i]*mul[i]+add[i]))) for i in range(3)]

def key_colors(src, mul=(1,1,1), add=(0,0,0)):
    return {k:scale_color(v,mul,add) for k,v in src.items()}

def atmosphere(identifier='dlavie:default_atmospherics', variant='default', dimension='overworld'):
    if dimension=='nether':
        return {"format_version":"1.21.40","minecraft:atmosphere_settings":{
          "description":{"identifier":identifier},"horizon_blend_stops":{"min":{"0":0,"1":0},"start":{"0":0.32,"1":0.32},"mie_start":{"0":0.48,"1":0.48},"max":{"0":0.28,"1":0.28}},
          "rayleigh_strength":{"0":0.7,"1":0.7},"sun_mie_strength":{"0":0.65,"1":0.65},"moon_mie_strength":{"0":0,"1":0},"sun_glare_shape":{"0":0.05,"1":0.05},
          "sky_zenith_color":{"0":[20,3,5],"1":[20,3,5]},"sky_horizon_color":{"0":[112,24,12],"1":[112,24,12]}}}
    if dimension=='end':
        return {"format_version":"1.21.40","minecraft:atmosphere_settings":{
          "description":{"identifier":identifier},"horizon_blend_stops":{"min":{"0":0,"1":0},"start":{"0":0.40,"1":0.40},"mie_start":{"0":0.44,"1":0.44},"max":{"0":0.30,"1":0.30}},
          "rayleigh_strength":{"0":1.1,"1":1.1},"sun_mie_strength":{"0":0.25,"1":0.25},"moon_mie_strength":{"0":0.45,"1":0.45},"sun_glare_shape":{"0":0.04,"1":0.04},
          "sky_zenith_color":{"0":[8,4,23],"1":[8,4,23]},"sky_horizon_color":{"0":[62,40,99],"1":[62,40,99]}}}
    zen={"0.0":[76,121,166],"0.16":[82,132,180],"0.22":[55,90,133],"0.25":[34,58,91],"0.34":[14,24,48],"0.50":[7,12,30],"0.66":[14,24,48],"0.75":[38,66,103],"0.80":[75,125,174],"1.0":[76,121,166]}
    hor={"0.0":[184,198,214],"0.16":[199,210,220],"0.205":[248,209,164],"0.235":[255,168,111],"0.25":[250,122,80],"0.29":[177,78,91],"0.36":[91,72,115],"0.50":[28,40,75],"0.64":[91,72,115],"0.71":[193,91,104],"0.75":[252,136,88],"0.785":[250,191,137],"0.84":[200,211,221],"1.0":[184,198,214]}
    # Current vanilla sample is around rayleigh 10 / sun Mie .75 / glare .074. This pass stays in that scale,
    # but raises low-sun Mie and fog instead of multiplying the sun by 1000x.
    ray={"0.0":9.8,"0.16":9.5,"0.25":5.4,"0.34":4.2,"0.50":3.4,"0.66":4.2,"0.75":5.4,"0.84":9.5,"1.0":9.8}
    mie={"0.0":0.10,"0.16":0.18,"0.20":0.55,"0.225":1.05,"0.25":1.35,"0.285":0.85,"0.34":0.20,"0.50":0.03,"0.66":0.20,"0.715":0.85,"0.75":1.35,"0.775":1.05,"0.80":0.55,"0.84":0.18,"1.0":0.10}
    moon={"0.0":0.0,"0.30":0.12,"0.38":0.34,"0.50":0.48,"0.62":0.34,"0.70":0.12,"1.0":0.0}
    glare={"0.0":0.012,"0.16":0.020,"0.20":0.052,"0.225":0.090,"0.25":0.115,"0.285":0.070,"0.34":0.025,"0.50":0.0,"0.66":0.025,"0.715":0.070,"0.75":0.115,"0.775":0.090,"0.80":0.052,"0.84":0.020,"1.0":0.012}
    profiles={
      'default':((1,1,1),(0,0,0),1.0,1.0),
      'forest':((0.91,0.98,0.96),(-2,0,-1),0.96,1.08),
      'dense':((0.78,0.92,0.88),(-4,-1,-2),0.88,1.18),
      'dry':((1.03,0.96,0.86),(3,0,-4),0.82,0.88),
      'cold':((0.88,0.96,1.08),(-4,0,5),1.05,0.78),
      'swamp':((0.73,0.86,0.75),(-5,-2,-5),0.74,1.20),
      'cave':((0.42,0.50,0.62),(-10,-9,-5),0.45,0.32),
      'ocean':((0.92,1.00,1.08),(-2,0,4),1.04,0.90)
    }
    cmul,cadd,rf,mf=profiles.get(variant,profiles['default'])
    zen=key_colors(zen,cmul,cadd); hor=key_colors(hor,cmul,cadd)
    ray={k:v*rf for k,v in ray.items()}; mie={k:v*mf for k,v in mie.items()}
    return {"format_version":"1.21.40","minecraft:atmosphere_settings":{
      "description":{"identifier":identifier},
      "horizon_blend_stops":{"min":{"0":0,"1":0},"start":{"0":0.68,"0.20":0.46,"0.25":0.28,"0.34":0.32,"0.50":0.36,"0.66":0.32,"0.75":0.28,"0.80":0.46,"1":0.68},"mie_start":{"0":0.52,"0.20":0.88,"0.25":0.76,"0.34":0.48,"0.50":0.30,"0.66":0.48,"0.75":0.76,"0.80":0.88,"1":0.52},"max":{"0":0.25,"1":0.25}},
      "rayleigh_strength":ray,"sun_mie_strength":mie,"moon_mie_strength":moon,"sun_glare_shape":glare,
      "sky_zenith_color":zen,"sky_horizon_color":hor}}

LIGHT_PROFILES={
 'default':dict(sun=1.00,amb=1.00,sky=1.00,ambient_mul=(1,1,1)),
 'forest':dict(sun=.82,amb=.90,sky=.78,ambient_mul=(.93,1.02,.96)),
 'dense':dict(sun=.66,amb=.82,sky=.64,ambient_mul=(.86,1.00,.90)),
 'dry':dict(sun=1.05,amb=.86,sky=.92,ambient_mul=(1.05,.98,.88)),
 'cold':dict(sun=.90,amb=.96,sky=.94,ambient_mul=(.90,.97,1.08)),
 'swamp':dict(sun=.68,amb=.90,sky=.62,ambient_mul=(.84,.97,.86)),
 'cave':dict(sun=.24,amb=.58,sky=.22,ambient_mul=(.76,.84,1.02)),
 'ocean':dict(sun=1.00,amb=1.02,sky=1.08,ambient_mul=(.94,1.00,1.08)),
}

def lighting(c,identifier='dlavie:default_lighting',variant='default',dimension='overworld'):
    if dimension=='nether':
        return {"format_version":"1.21.80","minecraft:lighting_settings":{"description":{"identifier":identifier},"directional_lights":{"orbital":{"sun":{"illuminance":{"0":18,"1":18},"color":[255,92,55]},"moon":{"illuminance":{"0":0,"1":0},"color":[120,65,90]},"orbital_offset_degrees":0},"flash":{"illuminance":3,"color":[255,185,150]}},"emissive":{"desaturation":0.04},"ambient":{"color":[255,104,72],"illuminance":0.024},"sky":{"intensity":0.18}}}
    if dimension=='end':
        return {"format_version":"1.21.80","minecraft:lighting_settings":{"description":{"identifier":identifier},"directional_lights":{"orbital":{"sun":{"illuminance":{"0":9,"1":9},"color":[175,155,255]},"moon":{"illuminance":{"0":0.12,"1":0.12},"color":[190,202,255]},"orbital_offset_degrees":0},"flash":{"illuminance":8,"color":[220,225,255]}},"emissive":{"desaturation":0.04},"ambient":{"color":[142,128,205],"illuminance":0.020},"sky":{"intensity":0.20}}}
    p=LIGHT_PROFILES.get(variant,LIGHT_PROFILES['default'])
    s=c['sun_illuminance']*p['sun']; m=c['moon_illuminance']; ad=c['ambient_day']*p['amb']; an=c['ambient_night']*p['amb']; sd=max(.1,c['sky_day']*p['sky']); sn=max(.1,c['sky_night']*p['sky'])
    sun_i={"0.0":s,"0.14":s,"0.20":s*.72,"0.24":s*.30,"0.265":s*.09,"0.282":1.0,"0.2915":0.01,"0.292":0.0,"0.708":0.0,"0.7085":0.01,"0.718":1.0,"0.735":s*.09,"0.76":s*.30,"0.80":s*.72,"0.86":s,"1.0":s}
    sun_c={"0.0":[255,246,232],"0.16":[255,238,215],"0.205":[255,209,163],"0.24":[255,166,103],"0.265":[255,121,72],"0.32":[248,111,78],"0.50":[255,235,226],"0.68":[248,111,78],"0.735":[255,128,77],"0.76":[255,176,112],"0.795":[255,214,169],"0.84":[255,238,215],"1.0":[255,246,232]}
    moon_i={"0.0":0,"0.20":0,"0.225":m*.35,"0.30":m*.75,"0.40":m,"0.60":m,"0.70":m*.75,"0.735":m*.35,"0.75":0,"1.0":0}
    moon_c={"0.0":[158,183,255],"0.50":[175,198,255],"1.0":[158,183,255]}
    amb_i={"0.0":ad,"0.18":ad,"0.24":ad*.60,"0.30":an*1.25,"0.38":an,"0.50":an,"0.62":an,"0.70":an*1.25,"0.76":ad*.60,"0.82":ad,"1.0":ad}
    base_amb={"0.0":[214,226,242],"0.20":[245,218,184],"0.25":[245,176,126],"0.34":[112,133,181],"0.50":[79,101,153],"0.66":[112,133,181],"0.75":[247,182,132],"0.80":[246,220,187],"1.0":[214,226,242]}
    am=key_colors(base_amb,p['ambient_mul'])
    sky_i={"0.0":sd,"0.18":sd,"0.24":max(.1,sd*.65),"0.32":sn,"0.50":sn,"0.68":sn,"0.76":max(.1,sd*.65),"0.82":sd,"1.0":sd}
    return {"format_version":"1.21.80","minecraft:lighting_settings":{"description":{"identifier":identifier},"directional_lights":{"orbital":{"sun":{"illuminance":sun_i,"color":sun_c},"moon":{"illuminance":moon_i,"color":moon_c},"orbital_offset_degrees":3.0},"flash":{"illuminance":10.0,"color":[228,233,255]}},"emissive":{"desaturation":0.04},"ambient":{"color":am,"illuminance":amb_i},"sky":{"intensity":sky_i}}}

def grading(c,identifier='dlavie:default_color_grading',variant='default',dimension='overworld'):
    contrast=c['contrast']; sat=c['saturation']; temp=c['temperature']
    if dimension=='nether': contrast=1.12; sat=.98; temp=6200
    elif dimension=='end': contrast=1.14; sat=.92; temp=7600
    gain=[1,1,1]; shadow=[.93,.97,1.03]; hi=[1.025,1.01,.98]
    if variant=='forest': gain=[.98,1.015,.985]; sat*=1.01
    elif variant=='dense': gain=[.94,1.00,.95]; shadow=[.86,.94,.91]; contrast*=1.03
    elif variant=='dry': gain=[1.025,1.00,.95]; hi=[1.04,1.01,.94]
    elif variant=='cold': gain=[.96,1.00,1.045]; shadow=[.90,.96,1.07]; sat*=.97
    elif variant=='swamp': gain=[.91,.99,.91]; shadow=[.82,.93,.86]; sat*=.92
    elif variant=='cave': gain=[.86,.91,1.00]; shadow=[.76,.84,1.03]; contrast*=1.05; sat*=.88
    elif variant=='ocean': gain=[.95,1.00,1.035]; sat*=1.00
    grade={"shadows":{"enabled":True,"contrast":[contrast*1.02]*3,"gain":shadow,"gamma":[2.2,2.2,2.22],"offset":[-.003,-.002,0],"saturation":[sat*.90]*3,"shadowsMax":0.68},"midtones":{"contrast":[contrast]*3,"gain":gain,"gamma":[2.18,2.20,2.22],"offset":[0,0,0],"saturation":[sat]*3},"highlights":{"enabled":True,"contrast":[contrast*.96]*3,"gain":hi,"gamma":[2.14,2.17,2.20],"offset":[0,0,0],"saturation":[sat*.92]*3,"highlightsMin":1.12},"temperature":{"enabled":True,"temperature":temp,"type":"white_balance"}}
    return {"format_version":"1.21.90","minecraft:color_grading_settings":{"description":{"identifier":identifier},"color_grading":grade,"tone_mapping":{"operator":"aces"}}}

def pbr(c):
    return {"format_version":"1.21.40","minecraft:pbr_fallback_settings":{"blocks":{"global_metalness_emissive_roughness_subsurface":[0,0,c['roughness'],0]},"actors":{"global_metalness_emissive_roughness_subsurface":[0,0,c['actor_roughness'],0]},"particles":{"global_metalness_emissive_roughness_subsurface":[0,0,225,0]},"items":{"global_metalness_emissive_roughness_subsurface":[0,0,205,0]}}}

def water(c,identifier,kind='default'):
    profiles={
      'default':dict(ch=.14,sed=.025,cdom=.05,freq=.021,depth=.43,shape=3.6,pull=.20,mix=.62,scale=.60,speedscale=.20,color=.50),
      'river':dict(ch=.18,sed=.035,cdom=.065,freq=.016,depth=.35,shape=4.0,pull=.18,mix=.66,scale=.56,speedscale=.18,color=.62),
      'ocean':dict(ch=.09,sed=.014,cdom=.022,freq=.025,depth=.52,shape=3.3,pull=.23,mix=.56,scale=.62,speedscale=.22,color=.58),
      'swamp':dict(ch=.68,sed=.18,cdom=.54,freq=.011,depth=.20,shape=4.5,pull=.14,mix=.72,scale=.52,speedscale=.15,color=.74),
      'frozen':dict(ch=.04,sed=.008,cdom=.012,freq=.014,depth=.25,shape=4.2,pull=.14,mix=.70,scale=.54,speedscale=.16,color=.66)}
    p=profiles[kind]; ca={"enabled":bool(c['caustics']),"frame_length":.05,"scale":.60 if kind!='swamp' else .82,"power":int(c['caustics_power'])}
    if c['caustics']: ca['texture']='textures/dlavie/derivative_caustics'
    return {"format_version":"1.26.0","minecraft:water_settings":{"description":{"identifier":identifier},"particle_concentrations":{"chlorophyll":p['ch'],"suspended_sediment":p['sed'],"cdom":p['cdom']},"caustics":ca,"waves":{"enabled":True,"frequency":p['freq'],"octaves":c['water_octaves'],"depth":p['depth'],"direction_increment":73.0,"speed":.90,"shape":p['shape'],"pull":p['pull'],"mix":p['mix'],"frequency_scaling":p['scale'],"speed_scaling":p['speedscale']},"biome_water_color_contribution":p['color']}}

FOG_FACTOR={'default':1.0,'forest':1.18,'dense':1.48,'dry':.52,'cold':.76,'swamp':1.60,'cave':1.90,'ocean':.68}
FOG_SCAT={'default':[.027,.034,.045],'forest':[.030,.039,.048],'dense':[.034,.044,.052],'dry':[.019,.022,.027],'cold':[.022,.030,.043],'swamp':[.031,.043,.035],'cave':[.015,.021,.032],'ocean':[.020,.029,.041]}
def fog(c,identifier,kind='default',dimension='overworld'):
    if dimension=='nether': air={"max_density":.040,"uniform":True}; wd=.46; scat=[.030,.012,.008]; absorb=[.020,.017,.016]
    elif dimension=='end': air={"max_density":.020,"uniform":True}; wd=.42; scat=[.020,.018,.033]; absorb=[.006,.005,.009]
    else:
        den=c['fog_density']*FOG_FACTOR.get(kind,1)
        if kind=='cave': air={"max_density":min(.030,den),"uniform":True}
        else: air={"max_density":den,"zero_density_height":172.0 if kind in ('forest','dense','swamp') else 158.0,"max_density_height":60.0 if kind in ('dense','swamp') else 50.0}
        wd=c['water_fog_density']*(1.18 if kind=='swamp' else 1.0); scat=FOG_SCAT.get(kind,FOG_SCAT['default']); absorb=[.0006,.0008,.0012]
    return {"format_version":"1.16.100","minecraft:fog_settings":{"description":{"identifier":identifier},"volumetric":{"density":{"water":{"max_density":wd,"uniform":True},"air":air},"media_coefficients":{"water":{"scattering":[.028,.064,.080],"absorption":[.36,.13,.075]},"air":{"scattering":scat,"absorption":absorb}}}}}

BASE_LIGHTS={
 "minecraft:torch":("#FFC38A",True),"minecraft:lantern":("#FFAB5C",True),"minecraft:soul_torch":("#5FD7FF",True),"minecraft:soul_lantern":("#5FD7FF",True),"minecraft:end_rod":("#DDEAFF",True),"minecraft:redstone_torch":("#FF3A2B",True),"minecraft:candle":("#FFD09B",True),"minecraft:sea_pickle":("#ADFFD0",True),
 "minecraft:glowstone":("#FFC785",False),"minecraft:sea_lantern":("#BDEBFF",False),"minecraft:redstone_lamp":("#FFAA62",False),"minecraft:shroomlight":("#FFA95E",False),"minecraft:ochre_froglight":("#FFD594",False),"minecraft:verdant_froglight":("#BDFFD1",False),"minecraft:pearlescent_froglight":("#E8C8FF",False),"minecraft:campfire":("#FF9B4B",False),"minecraft:soul_campfire":("#5DCCFF",False)
}
def local_lights(level):
    medium_point={'minecraft:glowstone','minecraft:sea_lantern','minecraft:redstone_lamp','minecraft:shroomlight','minecraft:ochre_froglight','minecraft:verdant_froglight','minecraft:pearlescent_froglight'}
    high_point=set(BASE_LIGHTS)
    out={}
    for b,(col,base_point) in BASE_LIGHTS.items():
        point=base_point or (level>=1 and b in medium_point) or (level>=2 and b in high_point)
        out[b]={"light_color":col,"light_type":"point_light" if point else "static_light"}
    return out

PROFILES=('default','forest','dense','dry','cold','swamp','cave','ocean')
for name,c in PRESETS.items():
    base=Path('subpacks')/name
    for v in PROFILES:
        aid='dlavie:default_atmospherics' if v=='default' else f'dlavie:{v}_atmospherics'
        lid='dlavie:default_lighting' if v=='default' else f'dlavie:{v}_lighting'
        gid='dlavie:default_color_grading' if v=='default' else f'dlavie:{v}_color_grading'
        fid='dlavie:overworld_fog' if v=='default' else f'dlavie:{v}_fog'
        dump(base/f'atmospherics/{v}.json',atmosphere(aid,v))
        dump(base/f'lighting/{v}.json',lighting(c,lid,v))
        dump(base/f'color_grading/{v}.json',grading(c,gid,v))
        dump(base/f'fogs/{v}.json',fog(c,fid,v))
    dump(base/'atmospherics/nether.json',atmosphere('dlavie:nether_atmospherics','default','nether'))
    dump(base/'atmospherics/end.json',atmosphere('dlavie:end_atmospherics','default','end'))
    dump(base/'lighting/nether.json',lighting(c,'dlavie:nether_lighting','default','nether'))
    dump(base/'lighting/end.json',lighting(c,'dlavie:end_lighting','default','end'))
    dump(base/'color_grading/nether.json',grading(c,'dlavie:nether_color_grading','default','nether'))
    dump(base/'color_grading/end.json',grading(c,'dlavie:end_color_grading','default','end'))
    dump(base/'fogs/nether.json',fog(c,'dlavie:nether_fog','default','nether'))
    dump(base/'fogs/end.json',fog(c,'dlavie:end_fog','default','end'))
    dump(base/'pbr/global.json',pbr(c))
    for wk in ('default','river','ocean','swamp','frozen'):
        wid='dlavie:default_water' if wk=='default' else f'dlavie:{wk}_water'; dump(base/f'water/{wk}.json',water(c,wid,wk))
    dump(base/'local_lighting/local_lighting.json',{"format_version":"1.21.120","minecraft:local_light_settings":local_lights(c['point_light_level'])})
    dump(base/'shadows/global.json',{"format_version":"1.21.80","minecraft:shadow_settings":{"shadow_style":c['shadow_style'],"texel_size":c['shadow_texel_size']}})

CAVE={'deep_dark','dripstone_caves','lush_caves'}
SWAMP=('swampland','mangrove_swamp')
DENSE=('roofed_forest','jungle','bamboo_jungle')
FOREST=('forest','birch_forest','flower_forest','taiga','mega_taiga','redwood_taiga','cherry_grove','meadow','mushroom_island')
DRY=('desert','mesa','savanna')
COLD=('cold','frozen','ice_','snowy','peaks','grove')

def group_for(b):
    if b in CAVE:return 'cave'
    if any(x in b for x in SWAMP):return 'swamp'
    if any(x in b for x in DENSE):return 'dense'
    if any(x in b for x in DRY):return 'dry'
    if any(x in b for x in COLD):return 'cold'
    if 'ocean' in b:return 'ocean'
    if any(x in b for x in FOREST):return 'forest'
    return 'default'

def water_kind(b):
    if any(x in b for x in SWAMP):return 'swamp'
    if 'ocean' in b:return 'frozen' if any(x in b for x in ('cold','frozen')) else 'ocean'
    if 'river' in b or 'beach' in b:return 'frozen' if ('frozen' in b or 'cold' in b) else 'river'
    return 'default'

def water_color(b,k):
    if k=='swamp': return '#496A54'
    if k=='frozen': return '#39768F'
    if k=='ocean':
        if 'warm' in b:return '#218E9F'
        if 'lukewarm' in b:return '#237F98'
        return '#1F6D8C'
    if k=='river':return '#2B879A'
    return '#2A7E95'

for b in BIOME_CFG['biomes']:
    g=group_for(b); wk=water_kind(b)
    aid='dlavie:default_atmospherics' if g=='default' else f'dlavie:{g}_atmospherics'
    lid='dlavie:default_lighting' if g=='default' else f'dlavie:{g}_lighting'
    gid='dlavie:default_color_grading' if g=='default' else f'dlavie:{g}_color_grading'
    fid='dlavie:overworld_fog' if g=='default' else f'dlavie:{g}_fog'
    wid='dlavie:default_water' if wk=='default' else f'dlavie:{wk}_water'
    opacity={'swamp':.91,'frozen':.86,'ocean':.84,'river':.80,'default':.82}[wk]
    comps={"minecraft:fog_appearance":{"fog_identifier":fid},"minecraft:water_appearance":{"surface_color":water_color(b,wk),"surface_opacity":opacity},"minecraft:atmosphere_identifier":{"atmosphere_identifier":aid},"minecraft:color_grading_identifier":{"color_grading_identifier":gid},"minecraft:lighting_identifier":{"lighting_identifier":lid},"minecraft:water_identifier":{"water_identifier":wid}}
    dump(Path('biomes')/(b+'.client_biome.json'),{"format_version":"1.21.130","minecraft:client_biome":{"description":{"identifier":b},"components":comps}})
for b in ['hell','crimson_forest','warped_forest','soulsand_valley','basalt_deltas']:
    dump(Path('biomes')/(b+'.client_biome.json'),{"format_version":"1.21.130","minecraft:client_biome":{"description":{"identifier":b},"components":{"minecraft:fog_appearance":{"fog_identifier":"dlavie:nether_fog"},"minecraft:atmosphere_identifier":{"atmosphere_identifier":"dlavie:nether_atmospherics"},"minecraft:color_grading_identifier":{"color_grading_identifier":"dlavie:nether_color_grading"},"minecraft:lighting_identifier":{"lighting_identifier":"dlavie:nether_lighting"}}}})
dump(Path('biomes/the_end.client_biome.json'),{"format_version":"1.21.130","minecraft:client_biome":{"description":{"identifier":"the_end"},"components":{"minecraft:fog_appearance":{"fog_identifier":"dlavie:end_fog"},"minecraft:atmosphere_identifier":{"atmosphere_identifier":"dlavie:end_atmospherics"},"minecraft:color_grading_identifier":{"color_grading_identifier":"dlavie:end_color_grading"},"minecraft:lighting_identifier":{"lighting_identifier":"dlavie:end_lighting"}}}})
print(f'Generated DLavie Visual 3.0: {len(PRESETS)} presets, {len(PROFILES)} Overworld render profiles, 5 water profiles')
