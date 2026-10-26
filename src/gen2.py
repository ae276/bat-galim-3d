exec(open('base_part.py').read())
from dec2 import dec
from shapely.affinity import rotate as srot
# ---------- official XPLAN data (0.5 m units, relative to origin) ----------
def toP(rings):  # rings in rel metres -> shapely polygon (abs coords)
    rs=[[(x+OX,y+OY) for x,y in r] for r in rings]
    return Polygon(rs[0],rs[1:]).buffer(0)
BL={}
for r in open('bl.txt').read().strip().split(';'):
    k,s=r.split('|'); BL['304-'+k]=[toP([ring]) for ring in dec(s)]
LU=[]
for r in open('lu.txt').read().strip().split(';'):
    p=r.split('|'); LU.append(dict(pl='304-'+p[0],num=p[1],use=p[2],poly=toP(dec(p[4]))))
ENV={}; KEEP=[]
for r in open('blines.txt').read().strip().split(';'):
    t,pl,kind,s=r.split('|'); rings=dec(s)
    if t=='L':
        for rr in rings:
            if len(rr)>=4 and math.hypot(rr[0][0]-rr[-1][0],rr[0][1]-rr[-1][1])<1.5:
                ENV.setdefault('304-'+pl,[]).append((kind,toP([rr])))
    elif t=='G' and kind=='k': KEEP.append(toP(rings))
def cell(pl,num): return [c for c in LU if c['pl']==pl and c['num']==num][0]['poly']

P={}; order=[]
def plan(id, **kw):
    P[id]=dict(id=id, bld=[], **kw); order.append(id)
def addpoly(id, poly, fl, use='מגורים', h=None, est=False, label=None, tag=None):
    for g in (poly.geoms if hasattr(poly,'geoms') else [poly]):
        if g.geom_type!='Polygon' or g.area<40: continue
        g=g.simplify(0.4)
        d={'p':[[R(x-OX),R(y-OY)] for x,y in list(g.exterior.coords)[:-1]],'f':fl,'h':h or fh(fl),'u':use}
        hl=[[[R(x-OX),R(y-OY)] for x,y in list(i.coords)[:-1]] for i in g.interiors if Polygon(i).area>30]
        if hl: d['hl']=hl
        if est: d['n']='משוער'
        if label: d['l']=label
        if tag: d['tag']=tag
        P[id]['bld'].append(d)
def axis(poly):
    mrr=poly.minimum_rotated_rectangle; pts=list(mrr.exterior.coords)[:4]
    e1=(pts[1][0]-pts[0][0],pts[1][1]-pts[0][1]); e2=(pts[2][0]-pts[1][0],pts[2][1]-pts[1][1])
    L1,L2=math.hypot(*e1),math.hypot(*e2)
    v,L=(e1,L1) if L1>=L2 else (e2,L2)
    u=(v[0]/L,v[1]/L); c=mrr.centroid
    return c,u,L,math.degrees(math.atan2(u[1],u[0]))
def mass(id, poly, towers=(), mid=None, tsize=26, prefer='east', use='מגורים', est=False, th=None, mh=None, setback=4, depth=14, podium=False):
    inner=poly.buffer(-setback,join_style=2)
    if inner.is_empty: inner=poly
    c,u,L,ang=axis(inner)
    sgn=1
    pref={'east':(1,0),'west':(-1,0),'north':(0,1),'south':(0,-1)}[prefer]
    if u[0]*pref[0]+u[1]*pref[1]<0: u=(-u[0],-u[1]); ang+=180
    n=len(towers); fr={0:[],1:[0.72],2:[0.24,0.76],3:[0.17,0.5,0.83],4:[0.12,0.37,0.63,0.88],5:[0.1,0.3,0.5,0.7,0.9]}[n]
    tps=[]
    for i,f in enumerate(fr):
        s=tsize
        for shrink in range(12):
            t=(f-0.5)*L*(1-shrink*0.06)
            cx,cy=c.x+u[0]*t,c.y+u[1]*t
            sq=Polygon(rect(cx,cy,s,s,ang))
            if inner.buffer(0.5).contains(sq) or shrink==11: break
        sq=sq.intersection(inner)
        tps.append(sq)
        fl=towers[i]
        addpoly(id,sq,fl,use,h=(th[i] if th else None),est=est)
    if mid:
        if podium: ring=inner
        else:
            core=inner.buffer(-depth,join_style=2)
            ring=inner.difference(core) if not core.is_empty else inner
        if tps: ring=ring.difference(unary_union([t.buffer(0 if podium else 6,join_style=2) for t in tps]))
        addpoly(id,ring,mid,use if not podium else 'קומות מסד – מסחר',h=mh,est=est)

