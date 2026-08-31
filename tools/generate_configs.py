#!/usr/bin/env python3
"""Generate DLavie Visual Vibrant Visuals JSON and biome bindings."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]
PRESETS=json.loads((ROOT/'config/presets.json').read_text(encoding='utf-8'))
BIOME_CFG=json.loads((ROOT/'config/biomes.json').read_text(encoding='utf-8'))

def dump(path,obj):
    p=ROOT/path; p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(obj,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')

def atmosphere(name):
    boost={'low':0,'medium':8,'high':15}[name]
    return {"format_version":"1.21.40","minecraft:atmosphere_settings":{
      "description":{"identifier":"dlavie:default_atmospherics"},
      "sky_zenith_color":{"0.000000":[82,132+boost//3,194+boost//3],"0.199685":[82,132+boost//3,194+boost//3],"0.352560":[10,15,30],"0.644880":[10,15,30],"0.800315":[82,132+boost//3,194+boost//3]},
      "sky_horizon_color":{"0.000000":[173,191,218],"0.167053":[181,195,218],"0.217114":[255,180-min(boost,10),126],"0.239274":[255,144,101],"0.276382":[130,94,111],"0.361464":[73,79,134],"0.401799":[43,70,111],"0.616996":[43,70,111],"0.654508":[96,91,151],"0.706861":[222,166,194],"0.748744":[255,176,114],"0.786432":[238,201,163],"0.830049":[173,191,218]},
      "rayleigh_strength":{"0.000000":8.5,"0.138743":8.5,"0.250000":4.5,"0.330402":4.0,"0.640704":4.0,"0.717412":4.5,"0.929310":8.5,"1.000000":8.5},
      "sun_mie_strength":{"0.000000":0.0,"0.200000":0.0,"0.250000":0.9,"0.400000":0.0,"0.600000":0.0,"0.750000":0.9,"0.800000":0.0,"1.000000":0.0},
      "moon_mie_strength":{"0.000000":0.03,"1.000000":0.03},
      "sun_glare_shape":{"0.000000":0.0,"0.200000":0.0,"0.250000":0.065,"0.400000":0.0,"0.600000":0.0,"0.750000":0.055,"0.800000":0.0,"1.000000":0.0},
      "horizon_blend_stops":{"min":{"0.000000":0.0,"1.000000":0.0},"start":{"0.000000":0.78,"0.250000":0.48,"0.300912":0.24,"0.750000":0.24,"0.827004":0.48,"1.000000":0.78},"mie_start":{"0.000000":0.52,"0.100000":0.52,"0.200000":1.0,"0.800000":1.0,"0.900000":0.52,"1.000000":0.52},"max":{"0.000000":0.27,"1.000000":0.27}}
    }}

def lighting(c):
    s=c['sun_illuminance']; m=c['moon_illuminance']
    return {"format_version":"1.21.80","minecraft:lighting_settings":{
      "description":{"identifier":"dlavie:default_lighting"},
      "directional_lights":{"orbital":{"sun":{"illuminance":{"0.000000":s,"0.050000":s,"0.313846":0.0,"0.684230":0.0,"0.950000":s,"1.000000":s},"color":{"0.000000":[255,205,145],"0.140811":[255,178,106],"0.216944":[255,145,88],"0.269504":[255,131,67],"0.506998":[255,210,174],"0.717949":[255,144,128],"0.801062":[255,178,106],"1.000000":[255,205,145]}},"moon":{"illuminance":{"0.000000":0.0,"0.200000":0.0,"0.225000":m,"0.735000":m,"0.750000":0.0,"1.000000":0.0},"color":{"0.000000":[164,190,255],"1.000000":[164,190,255]}},"orbital_offset_degrees":0.0},"flash":{"illuminance":12.0,"color":[225,235,255]}},
      "emissive":{"desaturation":0.02},"ambient":{"color":"#EAF2FF","illuminance":c['ambient_illuminance']},"sky":{"intensity":1.0}
    }}

def grading(c):
    v=c['contrast']; s=c['saturation']
    return {"format_version":"1.21.90","minecraft:color_grading_settings":{"description":{"identifier":"dlavie:default_color_grading"},"color_grading":{"midtones":{"contrast":[v,v,v],"gain":[1,1,1],"gamma":[2.2,2.2,2.2],"offset":[0,0,0],"saturation":[s,s,s]},"temperature":{"enabled":True,"temperature":c['temperature'],"type":"color_temperature"}},"tone_mapping":{"operator":"generic"}}}

def pbr(c):
    r=c['roughness']; ar=c['actor_roughness']
    return {"format_version":"1.21.40","minecraft:pbr_fallback_settings":{"blocks":{"global_metalness_emissive_roughness_subsurface":[0,0,r,0]},"actors":{"global_metalness_emissive_roughness_subsurface":[0,0,ar,0]},"particles":{"global_metalness_emissive_roughness_subsurface":[0,0,235,0]},"items":{"global_metalness_emissive_roughness_subsurface":[0,0,min(230,r+20),0]}}}

def water(c):
    return {"format_version":"1.26.20","minecraft:water_settings":{"description":{"identifier":"dlavie:default_water"},"particle_concentrations":{"chlorophyll":0.08,"suspended_sediment":0.05,"cdom":0.10},"caustics":{"enabled":c['caustics'],"frame_length":0.075 if c['caustics'] else 0.1,"scale":0.48,"power":c['caustics_power']},"waves":{"enabled":True,"frequency":1.0,"octaves":c['water_octaves'],"depth":c['wave_depth'],"direction_increment":80.0,"sampleWidth":0.012 if c['water_octaves']<=8 else 0.01,"speed":c['water_speed'],"shape":1.45,"pull":0.36,"mix":0.20,"frequency_scaling":1.2,"speed_scaling":1.03},"biome_water_color_contribution":0.18}}

def fog(c):
    return {"format_version":"1.16.100","minecraft:fog_settings":{"description":{"identifier":"dlavie:overworld_fog"},"volumetric":{"density":{"water":{"max_density":c['water_fog_density'],"uniform":True},"air":{"max_density":c['fog_density'],"zero_density_height":190.0,"max_density_height":46.0}},"media_coefficients":{"water":{"scattering":[0.014,0.023,0.032],"absorption":[0.12,0.065,0.05]},"air":{"scattering":[0.018,0.020,0.024],"absorption":[0,0,0]}}}}}

POINTS={
 'low':{"minecraft:torch":[245,178,94],"minecraft:lantern":[255,166,75],"minecraft:soul_torch":[75,208,255],"minecraft:soul_lantern":[75,208,255],"minecraft:end_rod":[220,235,255],"minecraft:redstone_torch":[255,65,35]},
 'medium':{"minecraft:torch":[250,183,92],"minecraft:lantern":[255,162,70],"minecraft:soul_torch":[70,205,255],"minecraft:soul_lantern":[70,205,255],"minecraft:end_rod":[222,238,255],"minecraft:redstone_torch":[255,55,30],"minecraft:candle":[255,205,132],"minecraft:white_candle":[255,208,138],"minecraft:orange_candle":[255,184,91],"minecraft:yellow_candle":[255,218,118],"minecraft:blue_candle":[116,156,255],"minecraft:cyan_candle":[84,213,238],"minecraft:red_candle":[255,103,76]},
}
POINTS['high']={"minecraft:torch":[252,184,90],"minecraft:lantern":[255,158,66],"minecraft:soul_torch":[64,210,255],"minecraft:soul_lantern":[64,210,255],"minecraft:end_rod":[226,240,255],"minecraft:redstone_torch":[255,50,28],"minecraft:candle":[255,204,130]}
for x in ['white','gray','light_gray','black','brown','red','orange','yellow','lime','green','cyan','light_blue','blue','purple','magenta','pink']:
    POINTS['high'][f'minecraft:{x}_candle']=[255,200,125]

for name,c in PRESETS.items():
    base=Path('subpacks')/name
    dump(base/'atmospherics/atmospherics.json',atmosphere(name))
    dump(base/'lighting/global.json',lighting(c))
    dump(base/'color_grading/color_grading.json',grading(c))
    dump(base/'pbr/global.json',pbr(c))
    dump(base/'water/water.json',water(c))
    dump(base/'fogs/dlavie_overworld.json',fog(c))
    dump(base/'point_lights/global.json',{"format_version":"1.21.40","minecraft:point_light_settings":{"colors":POINTS[name]}})
    dump(base/'shadows/shadows.json',{"format_version":"1.21.80","minecraft:shadow_settings":{"shadow_style":c['shadow_style'],"texel_size":c['shadow_texel_size']}})

colors=BIOME_CFG['water_colors']
for b in BIOME_CFG['biomes']:
    dump(Path('biomes')/(b+'.client_biome.json'),{"format_version":"1.21.120","minecraft:client_biome":{"description":{"identifier":b},"components":{"minecraft:fog_appearance":{"fog_identifier":"dlavie:overworld_fog"},"minecraft:water_appearance":{"surface_color":colors.get(b,'#44AFF5')},"minecraft:atmosphere_identifier":{"atmosphere_identifier":"dlavie:default_atmospherics"},"minecraft:color_grading_identifier":{"color_grading_identifier":"dlavie:default_color_grading"},"minecraft:lighting_identifier":{"lighting_identifier":"dlavie:default_lighting"},"minecraft:water_identifier":{"water_identifier":"dlavie:default_water"}}}})
print(f"Generated configs for {len(PRESETS)} presets and {len(BIOME_CFG['biomes'])} biomes")
