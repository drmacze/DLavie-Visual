#!/usr/bin/env python3
"""Generate DLavie Visual 2.3 runtime environment assets. No AI image generation."""
from pathlib import Path
import math
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance
ROOT=Path(__file__).resolve().parents[1]

# Pack icon: simple procedural DL mark.
im=Image.new('RGBA',(512,512),(8,17,31,255)); d=ImageDraw.Draw(im,'RGBA')
d.ellipse((38,42,474,478),fill=(33,126,180,24)); d.ellipse((250,36,500,286),fill=(255,174,88,25))
d.rounded_rectangle((102,94,180,418),20,fill=(232,246,252,245)); d.ellipse((135,94,416,418),fill=(232,246,252,245)); d.ellipse((203,165,349,348),fill=(9,26,47,255))
im.save(ROOT/'pack_icon.png',optimize=True)

# Canonical Bedrock environment texture sizes are deliberately used here for maximum compatibility.
env=ROOT/'textures'/'environment'; env.mkdir(parents=True,exist_ok=True)

# --- Sun: small crisp disc plus soft corona so it does not look like a giant square sprite. ---
sz=32; sun=Image.new('RGBA',(sz,sz),(0,0,0,0)); px=sun.load(); c=(sz-1)/2
for y in range(sz):
    for x in range(sz):
        r=math.hypot(x-c,y-c)
        disc=max(0.0,min(1.0,(6.4-r)*2.4))
        halo=max(0.0,min(1.0,(13.2-r)/7.0))**2.2
        a=int(255*max(disc,halo*0.28))
        if a:
            t=min(1,r/13.2); px[x,y]=(255,int(247-20*t),int(205-48*t),a)
sun.save(env/'sun.png',optimize=True)