src_mavat=lambda mid:['מבא"ת – דף התוכנית', f'https://mavat.iplan.gov.il/SV4/1/{mid}/310']

# ---- 1. RMI navy base
plan('rmi', name='תוכנית בת גלים – בה"ד חיל הים', code='304-0889832 · חפ/2177/ד', status='approved', statusLabel='מאושרת · 7/2024',
  units=1240, unitsTxt='1,240 יח"ד + 260 דיור מיוחד', extra='250 חדרי מלון, מסחר ותעסוקה, מבני ציבור, טיילת וחוף',
  heights='תאים 202–203: עד 25 ק\' (100 מ\'); תא 207: 23 ו-18 ק\'; תא 402 (רמב"ם): 25 ק\'; שאר המגורים 8–10 ק\'; מלון 10 ק\'',
  accuracy='גבולות ותאי שטח מ-XPLAN; קומות וגובה לפי טבלה 5 בהוראות. מיקום המגדל בתוך כל תא סכמטי',
  boundary=BL['304-0889832'], color='#2f7fbf', mid='3005087730',
  src=[['הוראות התוכנית (רמ"י)','https://apps.land.gov.il/IturTabotData/takanonim/haifa/3050408.pdf']])
R_=lambda n:cell('304-0889832',n)
mass('rmi',R_('101'),mid=10,mh=39); mass('rmi',R_('102'),mid=10,mh=39); mass('rmi',R_('103'),mid=8,mh=32)
mass('rmi',R_('200'),mid=8,mh=32,use='דיור מיוחד ומבני ציבור')
mass('rmi',R_('202'),towers=[25],th=[100],mid=8,prefer='east',use='מגורים, מסחר ותעסוקה')
mass('rmi',R_('203'),towers=[25],th=[100],mid=8,prefer='east',use='מגורים, מסחר ותעסוקה')
mass('rmi',R_('204'),mid=10,mh=39,use='מגורים, מסחר ותעסוקה'); mass('rmi',R_('206'),mid=10,mh=39,use='מגורים ותיירות')
mass('rmi',R_('207'),towers=[18,23],th=[None,100],mid=6,prefer='east',use='מגורים ודיור מיוחד')
mass('rmi',R_('501'),mid=10,mh=38.6,use='מלונאות (250 חדרים)',depth=16)
mass('rmi',R_('400'),mid=4,use='מבני ציבור'); mass('rmi',R_('402'),towers=[25],th=[110],mid=6,use='מבני ציבור לבריאות (רמב"ם)',tsize=30)
mass('rmi',R_('404'),mid=7,mh=25,use='מבני ציבור')
for n in ('302','303','304','305'): addpoly('rmi',R_(n).buffer(-1),1,'מסחר',h=5.5)

