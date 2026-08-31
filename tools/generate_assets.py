#!/usr/bin/env python3
"""Generate deterministic DLavie Visual runtime assets. The cover is hand-authored SVG."""
from pathlib import Path
import math
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance

ROOT = Path(__file__).resolve().parents[1]
PRESETS = {"low": 128, "medium": 256, "high": 512}


def gradient(size):
    w, h = size
    im = Image.new("RGB", size)
    p = im.load()
    for y in range(h):
        t = y / max(1, h - 1)
        for x in range(w):
            p[x, y] = (int(8 + 15 * (1 - t)), int(18 + 28 * (1 - t)), int(34 + 48 * (1 - t)))
    return im


# Pack icon: procedural/vector-like mark. No AI image generation.
im = gradient((512, 512)).convert("RGBA")
d = ImageDraw.Draw(im, "RGBA")
d.ellipse((74, 64, 438, 428), fill=(58, 187, 255, 24))
d.rounded_rectangle((106, 96, 184, 418), 24, fill=(225, 245, 255, 240))
d.ellipse((136, 96, 418, 418), fill=(225, 245, 255, 240))
d.ellipse((202, 166, 347, 348), fill=(11, 28, 52, 255))
d.ellipse((278, 40, 470, 232), fill=(255, 183, 101, 32))
im = im.filter(ImageFilter.GaussianBlur(0.25))
im.save(ROOT / "pack_icon.png", optimize=True)


# Derivative Profile.Derivative uses planar CIRRUS_CLOUDS=2 and disables volumetric clouds.
# Build a deterministic wispy planar density field instead of shipping unusable Java 3D cloud LUT/noise data.
BASE = 512
seed = Image.new("L", (BASE, BASE))
sp = seed.load()
for y in range(BASE):
    v = y / BASE
    for x in range(BASE):
        u = x / BASE
        broad = (
            math.sin(u * math.tau * 3.2 + math.sin(v * math.tau * 2.1) * 1.7)
            + 0.62 * math.sin((u * 5.7 + v * 1.3) * math.tau)
            + 0.37 * math.sin((u * 11.4 - v * 3.8) * math.tau + 1.9)
            + 0.21 * math.sin((u * 23.1 + v * 7.2) * math.tau)
        )
        streak = 0.5 + 0.5 * math.sin((u * 7.0 + 0.13 * math.sin(v * math.tau * 4.0)) * math.tau)
        value = 112 + broad * 34 + streak * 24
        sp[x, y] = max(0, min(255, int(value)))
seed = seed.filter(ImageFilter.GaussianBlur(2.4))

