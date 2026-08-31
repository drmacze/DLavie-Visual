#!/usr/bin/env python3
"""DLavie Visual 4.3 weather + advanced water pass.

Visual-only: no block textures, no per-block Texture Sets, no gameplay changes.
Uses official Vibrant Visuals weather fog/media and water controls.
"""
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
THEMES = ("natural", "cozy", "gloomy")
QUALITIES = ("low", "medium", "high")
PROFILES = ("default", "forest", "dense", "dry", "cold", "swamp", "cave", "ocean")
Q = {"low": 0, "medium": 1, "high": 2}

WATER_MEDIA = {
    "default": dict(sc=[0.020,0.052,0.070], ab=[0.155,0.060,0.033], color="#277E96", end=24.0, g=.74),
    "forest":  dict(sc=[0.022,0.058,0.070], ab=[0.170,0.065,0.038], color="#2A7887", end=22.0, g=.76),
    "dense":   dict(sc=[0.024,0.062,0.066], ab=[0.195,0.074,0.044], color="#2C727A", end=19.0, g=.77),
    "dry":     dict(sc=[0.018,0.049,0.068], ab=[0.140,0.050,0.030], color="#287D9B", end=27.0, g=.73),
    "cold":    dict(sc=[0.017,0.048,0.074], ab=[0.125,0.047,0.027], color="#397F99", end=31.0, g=.75),
    "swamp":   dict(sc=[0.040,0.072,0.050], ab=[0.260,0.095,0.075], color="#4D7059", end=12.0, g=.68),
    "cave":    dict(sc=[0.025,0.047,0.059], ab=[0.205,0.088,0.058], color="#31596A", end=16.0, g=.62),
    "ocean":   dict(sc=[0.016,0.045,0.075], ab=[0.115,0.040,0.022], color="#1C6B8D", end=36.0, g=.80),
}

WEATHER = {
    "default": dict(fog=.020, start=.50, cloud_sc=[.045,.052,.060], cloud_ab=[.0032,.0035,.0040]),
    "forest":  dict(fog=.025, start=.44, cloud_sc=[.050,.059,.064], cloud_ab=[.0036,.0038,.0042]),
    "dense":   dict(fog=.031, start=.38, cloud_sc=[.057,.066,.069], cloud_ab=[.0043,.0046,.0050]),
    "dry":     dict(fog=.014, start=.58, cloud_sc=[.038,.043,.050], cloud_ab=[.0026,.0028,.0032]),
    "cold":    dict(fog=.024, start=.43, cloud_sc=[.048,.055,.066], cloud_ab=[.0036,.0038,.0044]),
    "swamp":   dict(fog=.038, start=.30, cloud_sc=[.062,.072,.062], cloud_ab=[.0050,.0054,.0052]),
    "cave":    dict(fog=.000, start=.74, cloud_sc=[.018,.021,.027], cloud_ab=[.0010,.0011,.0013]),
    "ocean":   dict(fog=.022, start=.47, cloud_sc=[.047,.056,.069], cloud_ab=[.0034,.0037,.0043]),
}

WATER_KIND = {
    "default": dict(ch=.10, sed=.018, cdom=.034, freq=.020, depth=.48, shape=3.7, pull=.22, mix=.60, color=.48),
    "river":   dict(ch=.16, sed=.038, cdom=.070, freq=.016, depth=.38, shape=4.0, pull=.20, mix=.65, color=.61),
    "ocean":   dict(ch=.045,sed=.008, cdom=.012, freq=.024, depth=.62, shape=3.25,pull=.25, mix=.54, color=.54),
    "swamp":   dict(ch=.72, sed=.21,  cdom=.62,  freq=.011, depth=.23, shape=4.5, pull=.15, mix=.73, color=.76),
    "frozen":  dict(ch=.025,sed=.004, cdom=.008, freq=.013, depth=.27, shape=4.15,pull=.15, mix=.69, color=.63),
}

def load(p):
    return json.loads(p.read_text(encoding="utf-8"))