# ---- 2. Chel HaYam
plan('chelhayam', name='מתחם חיל הים', code='304-0540567 · חפ/מק/1/2400', status='permit', statusLabel='מאושרת · היתר בנייה',
  units=467, unitsTxt='467 יח"ד (במקום 119)', extra='מסחר, 2 כיתות גן, מרכז שיטור קהילתי, חניונים עיליים',
  heights='תאים 1 ו-3: מגדל 27 ק\' (89 מ\') ואגף 8 ק\'; תא 2: מגדל 33 ק\' (108 מ\')',
  accuracy='גבולות ותאי שטח מ-XPLAN; קומות וגובה לפי טבלה 5. מיקום המגדל בתוך התא סכמטי',
  boundary=BL['304-0540567'], color='#d9822b', mid='3000882579',
  src=[['הוראות התוכנית (רמ"י)','https://apps.land.gov.il/IturTabotData/takanonim/haifa/3050898.pdf'],['מרכז הנדל"ן – היתר','https://www.nadlancenter.co.il/article/8432']])
C_=lambda n:cell('304-0540567',n)
mass('chelhayam',C_('1'),towers=[27],th=[89],mid=8,mh=28,prefer='north')
mass('chelhayam',C_('2'),towers=[33],th=[108],prefer='north',tsize=28)
mass('chelhayam',C_('3'),towers=[27],th=[89],mid=8,mh=28,prefer='north')

# ---- 3. Aliya complex
plan('aliya', name='מתחם העלייה השנייה', code='304-0540534 · חפ/מק/1/2404', status='approved', statusLabel='מאושרת · 11/2022',
  units=725, unitsTxt='725 יח"ד (במקום 175)', extra='מבני ציבור וגני ילדים, מסחר, שצ"פ של 3.6 ד\'',
  heights='T1–T2: 34 ק\' (112 מ\'); T3: 32 ק\' (105 מ\'); T4: 16 ק\' לפי היזם (התוכנית מתירה עד 32); M1–M3 ו-B1–B2: 10 ק\'; B3: 9 ק\'',
  accuracy='גבולות ותאי שטח מ-XPLAN; קומות וגובה לפי טבלה 5; מיקום ושמות הבניינים לפי תוכנית המגרש של היזם',
  boundary=BL['304-0540534'], color='#c2457a', mid='3000882565',
  src=[['הוראות התוכנית (רמ"י)','https://apps.land.gov.il/IturTabotData/takanonim/haifa/3051307.pdf'],['מרכז הנדל"ן – בית וגג והכשרת היישוב','https://www.nadlancenter.co.il/article/7705']])
A_=lambda n:cell('304-0540534',n)
from shapely.geometry import Point
def B(x0,y0,x1,y1): return box(x0+OX,y0+OY,x1+OX,y1+OY)
def round_corner(poly_box,corner,r):
    x0,y0,x1,y1=poly_box.bounds
    cx,cy={'nw':(x0+r,y1-r),'ne':(x1-r,y1-r)}[corner]
    q={'nw':box(x0,y1-r,x0+r,y1),'ne':box(x1-r,y1-r,x1,y1)}[corner]
    return poly_box.difference(q).union(Point(cx,cy).buffer(r,resolution=12).intersection(q))
# site plan supplied by the developer (marketing names), fitted to the XPLAN cells
T4=round_corner(B(75,-58.7,99,-26.5),'nw',12)
addpoly('aliya',T4,16,h=54,tag='T4'); addpoly('aliya',B(113.4,-59.4,142.2,-24),32,h=105,tag='T3')
addpoly('aliya',B(144.6,-120.4,172.4,-85),34,h=112,tag='T2'); addpoly('aliya',B(191.4,-120.4,219.8,-85).intersection(A_('1').buffer(-1)),34,h=112,tag='T1')
addpoly('aliya',B(76,-97,102,-69),10,h=32,tag='M1'); addpoly('aliya',B(76,-120,102,-97.5),10,h=32,tag='M2'); addpoly('aliya',B(102.5,-120,127.6,-97.5),10,h=32,tag='M3')
B1=round_corner(B(26,-54,56,-27),'ne',13)
addpoly('aliya',B1,10,h=32,tag='B1'); addpoly('aliya',B(41,-93,57,-63),10,h=32,tag='B2'); addpoly('aliya',B(24,-121,55,-104.5),9,h=32,tag='B3')
mass('aliya',A_('6'),mid=10,mh=32,setback=3)
for n in ('201','202','203'): mass('aliya',A_(n),mid=3,use='מבני ציבור',est=True,setback=4)

