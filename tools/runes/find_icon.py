import sys, numpy as np
from PIL import Image
def find_icon(path):
    a=np.asarray(Image.open(path).convert("RGB")).astype(int)
    H,W,_=a.shape
    R,G,B=a[...,0],a[...,1],a[...,2]
    cream=(R>235)&(G>220)&(B>180)&(B<235)
    # icon tile: gold/orange/red/purple, not cream; check center band vs side band
    notcream=~cream
    cx=W//2
    band=notcream[:, cx-110:cx+110].mean(1)
    side=cream[:, int(W*0.27):int(W*0.33)].mean(1)
    rows=np.where((band>0.9)&(side>0.9))[0]
    if len(rows)==0: return None
    # longest contiguous run
    runs=[];s=rows[0];p=rows[0]
    for r in rows[1:]:
        if r!=p+1: runs.append((s,p)); s=r
        p=r
    runs.append((s,p)); runs=[r for r in runs if r[0]>650 and r[1]-r[0]>=60]; s,e=runs[0]
    # horizontal extent at the run's middle row
    m=(s+e)//2; cols=np.where(notcream[m, int(W*0.3):int(W*0.7)])[0]+int(W*0.3)
    return (int(cols.min()), int(s), int(cols.max()), int(e))
if __name__=="__main__":
    for p in sys.argv[1:]: print(p, find_icon(p))
