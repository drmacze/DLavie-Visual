#!/usr/bin/env python3
"""Generate DLavie optical caustics with offline Snell-law photon tracing."""
from pathlib import Path
from PIL import Image, ImageFilter
import numpy as np, math, json
ROOT=Path(__file__).resolve().parents[1]

def refract(I,N,n1=1.0,n2=1.333):
    eta=n1/n2
    cosi=-(I[0]*N[...,0]+I[1]*N[...,1]+I[2]*N[...,2])
    k=1-eta*eta*(1-cosi*cosi)
    sq=np.sqrt(np.clip(k,0,None))
    T=np.empty_like(N)
    T[...,0]=eta*I[0]+(eta*cosi-sq)*N[...,0]
    T[...,1]=eta*I[1]+(eta*cosi-sq)*N[...,1]
    T[...,2]=eta*I[2]+(eta*cosi-sq)*N[...,2]
    return T

def clamp(a): return np.clip(a,0,255).astype(np.uint8)
def main(frames=60,res=128,photons=320):
    u=(np.arange(photons)+0.5)/photons
    yy,xx=np.meshgrid(u,u,indexing='ij')
    waves=[(1.0,0.17,0.035,1.0),(0.62,0.78,0.022,1.6),(-0.35,0.94,0.014,2.4),(0.88,-0.48,0.009,3.2)]
    I=np.array([0.28,0.08,-0.956],np.float32); I/=np.linalg.norm(I)
    atlas=Image.new('RGB',(res,res*frames))
    for f in range(frames):
        t=f/frames*2*math.pi
        h=np.zeros_like(xx); hx=np.zeros_like(xx); hy=np.zeros_like(xx)
        for dx,dy,a,k in waves:
            phase=2*math.pi*k*(dx*xx+dy*yy)+t*(0.75+0.25*k)
            h += a*np.sin(phase)
            c=a*2*math.pi*k*np.cos(phase)
            hx += c*dx; hy += c*dy
        N=np.stack([-hx,-hy,np.ones_like(h)],2)
        N/=np.linalg.norm(N,axis=2,keepdims=True)+1e-8
        T=refract(I,N)
        s=(-1.7-h)/(T[...,2]-1e-8)
        xhit=(xx+T[...,0]*s)%1.0; yhit=(yy+T[...,1]*s)%1.0
        hist,_,_=np.histogram2d(yhit.ravel(),xhit.ravel(),bins=res,range=[[0,1],[0,1]])
        hmax=max(float(hist.max()),1.0)
        im=Image.fromarray(np.clip(hist/hmax*255,0,255).astype(np.uint8),'L').filter(ImageFilter.GaussianBlur(0.85))
        arr=np.asarray(im,np.float32)/255.0
        lo,hi=np.percentile(arr,[18,99.65])
        arr=np.clip((arr-lo)/(hi-lo+1e-6),0,1)**0.58
        rgb=np.dstack([arr*255,arr*247,arr*222])
        atlas.paste(Image.fromarray(clamp(rgb),'RGB'),(0,f*res))
    p=ROOT/'textures/dlavie/optical_caustics.png'; p.parent.mkdir(parents=True,exist_ok=True); atlas.save(p,optimize=True)
    tl=ROOT/'textures/textures_list.json'
    try:data=json.loads(tl.read_text())
    except: data=[]
    if isinstance(data,dict): data=data.get('texture_data',[]) or []
    if 'textures/dlavie/optical_caustics' not in data:data.append('textures/dlavie/optical_caustics')
    tl.write_text(json.dumps(data,indent=2)+'\n')
    print(f'Generated optical caustics: {p} ({res}x{res*frames}, {frames} frames)')
if __name__=='__main__': main()