# ---- 4. Aliya 15-23 (new)
plan('aliya15', name='העלייה השנייה 15–23', code='304-1477090', status='submitted', statusLabel='בבדיקה · 3/2026',
  units=1044, unitsTxt='1,044 יח"ד (במקום 286)', extra='מגורים, מסחר ומבני ציבור; שצ"פ של 3.2 ד\'',
  heights='לא פורסמו. במודל: 3 מגדלים של 35 ק\' ואגף 8 ק\' – הנחה',
  accuracy='גבולות ותאי שטח ומספר יח"ד מ-XPLAN; הגבהים משוערים',
  boundary=BL['304-1477090'], color='#a8326e', mid='3005467042',
  src=[['מבא"ת – דף התוכנית','https://mavat.iplan.gov.il/SV4/1/3005467042/310']])
mass('aliya15',cell('304-1477090','201'),towers=[35,35,35],mid=8,est=True,use='מגורים, מסחר ומבני ציבור')
mass('aliya15',cell('304-1477090','401'),mid=4,est=True,use='מבני ציבור')

# ---- 5. Aliya 20 / Efron
plan('efron', name='העלייה השנייה 20', code='304-0921189', status='approved', statusLabel='מאושרת · 1/2025',
  units=309, unitsTxt='309 יח"ד (במקום 76)', extra='כ-2,000 מ"ר משרדים וכ-1,600 מ"ר מסחר, אפשרות למלונאות',
  heights='תא 101: עד 25 ק\' (96 מ\'); תא 102: עד 28 ק\' (105 מ\'); 6–7 ק\' לחזית העלייה השנייה',
  accuracy='קווי הבניין מ-XPLAN; גבהים לפי טבלה 5. חלוקת הגבהים בתוך קו הבניין סכמטית',
  boundary=BL['304-0921189'], color='#7a5cc4', mid='3005107076',
  src=[['הוראות התוכנית (רמ"י)','https://apps.land.gov.il/IturTabotData/takanonim/haifa/3052116.pdf'],['מרכז הנדל"ן – קרסו וא.ד חבצלת','https://www.nadlancenter.co.il/article/12710']])
for kind,env in ENV.get('304-0921189',[]):
    c0=env.centroid; inC=lambda n: cell('304-0921189',n).contains(c0)
    big=inC('102'); low=env.intersection(box(0,0,9999,1400+12.5))  # strip toward Aliya street (south)
    rest=env.difference(low)
    c,u,L,ang=axis(rest)
    tw=Polygon(rect(rest.centroid.x+(6 if big else 0),rest.centroid.y+(-4 if big else 6),26,26,ang)).intersection(rest)
    addpoly('efron',low,7,'מגורים ומסחר')
    addpoly('efron',tw,28 if big else 25,'מגורים' if big else 'מגורים ומשרדים',h=105 if big else 96)
    addpoly('efron',rest.difference(tw.buffer(4,join_style=2)),10,'מגורים')

# ---- 6. Egged
plan('egged', name='מתחם אגד – בת גלים', code='304-1327394', status='submitted', statusLabel='בבדיקה · 12/2025',
  units=1650, unitsTxt='1,650 יח"ד', extra='מסחר ותעסוקה, מלונאות, בית ספר; מבנה התחנה ההיסטורי לשימור',
  heights='לא פורסמו. במודל: 5 מגדלי מגורים 30 ק\', 3 מבנים מעורבים 25 ק\', 2 מבני תעסוקה 20 ק\' – הנחה',
  accuracy='גבולות ותאי שטח מ-XPLAN (75.2 ד\'); מספר המבנים לפי הפרסומים; הגבהים משוערים',
  boundary=BL['304-1327394'], color='#b3473a', mid='3005376000',
  src=[['מבא"ת – דף התוכנית','https://mavat.iplan.gov.il/SV4/1/3005376000/310'],['מעריב – התוכנית למתחם','https://www.maariv.co.il/economy/realestate/article-1267387']])
