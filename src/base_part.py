import json, math
from decode import *
from shapely.geometry import Polygon, LineString, box, Point, MultiPolygon
from shapely.ops import unary_union
OX,OY=1500,1400
VIEW=box(350,-300,4050,2250)
def R(v): return round(v,1)
def ring(poly):  # shapely polygon -> list of [x,y] relative
    return [[R(x-OX),R(y-OY)] for x,y in list(poly.exterior.coords)[:-1]]
def rect(cx,cy,w,d,ang):
    a=math.radians(ang); c,s=math.cos(a),math.sin(a); pts=[]
    for dx,dy in [(-w/2,-d/2),(w/2,-d/2),(w/2,d/2),(-w/2,d/2)]:
        pts.append((cx+dx*c-dy*s, cy+dx*s+dy*c))
    return pts
def fh(fl, ground=4.5, typ=3.2): return round(ground+(fl-1)*typ,1)

b=load_bld(); c=load_ctx()
# ---- sea
segs={x['pts'][0]:x['pts'] for x in c if x['k']=='C'}
chain=[]; p=(3428.0,260.0)
while p in segs:
    s=segs.pop(p); chain+= s if not chain else s[1:]; p=s[-1]
sea=Polygon(chain+[(-1500,chain[-1][1]),(-1500,4000),(4500,4000),(4500,260)]).buffer(0).intersection(VIEW)
land=VIEW.difference(sea)
def polys(g):
    if g.is_empty: return []
    return [q for q in (g.geoms if hasattr(g,'geoms') else [g]) if q.geom_type=='Polygon' and q.area>20]
def pj(q):  # polygon with holes
    return {'o':ring(q),'h':[[[R(x-OX),R(y-OY)] for x,y in list(i.coords)[:-1]] for i in q.interiors]}
# ---- roads
W={'H1':16,'H2':13,'H3':10,'H4':7,'H5':3.5}
rg={k:[] for k in W}; rail=[]; parks=[]; beach=[]; piers=[]
for x in c:
    k=x['k']
    if k in W and len(x['pts'])>1: rg[k].append(LineString(x['pts']).buffer(W[k]/2,cap_style=1,join_style=1))
    elif k=='R' and len(x['pts'])>1: rail.append(LineString(x['pts']).buffer(2.2))
    elif k=='P' and len(x['pts'])>2: parks.append(Polygon(x['pts']).buffer(0))
    elif k=='B' and len(x['pts'])>2: beach.append(Polygon(x['pts']).buffer(0))
    elif k=='M' and len(x['pts'])>2: piers.append(Polygon(x['pts']).buffer(0))
roads=unary_union([g for k in rg for g in rg[k]]).intersection(land).simplify(0.6)
promen=unary_union(rg['H5']).intersection(land)
rails=unary_union(rail).intersection(VIEW).simplify(0.5)
parks_u=unary_union(parks).intersection(land); beach_u=unary_union(beach).intersection(land)
piers_u=unary_union(piers).intersection(VIEW)
labels=[]
seen=set()
for x in c:
    if x['k'] in ('H1','H3','H4') and x['n'] and x['n'] not in seen and len(x['pts'])>1:
        ls=LineString(x['pts'])
        if ls.length<60: continue
        m=ls.interpolate(0.5,normalized=True)
        if not VIEW.contains(m): continue
        seen.add(x['n']); labels.append({'t':x['n'],'x':R(m.x-OX),'y':R(m.y-OY)})

