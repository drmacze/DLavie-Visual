#!/usr/bin/env python3
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]
THEMES=('natural','cozy','gloomy'); QUALITIES=('low','medium','high')
# zero_height, max_height, weather_mult, air_g, water_g, haze_start, rain_start, haze_color, rain_color
P={
'default':(158,48,2.15,.79,.62,.92,.52,'#B8C7D3','#A9B8C4'),
'forest':(172,52,2.35,.82,.62,.89,.47,'#A8BAAF','#9EAEA4'),
'dense':(184,54,2.55,.84,.63,.85,.40,'#879C8F','#819387'),
'dry':(142,46,1.55,.72,.60,.95,.60,'#C9BEA8','#B8AE9C'),
'cold':(168,58,2.45,.77,.61,.91,.46,'#BFCBD6','#AEBBC7'),
'swamp':(178,46,2.85,.86,.66,.82,.34,'#7E9482','#748979'),
'cave':(None,None,1,.48,.58,.74,.74,'#465565','#465565'),
'ocean':(148,42,2.25,.81,.68,.93,.50,'#A9BFCE','#97ADBC'),
'nether':(None,None,1,.70,.58,.72,.72,'#5B1E16','#5B1E16'),
'end':(None,None,1,.78,.60,.80,.80,'#413C62','#413C62')}
ABS={
'default':[.00035,.00045,.00065],'forest':[.00040,.00048,.00062],'dense':[.00048,.00054,.00065],
'dry':[.00055,.00050,.00042],'cold':[.00030,.00038,.00058],'swamp':[.00070,.00072,.00066],
'cave':[.001,.0011,.0013],'ocean':[.00028,.00038,.00058],'nether':[.018,.016,.015],'end':[.005,.005,.008]}
CLOUD={
'default':[.035,.040,.047],'forest':[.037,.044,.049],'dense':[.040,.048,.052],'dry':[.030,.031,.032],
'cold':[.034,.041,.052],'swamp':[.043,.052,.043],'cave':[.018,.021,.027],'ocean':[.034,.041,.050],
'nether':[.040,.018,.011],'end':[.025,.022,.038]}
def load(p):return json.loads(p.read_text())
def save(p,o):p.write_text(json.dumps(o,indent=2,ensure_ascii=False)+'\n')
def patch(path,theme,quality):
 o=load(path); fg=o.get('minecraft:fog_settings');
 if not fg:return
 kind=path.stem if path.stem in P else 'default'; z,mh,wm,ag,wg,hs,rs,hc,rc=P[kind]; qi={'low':0,'medium':1,'high':2}[quality]
 o['format_version']='1.21.90'; vol=fg.setdefault('volumetric',{}); den=vol.setdefault('density',{}); air=den.setdefault('air',{'max_density':.006})
 cur=max(.0001,float(air.get('max_density',.006))); cap=.045 if kind in ('nether','end') else .036; cur=min(cap,cur*[.92,1,1.06][qi])
 if z is None: air.clear(); air.update({'max_density':round(cur,6),'uniform':True})
 else: air.pop('uniform',None); air.update({'max_density':round(cur,6),'zero_density_height':float(z),'max_density_height':float(mh)})
 if kind not in ('nether','end','cave'):
  tf={'natural':1,'cozy':1.05,'gloomy':1.20}[theme]; den['weather']={'max_density':round(min(.048,cur*wm*tf),6),'zero_density_height':float(z+28),'max_density_height':float(mh+8)}
 else: den.pop('weather',None)
 water=den.setdefault('water',{'max_density':.22,'uniform':True}); water['uniform']=True; water['max_density']=round(min(.58,max(.08,float(water.get('max_density',.22)))),6)
 media=vol.setdefault('media_coefficients',{}); am=media.setdefault('air',{}); sf=[.92,1,1.07][qi]
 if isinstance(am.get('scattering'),list): am['scattering']=[round(min(.09,max(0,float(x)*sf)),7) for x in am['scattering'][:3]]
 am['absorption']=ABS[kind]
 cf={'natural':1,'cozy':1.04,'gloomy':1.12}[theme]; media['cloud']={'scattering':[round(min(.1,x*cf),7) for x in CLOUD[kind]],'absorption':[.001,.0011,.0013]}
 wmda=media.setdefault('water',{}); wmda.setdefault('scattering',[.028,.064,.080]); wmda.setdefault('absorption',[.36,.13,.075])
 gq=[-.015,0,.018][qi]; gt={'natural':0,'cozy':.012,'gloomy':.022}[theme]; hg=vol.setdefault('henyey_greenstein_g',{}); hg['air']={'henyey_greenstein_g':round(min(.92,ag+gq+gt),4)}; hg['water']={'henyey_greenstein_g':wg}
 dist=fg.setdefault('distance',{}); dist['air']={'fog_start':hs,'fog_end':1.0,'fog_color':hc,'render_distance_type':'render'}
 if kind not in ('nether','end','cave'): dist['weather']={'fog_start':rs,'fog_end':.95,'fog_color':rc,'render_distance_type':'render'}
 else: dist.pop('weather',None)
 save(path,o)
def main():
 n=0
 for t in THEMES:
  for q in QUALITIES:
   d=ROOT/'subpacks'/f'{t}_{q}'/'fogs'
   if not d.is_dir():raise SystemExit(f'missing {d}')
   for p in d.glob('*.json'):patch(p,t,q);n+=1
 print(f'Enhanced volumetric fog realism: {n} profiles')
if __name__=='__main__':main()