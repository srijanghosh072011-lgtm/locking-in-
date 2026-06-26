/* ==========================================================================
   BlueLine Plumbing — site interactions (vanilla JS, no dependencies)
   Progressive enhancement: every feature checks its elements exist first.
   ========================================================================== */
(function () {
  "use strict";

  var $ = function (sel, ctx) { return (ctx || document).querySelector(sel); };
  var $$ = function (sel, ctx) { return Array.prototype.slice.call((ctx || document).querySelectorAll(sel)); };

  /* ---------------------------------------------------- Footer year -- */
  $$("[data-year]").forEach(function (el) { el.textContent = new Date().getFullYear(); });

  /* ---------------------------------------------------- Mobile nav -- */
  var toggle = $(".nav-toggle");
  var links = $("#nav-links");
  if (toggle && links) {
    toggle.addEventListener("click", function () {
      var open = links.classList.toggle("is-open");
      toggle.setAttribute("aria-expanded", String(open));
    });
    // Close drawer when a link is chosen
    $$("a", links).forEach(function (a) {
      a.addEventListener("click", function () {
        links.classList.remove("is-open");
        toggle.setAttribute("aria-expanded", "false");
      });
    });
  }

  /* --------------------------------------------- Sticky header shadow -- */
  var header = $(".site-header");
  if (header) {
    var onScroll = function () { header.classList.toggle("is-scrolled", window.scrollY > 8); };
    window.addEventListener("scroll", onScroll, { passive: true });
    onScroll();
  }

  /* ----------------------------------------------------- FAQ accordion -- */
  $$(".faq-q").forEach(function (btn) {
    btn.addEventListener("click", function () {
      var expanded = btn.getAttribute("aria-expanded") === "true";
      var panel = document.getElementById(btn.getAttribute("aria-controls"));
      btn.setAttribute("aria-expanded", String(!expanded));
      if (panel) {
        panel.style.maxHeight = expanded ? null : panel.scrollHeight + "px";
      }
    });
  });

  /* --------------------------------------------------------- Toast -- */
  function showToast(message) {
    var toast = $("#toast");
    if (!toast) {
      toast = document.createElement("div");
      toast.id = "toast";
      toast.className = "toast";
      toast.setAttribute("role", "status");
      toast.setAttribute("aria-live", "polite");
      document.body.appendChild(toast);
    }
    toast.innerHTML =
      '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" aria-hidden="true"><polyline points="20 6 9 17 4 12"/></svg>' +
      '<span></span>';
    $("span", toast).textContent = message;
    toast.classList.add("is-visible");
    window.clearTimeout(toast._t);
    toast._t = window.setTimeout(function () { toast.classList.remove("is-visible"); }, 4200);
  }
  window.BlueLine = window.BlueLine || {};
  window.BlueLine.toast = showToast;

  /* ------------------------------------------------ Form validation -- */
  var EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/;
  var PHONE_RE = /^[+]?[\d\s().-]{7,}$/;

  function setError(field, msg) {
    field.classList.add("has-error");
    var input = $(".input, .select, .textarea", field) || $("input,select,textarea", field);
    if (input) input.setAttribute("aria-invalid", "true");
    var em = $(".error-msg", field);
    if (em && msg) em.textContent = msg;
  }
  function clearError(field) {
    field.classList.remove("has-error");
    var input = $(".input, .select, .textarea", field) || $("input,select,textarea", field);
    if (input) input.removeAttribute("aria-invalid");
  }

  function validateField(input) {
    var field = input.closest(".field");
    if (!field) return true;
    var val = (input.value || "").trim();
    if (input.hasAttribute("required") && !val) { setError(field, "This field is required."); return false; }
    if (val && input.type === "email" && !EMAIL_RE.test(val)) { setError(field, "Enter a valid email address."); return false; }
    if (val && input.getAttribute("inputmode") === "tel" && !PHONE_RE.test(val)) { setError(field, "Enter a valid phone number."); return false; }
    if (input.type === "checkbox" && input.hasAttribute("required") && !input.checked) { setError(field, "Please tick to continue."); return false; }
    clearError(field);
    return true;
  }

  $$("form[data-validate]").forEach(function (form) {
    // live-clear errors as the user types
    $$("input, select, textarea", form).forEach(function (input) {
      input.addEventListener("blur", function () { if (input.value) validateField(input); });
      input.addEventListener("input", function () {
        var field = input.closest(".field");
        if (field && field.classList.contains("has-error")) validateField(input);
      });
    });

    form.addEventListener("submit", function (e) {
      e.preventDefault();

      // Honeypot: real users never fill this hidden field
      var hp = $(".honeypot input", form);
      if (hp && hp.value) { return; /* silently drop bots */ }

      var ok = true;
      var firstBad = null;
      $$("input, select, textarea", form).forEach(function (input) {
        if (input.closest(".honeypot")) return;
        if (!validateField(input)) { ok = false; if (!firstBad) firstBad = input; }
      });

      var status = $(".form-status", form);
      if (!ok) {
        if (status) { status.className = "form-status is-error"; status.textContent = "Please fix the highlighted fields and try again."; }
        if (firstBad) firstBad.focus();
        return;
      }

      // Optimistic UI: disable + show progress.
      var submitBtn = $('button[type="submit"]', form);
      var original = submitBtn ? submitBtn.innerHTML : "";
      if (submitBtn) { submitBtn.disabled = true; submitBtn.innerHTML = "Sending…"; }

      function onSuccess() {
        if (status) {
          status.className = "form-status is-success";
          status.textContent = form.getAttribute("data-success") ||
            "Thanks! Your request has been received — we’ll be in touch shortly.";
        }
        showToast(form.getAttribute("data-toast") || "Sent successfully");
        form.reset();
        if (submitBtn) { submitBtn.disabled = false; submitBtn.innerHTML = original; }
      }
      function onError() {
        if (status) {
          status.className = "form-status is-error";
          status.textContent = "Sorry — that didn’t send. Please call (604) 555-0188 or try again.";
        }
        if (submitBtn) { submitBtn.disabled = false; submitBtn.innerHTML = original; }
      }

      // Real submission when configured. `data-netlify` works with zero config on
      // Netlify; `data-endpoint="https://…"` posts anywhere (Formspree, your API).
      // With neither, fall back to an optimistic demo so the UX is still complete.
      var endpoint = form.getAttribute("data-endpoint");
      var isNetlify = form.hasAttribute("data-netlify");
      if (endpoint || isNetlify) {
        var url = endpoint || form.getAttribute("action") || location.pathname;
        var body = new URLSearchParams(new FormData(form)).toString();
        fetch(url, {
          method: "POST",
          headers: { "Content-Type": "application/x-www-form-urlencoded" },
          body: body
        }).then(function (r) { return r.ok ? onSuccess() : onError(); }).catch(onError);
      } else {
        window.setTimeout(onSuccess, 700);
      }
    });
  });

  /* --------------------------------------------- Quote estimator -- */
  // Transparent ballpark ranges (CAD) for instant expectations — final price on inspection.
  var QUOTE = {
    "blocked-drain": [149, 420, "Blocked drain clearing"],
    "hot-water": [320, 1900, "Hot water repair / replace"],
    "tap-toilet": [120, 380, "Tap, toilet & leak repairs"],
    "gas": [180, 950, "Gas fitting & appliances"],
    "leak-detection": [160, 560, "Leak detection"],
    "emergency": [180, 700, "Emergency call-out"],
    "renovation": [2500, 18000, "Bathroom / kitchen rough-in"]
  };
  $$("form[data-quote]").forEach(function (form) {
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      var svc = $('[name="service"]', form);
      var result = $(".quote-result", form);
      if (!svc || !result) return;
      var pick = QUOTE[svc.value];
      if (!pick) { result.classList.add("is-visible"); result.querySelector("[data-est]").textContent = "Select a service"; return; }
      var fmt = function (n) { return "$" + n.toLocaleString("en-CA"); };
      result.classList.add("is-visible");
      result.querySelector("[data-est]").textContent = fmt(pick[0]) + "–" + fmt(pick[1]);
      var label = result.querySelector("[data-est-label]");
      if (label) label.textContent = pick[2];
      showToast("Estimate ready — book to lock it in");
    });
  });

  /* ----------------------------------------------- Cookie consent -- */
  // GDPR / Canada-aware: no non-essential cookies set until the visitor accepts.
  var CONSENT_KEY = "bl_cookie_consent_v1";
  var banner = $("#cookie-banner");
  function hasConsent() { try { return localStorage.getItem(CONSENT_KEY); } catch (e) { return "essential"; } }
  function saveConsent(value) {
    try { localStorage.setItem(CONSENT_KEY, value); } catch (e) {}
    if (banner) banner.classList.remove("is-visible");
    // If accepted, this is where analytics/marketing scripts would be initialised.
    if (value === "all") { /* loadAnalytics(); */ }
  }
  if (banner && !hasConsent()) {
    window.setTimeout(function () { banner.classList.add("is-visible"); }, 900);
  }
  var acceptBtn = $("#cookie-accept");
  var declineBtn = $("#cookie-decline");
  if (acceptBtn) acceptBtn.addEventListener("click", function () { saveConsent("all"); });
  if (declineBtn) declineBtn.addEventListener("click", function () { saveConsent("essential"); });

  /* ------------------------------------- Image load resilience -- */
  // If a remote photo fails to load, mark its frame so the navy block reads as intentional.
  $$("img[data-photo]").forEach(function (img) {
    img.addEventListener("error", function () { img.style.visibility = "hidden"; });
  });

  /* ----------------------------------------- Demo no-op links -- */
  $$("[data-noop]").forEach(function (a) {
    a.addEventListener("click", function (e) { e.preventDefault(); });
  });

  /* ------------------------------------------ Active nav state -- */
  (function () {
    var path = location.pathname.replace(/index\.html$/, "").replace(/\/$/, "") || "/";
    var seg = "/" + (path.split("/")[1] || "");
    $$(".nav-links > li > a[href]").forEach(function (a) {
      var href = a.getAttribute("href");
      if (!href || href.charAt(0) !== "/") return;
      var target = href.replace(/index\.html$/, "").replace(/\/$/, "") || "/";
      var tseg = "/" + (target.split("/")[1] || "");
      if (target === path || (tseg !== "/" && tseg === seg)) {
        a.setAttribute("aria-current", "page");
      }
    });
  })();

})();
