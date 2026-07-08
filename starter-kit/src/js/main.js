/* Starter kit — shared behaviour (no dependencies, no inline scripts). */
(function () {
  'use strict';

  /* Enhancement flag — replaces the old inline <head> script, so the CSP
     can use script-src 'self' with NO 'unsafe-inline'. */
  document.documentElement.classList.add('js');

  /* ---------- mobile nav ---------- */
  var toggle = document.querySelector('.nav-toggle');
  var nav = document.querySelector('.main-nav');
  if (toggle && nav) {
    toggle.addEventListener('click', function () {
      var open = nav.classList.toggle('open');
      toggle.setAttribute('aria-expanded', String(open));
    });
  }

  /* ---------- reveal on scroll ---------- */
  var reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var revealEls = document.querySelectorAll('.reveal');
  if (reduced || !('IntersectionObserver' in window)) {
    revealEls.forEach(function (el) { el.classList.add('in'); });
  } else {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) { entry.target.classList.add('in'); io.unobserve(entry.target); }
      });
    }, { threshold: 0.12, rootMargin: '0px 0px -40px 0px' });
    revealEls.forEach(function (el) { io.observe(el); });
  }

  /* ---------- forms: validation + honeypot + inline feedback ---------- */
  document.querySelectorAll('form[data-validate]').forEach(function (form) {
    var status = form.querySelector('.form-status');
    form.addEventListener('submit', function (e) {
      var hp = form.querySelector('.hp-field input');
      if (hp && hp.value) { e.preventDefault(); return; } /* bot */

      var ok = true;
      form.querySelectorAll('[required]').forEach(function (input) {
        var field = input.closest('.field');
        var valid = input.checkValidity();
        if (input.type === 'tel' && input.value) {
          valid = /^[0-9()+\-.\s]{7,20}$/.test(input.value);
        }
        if (field) field.classList.toggle('invalid', !valid);
        input.setAttribute('aria-invalid', String(!valid));
        if (!valid) ok = false;
      });
      if (!ok) {
        e.preventDefault();
        if (status) { status.className = 'form-status fail'; status.textContent = 'Please fix the highlighted fields.'; }
        var firstBad = form.querySelector('[aria-invalid="true"]');
        if (firstBad) firstBad.focus();
        return;
      }

      e.preventDefault(); /* take over so we can show inline feedback */
      var keyField = form.querySelector('input[name="access_key"]');
      var key = keyField ? keyField.value : '';

      /* Placeholder key -> demo mode instead of POSTing to a dead endpoint.
         The build script REFUSES to ship a placeholder, so this only fires
         during local preview. */
      if (!key || key.indexOf('YOUR_') === 0 || key.indexOf('{{') === 0) {
        if (status) { status.className = 'form-status ok'; status.textContent = 'Looks good! (Demo mode — set a real Web3Forms key to go live.)'; }
        form.reset();
        return;
      }

      var btn = form.querySelector('button[type="submit"]');
      var label = btn ? btn.textContent : '';
      if (btn) { btn.disabled = true; btn.textContent = 'Sending…'; }
      fetch(form.action, { method: 'POST', body: new FormData(form), headers: { 'Accept': 'application/json' } })
        .then(function (r) { return r.json().catch(function () { return {}; }).then(function (j) { return { ok: r.ok, data: j }; }); })
        .then(function (res) {
          if (status) {
            status.className = 'form-status ' + (res.ok ? 'ok' : 'fail');
            status.textContent = res.ok ? "Thanks! We'll call you back shortly."
              : ((res.data && res.data.message) || 'Something went wrong — please call us instead.');
          }
          if (res.ok) form.reset();
        })
        .catch(function () {
          if (status) { status.className = 'form-status fail'; status.textContent = 'Network error — please call us or try again.'; }
        })
        .then(function () { if (btn) { btn.disabled = false; btn.textContent = label; } });
    });
  });

  /* ---------- cookie consent ---------- */
  var banner = document.querySelector('.cookie-banner');
  if (banner) {
    var choice = null;
    try { choice = localStorage.getItem('cookie-choice'); } catch (err) {}
    if (!choice) banner.classList.add('show');
    banner.querySelectorAll('[data-cookie]').forEach(function (btn) {
      btn.addEventListener('click', function () {
        try { localStorage.setItem('cookie-choice', btn.getAttribute('data-cookie')); } catch (err) {}
        banner.classList.remove('show');
        /* Only inject analytics/marketing scripts here when choice === 'accept'. */
      });
    });
  }

  /* ---------- footer year ---------- */
  document.querySelectorAll('[data-year]').forEach(function (el) {
    el.textContent = String(new Date().getFullYear());
  });
})();
