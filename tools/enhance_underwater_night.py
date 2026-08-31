#!/usr/bin/env python3
"""DLavie Visual 4.4 underwater + night lighting pass.

Visual-only. No block textures or per-block Texture Sets are generated.
- migrates Overworld lighting files to schema 1.26.0 so ambient/sky keyframes are valid
- adds violet twilight and deep midnight lighting/atmosphere
- strengthens underwater directional scattering, depth absorption and optical caustics
- registers safe ore local-light color/type hooks; actual light strength still comes from block light_emission
"""
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
THEMES = ("natural", "cozy", "gloomy")
QUALITIES = ("low", "medium", "high")
Q = {"low": 0, "medium": 1, "high": 2}

# local_lighting can choose color/type, while actual strength is controlled by block light_emission.
# These entries therefore remain visual-only hooks and do not fake a behavior-pack emission value.
ORE_LIGHTS = {
    "minecraft:coal_ore": "#8AA0B5",
    "minecraft:deepslate_coal_ore": "#8297AB",
    "minecraft:iron_ore": "#FFD2AE",
    "minecraft:deepslate_iron_ore": "#F4C7A7",
    "minecraft:copper_ore": "#E99465",
    "minecraft:deepslate_copper_ore": "#D98760",
    "minecraft:gold_ore": "#FFD45C",
    "minecraft:deepslate_gold_ore": "#F6C84F",
    "minecraft:redstone_ore": "#FF342A",
    "minecraft:deepslate_redstone_ore": "#F72C25",
    "minecraft:lapis_ore": "#527CFF",
    "minecraft:deepslate_lapis_ore": "#4E72E8",
    "minecraft:diamond_ore": "#70F1FF",
    "minecraft:deepslate_diamond_ore": "#68DDE9",
    "minecraft:emerald_ore": "#69FF9C",
    "minecraft:deepslate_emerald_ore": "#62E88E",
    "minecraft:nether_gold_ore": "#FFB94B",
    "minecraft:nether_quartz_ore": "#FFE8D8",
    "minecraft:ancient_debris": "#C77B61",
}

MIDNIGHT = {
    "natural": {
        "zenith": [4, 7, 22], "horizon": [14, 18, 42],
        "twilight_zenith": [45, 40, 91], "twilight_horizon": [122, 78, 139],
        "ambient": [52, 66, 112], "moon": [154, 183, 255],
    },
    "cozy": {
        "zenith": [5, 6, 21], "horizon": [17, 16, 39],
        "twilight_zenith": [61, 37, 91], "twilight_horizon": [145, 76, 129],
        "ambient": [57, 61, 104], "moon": [160, 183, 248],
    },
    "gloomy": {
        "zenith": [1, 3, 13], "horizon": [7, 9, 26],
        "twilight_zenith": [37, 31, 83], "twilight_horizon": [91, 58, 116],
        "ambient": [35, 46, 88], "moon": [127, 166, 245],
    },
}

WATER_PROFILE = {
    "default": {"g": .83, "density": .235, "sc": [0.018,0.052,0.074], "ab": [0.175,0.061,0.031]},
    "forest":  {"g": .84, "density": .245, "sc": [0.020,0.057,0.073], "ab": [0.190,0.067,0.036]},
    "dense":   {"g": .85, "density": .255, "sc": [0.022,0.061,0.070], "ab": [0.215,0.075,0.041]},
    "dry":     {"g": .82, "density": .220, "sc": [0.016,0.049,0.073], "ab": [0.153,0.053,0.029]},
    "cold":    {"g": .84, "density": .205, "sc": [0.015,0.048,0.079], "ab": [0.135,0.049,0.025]},
    "swamp":   {"g": .75, "density": .330, "sc": [0.038,0.074,0.055], "ab": [0.285,0.104,0.076]},
    "cave":    {"g": .68, "density": .285, "sc": [0.025,0.050,0.064], "ab": [0.230,0.094,0.057]},
    "ocean":   {"g": .88, "density": .185, "sc": [0.014,0.044,0.081], "ab": [0.118,0.039,0.020]},
}


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def save(path, obj):
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def set_keys(dst, items):
    if not isinstance(dst, dict):
        return
    for k, v in items.items():
        dst[str(k)] = v


