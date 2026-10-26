# ---- public institutions (existing + planned)
from pyproj import Transformer
from shapely.geometry import Point
from shapely.strtree import STRtree
_itm=Transformer.from_crs(2039,4326,always_xy=True)
_kx=math.cos(math.radians(32.83))*111320; _ky=110574
def ll2abs(lon,lat): return ((lon-34.964)*_kx,(lat-32.8195)*_ky)
EXP=[(Polygon([(x+OX,y+OY) for x,y in e['p']]).buffer(0),e) for e in ex if len(e['p'])>2]
_tree=STRtree([g for g,_ in EXP])
def ex_at(pt,rad=0):
    q=Point(pt); best=None
    for i in _tree.query(q.buffer(max(rad,0.1))):
        g,e=EXP[int(i)]
        d=g.distance(q)
        if d<=rad and (best is None or d<best[0]): best=(d,e)
    return best[1] if best else None
def near_any(pt,rad): return len(_tree.query(Point(pt).buffer(rad)))>0
INST=[]
FIXN={'עליה':'העלייה','הנריטה סאלד':'הנרייטה סאלד','ברכ"ה - כתות חולים':'ברכ"ה – כיתות אשפוז ברמב"ם','מחוזי חינוך ימי חיפה':'מרכז החינוך הימי המחוזי חיפה',"עירוני א'":"עירוני א'"}
def schname(i):
    n=FIXN.get(i[0],i[0]); t,st=i[1],i[2]
    if any(n.startswith(p) for p in ('בי"ס','ביה"ס','בית ספר','תיכון','מכללת','מרכז','המרכז','חטב','מקיף')):
        return n.replace('חטב ','חטיבת ביניים ').replace('מקיף ','מקיף ')
    if 'מכללה' in t or 'סמינר' in t: return n
    pre={'יסודי בלבד':'בית ספר יסודי','חט"ב בלבד':'חטיבת ביניים','עליונה בלבד':'תיכון','חט"ב + עליונה':'בית ספר תיכון (ז׳–י״ב)'}.get(st,'בית ספר')
    return pre+' '+n
def inzone(pt): return 850<=pt[0]<=OX+800 and pt[1]>=OY-560
def add_inst(pt,cat,name,sub,src,fut=False,pl=None,note='',h=None):
    x,y=pt
    if h is None:
        e=ex_at(pt,12); h=e['h'] if e else 0
        dem=e.get('d') if e else None
    else: dem=None
    d={'x':R(x-OX),'y':R(y-OY),'c':cat,'n':name,'s':sub,'src':src,'h':round(h,1)}
    if fut: d['f']=1; d['pl']=pl
    if note: d['note']=note
    if dem and 'רמב"ם' not in name: d['d']=dem
    INST.append(d)
# --- Ministry of Education (data.gov.il)
OSMSCH={'עליה':(34.98182,32.83190),'דרור':(34.98266,32.82256),'יבניאלי':(34.97720,32.82830),'הנריטה סאלד':(34.97770,32.82941),
        'מוריה':(34.98815,32.82196),"עירוני א'":(34.98507,32.82550),'גן מיחא':(34.97691,32.82766)}
for ln in open('edu.txt',encoding='utf8').read().strip().split('\n'):
    xy,rest=ln.split('|',1); X,Y=map(float,xy.split(','))
    lon,lat=_itm.transform(X,Y); pt=ll2abs(lon,lat)
    items=[r.split('~') for r in rest.split('^')]
    sch=[i for i in items if any(k in i[1] for k in ('בית ספר','בי"ס','מרכז ימי','מכללה','סמינר'))]
    oth=[i for i in items if i not in sch]
    for k,v in OSMSCH.items():
        if any(i[0]==k for i in items):
            p2=ll2abs(*v)
            if math.dist(p2,pt)<250: pt=p2
    if not inzone(pt) or not near_any(pt,60): continue
    if sch:
        cat='edu'; name=' · '.join(dict.fromkeys(schname(i) for i in sch))
        sub=' · '.join(dict.fromkeys(f"{i[1]}{(' – '+i[2]) if i[2] else ''}{' (חינוך מיוחד)' if i[3] else ''}" for i in sch))
        if oth: sub+=' · באותו מתחם: '+', '.join(dict.fromkeys(i[0] for i in oth))
    else:
        cat='kg'; kinds=set(i[1] for i in oth)
        lab='מעון יום' if kinds=={'מעון יום'} else ('גן ילדים' if len(oth)==1 else 'גני ילדים')
        name=lab+' '+', '.join(dict.fromkeys((i[0][3:] if i[0].startswith('גן ') else i[0]) if lab!='מעון יום' else i[0] for i in oth))
        sub=' · '.join(dict.fromkeys(i[1]+(' (חינוך מיוחד)' if i[3] else '') for i in oth))
    add_inst(pt,cat,name,sub,'משרד החינוך (data.gov.il)')
# --- OpenStreetMap
for ln in open('osm_inst.txt',encoding='utf8').read().strip().split('\n'):
    cat,name,sub,co=ln.split('|')
    if co.startswith('abs:'): pt=tuple(map(float,co[4:].split(',')))
    else: pt=ll2abs(*map(float,co.split(',')))
    if not inzone(pt): continue
    add_inst(pt,cat,name,sub,'OpenStreetMap')
# --- planned (from plan instructions + public-facilities programmes)
def ctr(pl,num):
    g=cell(pl,num); return g.centroid.coords[0] if g.contains(g.centroid) else g.representative_point().coords[0]
