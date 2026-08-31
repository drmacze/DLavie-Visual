#!/usr/bin/env python3
"""Generate DLavie Visual Vibrant Visuals configs from Derivative profile mapping."""
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
        zen={"0.0":[28,4,5],"0.5":[12,1,3],"1.0":[28,4,5]}; hor={"0.0":[118,26,12],"0.5":[58,7,10],"1.0":[118,26,12]}
        ray={"0.0":1.0,"1.0":1.0}; sm={"0.0":0.15,"1.0":0.15}; mm={"0.0":0.0,"1.0":0.0}; glare={"0.0":0.04,"1.0":0.04}
    elif dimension=='end':
        zen={"0.0":[14,7,30],"0.5":[5,3,15],"1.0":[14,7,30]}; hor={"0.0":[64,40,104],"0.5":[30,20,58],"1.0":[64,40,104]}
        ray={"0.0":1.4,"1.0":1.4}; sm={"0.0":0.12,"1.0":0.12}; mm={"0.0":0.08,"1.0":0.08}; glare={"0.0":0.035,"1.0":0.035}
    else:
        # Derivative profile: 7000K, FOG_TYPE=2, VOLUMETRIC_LIGHT_STRENGTH=0.5.
        # Values below stay within the Bedrock atmospheric ranges used by Mojang's own VV defaults.
        zen={"0.0":[61,129,186],"0.16":[70,139,194],"0.215":[50,105,164],"0.25":[26,58,106],"0.31":[12,25,54],"0.42":[6,10,28],"0.5":[4,7,22],"0.58":[6,10,28],"0.69":[12,25,54],"0.75":[31,68,119],"0.785":[55,116,175],"0.84":[70,139,194],"1.0":[61,129,186]}
        hor={"0.0":[178,207,228],"0.16":[192,211,227],"0.205":[240,194,160],"0.225":[255,166,114],"0.25":[255,116,76],"0.285":[174,79,101],"0.34":[79,65,119],"0.42":[35,48,90],"0.5":[20,29,66],"0.58":[35,48,90],"0.66":[79,65,119],"0.715":[198,91,116],"0.75":[255,126,82],"0.775":[255,177,124],"0.81":[236,204,170],"0.86":[192,211,227],"1.0":[178,207,228]}
        ray={"0.0":9.4,"0.14":9.2,"0.22":6.2,"0.25":4.8,"0.32":4.2,"0.5":3.8,"0.68":4.2,"0.75":4.8,"0.78":6.2,"0.86":9.2,"1.0":9.4}
        sm={"0.0":0.14,"0.16":0.20,"0.205":0.48,"0.225":0.78,"0.25":0.95,"0.29":0.42,"0.36":0.10,"0.5":0.04,"0.64":0.10,"0.71":0.42,"0.75":0.95,"0.775":0.78,"0.795":0.48,"0.84":0.20,"1.0":0.14}
        mm={"0.0":0.0,"0.28":0.04,"0.36":0.12,"0.5":0.18,"0.64":0.12,"0.72":0.04,"1.0":0.0}
        glare={"0.0":0.018,"0.16":0.026,"0.205":0.045,"0.225":0.065,"0.25":0.078,"0.30":0.042,"0.38":0.015,"0.5":0.008,"0.62":0.015,"0.70":0.042,"0.75":0.078,"0.775":0.065,"0.795":0.045,"0.84":0.026,"1.0":0.018}
    return {"format_version":"1.21.40","minecraft:atmosphere_settings":{
      "description":{"identifier":identifier},
      "horizon_blend_stops":{"min":{"0.0":0.0,"1.0":0.0},"start":{"0.0":0.68,"0.20":0.56,"0.25":0.34,"0.32":0.24,"0.5":0.34,"0.68":0.24,"0.75":0.34,"0.80":0.56,"1.0":0.68},"mie_start":{"0.0":0.60,"0.18":0.72,"0.25":0.92,"0.32":0.58,"0.5":0.42,"0.68":0.58,"0.75":0.92,"0.82":0.72,"1.0":0.60},"max":{"0.0":0.26,"1.0":0.26}},
      "rayleigh_strength":ray,"sun_mie_strength":sm,"moon_mie_strength":mm,"sun_glare_shape":glare,
      "sky_zenith_color":zen,"sky_horizon_color":hor}}

