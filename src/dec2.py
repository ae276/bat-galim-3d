def dec(s,scale=0.5):
    out=[]
    for r in s.split('#'):
        pts=[];x=y=0
        for t in r.strip().split(' '):
            if not t: continue
            a,b=t.split(','); x+=int(a); y+=int(b); pts.append((x*scale,y*scale))
        out.append(pts)
    return out
def load_bl():
    return {('304-'+r.split('|')[0]):dec(r.split('|')[1]) for r in open('bl.txt').read().strip().split(';')}
def load_lu():
    o=[]
    for r in open('lu.txt').read().strip().split(';'):
        p=r.split('|'); o.append(dict(pl='304-'+p[0],num=p[1],use=p[2],area=p[3],rings=dec(p[4])))
    return o