def fut_h(pid,pt):
    q=Point(pt[0]-OX,pt[1]-OY); hs=[b['h']+(b.get('z0') or 0) for b in P[pid]['bld'] if Polygon(b['p']).buffer(0).buffer(3).contains(q)]
    if not hs: hs=[b['h']+(b.get('z0') or 0) for b in P[pid]['bld'] if Polygon(b['p']).buffer(0).distance(q)<20]
    return max(hs) if hs else 0
PRG='נספח הפרוגרמה לשטחי ציבור (רמ"י / מבא"ת)'
TAK='הוראות התוכנית (רמ"י)'
def F(pid,pt,cat,name,sub,src,note=''): add_inst(pt,cat,name,sub,src,fut=True,pl=pid,note=note,h=fut_h(pid,pt))
R0='304-0889832'
_c403=cell(R0,'403'); _cc,_u,_L,_ang=axis(_c403)
addpoly('rmi',Polygon(rect(_cc.x,_cc.y,52,32,_ang)),4,'בית ספר יסודי וגני ילדים',est=True)
F('rmi',ctr(R0,'403'),'edu','בית ספר יסודי חדש (18 כיתות) + 8 כיתות גן','תא 403 · 6,510 מ"ר, עד 7 קומות · כולל אולם ספורט, אגף קהילתי ומועדון נוער',PRG)
F('rmi',ctr(R0,'400'),'edu','בית ספר על-יסודי חדש (18 כיתות)','תא 400 · 8,200 מ"ר בנוי (זכויות 9,000 מ"ר) · אולם הספורט הקיים בתא ישמש את בית הספר',PRG)
F('rmi',ctr(R0,'200'),'kg','מעון יום (6 כיתות) ומרפאה שכונתית','תא 200 · מעון 880 מ"ר במבנה המשלב דיור מיוחד ומסחר; מרפאה שכונתית 500–1,000 מ"ר',PRG)
F('rmi',ctr(R0,'404'),'comm','מרכז קהילתי ותרבות','תא 404 · מבנה קיים שישמש מרכז תרבות (כ-2,300 מ"ר) + זכויות להרחבה',PRG)
F('rmi',ctr(R0,'202'),'health','תחנה לבריאות המשפחה (טיפת חלב)','תא 202 · 250 מ"ר בבניין המגורים',PRG)
F('rmi',ctr(R0,'203'),'gov','שירותי עירייה ומועדונים חברתיים','תא 203 · 250 מ"ר בבניין המגורים (משרדי עירייה, שירות לתושב)',PRG)
F('rmi',ctr(R0,'101'),'rel','בית כנסת','תא 101 · 400 מ"ר בקומת הקרקע של בניין מגורים',PRG)
F('rmi',ctr(R0,'207'),'comm','מרכז פעילות ימית וחוגי נוער','תא 207 · 500 מ"ר (מעבדות, חוגי נוער, פעילות ימית)',PRG)
F('rmi',ctr(R0,'402'),'health','הרחבת רמב"ם (בתחום התוכנית)','תא 402 · כ-65,000 מ"ר למבני ציבור לבריאות, עד 25 קומות',PRG)
A0='304-0540534'
F('aliya',ctr(A0,'1'),'kg','מעון יום (3 כיתות) + 3 כיתות גן','תא 1 · בקומות הקרקע של בנייני המגורים',PRG+' · '+TAK)
F('aliya',ctr(A0,'201'),'comm','מגרשים למבני ציבור (3 תאים, כ-4 ד\')','תאים 201–203 · חינוך, תרבות, קהילה, ספורט, רווחה, בריאות ודת לפי צורכי העירייה',TAK,note='המבנים הציבוריים הקיימים בתאים 202–203 מיועדים להריסה')
C0='304-0540567'
F('chelhayam',ctr(C0,'2'),'kg','2 כיתות גן ילדים','בניין 2 · קומת הכניסה, כניסה נפרדת וחצר של כ-200 מ"ר',TAK)
F('chelhayam',ctr(C0,'1'),'gov','מרכז שיטור קהילתי ומקלט ציבורי','בניין 1 · קומת הכניסה למגדל, כניסה מהשצ"פ',TAK)
F('aliya15',ctr('304-1477090','401'),'comm','מגרש למבני ציבור (כ-6 ד\')','תא 401 · ושטחים מבונים לציבור בתא 201',"מבא\"ת – 304-1477090",note='התוכנית בבדיקה; השימוש המדויק טרם נקבע')
F('egged',(1721,1091),'edu','בתי ספר מבונים ומבני ציבור','"הקמת מבני ציבור כולל בתי ספר מבונים"; מבנה אגד ההיסטורי ישמש לציבור, מלונאות ומסחר',"מבא\"ת – 304-1327394",note='התוכנית בבדיקה; מיקום בתי הספר טרם פורסם')
F('rambam',RC['1'].representative_point().coords[0],'health','הרחבת הקריה הרפואית רמב"ם','כ-530,000 מ"ר לבריאות, עד 30 קומות',"מבא\"ת – 304-1536648")
for n_,lab in (('151','מבני ציבור לתרבות ופנאי'),('152','מבני ציבור לתרבות ופנאי')):
    g=[c['poly'] for c in NC if c['pl']=='13/ 3/ א' and c['num']==n_]
    if g: F('waterfront',g[0].representative_point().coords[0],'comm',lab,f'תמ"א 13/3/א · תא {n_} · {round(g[0].area/1000,1)} ד\'','XPLAN – תמ"א 13/3/א',note='גובה ונפח טרם נקבעו')
for i in INST:
    i['n']=i['n'].replace('רמבם','רמב"ם')
    if 'מיחא' in i['n']: i['n']='גני מיח"א (חינוך מיוחד)'
data['inst']=INST
print('inst',len(INST),sum(1 for i in INST if i.get('f')), {c:sum(1 for i in INST if i['c']==c) for c in set(i['c'] for i in INST)})