def save(p, o):
    p.write_text(json.dumps(o, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

def profile_name(p):
    return p.stem if p.stem in PROFILES else "default"

def patch_fog(path, theme, quality):
    o = load(path)
    fg = o.get("minecraft:fog_settings")
    if not fg: return
    stem = path.stem
    name = profile_name(path)
    wi = WATER_MEDIA[name]
    wa = WEATHER[name]
    qr = Q[quality]
    theme_weather = {"natural":1.00,"cozy":.96,"gloomy":1.22}[theme]
    quality_weather = [0.78,1.00,1.14][qr]
    weather_density = 0.0 if stem in ("cave","nether","end") else wa["fog"] * theme_weather * quality_weather
    vol = fg.setdefault("volumetric", {})
    density = vol.setdefault("density", {})

    # The weather density channel is only evaluated during active rain/snow.
    if weather_density > 0:
        air = density.get("air", {})
        zero_h = float(air.get("zero_density_height", 172.0)) + 26.0
        max_h = float(air.get("max_density_height", 52.0)) + 8.0
        density["weather"] = {
            "max_density": round(min(.060, weather_density), 6),
            "zero_density_height": round(zero_h, 2),
            "max_density_height": round(max_h, 2),
        }
    else:
        density.pop("weather", None)

    # Depth absorption / underwater medium. High gets stronger forward scattering shafts.
    water_density = density.setdefault("water", {"max_density": .22, "uniform": True})
    water_density["max_density"] = round(min(.55, float(water_density.get("max_density",.22))*[.92,1.00,1.06][qr]), 6)
    water_density["uniform"] = True

    media = vol.setdefault("media_coefficients", {})
    media["water"] = {"scattering": wi["sc"], "absorption": wi["ab"]}
    cloud_mul = {"natural":1.0,"cozy":1.05,"gloomy":1.18}[theme] * [.86,1.0,1.10][qr]
    cloud_abs_mul = {"natural":1.0,"cozy":1.08,"gloomy":1.30}[theme]
    media["cloud"] = {
        "scattering": [round(x*cloud_mul, 6) for x in wa["cloud_sc"]],
        "absorption": [round(x*cloud_abs_mul, 6) for x in wa["cloud_ab"]],
    }

    hg = vol.setdefault("henyey_greenstein_g", {})
    hg.setdefault("air", {"henyey_greenstein_g": .78})
    water_g = max(-.98, min(.98, wi["g"] + [-.06, 0.0, .05][qr]))
    hg["water"] = {"henyey_greenstein_g": round(water_g, 4)}

    # Smooth underwater entry + depth fade avoids an instant flat-color snap while diving.
    distance = fg.setdefault("distance", {})
    end = wi["end"] * [0.82, 1.0, 1.16][qr]
    distance["water"] = {
        "fog_start": 0.0,
        "fog_end": round(end,2),
        "fog_color": wi["color"],
        "render_distance_type": "fixed",
        "transition_fog": {
            "init_fog": {"fog_start":0.0,"fog_end":0.35,"fog_color":wi["color"],"render_distance_type":"fixed"},
            "min_percent": 0.18,
            "mid_seconds": 2.2,
            "mid_percent": 0.54,
            "max_seconds": 8.0,
        },
    }
    if weather_density > 0:
        base_color = {"natural":"#98A9B4","cozy":"#A89F92","gloomy":"#74828D"}[theme]
        distance["weather"] = {
            "fog_start": round(max(.18, wa["start"] - [.02,.04,.07][qr]), 3),
            "fog_end": .94,
            "fog_color": base_color,
            "render_distance_type": "render",
        }
    else:
        distance.pop("weather", None)
    save(path, o)

def patch_water(path, theme, quality):
    o=load(path); ws=o.get("minecraft:water_settings")
    if not ws:return
    kind=path.stem if path.stem in WATER_KIND else "default"
    p=WATER_KIND[kind]; qr=Q[quality]
    ws["particle_concentrations"]={
        "chlorophyll":p["ch"],"suspended_sediment":p["sed"],"cdom":p["cdom"]
    }
    waves=ws.setdefault("waves",{})
    waves.update({
        "enabled":True,
        "frequency":round(p["freq"]*[1.08,1.0,.94][qr],5),
        "octaves":[6,12,18][qr],
        "depth":round(p["depth"]*[.78,1.0,1.12][qr],4),
        "speed":[1.00,1.12,1.20][qr],
        "shape":p["shape"],"pull":p["pull"],"mix":p["mix"],
        "frequency_scaling":[.58,.60,.62][qr],
        "speed_scaling":[.16,.19,.22][qr],
        "direction_increment":71.0,
    })
    ws["biome_water_color_contribution"]=p["color"]
    # Low keeps caustics at power 1 rather than disabling them entirely; quality scales cost/intensity.
    ca=ws.setdefault("caustics",{})
    ca.update({
        "enabled":True,
        "texture":"textures/dlavie/optical_caustics",
        "frame_length":[.058,.048,.041][qr],
        "scale": [0.72,0.60,0.52][qr] if kind!="swamp" else [0.86,0.74,0.66][qr],
        "power": [1,2,3][qr] if theme!="gloomy" else [1,2,2][qr],
    })
    save(path,o)

def patch_atmosphere(path, theme, quality):
    # Cloud optical media is handled in fog JSON. Restrain clear-sky glare in Gloomy so storms
    # read darker rather than simply blooming brighter.
    o=load(path); at=o.get("minecraft:atmosphere_settings")
    if not at:return
    if theme=="gloomy" and isinstance(at.get("sun_glare_shape"),dict):
        at["sun_glare_shape"]={k:round(float(v)*[.96,.92,.88][Q[quality]],5) for k,v in at["sun_glare_shape"].items()}
    save(path,o)

def main():
    fogs=waters=0
    for theme in THEMES:
        for quality in QUALITIES:
            root=ROOT/'subpacks'/f'{theme}_{quality}'
            if not root.is_dir(): raise SystemExit(f'missing subpack {root.name}')
            for p in (root/'fogs').glob('*.json'):
                patch_fog(p,theme,quality); fogs+=1
            for p in (root/'water').glob('*.json'):
                patch_water(p,theme,quality); waters+=1
            for p in (root/'atmospherics').glob('*.json'):
                patch_atmosphere(p,theme,quality)
    print(f'Enhanced interactive weather/water: {fogs} fog profiles, {waters} water profiles; no block materials generated')

if __name__=='__main__': main()
