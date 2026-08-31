#!/usr/bin/env python3
"""Regenerate deterministic DLavie Visual binary art/environment assets."""
from pathlib import Path
import math
from PIL import Image, ImageDraw, ImageFont, ImageFilter
ROOT=Path(__file__).resolve().parents[1]
PRESETS={"low":64,"medium":128,"high":256}
SAT={"low":1.03,"medium":1.08,"high":1.12}
def font(size,bold=False):
    choices=["/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf","/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf"]
    for p in choices:
        if Path(p).exists(): return ImageFont.truetype(p,size)
    return ImageFont.load_default()
def gradient(size):
    w,h=size; im=Image.new("RGB",size); px=im.load()
    for y in range(h):
        t=y/max(1,h-1)
        for x in range(w): px[x,y]=(7+int(17*(1-t))+int(10*x/w),15+int(24*(1-t))+int(8*x/w),28+int(45*(1-t))+int(28*x/w))
    return im
def mark(im,box):
    d=ImageDraw.Draw(im,"RGBA"); x0,y0,x1,y1=box; w=x1-x0; h=y1-y0
    mask=Image.new("L",im.size,0); md=ImageDraw.Draw(mask)
    md.rounded_rectangle((x0+int(.10*w),y0+int(.06*h),x0+int(.29*w),y1-int(.06*h)),radius=int(.04*w),fill=255)
    md.ellipse((x0+int(.16*w),y0+int(.06*h),x1-int(.05*w),y1-int(.06*h)),fill=255); md.ellipse((x0+int(.33*w),y0+int(.24*h),x1-int(.23*w),y1-int(.24*h)),fill=0)
    g=Image.new("RGBA",im.size,(0,0,0,0)); gp=g.load()
    for yy in range(max(0,y0),min(im.height,y1)):
        t=(yy-y0)/max(1,h); c=(int(47+207*t),int(224-56*t),int(255-137*t),255)
        for xx in range(max(0,x0),min(im.width,x1)): gp[xx,yy]=c
    im.alpha_composite(Image.composite(g,Image.new("RGBA",im.size,(0,0,0,0)),mask))
# icon
im=gradient((512,512)).convert("RGBA"); glow=Image.new("RGBA",im.size,(0,0,0,0)); ImageDraw.Draw(glow).ellipse((60,70,470,480),fill=(43,182,255,75)); im.alpha_composite(glow.filter(ImageFilter.GaussianBlur(70))); mark(im,(86,46,435,468)); im.save(ROOT/"pack_icon.png",optimize=True)
# cover
cover=gradient((1280,720)).convert("RGBA"); d=ImageDraw.Draw(cover,"RGBA"); d.rectangle((0,420,1280,720),fill=(7,39,65,255))
rays=Image.new("RGBA",cover.size,(0,0,0,0)); rd=ImageDraw.Draw(rays,"RGBA")
for i in range(18):
    x=70+i*72; rd.polygon([(x,0),(x+45,0),(x+260,720),(x+180,720)],fill=(70,190,255,7+i%3*3))
cover.alpha_composite(rays.filter(ImageFilter.GaussianBlur(3)))
g=Image.new("RGBA",cover.size,(0,0,0,0)); ImageDraw.Draw(g).ellipse((940,80,1190,330),fill=(255,171,73,120)); cover.alpha_composite(g.filter(ImageFilter.GaussianBlur(70))); d=ImageDraw.Draw(cover,"RGBA"); d.polygon([(0,490),(170,350),(315,480),(460,315),(650,482),(820,360),(1010,480),(1160,330),(1280,450),(1280,720),(0,720)],fill=(8,22,34,255))
for y in range(500,710,17): d.line((650-(y-500),y,1260,y),fill=(80,207,255,max(12,80-(y-500)//4)),width=2)
mark(cover,(75,115,355,545)); d=ImageDraw.Draw(cover,"RGBA"); d.text((390,180),"DLavie",font=font(105,True),fill=(245,250,255,255)); d.text((397,292),"VISUAL",font=font(64,True),fill=(94,215,255,255),stroke_width=1,stroke_fill=(20,80,110,255)); d.text((400,382),"VIBRANT VISUALS  •  PBR  •  MOBILE TUNED",font=font(28,True),fill=(232,238,245,220)); d.text((400,438),"Low  /  Medium  /  High",font=font(25),fill=(194,212,228,220)); (ROOT/"branding").mkdir(exist_ok=True); cover.convert("RGB").save(ROOT/"branding/cover.jpg",quality=88,optimize=True,progressive=True)
for name,size in PRESETS.items():
    base=ROOT/"subpacks"/name/"textures"/"environment"; base.mkdir(parents=True,exist_ok=True)
    cloud=Image.new("RGBA",(size,size),(0,0,0,0)); cp=cloud.load()
    for y in range(size):
        for x in range(size):
            u=x/size; v=y/size; n=(math.sin(u*11.3+math.sin(v*8.1))*.28+math.sin(v*15.7+u*4.3)*.24+math.sin((u+v)*29)*.12+.5); h=math.sin((x*12.9898+y*78.233+size*2.1))*43758.5453; detail=h-math.floor(h); dens=max(0,min(1,n*.74+detail*.26-.18)); a=int((120 if name=="low" else 165 if name=="medium" else 195)*(dens**1.75)); cp[x,y]=(232,241,250,a)
    cloud.filter(ImageFilter.GaussianBlur(.45 if name=="high" else .7)).save(base/"clouds.png",optimize=True)
    sun=Image.new("RGBA",(size,size),(0,0,0,0)); sp=sun.load(); c=(size-1)/2
    for y in range(size):
        for x in range(size):
            q=math.hypot(x-c,y-c)/(size*.5); sp[x,y]=(255,230,165,int(255*max(0,min(1,(1.02-q)*8))))
    sun.save(base/"sun.png",optimize=True)
    atlas=Image.new("RGBA",(size*4,size*2),(0,0,0,0)); ap=atlas.load()
    for py in range(2):
        for pxidx in range(4):
            phase=py*4+pxidx
            for y in range(size):
                for x in range(size):
                    dx=(x-c)/(size*.5); dy=(y-c)/(size*.5); r=math.hypot(dx,dy)
                    if r>1: continue
                    limb=math.cos(phase/8*math.tau)*.78; lit=(dx>=limb) if phase<4 else (dx<=limb); val=max(145,min(245,int(215+math.sin((x*7+y*13+phase*19)*.33)*7))); a=int(255*max(0,min(1,(1.01-r)*12))); ap[pxidx*size+x,py*size+y]=(val,val+4,min(255,val+16),a if lit else int(a*.18))
    atlas.save(base/"moon_phases.png",optimize=True)
    cb=ROOT/"subpacks"/name/"textures"/"colormap"; cb.mkdir(parents=True,exist_ok=True)
    for kind in ("grass","foliage"):
        cm=Image.new("RGBA",(size,size)); pp=cm.load()
        for y in range(size):
            for x in range(size):
                heat=x/max(1,size-1); rain=1-y/max(1,size-1)
                col=(int(42+56*heat),int(105+75*rain*SAT[name]),int(42+48*rain),255) if kind=="grass" else (int(34+40*heat),int(88+90*rain*SAT[name]),int(38+54*rain),255)
                pp[x,y]=tuple(max(0,min(255,v)) for v in col)
        cm.save(cb/(kind+".png"),optimize=True)
print("Generated DLavie Visual assets")