E_=lambda n:cell('304-1327394',n)
mass('egged',E_('1'),towers=[30]*5,mid=3,podium=True,est=True,tsize=24)
mass('egged',E_('2'),towers=[25]*3,mid=3,podium=True,est=True,use='מגורים, מסחר ותעסוקה',tsize=26)
KU=unary_union(KEEP).buffer(8)
c4=E_('4').difference(KU)
mass('egged',c4,towers=[20,20],mid=2,podium=True,est=True,use='מסחר ותעסוקה',tsize=26)

# ---- 7. Casino
plan('casino', name='מלון הקזינו', code='304-1268317 · חפ/1602/ט', status='deposited', statusLabel='לקראת הפקדה · 9/2025',
  units=0, unitsTxt='110 חדרי מלון', extra='בריכה וחזית פעילה לטיילת',
  heights='7 קומות (תוספת 4 קומות לצד הים) ומבנה קטן נוסף ממזרח',
  accuracy='קווי הבניין מ-XPLAN; גבהים לפי הפרסומים',
  boundary=BL['304-1268317'], color='#c99a1e', mid='3005337672',
  src=[['כלכליסט – החלטת ההפקדה','https://www.calcalist.co.il/real-estate/article/hjap6rujge']])
ce=sorted(ENV.get('304-1268317',[]),key=lambda e:e[1].centroid.x)
if ce: addpoly('casino',ce[0][1],7,'מלונאות',h=24)
if len(ce)>1: addpoly('casino',ce[1][1],3,'מלונאות')

# ---- 8. small approved infill plans
plan('infill', name='תוכניות נקודתיות מאושרות', code='11 תוכניות', status='approved', statusLabel='מאושרות · 2018–2025',
  units=213, unitsTxt='כ-213 יח"ד נוספות', extra='שד\' בת גלים 4 ו-6, חפ/2626, פינת גן 2, רחף 1,3, רוזנפלד 27, מרגולין, העלייה השנייה 62, מלון ליד הרכבל',
  heights='בת גלים 6: 7 ק\'; מלון ליד הרכבל: 4 ק\'; לשאר: 5–7 ק\' משוער',
  accuracy='גבולות, תאי שטח וקווי בניין מ-XPLAN; גבהים מוחלטים רק לשתי תוכניות',
  boundary=None, color='#5d7f8c', mid=None,
  src=[['הוראות בת גלים 6 (רמ"י)','https://apps.land.gov.il/IturTabotData/takanonim/haifa/3052709.pdf'],['הוראות מלון ליד הרכבל (רמ"י)','https://apps.land.gov.il/IturTabotData/takanonim/haifa/3051664.pdf']])
SM=[('304-1099209','חפ/2626 – פינת שד\' בת גלים והעלייה השנייה',7,True),('304-1082031','שד\' בת גלים 6',7,False),('304-0743799','פינת גן 2',6,True),
    ('304-0830760','רחף 1,3',6,True),('304-0853481','רציף מרגולין 43',5,True),('304-0310896','שד\' בת גלים 4',6,True),('304-0454678','רציף רוזנפלד 27',5,True),
    ('304-0352997','מרגולין על המים',5,True),('304-0407908','רציף מרגולין 39',5,True),('304-0137406','העלייה השנייה 62',5,True)]
infill_bounds=[]
for pl,nm,fl,est in SM:
    infill_bounds+= BL.get(pl,[])
    envs=[e for k,e in ENV.get(pl,[]) if k in ('b','u')]
    if envs:
        u_=unary_union(envs)
    else:
        u_=unary_union([c['poly'] for c in LU if c['pl']==pl and 'מגורים' in c['use']]).buffer(-2.5,join_style=2)
    for k in KEEP: u_=u_.difference(k.buffer(1))
    addpoly('infill',u_,fl,'מגורים / תיירות',est=est,label=nm)
