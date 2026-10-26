exec(open('gen2.py').read())
from dec2 import dec
from shapely.geometry import Polygon, box
NB={}; NC=[]; NG=[]; NL=[]
for r in open('new.txt').read().strip().split(';'):
    p=r.split('|')
    if p[0]=='B': NB.setdefault(p[1],[]).append(toP(dec(p[2])))
    elif p[0]=='C': NC.append(dict(pl=p[1],num=p[2],use=p[3],poly=toP(dec(p[4]))))
    elif p[0]=='G': NG.append(toP(dec(p[3])))
    elif p[0]=='L':
        for rr in dec(p[2]):
            if len(rr)>=4: NL.append((p[1],Polygon([(x+OX,y+OY) for x,y in rr]).buffer(0)))
order2=[]
def plan2(id,**kw): P[id]=dict(id=id,bld=[],**kw); order2.append(id)
keepR=unary_union(NG).buffer(4)
# ---- Rambam
plan2('rambam', name='הקריה הרפואית רמב"ם – תוכנית ההרחבה', code='304-1536648', status='submitted', statusLabel='בבדיקה תכנונית · 10/2026',
  units=0, unitsTxt='כ-530,000 מ"ר לבריאות', extra='תוכנית האב "רמב"ם 2065": גידול מ-180 אלף ל-900 אלף מ"ר בנוי ועד 2,700 מיטות; מבנים לשימור, מנחת מסוקים, חניונים',
  heights='עד 30 קומות לפי מטרות התוכנית; פריסת המבנים משוערת (נספח הבינוי עדיין לא פורסם)',
  accuracy='גבול ותאי שטח מ-XPLAN; היקף וגובה מקסימלי מדף התוכנית במבא"ת; מיקום ונפח המבנים משוער',
  boundary=NB['304-1536648'], color='#0f8b8d', mid='3005504486',
  src=[['מבא"ת – דף התוכנית','https://mavat.iplan.gov.il/SV4/1/3005504486/310'],['TheMarker – "ברמב"ם חושבים 40 שנה קדימה"','https://www.themarker.com/labels/hayf2023/2023-08-31/ty-article-labels/0000018a-408e-d435-a59e-ceeecac80000']])
RC={c['num']:c['poly'] for c in NC if c['pl']=='304-1536648'}
big=[g for k,g in NL if k=='304-1536648' and g.area>8000]
c1=(big[0] if big else RC['1']).difference(keepR)
HF=4.2
mass('rambam',c1,towers=[30,24,20],th=[4.5+29*HF,4.5+23*HF,4.5+19*HF],mid=6,mh=4.5+5*HF,est=True,use='מבני בריאות',tsize=32,prefer='north',depth=18)
for k,fl in (('4',10),('2',8),('6',6)):
    if k in RC: mass('rambam',RC[k].difference(keepR),mid=fl,mh=4.5+(fl-1)*HF,est=True,use='מבני בריאות',setback=4,depth=18,podium=True)
P['rambam']['cells']=[{'o':ring(g),'k':'public','n':c['num'],'u':c['use']} for c in NC if c['pl']=='304-1536648' for g in ([c['poly']] if c['poly'].geom_type=='Polygon' else c['poly'].geoms)]
gfa=sum(Polygon(b['p']).area*b['f'] for b in P['rambam']['bld']); print('rambam est GFA',round(gfa))
# ---- children hospital +2 floors (approved)
kid=[e for e in ex if 'רות רפפורט' in e.get('n','')]
plan2('rambamkids', name='רמב"ם – תוספת 2 קומות לבית החולים לילדים', code='304-0875278 · חפ/מק/1481/ו', status='approved', statusLabel='מאושרת · 7/2022',
  units=0, unitsTxt='+2 קומות', extra='הרחבת בית החולים לילדים רות רפפורט, ללא תוספת זכויות',
  heights='תוספת 2 קומות מעל המבנה הקיים', accuracy='גבול מ-XPLAN; גובה המבנה הקיים מוערך',
  boundary=NB['304-0875278'], color='#2a9d8f', mid='3005078684', src=[['מבא"ת – דף התוכנית','https://mavat.iplan.gov.il/SV4/1/3005078684/310']])
for e in kid:
    base=max(e['h'],7*HF)
    e['h']=base
    P['rambamkids']['bld'].append({'p':e['p'],'f':2,'h':round(2*HF,1),'z0':round(base,1),'u':'מבני בריאות (קומות נוספות)'})