# --- Moon phases: 8 x 32px tiles in the canonical 128x64 atlas. ---
tile=32; moon=Image.new('RGBA',(128,64),(0,0,0,0)); mp=moon.load(); cc=(tile-1)/2
for phase in range(8):
    ox=(phase%4)*tile; oy=(phase//4)*tile; term=math.cos(phase/8*math.tau)*0.78
    for y in range(tile):
        for x in range(tile):
            dx=(x-cc)/(tile*.5); dy=(y-cc)/(tile*.5); rr=math.hypot(dx,dy)
            if rr>1: continue
            lit=(dx>=term) if phase<4 else (dx<=term)
            edge=max(0,min(1,(1.01-rr)*15)); a=int(255*edge*(1 if lit else .12)); val=int(212+18*(1-rr))
            mp[ox+x,oy+y]=(val,min(255,val+7),255,a)
moon.save(env/'moon_phases.png',optimize=True)

# --- Cirrus cloud field: thin diagonal filaments like Derivative's CIRRUS_CLOUDS=2 target. ---
S=256; base=Image.new('L',(S,S),0); bp=base.load()
for y in range(S):
    v=y/S
    for x in range(S):
        u=x/S
        # Long anisotropic waves plus smaller warped bands. Tiling-safe periodic functions only.
        f1=math.sin((u*2.0+v*0.18)*math.tau + 0.8*math.sin(v*2.0*math.tau))
        f2=math.sin((u*4.5-v*0.32)*math.tau + 1.1*math.sin((u+v)*1.5*math.tau))
        f3=math.sin((u*9.0+v*0.55)*math.tau + 0.55*math.sin(v*5.0*math.tau))
        f4=math.sin((u*17.0-v*1.1)*math.tau)
        ridge=max(0,1-abs(f1)*1.75)**2.4 + .58*max(0,1-abs(f2)*2.1)**3 + .28*max(0,1-abs(f3)*2.4)**3.2 + .10*max(0,1-abs(f4)*2.7)**4
        # Large gaps keep the sky readable.
        mask=.58+.42*math.sin((u*.75+v*.45)*math.tau)
        bp[x,y]=int(max(0,min(255,255*ridge*mask*.54)))
base=base.filter(ImageFilter.GaussianBlur(1.15))
# Horizontal stretch produces shader-like cirrus streaks rather than vanilla puffs.
stretched=base.resize((512,128),Image.Resampling.BICUBIC).resize((256,256),Image.Resampling.BICUBIC)
stretched=ImageEnhance.Contrast(stretched).enhance(1.28)
cloud=Image.new('RGBA',(S,S),(239,244,248,0)); cloud.putalpha(stretched.point(lambda a:max(0,min(150,int(a*.78)))))
cloud.save(env/'clouds.png',optimize=True)

# --- Rain: fine long streaks with low opacity. 64x256 canonical texture. ---
rain=Image.new('RGBA',(64,256),(0,0,0,0)); rd=ImageDraw.Draw(rain,'RGBA')
for i in range(28):
    x=(i*23+7)%64; y=(i*71+13)%256; length=36+(i*17)%82; alpha=48+(i*19)%55
    rd.line((x,y,x-3,(y+length)%256),fill=(188,211,224,alpha),width=1)
    if y+length>=256: rd.line((x,y-256,x-3,y+length-256),fill=(188,211,224,alpha),width=1)
rain=rain.filter(ImageFilter.GaussianBlur(.35)); rain.save(env/'rain.png',optimize=True)

# --- Snow: restrained flakes so VV fog remains the visual focus. ---
snow=Image.new('RGBA',(64,256),(0,0,0,0)); sd=ImageDraw.Draw(snow,'RGBA')
for i in range(42):
    x=(i*37+5)%64; y=(i*53+19)%256; r=1+(i%3==0); a=75+(i*13)%85
    sd.ellipse((x-r,y-r,x+r,y+r),fill=(238,247,255,a))
snow=snow.filter(ImageFilter.GaussianBlur(.22)); snow.save(env/'snow.png',optimize=True)

# --- Derivative 60-frame caustics atlas. Prefer exact supplied source. ---
W=128; FRAMES=60
source_candidates=[
    ROOT/'third_party_runtime'/'Derivative_Caustics.png',
    ROOT.parent/'derivative_src'/'shaders'/'texture'/'water'/'Caustics.png',
]
source=next((p for p in source_candidates if p.is_file()),None)
if source:
    # Preserve the original Derivative PNG byte-for-byte when available; no resampling or re-encoding.
    caustics=None
else:
    # Deterministic fallback only for CI if source asset is absent.
    caustics=Image.new('RGBA',(W,W*FRAMES),(0,0,0,0))
    for frame in range(FRAMES):
        ph=frame/FRAMES*math.tau; fr=Image.new('L',(W,W),0); fp=fr.load()
        for y in range(W):
            yy=y/W*math.tau
            for x in range(W):
                xx=x/W*math.tau
                a=math.sin(xx*2.2+.7*math.sin(yy*1.6+ph)+ph)
                b=math.sin(yy*2.7+.65*math.sin(xx*1.8-ph)-ph*1.1)
                q=max(0,1-abs(a+b)*1.6)**4
                fp[x,y]=int(10+115*q)
        fr=fr.filter(ImageFilter.GaussianBlur(.45)); rgba=Image.new('RGBA',(W,W),(255,244,218,0)); rgba.putalpha(fr)
        caustics.paste(rgba,(0,frame*W))
dst=ROOT/'textures'/'dlavie'; dst.mkdir(parents=True,exist_ok=True)
if source:
    (dst/'derivative_caustics.png').write_bytes(source.read_bytes())
else:
    caustics.save(dst/'derivative_caustics.png',optimize=True)
(ROOT/'textures'/'textures_list.json').write_text('[\n  "textures/dlavie/derivative_caustics"\n]\n',encoding='utf-8')

# Mirror environment assets into each selectable subpack so Bedrock resolves them regardless of overlay order.
for pre in ('low','medium','high'):
    pe=ROOT/'subpacks'/pre/'textures'/'environment'; pe.mkdir(parents=True,exist_ok=True)
    for n in ('sun.png','moon_phases.png','clouds.png','rain.png','snow.png'):
        (pe/n).write_bytes((env/n).read_bytes())
print('Generated DLavie Visual 2.3 environment: cirrus, round sun, rain/snow, Derivative caustics')
