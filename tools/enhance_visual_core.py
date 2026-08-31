#!/usr/bin/env python3
"""DLavie Visual 4.1 visual-only post pass.

This file intentionally edits only renderer configuration generated into subpacks.
It never creates block albedo/normal/AO/MERS textures.
"""
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
THEMES = ("natural", "cozy", "gloomy")
QUALITIES = ("low", "medium", "high")

def load(p):
    return json.loads(p.read_text(encoding="utf-8"))

def save(p, obj):
    p.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

def mul_map(v, fac, floor=None):
    if isinstance(v, dict):
        out = {k: round(float(x) * fac, 6) for k, x in v.items()}
        if floor is not None:
            out = {k: max(floor, x) for k, x in out.items()}
        return out
    if isinstance(v, (int, float)):
        x = float(v) * fac
        return max(floor, x) if floor is not None else x
    return v

def tint(c, m):
    if not isinstance(c, list) or len(c) < 3:
        return c
    return [max(0, min(255, round(float(c[i]) * m[i]))) for i in range(3)]

def tint_map(v, m):
    if isinstance(v, dict):
        return {k: tint(x, m) for k, x in v.items()}
    return tint(v, m)

def patch_lighting(path, theme, quality):
    o = load(path); ls = o.get("minecraft:lighting_settings")
    if not ls: return
    qr = {"low":0, "medium":1, "high":2}[quality]
    sun = ls.get("directional_lights",{}).get("orbital",{}).get("sun",{})
    moon = ls.get("directional_lights",{}).get("orbital",{}).get("moon",{})
    amb = ls.get("ambient",{}); sky = ls.get("sky",{})
    amb_fac = {"natural":[0.94,0.88,0.82],"cozy":[0.92,0.84,0.77],"gloomy":[0.78,0.68,0.58]}[theme][qr]
    sky_fac = {"natural":[0.98,0.91,0.84],"cozy":[0.94,0.86,0.78],"gloomy":[0.82,0.70,0.60]}[theme][qr]
    amb["illuminance"] = mul_map(amb.get("illuminance"), amb_fac)
    sky["intensity"] = mul_map(sky.get("intensity"), sky_fac, 0.08)
    if isinstance(sun.get("color"), dict):
        tm = {"natural":(1.0,0.99,0.97), "cozy":(1.0,0.91,0.76), "gloomy":(0.90,0.96,1.02)}[theme]
        sun["color"] = tint_map(sun["color"], tm)
    if isinstance(moon.get("color"), dict):
        mm = {"natural":(0.94,0.99,1.05), "cozy":(0.92,0.96,1.03), "gloomy":(0.82,0.94,1.12)}[theme]
        moon["color"] = tint_map(moon["color"], mm)
    ls.setdefault("emissive", {})["desaturation"] = {"natural":0.025,"cozy":0.015,"gloomy":0.04}[theme]
    save(path, o)

def patch_atmosphere(path, theme, quality):
    o=load(path); at=o.get("minecraft:atmosphere_settings")
    if not at:return
    qr={"low":0,"medium":1,"high":2}[quality]
    mie_fac={"natural":[1.05,1.16,1.28],"cozy":[1.12,1.28,1.44],"gloomy":[1.16,1.34,1.52]}[theme][qr]
    glare_fac={"natural":[1.00,1.10,1.20],"cozy":[1.04,1.16,1.28],"gloomy":[1.02,1.12,1.22]}[theme][qr]
    if isinstance(at.get("sun_mie_strength"),dict):
        at["sun_mie_strength"]={k:round(min(2.35,float(v)*mie_fac),5) for k,v in at["sun_mie_strength"].items()}
    if isinstance(at.get("sun_glare_shape"),dict):
        at["sun_glare_shape"]={k:round(min(0.155,float(v)*glare_fac),5) for k,v in at["sun_glare_shape"].items()}
    if isinstance(at.get("moon_mie_strength"),dict):
        mf={"natural":1.0,"cozy":0.92,"gloomy":1.18}[theme]
        at["moon_mie_strength"]={k:round(float(v)*mf,5) for k,v in at["moon_mie_strength"].items()}
    save(path,o)

