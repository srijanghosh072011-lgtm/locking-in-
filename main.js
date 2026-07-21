/* VALE LEGAL — lean interactions (no dependencies) */
(function () {
  "use strict";
  var reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  /* Year */
  var y = document.getElementById("year");
  if (y) y.textContent = new Date().getFullYear();

  /* Header scrolled state */
  var header = document.getElementById("header");
  var onScroll = function () {
    if (header) header.classList.toggle("scrolled", window.scrollY > 24);
  };
  onScroll();
  window.addEventListener("scroll", onScroll, { passive: true });

  /* Mobile nav */
  var toggle = document.getElementById("navToggle");
  var panel = document.getElementById("navMobile");
  var closeBtn = document.getElementById("navClose");
  function setNav(open) {
    if (!panel || !toggle) return;
    panel.classList.toggle("open", open);
    toggle.classList.toggle("active", open);
    toggle.setAttribute("aria-expanded", String(open));
    panel.setAttribute("aria-hidden", String(!open));
    document.body.classList.toggle("nav-open", open);
  }
  if (toggle) toggle.addEventListener("click", function () { setNav(!panel.classList.contains("open")); });
  if (closeBtn) closeBtn.addEventListener("click", function () { setNav(false); });
  if (panel) panel.querySelectorAll("a").forEach(function (a) { a.addEventListener("click", function () { setNav(false); }); });
  document.addEventListener("keydown", function (e) { if (e.key === "Escape") setNav(false); });

  /* Scroll reveal */
  var reveals = document.querySelectorAll(".reveal");
  if (reduce || !("IntersectionObserver" in window)) {
    reveals.forEach(function (el) { el.classList.add("in"); });
  } else {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (e.isIntersecting) { e.target.classList.add("in"); io.unobserve(e.target); }
      });
    }, { threshold: 0.12, rootMargin: "0px 0px -8% 0px" });
    reveals.forEach(function (el) { io.observe(el); });
  }

  /* Newsletter (demo: no backend — wire to your provider) */
  var nl = document.getElementById("newsletter");
  if (nl) nl.addEventListener("submit", function (e) {
    e.preventDefault();
    var btn = nl.querySelector("button");
    if (btn) { btn.textContent = "Thank you"; btn.disabled = true; }
  });

  /* Stat count-up */
  var stats = document.querySelectorAll("[data-count]");
  function countUp(el) {
    var target = parseInt(el.getAttribute("data-count"), 10);
    var suffix = el.getAttribute("data-suffix") || "";
    if (reduce || !target) { el.textContent = target + suffix; return; }
    var start = null, dur = 1600;
    function step(ts) {
      if (!start) start = ts;
      var p = Math.min((ts - start) / dur, 1);
      var eased = 1 - Math.pow(1 - p, 3);
      el.textContent = Math.round(target * eased) + suffix;
      if (p < 1) requestAnimationFrame(step);
    }
    requestAnimationFrame(step);
  }
  if ("IntersectionObserver" in window && !reduce) {
    var so = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) { if (e.isIntersecting) { countUp(e.target); so.unobserve(e.target); } });
    }, { threshold: 0.6 });
    stats.forEach(function (el) { so.observe(el); });
  } else {
    stats.forEach(function (el) { el.textContent = el.getAttribute("data-count") + (el.getAttribute("data-suffix") || ""); });
  }
})();