def lighting(c,identifier='dlavie:default_lighting',dimension='overworld'):
    if dimension=='nether':
        sun_i={"0.0":24.0,"1.0":24.0}; sun_c=[255,92,50]; moon_i=0.0; moon_c=[140,70,95]
        amb_i={"0.0":0.055,"1.0":0.055}; amb_c=[255,112,80]; sky_i={"0.0":0.28,"1.0":0.28}; flash=3.0
    elif dimension=='end':
        sun_i={"0.0":15.0,"1.0":15.0}; sun_c=[176,154,255]; moon_i={"0.0":0.08,"1.0":0.08}; moon_c=[180,196,255]
        amb_i={"0.0":0.04,"1.0":0.04}; amb_c=[154,132,214]; sky_i={"0.0":0.34,"1.0":0.34}; flash=12.0
    else:
        s=c['sun_illuminance']; m=c['moon_illuminance']
        sun_i={"0.0":s,"0.18":s*0.92,"0.225":s*0.45,"0.25":s*0.035,"0.29":120.0,"0.33":0.0,"0.67":0.0,"0.71":120.0,"0.75":s*0.035,"0.775":s*0.45,"0.82":s*0.92,"1.0":s}
        sun_c={"0.0":[255,247,235],"0.18":[255,236,212],"0.225":[255,192,128],"0.25":[255,136,78],"0.31":[255,154,108],"0.5":[255,238,225],"0.69":[255,154,108],"0.75":[255,145,91],"0.775":[255,199,140],"0.82":[255,236,212],"1.0":[255,247,235]}
        moon_i={"0.0":0.0,"0.22":0.0,"0.27":m*0.18,"0.34":m*0.72,"0.45":m,"0.55":m,"0.66":m*0.72,"0.73":m*0.18,"0.78":0.0,"1.0":0.0}
        moon_c=[166,191,255]
        ad=c['ambient_day']; an=c['ambient_night']; sd=c['sky_day']; sn=c['sky_night']
        amb_i={"0.0":ad,"0.20":ad*0.8,"0.25":ad*0.42,"0.34":an,"0.5":an,"0.66":an,"0.75":ad*0.42,"0.80":ad*0.8,"1.0":ad}
        amb_c={"0.0":[234,242,255],"0.25":[255,183,143],"0.5":[113,139,194],"0.75":[255,192,151],"1.0":[234,242,255]}
        sky_i={"0.0":sd,"0.20":sd*0.85,"0.25":0.50,"0.34":sn,"0.5":sn,"0.66":sn,"0.75":0.50,"0.80":sd*0.85,"1.0":sd}
        flash=12.0
    return {"format_version":"1.26.0","minecraft:lighting_settings":{
      "description":{"identifier":identifier},"directional_lights":{"orbital":{"sun":{"illuminance":sun_i,"color":sun_c},"moon":{"illuminance":moon_i,"color":moon_c},"orbital_offset_degrees":0.0},"flash":{"illuminance":flash,"color":[225,235,255]}},
      "emissive":{"desaturation":0.035},"ambient":{"color":amb_c,"illuminance":amb_i},"sky":{"intensity":sky_i}}}

