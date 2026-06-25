/* =====================================================================
   Wascana Plumbing & Drain — site behaviour
   Vanilla JS, no dependencies. Progressive enhancement only:
   the site is fully usable with JavaScript disabled.
   ===================================================================== */
(function () {
  "use strict";

  /* ---------- Mobile navigation ---------- */
  var toggle = document.querySelector(".nav-toggle");
  var links = document.getElementById("nav-links");
  var scrim = document.querySelector(".nav-scrim");

  function setNav(open) {
    if (!links) return;
    links.classList.toggle("open", open);
    if (scrim) scrim.classList.toggle("show", open);
    if (toggle) toggle.setAttribute("aria-expanded", String(open));
    document.body.style.overflow = open ? "hidden" : "";
  }
  if (toggle && links) {
    toggle.addEventListener("click", function () {
      setNav(!links.classList.contains("open"));
    });
  }
  if (scrim) scrim.addEventListener("click", function () { setNav(false); });
  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape") setNav(false);
  });

  /* ---------- Accordions (FAQ) ---------- */
  document.querySelectorAll(".acc-trigger").forEach(function (btn) {
    btn.addEventListener("click", function () {
      var expanded = btn.getAttribute("aria-expanded") === "true";
      var panel = document.getElementById(btn.getAttribute("aria-controls"));
      btn.setAttribute("aria-expanded", String(!expanded));
      if (panel) panel.style.maxHeight = expanded ? null : panel.scrollHeight + "px";
    });
  });

  /* ---------- Image graceful fallback ----------
     Every photo sits in an .imgframe that already contains a styled
     navy fallback panel. If the real photo is missing or not yet
     dropped in, hide the broken <img> and reveal the branded panel
     so the layout never shows a broken-image icon. */
  document.querySelectorAll(".imgframe img, .hero .media-frame img").forEach(function (img) {
    function fail() {
      img.style.display = "none";
      var fb = img.parentElement.querySelector(".fallback");
      if (fb) fb.style.display = "flex";
      var hero = img.closest(".media-frame");
      if (hero) hero.style.background = "var(--navy-800)";
    }
    img.addEventListener("error", fail);
    // Catch images that resolved to 0x0 (blocked) after load.
    img.addEventListener("load", function () {
      if (img.naturalWidth === 0) fail();
    });
    // Catch images that already failed before this script ran (deferred).
    if (img.complete && img.naturalWidth === 0) fail();
  });

  /* ---------- Cookie consent (CASL / PIPEDA friendly) ---------- */
  var KEY = "wpd-cookie-consent";
  var bar = document.getElementById("cookie-bar");
  function consent() { try { return localStorage.getItem(KEY); } catch (e) { return "dismissed"; } }
  function setConsent(v) { try { localStorage.setItem(KEY, v); } catch (e) {} }
  if (bar && !consent()) {
    window.setTimeout(function () { bar.classList.add("show"); }, 800);
    bar.querySelectorAll("[data-consent]").forEach(function (b) {
      b.addEventListener("click", function () {
        setConsent(b.getAttribute("data-consent"));
        bar.classList.remove("show");
        // No non-essential scripts are loaded until accepted.
        if (b.getAttribute("data-consent") === "accepted") {
          document.dispatchEvent(new CustomEvent("cookies:accepted"));
        }
      });
    });
  }

  /* ---------- Form validation (client side) ----------
     Client-side checks improve UX only. ALL validation, sanitisation,
     rate-limiting and CAPTCHA verification MUST be repeated server-side
     before any data is stored or emailed. See CUSTOMIZE.md. */
  var emailRe = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  var phoneRe = /^[\d\s()+.\-]{7,20}$/;

  function showError(field, msg) {
    field.classList.add("invalid");
    var el = field.querySelector(".error");
    if (el && msg) el.textContent = msg;
    var input = field.querySelector("input,select,textarea");
    if (input) input.setAttribute("aria-invalid", "true");
  }
  function clearError(field) {
    field.classList.remove("invalid");
    var input = field.querySelector("input,select,textarea");
    if (input) input.removeAttribute("aria-invalid");
  }

  document.querySelectorAll("form[data-validate]").forEach(function (form) {
    var status = form.querySelector(".form-status");
    form.setAttribute("novalidate", "novalidate");

    form.addEventListener("submit", function (e) {
      e.preventDefault();
      var ok = true;
      var firstBad = null;

      // Honeypot: real users never fill this.
      var hp = form.querySelector(".hp input");
      if (hp && hp.value) { return; /* silently drop bots */ }

      form.querySelectorAll(".field").forEach(function (field) {
        var input = field.querySelector("input,select,textarea");
        if (!input) return;
        clearError(field);
        var val = (input.value || "").trim();

        if (input.required && !val) { showError(field, "This field is required."); ok = false; firstBad = firstBad || field; return; }
        if (val && input.type === "email" && !emailRe.test(val)) { showError(field, "Enter a valid email address."); ok = false; firstBad = firstBad || field; return; }
        if (val && input.type === "tel" && !phoneRe.test(val)) { showError(field, "Enter a valid phone number."); ok = false; firstBad = firstBad || field; return; }
        if (input.type === "checkbox" && input.required && !input.checked) { showError(field, "Please tick this box to continue."); ok = false; firstBad = firstBad || field; return; }
      });

      if (!ok) {
        if (status) { status.className = "form-status err"; status.textContent = "Please fix the highlighted fields and try again."; }
        if (firstBad) { var fi = firstBad.querySelector("input,select,textarea"); if (fi) fi.focus(); }
        return;
      }

      // Demo behaviour: no live backend is wired in this static build.
      // Replace this block with a fetch() to your secured endpoint.
      var btn = form.querySelector('button[type="submit"]');
      if (btn) { btn.disabled = true; btn.dataset.label = btn.textContent; btn.textContent = "Sending…"; }
      window.setTimeout(function () {
        if (status) {
          status.className = "form-status ok";
          status.textContent = form.getAttribute("data-success") ||
            "Thanks! Your request has been received. A Wascana team member will call you back shortly.";
        }
        form.reset();
        if (btn) { btn.disabled = false; btn.textContent = btn.dataset.label; }
        if (status) status.scrollIntoView({ behavior: "smooth", block: "center" });
      }, 700);
    });

    // Clear error as the user fixes the field.
    form.querySelectorAll("input,select,textarea").forEach(function (input) {
      input.addEventListener("input", function () {
        var field = input.closest(".field");
        if (field && field.classList.contains("invalid")) clearError(field);
      });
    });
  });

  /* ---------- Footer year ---------- */
  var y = document.getElementById("year");
  if (y) y.textContent = new Date().getFullYear();

  /* ---------- Mark current nav link ---------- */
  var path = location.pathname.replace(/index\.html$/, "").replace(/\/$/, "");
  document.querySelectorAll(".nav-links a").forEach(function (a) {
    // a.pathname is the browser-resolved absolute path, so this works whether
    // links are relative or absolute and regardless of the mount point.
    var ap = a.pathname.replace(/index\.html$/, "").replace(/\/$/, "");
    if (ap && ap === path) a.setAttribute("aria-current", "page");
  });
})();
