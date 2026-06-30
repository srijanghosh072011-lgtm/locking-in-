/* BlueLine Plumbing — vanilla JS. nav, FAQ, forms+honeypot, quote estimator, cookies, toast, login. */
(function(){
  "use strict";
  // mobile nav
  var tgl=document.querySelector(".nav-toggle"),nav=document.getElementById("nav");
  if(tgl&&nav){tgl.addEventListener("click",function(){
    var open=nav.classList.toggle("open");tgl.setAttribute("aria-expanded",open);});}

  // toast
  function toast(msg){
    var t=document.getElementById("toast");if(!t)return;
    t.querySelector("span").textContent=msg;t.classList.add("show");
    clearTimeout(t._t);t._t=setTimeout(function(){t.classList.remove("show");},3200);}

  // form validation + honeypot + optimistic submit
  document.querySelectorAll("form[data-validate]").forEach(function(form){
    form.addEventListener("submit",function(e){
      // honeypot: bots fill this hidden field
      var hp=form.querySelector(".hp input");
      if(hp&&hp.value){e.preventDefault();return;}
      var ok=true;
      form.querySelectorAll("[required]").forEach(function(inp){
        var f=inp.closest(".field"),bad=false;
        if(inp.type==="checkbox"){bad=!inp.checked;}
        else if(!inp.value.trim()){bad=true;}
        else if(inp.type==="email"&&!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(inp.value)){bad=true;}
        else if(inp.dataset.tel&&inp.value.replace(/\D/g,"").length<10){bad=true;}
        if(f)f.classList.toggle("invalid",bad);if(bad)ok=false;});
      if(!ok){e.preventDefault();var first=form.querySelector(".invalid input,.invalid select,.invalid textarea");if(first)first.focus();return;}
      // demo fallback unless a real endpoint is wired
      if(!form.dataset.endpoint&&!form.hasAttribute("netlify")){
        e.preventDefault();
        var btn=form.querySelector("[type=submit]");if(btn){btn.disabled=true;}
        toast(form.dataset.success||"Thanks — we'll be in touch shortly.");
        form.reset();setTimeout(function(){if(btn)btn.disabled=false;},1500);}
    });
    // clear error as the user types
    form.querySelectorAll("input,select,textarea").forEach(function(inp){
      inp.addEventListener("input",function(){var f=inp.closest(".field");if(f)f.classList.remove("invalid");});});
  });

  // quote estimator
  var est=document.getElementById("estimator");
  if(est){
    var rates={drains:189,hotwater:320,emergency:149,gas:160,leak:210,reno:6500};
    var out=document.getElementById("est-out");
    function calc(){
      var svc=est.querySelector("[name=svc]").value;
      var urg=est.querySelector("[name=urg]").value;
      var base=rates[svc]||150;
      if(urg==="emergency")base=Math.round(base*1.6);
      if(urg==="weekend")base=Math.round(base*1.25);
      out.querySelector(".lo").textContent="$"+base;
      out.querySelector(".hi").textContent="$"+Math.round(base*1.9);}
    est.addEventListener("input",calc);est.addEventListener("change",calc);calc();
  }

  // FAQ: open first by default already handled via markup. nothing needed.

  // cookie consent — no non-essential cookies until accepted
  var KEY="bl_cookie_consent";
  if(!localStorage.getItem(KEY)){
    var c=document.getElementById("cookie");if(c){c.style.display="flex";
      c.querySelectorAll("[data-consent]").forEach(function(b){
        b.addEventListener("click",function(){
          localStorage.setItem(KEY,b.dataset.consent);c.style.display="none";});});}
  }

  // demo login redirect
  var lf=document.getElementById("loginForm");
  if(lf){lf.addEventListener("submit",function(e){
    var hp=lf.querySelector(".hp input");if(hp&&hp.value){e.preventDefault();return;}
    var em=lf.querySelector("[name=email]"),pw=lf.querySelector("[name=password]");
    var ok=true;[em,pw].forEach(function(i){var f=i.closest(".field"),bad=!i.value.trim();
      if(f)f.classList.toggle("invalid",bad);if(bad)ok=false;});
    if(!ok){e.preventDefault();return;}
    e.preventDefault();
    var btn=lf.querySelector("[type=submit]");btn.disabled=true;btn.textContent="Signing in…";
    setTimeout(function(){window.location.href=lf.dataset.next||"dashboard.html";},600);});}

  // settings toggles (admin)
  document.querySelectorAll(".toggle").forEach(function(t){
    t.addEventListener("click",function(){
      t.setAttribute("aria-checked",t.getAttribute("aria-checked")==="true"?"false":"true");});});

  // scroll-entry choreography — IntersectionObserver, transform/opacity only
  if(!window.matchMedia("(prefers-reduced-motion:reduce)").matches&&"IntersectionObserver" in window){
    var targets=document.querySelectorAll(".section .card, .section .tcard, .section .kpi, .section .why, .section .step, .section h2, .section .lead, .formcard, .tier, .pricetable");
    targets.forEach(function(el){el.classList.add("reveal");});
    var io=new IntersectionObserver(function(entries){
      entries.forEach(function(e){if(e.isIntersecting){
        // stagger siblings for a cascade
        var sibs=Array.prototype.slice.call(e.target.parentNode.children).filter(function(n){return n.classList&&n.classList.contains("reveal");});
        var i=sibs.indexOf(e.target);if(i>0&&i<4)e.target.classList.add("d"+i);
        e.target.classList.add("in");io.unobserve(e.target);}});
    },{threshold:.12,rootMargin:"0px 0px -8% 0px"});
    targets.forEach(function(el){io.observe(el);});
  }

  // image fallback to CDN if self-hosted file missing
  document.querySelectorAll("img[data-cdn]").forEach(function(img){
    img.addEventListener("error",function(){if(img.src!==img.dataset.cdn)img.src=img.dataset.cdn;},{once:true});});
})();