def patch_atmosphere(path, theme, quality):
    if path.stem in ("nether", "end"):
        return
    obj = load(path)
    at = obj.get("minecraft:atmosphere_settings")
    if not at:
        return
    pal = MIDNIGHT[theme]
    qr = Q[quality]
    zen = at.get("sky_zenith_color")
    hor = at.get("sky_horizon_color")
    # Purple transition after sunset, very dark navy at midnight, mirrored before sunrise.
    set_keys(zen, {
        "0.285": pal["twilight_zenith"], "0.315": [max(0,c-9) for c in pal["twilight_zenith"]],
        "0.36": [max(0,int(c*.56)) for c in pal["twilight_zenith"]], "0.50": pal["zenith"],
        "0.64": [max(0,int(c*.56)) for c in pal["twilight_zenith"]], "0.685": [max(0,c-9) for c in pal["twilight_zenith"]],
        "0.715": pal["twilight_zenith"],
    })
    set_keys(hor, {
        "0.285": pal["twilight_horizon"], "0.315": [max(0,int(c*.82)) for c in pal["twilight_horizon"]],
        "0.36": [max(0,int(c*.48)) for c in pal["twilight_horizon"]], "0.50": pal["horizon"],
        "0.64": [max(0,int(c*.48)) for c in pal["twilight_horizon"]], "0.685": [max(0,int(c*.82)) for c in pal["twilight_horizon"]],
        "0.715": pal["twilight_horizon"],
    })
    # Moon haze should remain visible enough to create a faint nocturnal shaft without brightening the whole sky.
    moon = at.get("moon_mie_strength")
    if isinstance(moon, dict):
        base = {"natural":[.30,.42,.54], "cozy":[.27,.38,.48], "gloomy":[.33,.48,.62]}[theme][qr]
        set_keys(moon, {"0.36": round(base*.55,4), "0.42": round(base*.88,4), "0.50": base,
                        "0.58": round(base*.88,4), "0.64": round(base*.55,4)})
    save(path, obj)


def patch_lighting(path, theme, quality):
    if path.stem in ("nether", "end"):
        return
    obj = load(path)
    ls = obj.get("minecraft:lighting_settings")
    if not ls:
        return
    # Ambient/sky keyframes are formally supported in lighting schema 1.26.0.
    obj["format_version"] = "1.26.0"
    qr = Q[quality]
    pal = MIDNIGHT[theme]
    amb = ls.setdefault("ambient", {})
    sky = ls.setdefault("sky", {})
    orbital = ls.setdefault("directional_lights", {}).setdefault("orbital", {})
    moon = orbital.setdefault("moon", {})

    # High intentionally has the darkest midnight; Low keeps a little extra visibility on mobile.
    mid_ambient = {
        "natural":[.0070,.0053,.0040],
        "cozy":[.0074,.0056,.0042],
        "gloomy":[.0052,.0036,.0025],
    }[theme][qr]
    dusk_ambient = mid_ambient * 2.25
    amb_i = amb.get("illuminance")
    if isinstance(amb_i, dict):
        set_keys(amb_i, {
            "0.285": round(dusk_ambient*1.35,6), "0.32": round(dusk_ambient,6),
            "0.38": round(mid_ambient*1.22,6), "0.50": round(mid_ambient,6),
            "0.62": round(mid_ambient*1.22,6), "0.68": round(dusk_ambient,6),
            "0.715": round(dusk_ambient*1.35,6),
        })
    amb_c = amb.get("color")
    if isinstance(amb_c, dict):
        set_keys(amb_c, {
            "0.285": pal["twilight_horizon"], "0.32": pal["twilight_zenith"],
            "0.38": [int(c*.72) for c in pal["ambient"]], "0.50": pal["ambient"],
            "0.62": [int(c*.72) for c in pal["ambient"]], "0.68": pal["twilight_zenith"],
            "0.715": pal["twilight_horizon"],
        })

    sky_i = sky.get("intensity")
    if isinstance(sky_i, dict):
        mid_sky = {
            "natural":[.18,.14,.11], "cozy":[.19,.15,.12], "gloomy":[.14,.11,.10]
        }[theme][qr]
        set_keys(sky_i, {
            "0.285": round(min(.36,mid_sky*2.35),4), "0.34": round(min(.26,mid_sky*1.55),4),
            "0.50": mid_sky, "0.66": round(min(.26,mid_sky*1.55),4),
            "0.715": round(min(.36,mid_sky*2.35),4),
        })

    moon["color"] = {"0.0":pal["moon"], "0.5":pal["moon"], "1.0":pal["moon"]}
    mi = moon.get("illuminance")
    if isinstance(mi, dict):
        # Keep the moon present but not enough to erase the frightening midnight contrast.
        peak = {"natural":[.28,.32,.36], "cozy":[.25,.29,.33], "gloomy":[.22,.26,.30]}[theme][qr]
        set_keys(mi, {"0.35":round(peak*.72,4), "0.42":peak, "0.50":peak, "0.58":peak, "0.65":round(peak*.72,4)})
    save(path, obj)


