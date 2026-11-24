import json, sys, numpy as np
from PIL import Image
from scipy import ndimage as ndi
N=40
def masks(a):
    R,G,B=a[...,0].astype(int),a[...,1].astype(int),a[...,2].astype(int)
    mx=np.maximum(np.maximum(R,G),B); mn=np.minimum(np.minimum(R,G),B)
    white=(mn>205)&(mx-mn<60)
    # rune body: warm saturated (orange/red/gold) or purple/magenta
    sat=(mx-mn)/np.maximum(mx,1)
    body=(sat>0.62)&(mx>150)
    return white, body
def shape_boxes(a, min_side, max_side):
    white, body=masks(a)
    m=ndi.binary_closing(body, iterations=3); m=ndi.binary_fill_holes(m)
    lab,n=ndi.label(m); out=[]
    for i,sl in enumerate(ndi.find_objects(lab),1):
        h=sl[0].stop-sl[0].start; w=sl[1].stop-sl[1].start
        if not(min_side<=h<=max_side and min_side<=w<=max_side): continue
        if not(0.75<=w/h<=1.33): continue
        reg=lab[sl]==i
        if reg.mean()<0.45: continue
        wh=white[sl][reg].mean()
        if wh<0.03 or wh>0.5: continue
        out.append((sl[1].start,sl[0].start,sl[1].stop,sl[0].stop))
    return sorted(out,key=lambda b:(b[1]//40,b[0]))
def desc(a, box):
    x0,y0,x1,y1=box; w=x1-x0; h=y1-y0
    cx,cy=(x0+x1)/2,(y0+y1)/2; r=0.36*min(w,h)
    sub=a[int(cy-r):int(cy+r), int(cx-r):int(cx+r)]
    mn=np.min(sub,axis=2).astype(float)
    wv=np.clip((mn-120)/120,0,1)
    g=np.asarray(Image.fromarray((wv*255).astype(np.uint8)).resize((N,N),Image.BILINEAR),dtype=float)/255
    return g
def sil(a, box):
    _,body=masks(a)
    x0,y0,x1,y1=box; m=body[y0:y1,x0:x1]; m=ndi.binary_fill_holes(ndi.binary_closing(m,iterations=2))
    return np.asarray(Image.fromarray((m*255).astype(np.uint8)).resize((24,24),Image.BILINEAR),dtype=float)/255
def ncc(p,q):
    p=p-p.mean(); q=q-q.mean(); d=np.sqrt((p*p).sum()*(q*q).sum()); return float((p*q).sum()/d) if d else 0
def best_shift(p,q):
    best=-1
    for dy in (-2,-1,0,1,2):
        for dx in (-2,-1,0,1,2):
            best=max(best,ncc(np.roll(np.roll(p,dy,0),dx,1),q))
    return best
refs=json.load(open("refs.json"))
for r in refs:
    a=np.asarray(Image.open(r["file"]).convert("RGB"))
    bx=shape_boxes(a,120,230)
    if not bx: print("NO SHAPE", r["name"]); continue
    b=max(bx,key=lambda b:(b[2]-b[0])*(b[3]-b[1])); r["box"]=b; r["d"]=desc(a,b); r["s"]=sil(a,b)
TYPES=["blessing","enhancement","ability","etched"]
def classify(a, box):
    d=desc(a,box); s=sil(a,box)
    sc=[]
    for r in refs:
        if "d" not in r: continue
        sc.append((best_shift(d,r["d"]), ncc(s,r["s"]), r["name"], r["type"]))
    sc.sort(reverse=True)
    return sc
if __name__=="__main__":
    path=sys.argv[1]; lo,hi=int(sys.argv[2]),int(sys.argv[3])
    a=np.asarray(Image.open(path).convert("RGB"))
    for b in shape_boxes(a,lo,hi):
        sc=classify(a,b); top=sc[0]; second=next(x for x in sc if x[2]!=top[2])
        print(b, f"{top[2]:20s} {top[0]:.2f} (next {second[2]} {second[0]:.2f}) shape {top[1]:.2f}")
