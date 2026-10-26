import json
def dec(coords, scale):
    pts=[];x=y=0
    for tok in coords.strip().split(' '):
        if not tok: continue
        dx,dy=tok.split(','); x+=int(dx); y+=int(dy); pts.append((x*scale,y*scale))
    return pts
def load_bld():
    out=[]
    for r in (open('bld.txt',encoding='utf8').read().strip()+';'+open('bld2.txt',encoding='utf8').read().strip()).split(';'):
        if not r.strip(): continue
        p=r.split('|')
        h,l,b,n,a,c=p[0],p[1],p[2],p[3],p[4],'|'.join(p[5:])
        out.append(dict(h=h,l=l,b=b,n=n,a=a,pts=dec(c,0.5)))
    return out
def load_ctx():
    out=[]
    for r in (open('ctx.txt',encoding='utf8').read().strip()+';'+open('ctx2.txt',encoding='utf8').read().strip()).split(';'):
        if not r.strip(): continue
        p=r.split('|'); out.append(dict(k=p[0],n=p[1],pts=dec(p[2],2.0)))
    return out
