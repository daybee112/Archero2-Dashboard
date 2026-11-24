import sys, numpy as np
from PIL import Image, ImageDraw
from match import shape_boxes, classify, desc, refs
def slot_types(boxes, W):
    cx=lambda b:(b[0]+b[2])/2/W; cy=lambda b:(b[1]+b[3])/2
    t={}
    mid=[b for b in boxes if 0.3<=cx(b)<=0.7]
    mid_sorted=sorted(mid,key=cy)
    for b in boxes:
        if cx(b)<0.3: t[b]="enhancement"
        elif cx(b)>0.7: t[b]="ability"
    for b in mid_sorted[-3:]: t[b]="etched"
    for b in mid_sorted[:-3]: t[b]="blessing"
    return t
def read(path, lo_frac=0.07, hi_frac=0.12):
    a=np.asarray(Image.open(path).convert("RGB")); W=a.shape[1]
    boxes=shape_boxes(a,int(lo_frac*W),int(hi_frac*W))
    boxes=sorted(boxes,key=lambda b:(b[1]+b[3])/2)[-13:]
    # keep the 13 rune boxes: those in the lower part with similar size
    tt=slot_types(boxes,W); out=[]
    for b in boxes:
        sc=[x for x in classify(a,b) if x[3]==tt[b]]
        top=sc[0]; nxt=next((x for x in sc if x[2]!=top[2]),(0,0,"",""))
        ok=(top[0]>=0.6 and top[0]-nxt[0]>=0.02) or (top[0]>=0.45 and top[0]-nxt[0]>=0.08)
        out.append((b,tt[b],top[2] if ok else "?"+top[2],top[0],nxt[2],nxt[0]))
    return a,out
if __name__=="__main__":
    rows=[]
    for path in sys.argv[1:]:
        a,out=read(path); print(path, len(out))
        for b,t,n,s,n2,s2 in out: print(f"   {t:11s} {n:20s} {s:.2f}  next {n2} {s2:.2f}")
        rows.append((a,out))
    # check sheet: target crop | best ref
    refimg={r["name"]:Image.open(r["file"]).convert("RGB").resize((90,90)) for r in refs}
    H=sum(len(o) for _,o in rows); sh=Image.new("RGB",(4*190,((H+3)//4)*100),"white"); d=ImageDraw.Draw(sh); k=0
    for a,out in rows:
        for b,t,n,s,n2,s2 in out:
            x=(k%4)*190; y=(k//4)*100
            sh.paste(Image.fromarray(a[b[1]:b[3],b[0]:b[2]]).resize((90,90)),(x,y)); sh.paste(refimg[n.lstrip('?')],(x+92,y))
            d.text((x+2,y+88),f"{n[:16]} {s:.2f}",fill="black"); k+=1
    sh.save("check.png")