# ---- Waterfront TAMA 13/3/A
plan2('waterfront', name='חזית הים העירונית (הנמל המערבי)', code='תמ"א 13/3/א · 304-1304294', status='approved', statusLabel='תמ"א מאושרת 2017 · תוכניות המשך בהכנה',
  units=1500, unitsTxt='כ-1,500 יח"ד', extra='טיילת 2.5 ק"מ מבית המכס ועד החוף השקט; שימור מחסני הנמל; 500 יח"ד בחיפה אל-עתיקה (Yoo); תוכנית בינוי של כ-100 אלף מ"ר אושרה 6/2025; "ניוד זכויות" 304-1304294 בבדיקה',
  heights='לא נקבעו בפרסומים. במודל, לפי מגבלות העירייה: עד 15 מ\' בחזית הים, עד 35 מ\' בעורף – הנחה. הבינוי מוצג רק בשטחים פנויים; המבנים הקיימים (כולל מחסני הנמל לשימור) נשארים',
  accuracy='גבול ותאי שטח מ-XPLAN (תמ"א 13/3/א); הגבהים והפריסה משוערים; מבנים קיימים מ-OpenStreetMap',
  boundary=NB['13/ 3/ א']+NB.get('304-1304294',[]), color='#d0611c', mid=None,
  src=[['כלכליסט – תוכנית חזית הים','https://www.calcalist.co.il/real-estate/article/synroof10'],['מרכז הנדל"ן – תוכנית הבינוי בנמל','https://www.nadlancenter.co.il/article/12246'],['מן-שנער – Haifa Waterfront','https://mann-shinar.com/project/haifa-waterfront-plan/']])
EXU=unary_union([Polygon([(x+OX,y+OY) for x,y in e['p']]).buffer(6) for e in ex if len(e['p'])>2 and not e.get('d')])
def wf(use):
    if 'עירוני מעורב' in use: return 10,35,'עירוני מעורב (מגורים ומסחר)'
    if 'מגורים מסחר ותיירות' in use: return 8,28,'מגורים, מסחר ותיירות'
    if "מגורים ג'" in use: return 6,21,'מגורים'
    if 'תעסוקה' in use: return 10,35,'תעסוקה ומבני ציבור'
    if 'מסחר' in use: return 4,15,use
    if 'תרבות' in use: return 4,15,use
    return None
for c in NC:
    if c['pl']!='13/ 3/ א': continue
    r_=wf(c['use'])
    if not r_ or not c['poly'].intersects(VIEW): continue
    fl,h,u=r_
    g=c['poly'].buffer(-4,join_style=2).difference(EXU)
    if g.is_empty: continue
    cc,uu,LL,ang=axis(c['poly'])
    from shapely import affinity
    gr=affinity.rotate(g,-ang,origin=cc)
    x0,y0,x1,y1=gr.bounds
    BS,GAP=(38,14) if fl>=8 else (30,12)
    xx=x0
    while xx<x1:
        yy=y0
        while yy<y1:
            cellb=box(xx,yy,xx+BS,yy+BS).intersection(gr)
            for q in polys(cellb):
                if q.area>=0.45*BS*BS:
                    q=affinity.rotate(q,ang,origin=cc).simplify(0.5)
                    addpoly('waterfront',q,fl,u,h=h,est=True)
            yy+=BS+GAP
        xx+=BS+GAP
P['waterfront']['cells']=[{'o':ring(g),'k':usecat(c['use']),'n':c['num'],'u':c['use']} for c in NC if c['pl']=='13/ 3/ א' for g in ([c['poly']] if c['poly'].geom_type=='Polygon' else c['poly'].geoms)]
for k in order2:
    v=dict(P[k]); v['boundary']=[ring(g) for g in v['boundary']]; plans_out.append(v)
data['plans']=plans_out; data['nplans']=22
newg={k:unary_union([Polygon([(x+OX,y+OY) for x,y in b_['p']]).buffer(0) for b_ in P[k]['bld']]) for k in ('rambam',)}
nd={}
for e in ex:
    if e.get('d') or 'רות רפפורט' in (e.get('n') or ''): continue
    g=Polygon([(x+OX,y+OY) for x,y in e['p']]).buffer(0)
    if g.area<5 or keepR.contains(g.centroid): continue
    for k,u in newg.items():
        if g.intersection(u).area>0.3*g.area: e['d']=k; nd[k]=nd.get(k,0)+1; break
print('new demolitions',nd)
exec(open('inst_part.py').read())
s=json.dumps(data,ensure_ascii=False,separators=(',',':'))
open('data.json','w').write(s)
print(len(s), {k:len(P[k]['bld']) for k in order2})
