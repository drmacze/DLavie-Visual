#!/usr/bin/env python3
"""Expand Low/Medium/High into Natural/Cozy/Gloomy x quality subpacks."""
from pathlib import Path
import json, shutil
ROOT=Path(__file__).resolve().parents[1]
THEMES=('natural','cozy','gloomy'); QUALITIES=('low','medium','high')

def adjust(c,m): return [max(0,min(255,round(c[i]*m[i]))) for i in range(3)]
def jwrite(p,o): p.write_text(json.dumps(o,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')

def patch(folder,theme,quality):
    qrank={'low':0,'medium':1,'high':2}[quality]
    for p in folder.rglob('*.json'):
        try:o=json.loads(p.read_text(encoding='utf-8'))
        except: continue
        ls=o.get('minecraft:lighting_settings')
        if ls:
            orbital=ls.get('directional_lights',{}).get('orbital',{})
            sun=orbital.get('sun',{}); illum=sun.get('illuminance')
            if isinstance(illum,dict) and illum:
                mx=max(float(v) for v in illum.values()) or 1
                target={'natural':[88,95,100],'cozy':[84,91,97],'gloomy':[68,75,82]}[theme][qrank]
                sun['illuminance']={k:round(float(v)*target/mx,5) for k,v in illum.items()}
            if isinstance(sun.get('color'),dict):
                mul={'natural':(1,1,1),'cozy':(1,0.94,0.84),'gloomy':(0.86,0.94,1)}[theme]
                sun['color']={k:adjust(v,mul) for k,v in sun['color'].items()}
            amb=ls.get('ambient',{})
            if isinstance(amb.get('color'),dict):
                mul={'natural':(1,1,1),'cozy':(1,0.91,0.80),'gloomy':(0.78,0.88,1)}[theme]
                amb['color']={k:adjust(v,mul) for k,v in amb['color'].items()}
            if isinstance(amb.get('illuminance'),dict):
                fac={'natural':1.0,'cozy':0.88,'gloomy':0.64}[theme]
                amb['illuminance']={k:round(float(v)*fac,6) for k,v in amb['illuminance'].items()}
            sky=ls.get('sky',{}).get('intensity')
            if isinstance(sky,dict):
                fac={'natural':1,'cozy':0.90,'gloomy':0.72}[theme]
                ls['sky']['intensity']={k:max(0.1,round(float(v)*fac,4)) for k,v in sky.items()}
            if p.name=='nether.json' and isinstance(amb,dict):
                if theme=='cozy': amb['color']={'0':[225,98,43],'1':[225,98,43]}
                elif theme=='gloomy': amb['color']={'0':[104,44,58],'1':[104,44,58]}
            if p.name=='end.json' and isinstance(amb,dict):
                if theme=='cozy': amb['color']={'0':[138,109,170],'1':[138,109,170]}
                elif theme=='gloomy': amb['color']={'0':[75,91,138],'1':[75,91,138]}
        at=o.get('minecraft:atmosphere_settings')
        if at:
            if isinstance(at.get('sky_zenith_color'),dict):
                mul={'natural':(1,1,1),'cozy':(1.02,0.95,0.84),'gloomy':(0.78,0.90,1.02)}[theme]
                at['sky_zenith_color']={k:adjust(v,mul) for k,v in at['sky_zenith_color'].items()}
            if isinstance(at.get('sky_horizon_color'),dict):
                mul={'natural':(1,1,1),'cozy':(1.04,0.90,0.76),'gloomy':(0.76,0.86,0.95)}[theme]
                at['sky_horizon_color']={k:adjust(v,mul) for k,v in at['sky_horizon_color'].items()}
            for key,fac in [('rayleigh_strength',{'natural':1,'cozy':0.92,'gloomy':1.18}[theme]),('sun_mie_strength',{'natural':1,'cozy':1.18,'gloomy':1.32}[theme])]:
                if isinstance(at.get(key),dict): at[key]={k:round(float(v)*fac,4) for k,v in at[key].items()}
        cg=o.get('minecraft:color_grading_settings')
        if cg:
            c=cg.get('color_grading',{}); temp={'natural':6500,'cozy':5600,'gloomy':7800}[theme]
            c.setdefault('temperature',{'enabled':True,'type':'white_balance'})['temperature']=temp
            for band in ('shadows','midtones','highlights'):
                b=c.get(band)
                if not isinstance(b,dict): continue
                if isinstance(b.get('saturation'),list):
                    sf={'natural':1,'cozy':1.04,'gloomy':0.78}[theme]; b['saturation']=[round(float(x)*sf,4) for x in b['saturation']]
                if isinstance(b.get('contrast'),list):
                    cf={'natural':1,'cozy':1.03,'gloomy':1.07}[theme]; b['contrast']=[round(float(x)*cf,4) for x in b['contrast']]
                if band=='highlights' and isinstance(b.get('gain'),list):
                    mul={'natural':(1,1,1),'cozy':(1.06,1.01,0.91),'gloomy':(0.91,0.97,1.05)}[theme]
                    b['gain']=[round(float(b['gain'][i])*mul[i],4) for i in range(3)]
        fg=o.get('minecraft:fog_settings')
        if fg:
            vol=fg.get('volumetric',{}); air=vol.get('density',{}).get('air')
            if isinstance(air,dict) and 'max_density' in air: air['max_density']=round(float(air['max_density'])*{'natural':1,'cozy':1.12,'gloomy':1.55}[theme],6)
            media=vol.get('media_coefficients',{}).get('air')
            if isinstance(media,dict) and isinstance(media.get('scattering'),list):
                mul={'natural':(1,1,1),'cozy':(1.15,1.02,0.86),'gloomy':(0.78,0.92,1.18)}[theme]
                media['scattering']=[round(float(media['scattering'][i])*mul[i],6) for i in range(3)]
        ws=o.get('minecraft:water_settings')
        if ws:
            ca=ws.get('caustics',{})
            if ca.get('enabled'):
                ca.update({'texture':'textures/dlavie/optical_caustics','frame_length':0.045,'scale':{'low':0.72,'medium':0.64,'high':0.58}[quality],'power':{'natural':[1.25,1.75,2.25],'cozy':[1.35,1.9,2.45],'gloomy':[1.0,1.45,1.9]}[theme][qrank]})
            w=ws.get('waves',{})
            if w: w.update({'octaves':{'low':6,'medium':11,'high':17}[quality],'frequency':{'low':0.026,'medium':0.022,'high':0.019}[quality]})
        ll=o.get('minecraft:local_light_settings')
        if ll:
            if theme=='cozy':
                warm={'minecraft:torch':'#FFB766','minecraft:lantern':'#FF9D48','minecraft:glowstone':'#FFB66E','minecraft:campfire':'#FF8D38','minecraft:redstone_lamp':'#FF9550','minecraft:candle':'#FFC47A'}
                for k,v in warm.items():
                    if k in ll:ll[k]['light_color']=v
            elif theme=='gloomy':
                for k,v in ll.items():
                    if 'soul' not in k and k not in ('minecraft:end_rod','minecraft:sea_lantern'):v['light_color']='#D89B78'
        jwrite(p,o)
    bdir=folder/'biomes'; bdir.mkdir(exist_ok=True)
    for bp in (ROOT/'biomes').glob('*.client_biome.json'):
        o=json.loads(bp.read_text()); wa=o.get('minecraft:client_biome',{}).get('components',{}).get('minecraft:water_appearance')
        if wa and 'surface_color' in wa:
            h=wa['surface_color'].lstrip('#'); c=tuple(int(h[i:i+2],16) for i in (0,2,4)); mul={'natural':(1,1,1),'cozy':(0.90,1.02,0.96),'gloomy':(0.72,0.91,1.04)}[theme]
            wa['surface_color']='#%02X%02X%02X'%tuple(adjust(c,mul))
        jwrite(bdir/bp.name,o)

def main():
    sub=ROOT/'subpacks'; tmp=ROOT/'_quality_subpacks'
    if tmp.exists():shutil.rmtree(tmp)
    tmp.mkdir()
    for q in QUALITIES:
        src=sub/q
        if not src.is_dir(): raise SystemExit(f'missing generated quality subpack: {src}')
        shutil.move(str(src),str(tmp/q))
    for theme in THEMES:
        for quality in QUALITIES:
            dest=sub/f'{theme}_{quality}'; shutil.copytree(tmp/quality,dest); patch(dest,theme,quality)
    shutil.rmtree(tmp)
    print('Generated 9 visual subpacks: Natural/Cozy/Gloomy x Low/Medium/High')
if __name__=='__main__':main()