def grading(c,identifier='dlavie:default_color_grading',dimension='overworld'):
    if dimension=='nether': contrast=1.10; sat=0.88; temp=6200; op='aces'
    elif dimension=='end': contrast=1.09; sat=0.86; temp=7600; op='aces'
    else: contrast=c['contrast']; sat=c['saturation']; temp=c['temperature']; op='aces'
    # Three-way grade approximates Derivative's IterationT_AgX intent using Bedrock-supported controls:
    # cool restrained shadows, neutral midtones, slightly warm compressed highlights.
    grade={
      "shadows":{"enabled":True,"contrast":[contrast*0.96]*3,"gain":[0.95,0.98,1.03],"gamma":[2.18,2.20,2.24],"offset":[0,0,0],"saturation":[sat*0.88]*3,"shadowsMax":0.68},
      "midtones":{"contrast":[contrast]*3,"gain":[0.985,0.995,1.0],"gamma":[2.2,2.2,2.2],"offset":[0,0,0],"saturation":[sat]*3},
      "highlights":{"enabled":True,"contrast":[contrast*0.94]*3,"gain":[1.025,1.0,0.965],"gamma":[2.16,2.18,2.22],"offset":[0,0,0],"saturation":[sat*0.90]*3,"highlightsMin":1.35},
      "temperature":{"enabled":True,"temperature":temp,"type":"white_balance"}}
    return {"format_version":"1.21.90","minecraft:color_grading_settings":{"description":{"identifier":identifier},"color_grading":grade,"tone_mapping":{"operator":op}}}

def pbr(c):
    r=c['roughness']; ar=c['actor_roughness']
    return {"format_version":"1.21.40","minecraft:pbr_fallback_settings":{"blocks":{"global_metalness_emissive_roughness_subsurface":[0,0,r,0]},"actors":{"global_metalness_emissive_roughness_subsurface":[0,0,ar,0]},"particles":{"global_metalness_emissive_roughness_subsurface":[0,0,230,0]},"items":{"global_metalness_emissive_roughness_subsurface":[0,0,192,0]}}}

def water(c):
    ca={"enabled":c['caustics'],"frame_length":0.05,"scale":2.2,"power":int(c['caustics_power'])}
    if c['caustics']: ca['texture']='textures/dlavie/derivative_caustics'
    return {"format_version":"1.26.0","minecraft:water_settings":{
      "description":{"identifier":"dlavie:default_water"},
      "particle_concentrations":{"chlorophyll":0.62,"suspended_sediment":0.14,"cdom":0.72},
      "caustics":ca,
      "waves":{"enabled":True,"frequency":c['water_frequency'],"octaves":c['water_octaves'],"depth":c['water_depth'],"direction_increment":78.0,"speed":c['water_speed'],"shape":c['water_shape'],"pull":c['water_pull'],"mix":c['water_mix'],"frequency_scaling":c['water_frequency_scaling'],"speed_scaling":c['water_speed_scaling']},
      "biome_water_color_contribution":0.42}}

def fog(c,identifier='dlavie:overworld_fog',dimension='overworld'):
    if dimension=='nether': air={"max_density":0.040,"uniform":True}; water_d=0.55; scat=[0.030,0.012,0.009]; absorb=[0.022,0.018,0.018]
    elif dimension=='end': air={"max_density":0.020,"uniform":True}; water_d=0.50; scat=[0.020,0.017,0.030]; absorb=[0.006,0.005,0.008]
    else: air={"max_density":c['fog_density'],"zero_density_height":176.0,"max_density_height":54.0}; water_d=c['water_fog_density']; scat=[0.026,0.032,0.043]; absorb=[0.0010,0.0013,0.0018]
    return {"format_version":"1.16.100","minecraft:fog_settings":{"description":{"identifier":identifier},"volumetric":{"density":{"water":{"max_density":water_d,"uniform":True},"air":air},"media_coefficients":{"water":{"scattering":[0.012,0.021,0.030],"absorption":[0.16,0.070,0.045]},"air":{"scattering":scat,"absorption":absorb}}}}}

LIGHTS={
 "minecraft:torch":{"light_color":"#FFD0A0","light_type":"point_light"},"minecraft:lantern":{"light_color":"#FFB16A","light_type":"point_light"},
 "minecraft:soul_torch":{"light_color":"#66D9FF","light_type":"point_light"},"minecraft:soul_lantern":{"light_color":"#62D7FF","light_type":"point_light"},
 "minecraft:end_rod":{"light_color":"#E2EDFF","light_type":"point_light"},"minecraft:redstone_torch":{"light_color":"#FF462D","light_type":"point_light"},
 "minecraft:candle":{"light_color":"#FFD7A2","light_type":"point_light"},"minecraft:sea_pickle":{"light_color":"#B9FFD1","light_type":"point_light"}
}