for name, size in PRESETS.items():
    env = ROOT / "subpacks" / name / "textures" / "environment"
    env.mkdir(parents=True, exist_ok=True)
    src = seed.resize((size, size), Image.Resampling.LANCZOS)
    src = ImageEnhance.Contrast(src).enhance(1.55 if name == "low" else 1.8)
    streak = src.resize((size * 2, max(1, size // 3)), Image.Resampling.BICUBIC).resize((size, size), Image.Resampling.BICUBIC)
    streak = streak.filter(ImageFilter.GaussianBlur(max(0.6, size / 180)))
    mask = Image.blend(src, streak, 0.72)
    mask = mask.point(lambda v: max(0, min(178, int((v - 100) * 1.78))))
    cloud = Image.new("RGBA", (size, size), (239, 246, 252, 0))
    cloud.putalpha(mask)
    cloud.save(env / "clouds.png", optimize=True)

    # Sun disc + soft corona. Shafts are created by Mie scattering + volumetric fog configs.
    sun = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    px = sun.load()
    c = (size - 1) / 2
    for y in range(size):
        for x in range(size):
            q = math.hypot(x - c, y - c) / (size * 0.5)
            disc = max(0.0, min(1.0, (0.44 - q) * 34.0))
            corona = max(0.0, min(1.0, (0.74 - q) / 0.30)) ** 2.2
            alpha = int(255 * max(disc, corona * 0.28))
            warm = max(0.0, min(1.0, q / 0.74))
            px[x, y] = (255, int(244 - 18*warm), int(205 - 42*warm), alpha)
    sun.save(env / "sun.png", optimize=True)

    moon = Image.new("RGBA", (size * 4, size * 2), (0, 0, 0, 0))
    mp = moon.load()
    for py in range(2):
        for pxi in range(4):
            phase = py * 4 + pxi
            for y in range(size):
                for x in range(size):
                    dx = (x - c) / (size * 0.5)
                    dy = (y - c) / (size * 0.5)
                    rr = math.hypot(dx, dy)
                    if rr > 1:
                        continue
                    terminator = math.cos(phase / 8 * math.tau) * 0.78
                    lit = (dx >= terminator) if phase < 4 else (dx <= terminator)
                    val = int(212 + 16 * (1 - rr))
                    aa = int(255 * max(0, min(1, (1.01 - rr) * 14)))
                    mp[pxi * size + x, py * size + y] = (val, min(255, val + 7), 255, aa if lit else int(aa * 0.14))
    moon.save(env / "moon_phases.png", optimize=True)

    # No grass/foliage colormap override: preserve natural colors from vanilla or the user's texture pack.


# Bedrock custom caustics are a vertical strip of square frames. Derivative ships 60 frames at 128px.
# Prefer the exact/converted Derivative atlas from the supplied source when available locally.
# CI/repository builds fall back to a deterministic low-contrast reconstruction with identical 128x60 layout.
W = 128
FRAMES = 60
source_candidates = [
    ROOT.parent / "derivative_src" / "shaders" / "texture" / "water" / "Caustics.png",
    ROOT / "third_party_runtime" / "Derivative_Caustics.png",
]
source = next((x for x in source_candidates if x.is_file()), None)
if source:
    caustics = Image.open(source).convert("RGBA")
else:
    caustics = Image.new("RGBA", (W, W * FRAMES), (0,0,0,0))
    for frame in range(FRAMES):
        phase = frame / FRAMES * math.tau
        fr = Image.new("L", (W, W), 0); fp=fr.load()
        for y in range(W):
            yy=y/W*math.tau
            for x in range(W):
                xx=x/W*math.tau
                a=math.sin(xx*2.4+0.70*math.sin(yy*1.7+phase)+phase)
                b=math.sin(yy*2.8+0.64*math.sin(xx*1.9-phase)-phase*1.1)
                c=math.sin((xx+yy)*1.65+0.52*math.sin(xx*3.5-yy*2.6+phase*.7))
                ridge=max(0.0,1.0-abs(a+b)*1.55)**4.0 + 0.55*max(0.0,1.0-abs(b+c*.7)*1.8)**4.6
                fp[x,y]=int(min(112, 8+92*min(1.0,ridge)))
        fr=fr.filter(ImageFilter.GaussianBlur(.55))
        rgba=Image.new("RGBA",(W,W),(255,238,208,0)); rgba.putalpha(fr.point(lambda v:max(4,min(72,int(v*.58)))))
        caustics.paste(rgba,(0,frame*W))
tex = ROOT / "textures"; tex.mkdir(exist_ok=True)
dst = tex / "dlavie"; dst.mkdir(parents=True, exist_ok=True)
caustics.save(dst / "derivative_caustics.png", optimize=True)
(tex / "textures_list.json").write_text('[\n  "textures/dlavie/derivative_caustics"\n]\n', encoding="utf-8")

# Environment textures are also written at pack root. Some Bedrock render paths resolve
# these canonical locations directly even when visual JSON comes from a subpack.
root_env = ROOT / "textures" / "environment"; root_env.mkdir(parents=True, exist_ok=True)
hi = ROOT / "subpacks" / "high" / "textures" / "environment"
for name in ("clouds.png","sun.png","moon_phases.png"):
    (root_env/name).write_bytes((hi/name).read_bytes())
print("Generated DLavie Visual runtime assets (60-frame caustics + Derivative-profile cirrus)")