def patch_fog(path, theme, quality):
    obj = load(path)
    fg = obj.get("minecraft:fog_settings")
    if not fg:
        return
    name = path.stem if path.stem in WATER_PROFILE else "default"
    p = WATER_PROFILE[name]
    qr = Q[quality]
    vol = fg.setdefault("volumetric", {})
    density = vol.setdefault("density", {})
    water = density.setdefault("water", {})
    water["max_density"] = round(min(.56, p["density"] * [.88,1.0,1.08][qr]), 6)
    water["uniform"] = True
    media = vol.setdefault("media_coefficients", {})
    theme_sc = {"natural":1.0,"cozy":1.03,"gloomy":.94}[theme]
    theme_ab = {"natural":1.0,"cozy":1.02,"gloomy":1.08}[theme]
    media["water"] = {
        "scattering": [round(x * theme_sc * [.88,1.0,1.10][qr],6) for x in p["sc"]],
        "absorption": [round(x * theme_ab * [.94,1.0,1.06][qr],6) for x in p["ab"]],
    }
    hg = vol.setdefault("henyey_greenstein_g", {})
    g = min(.94, p["g"] + [-.06,0,.035][qr])
    hg["water"] = {"henyey_greenstein_g": round(g,4)}
    # More visible near-surface shafts on High, while visibility still drops with depth.
    wd = fg.setdefault("distance", {}).get("water")
    if isinstance(wd, dict):
        end = float(wd.get("fog_end", 24.0)) * [.90,1.0,1.08][qr]
        wd["fog_end"] = round(end,2)
        tr = wd.get("transition_fog")
        if isinstance(tr, dict):
            tr["min_percent"] = [0.24,0.18,0.12][qr]
            tr["mid_seconds"] = [1.8,2.2,2.6][qr]
            tr["mid_percent"] = [0.58,0.52,0.46][qr]
            tr["max_seconds"] = [6.0,8.0,10.0][qr]
    save(path, obj)


def patch_water(path, theme, quality):
    obj = load(path)
    ws = obj.get("minecraft:water_settings")
    if not ws:
        return
    qr = Q[quality]
    waves = ws.setdefault("waves", {})
    waves["octaves"] = [7,14,20][qr]
    waves["speed"] = [1.02,1.14,1.22][qr]
    waves["frequency_scaling"] = [.57,.60,.625][qr]
    waves["speed_scaling"] = [.16,.19,.225][qr]
    ca = ws.setdefault("caustics", {})
    ca["enabled"] = True
    ca["texture"] = "textures/dlavie/optical_caustics"
    ca["frame_length"] = [.056,.045,.036][qr]
    ca["scale"] = [.70,.57,.46][qr] if path.stem != "swamp" else [.84,.70,.60][qr]
    base_power = [1,2,4][qr]
    if theme == "gloomy":
        base_power = [1,2,3][qr]
    ca["power"] = base_power
    save(path, obj)


def patch_local_lights(path, quality):
    obj = load(path)
    ll = obj.get("minecraft:local_light_settings")
    if not isinstance(ll, dict):
        return
    # Hook ore colors into the supported local-light map. This does not alter gameplay light levels.
    lt = "point_light" if quality == "high" else "static_light"
    for block, color in ORE_LIGHTS.items():
        ll[block] = {"light_color": color, "light_type": lt}
    save(path, obj)


def main():
    atmos = lights = fogs = waters = ore_maps = 0
    for theme in THEMES:
        for quality in QUALITIES:
            root = ROOT / "subpacks" / f"{theme}_{quality}"
            if not root.is_dir():
                raise SystemExit(f"missing subpack {root.name}")
            for p in (root / "atmospherics").glob("*.json"):
                patch_atmosphere(p, theme, quality); atmos += 1
            for p in (root / "lighting").glob("*.json"):
                patch_lighting(p, theme, quality); lights += 1
            for p in (root / "fogs").glob("*.json"):
                patch_fog(p, theme, quality); fogs += 1
            for p in (root / "water").glob("*.json"):
                patch_water(p, theme, quality); waters += 1
            lp = root / "local_lighting" / "local_lighting.json"
            if lp.is_file():
                patch_local_lights(lp, quality); ore_maps += 1
    print(f"Enhanced underwater/night: {atmos} atmospheres, {lights} lighting files, {fogs} fog profiles, {waters} water profiles, {ore_maps} ore-light hook maps")

if __name__ == "__main__":
    main()
