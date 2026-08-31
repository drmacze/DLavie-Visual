#!/usr/bin/env python3
"""Generate DLavie-owned 128x PBR materials with normal maps and baked AO."""
from pathlib import Path
from PIL import Image, ImageFilter
import numpy as np, json
ROOT=Path(__file__).resolve().parents[1]; D=ROOT/'textures/blocks'; D.mkdir(parents=True,exist_ok=True)
S=128; Y,X=np.mgrid[0:S,0:S]
def clamp(a):return np.clip(a,0,255).astype(np.uint8)
def rng(name):return np.random.default_rng(abs(hash(name))&0xffffffff)
def noise(name,scales=(4,12,28),weights=(.55,.3,.15)):
    r=rng(name); a=np.zeros((S,S),np.float32)
    for sc,w in zip(scales,weights):
        sm=r.random((max(2,S//sc),max(2,S//sc))).astype(np.float32)
        im=Image.fromarray((sm*255).astype(np.uint8)).resize((S,S),Image.Resampling.BICUBIC).filter(ImageFilter.GaussianBlur(max(.5,sc/6)))
        a+=(np.asarray(im,np.float32)/255)*w
    return (a-a.min())/(a.max()-a.min()+1e-6)
def colorize(base,n,c=.25):
    b=np.array(base,np.float32); f=1+(n-.5)*2*c; return np.clip(b[None,None,:]*f[...,None],0,255)
def normal(h,s=3):
    dx=(np.roll(h,-1,1)-np.roll(h,1,1))*.5*s; dy=(np.roll(h,-1,0)-np.roll(h,1,0))*.5*s
    nx=-dx;ny=-dy;nz=np.ones_like(h);l=np.sqrt(nx*nx+ny*ny+nz*nz)+1e-6
    return clamp(np.stack([(nx/l*.5+.5)*255,(ny/l*.5+.5)*255,(nz/l*.5+.5)*255],2))
def ao_map(h):
    im=Image.fromarray(clamp(h*255)); b1=np.asarray(im.filter(ImageFilter.GaussianBlur(2.3)),np.float32)/255; b2=np.asarray(im.filter(ImageFilter.GaussianBlur(7)),np.float32)/255
    cav=np.clip((b1-h)*1.8+(b2-h)*.75,0,1); return np.clip(1-cav*.65,.42,1)
def save(name,rgb,h,rough=190,metal=0,em=0,sub=0,alpha=None,ns=3):
    ao=ao_map(h); hi=np.asarray(rgb,np.float32)*ao[...,None]
    if alpha is None:alpha=np.full((S,S),255,np.uint8)
    rgba=np.dstack([clamp(hi),alpha.astype(np.uint8)]); im=Image.fromarray(rgba,'RGBA')
    low=im.resize((16,16),Image.Resampling.BOX).resize((128,128),Image.Resampling.NEAREST); im=Image.blend(low,im,.12); im.putalpha(low.getchannel('A')); im.save(D/f'{name}.png',optimize=True)
    Image.fromarray(normal(h,ns),'RGB').save(D/f'{name}_normal.png',optimize=True); Image.fromarray(clamp(ao*255),'L').save(D/f'{name}_ao.png',optimize=True)
    rr=np.clip(rough+(noise(name+'mers',(8,22,42),(.55,.3,.15))-.5)*22,0,255).astype(np.uint8); mers=np.zeros((S,S,4),np.uint8); mers[:,:,0]=metal;mers[:,:,1]=em;mers[:,:,2]=rr;mers[:,:,3]=sub
    Image.fromarray(mers,'RGBA').save(D/f'{name}_mers.png',optimize=True)
    o={"format_version":"1.21.30","minecraft:texture_set":{"color":name,"normal":name+"_normal","metalness_emissive_roughness_subsurface":name+"_mers"}}
    (D/f'{name}.texture_set.json').write_text(json.dumps(o,separators=(',',':'))+'\n')
def stone(n,b=(128,128,128),r=205,m=0):
    x=noise(n);sp=noise(n+'sp',(2,5,18),(.45,.35,.2));h=np.clip(.7*x+.3*sp,0,1);save(n,colorize(b,h,.28),h,r,m,ns=3.6)
def cobble(n,b=(120,120,120),moss=False):
    rr=rng(n);cells=np.zeros((S,S),np.float32)
    for _ in range(80):
        cx,cy=rr.integers(0,S,2);rad=rr.integers(7,15);dx=np.minimum(abs(X-cx),S-abs(X-cx));dy=np.minimum(abs(Y-cy),S-abs(Y-cy));cells=np.maximum(cells,np.clip(1-np.sqrt(dx*dx+dy*dy)/rad,0,1)**.55)
    h=np.clip(np.clip(cells*1.25,0,1)*.82+noise(n+'micro')*.18,0,1);rgb=colorize(b,h,.34)
    if moss:
        q=noise(n+'moss')>.62;rgb[q]=rgb[q]*.35+np.array([78,108,54])*.65
    save(n,rgb,h,220,ns=4.5)
def dirt(n,b=(116,82,54),grass=False):
    x=noise(n,(3,9,24),(.5,.3,.2));g=noise(n+'g',(2,4,12),(.5,.35,.15));h=np.clip(x*.65+g*.35,0,1);rgb=colorize(b,h,.38)
    if grass:
        green=colorize((86,135,55),noise(n+'green'),.35);mask=(Y<25)|((Y<36)&(noise(n+'fringe')>.57));rgb[mask]=green[mask];h[mask]=np.clip(h[mask]*.6+.35,0,1)
    save(n,rgb,h,210,ns=3.2)
def grass():
    n='grass_top';x=noise(n,(2,6,17),(.5,.32,.18));h=np.clip(x*.75+.15,0,1);rgb=colorize((82,142,55),x,.36);r=rng(n)
    for _ in range(650):
        xx=int(r.integers(0,S));yy=int(r.integers(0,S));l=int(r.integers(2,7));rgb[max(0,yy-l):yy+1,xx]=np.clip(rgb[max(0,yy-l):yy+1,xx]*np.array([.78,1.08,.72]),0,255);h[max(0,yy-l):yy+1,xx]=np.clip(h[max(0,yy-l):yy+1,xx]+.12,0,1)
    save(n,rgb,h,195,sub=95,ns=3)
def sand(n,b):x=noise(n,(2,5,15),(.55,.3,.15));h=.42+x*.28;save(n,colorize(b,x,.16),h,235,ns=2.2)
def planks(n,b):
    x=noise(n,(2,8,30),(.4,.35,.25));h=.45+x*.3;seam=((Y%32)<2)|((Y%32)>29);h[seam]*=.45;h=np.clip(h+np.sin(X/5.5+noise(n+'warp')*4)*.055,0,1);rgb=colorize(b,h,.34);rgb[seam]*=.62;save(n,rgb,h,180,ns=3.3)
def log_side(n,b):x=noise(n,(3,10,32),(.45,.35,.2));h=np.clip(.35+x*.25+(np.sin(X/3.4+noise(n+'warp')*5)+1)/2*.25,0,1);save(n,colorize(b,h,.42),h,205,ns=4)
def log_top(n,b):rr=np.sqrt((X-63.5)**2+(Y-63.5)**2);h=np.clip(.42+(np.sin(rr*.52+noise(n+'warp')*2)+1)/2*.28+noise(n)*.12,0,1);save(n,colorize(b,h,.3),h,190,ns=3)
def leaves(n,b):
    x=noise(n,(2,5,13),(.55,.3,.15));h=np.clip(.35+x*.55,0,1);alpha=np.full((S,S),255,np.uint8);alpha[noise(n+'holes',(3,7,19),(.55,.3,.15))<.19]=0;save(n,colorize(b,x,.5),h,170,sub=165,alpha=alpha,ns=2.8)
def glass(n,t=(205,235,245),a=54):
    x=noise(n,(16,32,64),(.5,.3,.2));h=.5+(x-.5)*.035;rgb=np.zeros((S,S,3),np.float32)+np.array(t);bd=(X<3)|(X>124)|(Y<3)|(Y>124);rgb[bd]*=.62;h[bd]=.58;al=np.full((S,S),a,np.uint8);al[bd]=110;save(n,rgb,h,26,alpha=al,ns=1.2)
def metal(n,b,r=48,m=245):x=noise(n,(5,17,45),(.5,.3,.2));h=np.clip(.48+(x-.5)*.18,0,1);save(n,colorize(b,x,.12),h,r,m,ns=1.8)
def ore(n,base=(122,122,122),c=(180,180,180),r=190,m=0,e=0):
    x=noise(n+'stone');h=np.clip(.36+x*.34,0,1);rgb=colorize(base,x,.26);v=noise(n+'vein',(3,8,19),(.5,.35,.15));q=v>.67;rgb[q]=np.array(c)*(.82+.25*v[q,None]);h[q]=np.clip(h[q]+.18,0,1);save(n,rgb,h,r,m,e,ns=3.8)
def brick(n,b,mortar):
    h=np.full((S,S),.35,np.float32);rgb=np.zeros((S,S,3),np.float32);rgb[:]=mortar
    for by in range(0,S,24):
        off=0 if (by//24)%2==0 else 18
        for bx in range(-36,S,36):
            x0=max(0,bx+off+2);x1=min(S,bx+off+34);y0=by+2;y1=min(S,by+22)
            if x1>x0:
                q=noise(f'{n}{bx}{by}')[y0:y1,x0:x1];rgb[y0:y1,x0:x1]=colorize(b,q,.2);h[y0:y1,x0:x1]=.62+q*.22
    save(n,rgb,np.clip(h,0,1),205,ns=4.2)
def emit(n,b):x=noise(n,(3,8,22),(.5,.3,.2));h=np.clip(.35+x*.5,0,1);save(n,colorize(b,x,.3),h,120,em=225,ns=2.4)

def main():
    for n,b in {'stone':(126,128,129),'stone_granite':(153,115,101),'stone_diorite':(188,188,184),'stone_andesite':(132,134,133),'bedrock':(82,82,82),'deepslate':(76,77,79),'deepslate_top':(80,81,84),'tuff':(112,116,108),'calcite':(211,209,202),'dripstone_block':(132,95,76),'blackstone':(53,48,57),'basalt_side':(78,78,80),'smooth_basalt':(89,89,91),'end_stone':(218,222,162),'netherrack':(112,48,50),'obsidian':(36,24,51),'prismarine_rough':(99,167,156),'prismarine_dark':(52,94,88)}.items():stone(n,b,220 if n in ('netherrack','tuff') else 198)
    for n,b,m in [('cobblestone',(119,120,116),0),('cobblestone_mossy',(108,116,99),1),('stonebrick',(126,127,124),0),('stonebrick_mossy',(113,122,104),1),('deepslate_bricks',(68,69,72),0),('nether_brick',(75,37,39),0)]:cobble(n,b,m)
    brick('brick',(157,82,65),(108,102,92));brick('mud_bricks',(129,96,75),(102,84,70));dirt('dirt');dirt('coarse_dirt',(106,76,51));dirt('grass_side',grass=True);grass()
    for n,b in [('sand',(216,200,155)),('red_sand',(185,102,61)),('soul_sand',(83,64,55))]:sand(n,b)
    stone('gravel',(132,127,121),235)
    for n,b in [('sandstone_normal',(214,196,145)),('sandstone_top',(221,204,160)),('sandstone_bottom',(205,188,140)),('red_sandstone_normal',(183,96,54)),('red_sandstone_top',(193,107,61))]:stone(n,b,230)
    woods={'oak':(164,128,78),'spruce':(110,81,52),'birch':(196,180,132),'jungle':(163,111,78),'acacia':(181,97,57),'big_oak':(91,67,44),'mangrove':(117,54,50),'cherry':(218,165,164),'bamboo':(191,178,76)}
    for k,c in woods.items():planks('planks_'+k,c)
    for n,c in [('bamboo_planks',woods['bamboo']),('cherry_planks',woods['cherry']),('mangrove_planks',woods['mangrove'])]:planks(n,c)
    logs={'oak':(105,78,47),'spruce':(73,54,37),'birch':(181,176,157),'jungle':(111,76,52),'acacia':(107,92,80),'big_oak':(65,52,39)}
    for k,c in logs.items():log_side('log_'+k,c);log_top('log_'+k+'_top',tuple(min(255,int(x*1.42)) for x in c))
    for k,c in [('mangrove',(88,50,48)),('cherry',(116,77,72))]:log_side(k+'_log_side',c);log_top(k+'_log_top',tuple(min(255,int(x*1.42)) for x in c))
    for k,c in {'oak':(63,116,48),'spruce':(55,91,64),'birch':(86,130,57),'jungle':(52,112,44),'acacia':(78,116,50),'big_oak':(48,92,41),'mangrove':(60,112,58),'cherry':(218,151,177)}.items():leaves('leaves_'+k,c)
    leaves('azalea_leaves',(69,120,53));leaves('azalea_leaves_flowered',(87,126,64));stone('snow',(235,241,244),220);stone('snow_block',(239,244,247),218)
    for n,b in [('ice',(177,214,236)),('packed_ice',(137,183,215)),('blue_ice',(94,160,210))]:metal(n,b,32,0)
    glass('glass')
    for n,t in [('glass_blue',(105,150,220)),('glass_cyan',(100,205,210)),('glass_gray',(145,150,155)),('glass_black',(65,68,73)),('tinted_glass',(92,78,105))]:glass(n,t)
    metal('iron_block',(190,194,193),52,245);metal('gold_block',(241,190,48),40,255);metal('copper_block',(190,109,76),62,235);metal('diamond_block',(92,220,207),48,25);metal('emerald_block',(48,184,92),52,18);metal('lapis_block',(40,72,145),100,5)
    metal('quartz_block_side',(225,221,212),112,0);metal('quartz_block_top',(232,229,220),108,0);metal('quartz_block_bottom',(219,215,207),116,0)
    ore('coal_ore',c=(45,45,48));ore('iron_ore',c=(183,145,112),m=100);ore('gold_ore',c=(235,190,55),m=190);ore('diamond_ore',c=(70,217,211),r=150);ore('emerald_ore',c=(56,206,102));ore('lapis_ore',c=(48,84,179));ore('redstone_ore',c=(209,54,45),e=32)
    for n,c in [('deepslate_coal_ore',(45,45,48)),('deepslate_iron_ore',(183,145,112)),('deepslate_gold_ore',(235,190,55)),('deepslate_diamond_ore',(70,217,211)),('deepslate_redstone_ore',(209,54,45))]:ore(n,(72,73,76),c,180,e=30 if 'redstone' in n else 0)
    for n,c in [('glowstone',(233,177,87)),('shroomlight',(238,145,75)),('redstone_lamp_on',(227,131,62)),('ochre_froglight_side',(230,211,149)),('sea_lantern',(183,226,218)),('verdant_froglight_side',(190,229,177)),('pearlescent_froglight_side',(226,196,226)),('end_rod',(223,226,239))]:emit(n,c)
    print(f'Generated {len(list(D.glob("*.texture_set.json")))} DLavie 128x PBR materials')
if __name__=='__main__':main()