def patch_grading(path, theme, quality):
    o=load(path); cg=o.get("minecraft:color_grading_settings")
    if not cg:return
    c=cg.get("color_grading",{})
    qr={"low":0,"medium":1,"high":2}[quality]
    c["tone_mapping"] = {"enabled": True, "type": "aces"}
    c.setdefault("temperature", {"enabled":True,"type":"white_balance"})["temperature"]={"natural":6600,"cozy":5650,"gloomy":7900}[theme]
    sat_fac={"natural":[0.99,1.00,1.01],"cozy":[1.01,1.03,1.04],"gloomy":[0.86,0.82,0.78]}[theme][qr]
    con_fac={"natural":[1.00,1.03,1.06],"cozy":[1.01,1.05,1.09],"gloomy":[1.04,1.09,1.14]}[theme][qr]
    for band in ("shadows","midtones","highlights"):
        b=c.get(band)
        if not isinstance(b,dict):continue
        if isinstance(b.get("saturation"),list): b["saturation"]=[round(float(x)*sat_fac,4) for x in b["saturation"]]
        if isinstance(b.get("contrast"),list): b["contrast"]=[round(float(x)*con_fac,4) for x in b["contrast"]]
    save(path,o)

def patch_fog(path, theme, quality):
    o=load(path); fg=o.get("minecraft:fog_settings")
    if not fg:return
    qr={"low":0,"medium":1,"high":2}[quality]
    vol=fg.get("volumetric",{}); air=vol.get("density",{}).get("air")
    fac={"natural":[0.90,1.00,1.08],"cozy":[0.98,1.10,1.20],"gloomy":[1.12,1.34,1.58]}[theme][qr]
    if isinstance(air,dict) and "max_density" in air:
        air["max_density"]=round(float(air["max_density"])*fac,6)
    media=vol.get("media_coefficients",{}).get("air")
    if isinstance(media,dict) and isinstance(media.get("scattering"),list):
        tm={"natural":(0.98,1.00,1.03),"cozy":(1.12,1.02,0.88),"gloomy":(0.76,0.91,1.20)}[theme]
        media["scattering"]=[round(float(media["scattering"][i])*tm[i],7) for i in range(3)]
    save(path,o)

def patch_water(path, theme, quality):
    o=load(path); ws=o.get("minecraft:water_settings")
    if not ws:return
    qr={"low":0,"medium":1,"high":2}[quality]
    waves=ws.setdefault("waves",{})
    waves["octaves"]={"low":6,"medium":12,"high":18}[quality]
    waves["frequency"]={"low":0.028,"medium":0.022,"high":0.018}[quality]
    waves["speed"]={"low":1.05,"medium":1.16,"high":1.24}[quality]
    ca=ws.setdefault("caustics",{})
    if ca.get("enabled"):
        ca["texture"]="textures/dlavie/optical_caustics"
        ca["frame_length"]={"low":0.060,"medium":0.050,"high":0.043}[quality]
        ca["power"]={"natural":[1.15,1.70,2.25],"cozy":[1.20,1.80,2.40],"gloomy":[0.95,1.45,1.90]}[theme][qr]
    save(path,o)

def patch_local_lights(path, theme, quality):
    o=load(path); ll=o.get("minecraft:local_light_settings")
    if not ll:return
    for name,v in ll.items():
        if quality=="high": v["light_type"]="point_light"
        elif quality=="medium" and name in ("minecraft:torch","minecraft:lantern","minecraft:glowstone","minecraft:sea_lantern","minecraft:shroomlight","minecraft:redstone_lamp","minecraft:campfire","minecraft:soul_lantern","minecraft:soul_torch"):
            v["light_type"]="point_light"
        if theme=="cozy" and "soul" not in name and name not in ("minecraft:sea_lantern","minecraft:end_rod"):
            v["light_color"]="#FFAA62"
        elif theme=="gloomy" and "soul" not in name and name not in ("minecraft:sea_lantern","minecraft:end_rod"):
            v["light_color"]="#D99B7D"
    save(path,o)

def main():
    touched=0
    for theme in THEMES:
        for quality in QUALITIES:
            root=ROOT/'subpacks'/f'{theme}_{quality}'
            if not root.is_dir(): raise SystemExit(f'missing subpack {root.name}')
            for p in (root/'lighting').glob('*.json'): patch_lighting(p,theme,quality); touched+=1
            for p in (root/'atmospherics').glob('*.json'): patch_atmosphere(p,theme,quality); touched+=1
            for p in (root/'color_grading').glob('*.json'): patch_grading(p,theme,quality); touched+=1
            for p in (root/'fogs').glob('*.json'): patch_fog(p,theme,quality); touched+=1
            for p in (root/'water').glob('*.json'): patch_water(p,theme,quality); touched+=1
            p=root/'local_lighting'/'local_lighting.json'
            if p.is_file(): patch_local_lights(p,theme,quality); touched+=1
    print(f'Enhanced shader visual core: {touched} renderer configs; zero block textures generated')

if __name__=='__main__': main()