cab=Polygon([(x/2+OX,y/2+OY) for x,y in [(-1752,-214),(-1768,-164),(-1703,-140),(-1683,-195),(-1732,-210)]]).buffer(-2)
addpoly('infill',cab,4,'מלונאות ומסחר',h=17,label='מלון ליד הרכבל התחתון')
infill_bounds.append(cab.buffer(2))
P['infill']['boundary']=infill_bounds

# ---- 9. Brigade (no plan yet)
plan('brigade', name='מתחם הבריגדה', code='טרם הוגשה תוכנית', status='prep', statusLabel='בתכנון · נבחרו יזמים',
  units=900, unitsTxt='כ-900 יח"ד (במקום כ-300)', extra='18.5 ד\', 14 מבנים קיימים; מבנים ותדהר',
  heights='טרם נקבעו. במודל: 3 מגדלים של 30 ק\' ואגפים של 9 ק\' – הנחה',
  accuracy='אין תוכנית במבא"ת; גבול לפי הסמטאות במתחם; מסה משוערת בלבד',
  boundary=[Polygon([(1150,1290),(1300,1288),(1304,1398),(1255,1404),(1175,1410),(1150,1404)])], color='#3d9a6a', mid=None,
  src=[['מרכז הנדל"ן – מבנים ותדהר','https://www.nadlancenter.co.il/article/10121']])
for x in (1172,1224,1276): addpoly('brigade',Polygon(rect(x,1372,24,24,4)),30,est=True)
addpoly('brigade',Polygon(rect(1190,1318,52,15,4)),9,est=True); addpoly('brigade',Polygon(rect(1262,1318,52,15,4)),9,est=True)

# context: Kiryat Eliezer
KE=['304-1571405','304-1554880','304-1474113','304-1409309','304-1404342','304-1391424','304-1335231','304-1217348','304-1199405','304-1014257']
context=[ring(b_) for k in KE for b_ in BL.get(k,[]) if b_.intersects(VIEW)]
# land-use cells for display (per plan, coloured by use)
def usecat(u):
    if 'פתוח' in u or 'ככר' in u: return 'open'
    if 'ציבור' in u and 'מגורים' not in u: return 'public'
    if 'מלונ' in u or 'תיירות'==u: return 'hotel'
    if 'מגורים' in u: return 'res'
    if 'מסחר' in u or 'תעסוקה' in u: return 'com'
    return 'other'
plan_of={'304-0889832':'rmi','304-0540567':'chelhayam','304-0540534':'aliya','304-1477090':'aliya15','304-0921189':'efron','304-1327394':'egged','304-1268317':'casino'}
for c in LU:
    pid=plan_of.get(c['pl'], 'infill' if c['pl'] in [s[0] for s in SM] else None)
    if not pid: continue
    for g in (c['poly'].geoms if hasattr(c['poly'],'geoms') else [c['poly']]):
        P[pid].setdefault('cells',[]).append({'o':ring(g),'k':usecat(c['use']),'n':c['num'],'u':c['use']})