for name,c in PRESETS.items():
    base=Path('subpacks')/name
    dump(base/'atmospherics/atmospherics.json',atmosphere())
    dump(base/'atmospherics/nether.json',atmosphere('dlavie:nether_atmospherics','nether'))
    dump(base/'atmospherics/end.json',atmosphere('dlavie:end_atmospherics','end'))
    dump(base/'lighting/global.json',lighting(c))
    dump(base/'lighting/nether.json',lighting(c,'dlavie:nether_lighting','nether'))
    dump(base/'lighting/end.json',lighting(c,'dlavie:end_lighting','end'))
    dump(base/'color_grading/color_grading.json',grading(c))
    dump(base/'color_grading/nether.json',grading(c,'dlavie:nether_color_grading','nether'))
    dump(base/'color_grading/end.json',grading(c,'dlavie:end_color_grading','end'))
    dump(base/'pbr/global.json',pbr(c))
    dump(base/'water/water.json',water(c))
    dump(base/'fogs/dlavie_overworld.json',fog(c))
    dump(base/'fogs/dlavie_nether.json',fog(c,'dlavie:nether_fog','nether'))
    dump(base/'fogs/dlavie_end.json',fog(c,'dlavie:end_fog','end'))
    dump(base/'local_lighting/local_lighting.json',{"format_version":"1.21.120","minecraft:local_light_settings":LIGHTS})
    dump(base/'shadows/global.json',{"format_version":"1.21.80","minecraft:shadow_settings":{"shadow_style":c['shadow_style'],"texel_size":c['shadow_texel_size']}})

colors=BIOME_CFG['water_colors']
for b in BIOME_CFG['biomes']:
    dump(Path('biomes')/(b+'.client_biome.json'),{"format_version":"1.21.130","minecraft:client_biome":{"description":{"identifier":b},"components":{"minecraft:fog_appearance":{"fog_identifier":"dlavie:overworld_fog"},"minecraft:water_appearance":{"surface_color":colors.get(b,'#44AFF5'),"surface_opacity":0.93},"minecraft:atmosphere_identifier":{"atmosphere_identifier":"dlavie:default_atmospherics"},"minecraft:color_grading_identifier":{"color_grading_identifier":"dlavie:default_color_grading"},"minecraft:lighting_identifier":{"lighting_identifier":"dlavie:default_lighting"},"minecraft:water_identifier":{"water_identifier":"dlavie:default_water"}}}})
for b in ['hell','crimson_forest','warped_forest','soulsand_valley','basalt_deltas']:
    dump(Path('biomes')/(b+'.client_biome.json'),{"format_version":"1.21.130","minecraft:client_biome":{"description":{"identifier":b},"components":{"minecraft:fog_appearance":{"fog_identifier":"dlavie:nether_fog"},"minecraft:atmosphere_identifier":{"atmosphere_identifier":"dlavie:nether_atmospherics"},"minecraft:color_grading_identifier":{"color_grading_identifier":"dlavie:nether_color_grading"},"minecraft:lighting_identifier":{"lighting_identifier":"dlavie:nether_lighting"}}}})
for b in ['the_end']:
    dump(Path('biomes')/(b+'.client_biome.json'),{"format_version":"1.21.130","minecraft:client_biome":{"description":{"identifier":b},"components":{"minecraft:fog_appearance":{"fog_identifier":"dlavie:end_fog"},"minecraft:atmosphere_identifier":{"atmosphere_identifier":"dlavie:end_atmospherics"},"minecraft:color_grading_identifier":{"color_grading_identifier":"dlavie:end_color_grading"},"minecraft:lighting_identifier":{"lighting_identifier":"dlavie:end_lighting"}}}})
print(f"Generated {len(PRESETS)} presets, {len(BIOME_CFG['biomes'])} Overworld + 6 Nether/End biome bindings")
