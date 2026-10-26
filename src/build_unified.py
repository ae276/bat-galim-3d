import json
D=open('data.json').read().replace('</','<\\/')
B={'d':open('template.html').read(),'m':open('template_m.html').read()}
boot=json.dumps(B,ensure_ascii=False).replace('</','<\\/')
JS=r'''(function(){
var W=window, B=JSON.parse(document.getElementById('bg-boot').textContent), DATA=document.getElementById('bg-data').textContent;
function ss(k,v){try{if(v===undefined)return sessionStorage.getItem(k); if(v===null)sessionStorage.removeItem(k); else sessionStorage.setItem(k,v);}catch(e){return null;}}
function auto(){var w=W.innerWidth||1200, sw=(W.screen&&W.screen.width)||w, sh=(W.screen&&W.screen.height)||W.innerHeight||800;
  var coarse=!!(W.matchMedia&&W.matchMedia('(pointer:coarse)').matches), phone=Math.min(sw,sh)<600;
  if(phone) return 'm'; if(w<760) return 'm'; if(coarse&&w<1000) return 'm'; return 'd';}
function pick(){var q=null; try{q=new URLSearchParams(location.search).get('view');}catch(e){}
  if(q==='m'||q==='d') return q; var o=ss('bg-layout'); return (o==='m'||o==='d')?o:auto();}
var raf=W.requestAnimationFrame.bind(W); W.__bgGen=0;
W.requestAnimationFrame=function(cb){var g=W.__bgGen; return raf(function(t){if(g===W.__bgGen) cb(t);});};
var loaded={};
function loadSrc(src){return loaded[src]||(loaded[src]=new Promise(function(res,rej){var s=document.createElement('script'); s.src=src; s.onload=res; s.onerror=function(){delete loaded[src]; rej(new Error('load '+src));}; document.head.appendChild(s);}));}
var busy=false;
function render(k){ if(busy) return; busy=true; W.__bgGen++; W.__bgLayout=k;
  document.querySelectorAll('canvas').forEach(function(c){try{var gl=c.getContext('webgl2')||c.getContext('webgl'); var x=gl&&gl.getExtension('WEBGL_lose_context'); if(x) x.loseContext();}catch(e){}});
  document.querySelectorAll('[data-bg]').forEach(function(n){n.remove();});
  document.body.innerHTML='';
  var doc=new DOMParser().parseFromString(B[k].replace('__DATA__',function(){return DATA;}),'text/html');
  document.documentElement.lang='he'; document.documentElement.dir='rtl'; document.title=doc.title||document.title;
  Array.prototype.slice.call(doc.head.children).forEach(function(n){ if(n.tagName==='TITLE'||n.tagName==='SCRIPT') return; var c=document.importNode(n,true); c.setAttribute('data-bg',''); document.head.appendChild(c);});
  var scripts=[];
  Array.prototype.slice.call(doc.body.childNodes).forEach(function(n){
    if(n.nodeType===1&&n.tagName==='SCRIPT'){ var t=(n.getAttribute('type')||'').toLowerCase();
      if(t==='application/json'){var j=document.createElement('script'); j.type=t; j.id=n.id; j.textContent=n.textContent; document.body.appendChild(j);}
      else scripts.push(n); }
    else document.body.appendChild(document.importNode(n,true)); });
  var p=Promise.resolve();
  scripts.forEach(function(n){ p=p.then(function(){ if(n.src) return loadSrc(n.getAttribute('src'));
    var s=document.createElement('script'); s.textContent=n.textContent; s.setAttribute('data-bg',''); document.body.appendChild(s); }); });
  p.catch(function(e){document.body.insertAdjacentHTML('beforeend','<div style="position:fixed;inset:auto 0 0 0;padding:12px;background:#b42318;color:#fff;font:14px Arial;direction:rtl;z-index:99">טעינת ספריית התלת-ממד נכשלה. בדקו את החיבור ורעננו את הדף.</div>');})
   .then(function(){busy=false;});
}
var tm=null;
function onResize(){clearTimeout(tm); tm=setTimeout(function(){ if(ss('bg-layout')) return; var k=auto(); if(k!==W.__bgLayout) render(k);},450);}
W.addEventListener('resize',onResize); W.addEventListener('orientationchange',onResize);
W.__bgSwitch=function(k){ss('bg-layout',k===auto()?null:k); render(k);};
render(pick());
})();'''
page=f'''<title>מודל בת גלים</title>
<meta name="claude:viewport-fit-sides" content="cover">
<style>html,body{{margin:0;height:100%;background:#e6edf0}}#bg-load{{height:100%;display:grid;place-items:center;font:15px Arial,sans-serif;color:#3d4b52;direction:rtl}}</style>
<div id="bg-load">טוען את המודל…</div>
<script id="bg-boot" type="application/json">{boot}</script>
<script id="bg-data" type="application/json">{D}</script>
<script>{JS}</script>
'''

print(len(page))

# STANDALONE (GitHub Pages)
import os
REPO=os.environ.get('BG_REPO',os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if os.path.isdir(REPO):
    full='<!doctype html>\n<html lang="he" dir="rtl">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">\n'+page.replace('<meta name="claude:viewport-fit-sides" content="cover">\n','',1).replace('<div id="bg-load">','</head>\n<body>\n<div id="bg-load">',1)+'</body>\n</html>\n'
    open(os.path.join(REPO,'index.html'),'w').write(full)
    print('standalone',len(full))