# ---- existing buildings + demolition
renew_bounds={k:unary_union(P[k]['boundary']) for k in ('rmi','chelhayam','aliya','aliya15','efron','egged','brigade')}
small_cells=unary_union([c['poly'] for c in LU if c['pl'] in [s[0] for s in SM]])
keep_u=unary_union(KEEP)
ex=[]
for bb in b:
    if len(bb['pts'])<3: continue
    poly=Polygon(bb['pts']).buffer(0)
    if poly.area<4: continue
    lv=None
    try: lv=float(bb['l']) if bb['l'] else None
    except: pass
    try: hh=float(bb['h']) if bb['h'] else None
    except: hh=None
    a=poly.area; t=bb['b']
    if hh is None:
        if lv is None:
            if t in ('roof','shed','guardhouse','service'): lv=1
            elif t=='house': lv=2
            elif t in ('hospital','university'): lv=6
            elif a<60: lv=1
            elif a<180: lv=2
            elif a<1500: lv=4
            else: lv=3
        hh=lv*3.2+0.6
        if t=='roof': hh=3.5
    cen=poly.centroid; dem=None
    keep = keep_u.buffer(3).contains(cen) or bb['n'] in ('מרכזית בת-גלים','הקזינו')
    if not keep:
        for k,pp in renew_bounds.items():
            if pp.contains(cen): dem=k; break
        if not dem and small_cells.contains(cen): dem='infill'
    d={'p':[[R(x-OX),R(y-OY)] for x,y in bb['pts']],'h':round(hh,1)}
    if lv: d['l']=int(lv) if lv==int(lv) else lv
    if bb['n']: d['n']=bb['n']
    if bb['a']: d['a']=bb['a']
    if dem: d['d']=dem
    if bb['n']=='מרכזית בת-גלים':
        kp=poly.intersection(keep_u.buffer(2)); rest=poly.difference(keep_u.buffer(2))
        for g in [kp]:
            if not g.is_empty: ex.append({'p':[[R(x-OX),R(y-OY)] for x,y in list(g.exterior.coords)[:-1]],'h':round(hh,1),'l':2,'n':bb['n'],'keep':'החלק המזרחי של מבנה התחנה – לשימור בתוכנית אגד'})
        for g in (rest.geoms if hasattr(rest,'geoms') else [rest]):
            if g.area>20: ex.append({'p':[[R(x-OX),R(y-OY)] for x,y in list(g.exterior.coords)[:-1]],'h':round(hh,1),'l':2,'n':bb['n'],'d':'egged'})
        continue
    ex.append(d)
plans_out=[]
for k in order:
    v=P[k]; v=dict(v); v['boundary']=[ring(g) for g in v['boundary']]
    plans_out.append(v)
data={'origin':[OX,OY],'view':[350-OX,-300-OY,4050-OX,2250-OY],
 'sea':[pj(q) for q in polys(sea)],'roads':[pj(q) for q in polys(roads)],'promenade':[pj(q) for q in polys(promen)],
 'rail':[pj(q) for q in polys(rails)],'parks':[pj(q) for q in polys(parks_u)],'beach':[pj(q) for q in polys(beach_u)],
 'piers':[pj(q) for q in polys(piers_u)],'labels':labels,'existing':ex,'plans':plans_out,'context':context,
 'units':[
  {'id':'t3d3','title':'T3 · דירה D3 · קומה 22','sub':'4 חדרים · 108 מ"ר + מרפסת שמש 9.7 מ"ר · דירה מס\' 132','face':'פונה מערבה, מול מגדל T4',
   'p':[[113.4,-45.0],[126.8,-45.0],[126.8,-35.4],[113.4,-35.4]],'z0':70.0,'z1':73.2,'eye':[112.7,-36.6],'look':[-1,0.08]},
  {'id':'b3c','title':'B3 · דירה C · קומה 4','sub':'3 חדרים · 83.5 מ"ר + מרפסות 15.3 ו-4.8 מ"ר · דירה מס\' 12','face':'בקצה המערבי של B3; מרפסת ראשית לצפון',
   'p':[[24.0,-119.0],[32.5,-119.0],[32.5,-106.5],[24.0,-106.5]],'z0':12.8,'z1':16.0,'eye':[30.4,-103.6],'look':[0.1,1]}]}
s=json.dumps(data,ensure_ascii=False,separators=(',',':'))
open('data.json','w').write(s)
print(len(s), len(ex), sum(1 for e in ex if 'd' in e), {k:len(P[k]['bld']) for k in order}, sum(P[k]['units'] for k in order))
