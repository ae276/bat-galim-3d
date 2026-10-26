/* הטמעת מודל בת גלים בכל אתר:
   <div data-bat-galim-3d></div>
   <script src="https://OWNER.github.io/REPO/embed.js" defer></script>
   מאפיינים אופציונליים על ה-div: data-height="600px", data-view="d" (מחשב) או "m" (נייד) */
(function(){
  var me=document.currentScript, base=(me&&me.src||'').replace(/embed\.js(\?.*)?$/,'');
  function mount(){
    document.querySelectorAll('[data-bat-galim-3d]:not([data-bg-ready])').forEach(function(el){
      el.setAttribute('data-bg-ready','');
      var f=document.createElement('iframe');
      f.src=base+(el.dataset.view?('?view='+encodeURIComponent(el.dataset.view)):'');
      f.title='מודל תלת-ממדי של שכונת בת גלים, חיפה';
      f.loading='lazy'; f.allow='fullscreen'; f.setAttribute('allowfullscreen','');
      f.style.cssText='display:block;width:100%;height:100%;border:0;border-radius:inherit';
      if(!el.style.height) el.style.height=el.dataset.height||'min(85vh,760px)';
      if(!el.style.width) el.style.width='100%';
      el.appendChild(f);
    });
  }
  if(document.readyState==='loading') document.addEventListener('DOMContentLoaded',mount); else mount();
})();
