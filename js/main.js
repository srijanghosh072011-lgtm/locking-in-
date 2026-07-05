/* Plumbo Regina — shared behaviour (no dependencies) */
(function () {
  'use strict';

  /* ---------- mobile nav ---------- */
  var toggle = document.querySelector('.nav-toggle');
  var nav = document.querySelector('.main-nav');
  if (toggle && nav) {
    toggle.addEventListener('click', function () {
      var open = nav.classList.toggle('open');
      toggle.setAttribute('aria-expanded', String(open));
    });
  }

  /* ---------- services dropdown ---------- */
  document.querySelectorAll('.nav-drop').forEach(function (drop) {
    var btn = drop.querySelector('button');
    if (!btn) return;
    btn.addEventListener('click', function (e) {
      e.stopPropagation();
      var open = drop.classList.toggle('open');
      btn.setAttribute('aria-expanded', String(open));
    });
  });
  document.addEventListener('click', function (e) {
    document.querySelectorAll('.nav-drop.open').forEach(function (drop) {
      if (!drop.contains(e.target)) {
        drop.classList.remove('open');
        var btn = drop.querySelector('button');
        if (btn) btn.setAttribute('aria-expanded', 'false');
      }
    });
  });
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') {
      document.querySelectorAll('.nav-drop.open').forEach(function (drop) {
        drop.classList.remove('open');
      });
    }
  });

  /* ---------- image fallback: swap broken hotlinked photos for styled placeholder ---------- */
  var FALLBACK =
    'data:image/svg+xml;utf8,' +
    encodeURIComponent(
      '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 600">' +
        '<defs><linearGradient id="g" x1="0" y1="0" x2="1" y2="1">' +
        '<stop offset="0" stop-color="#14232E"/><stop offset="1" stop-color="#244050"/>' +
        '</linearGradient></defs>' +
        '<rect width="800" height="600" fill="url(#g)"/>' +
        '<g transform="translate(340,240)" stroke="#F4520B" stroke-width="10" fill="none" stroke-linecap="round">' +
        '<path d="M20 100 L100 20"/><path d="M0 80 a28 28 0 1 0 40 40"/><path d="M80 0 a28 28 0 1 1 40 40"/>' +
        '</g>' +
        '<text x="400" y="420" text-anchor="middle" font-family="monospace" font-size="22" letter-spacing="4" fill="#B7AA9C">PLUMBO — PHOTO SLOT</text>' +
      '</svg>'
    );
  function armFallback(img) {
    img.addEventListener('error', function handler() {
      img.removeEventListener('error', handler);
      img.src = FALLBACK;
      img.removeAttribute('srcset');
    });
    /* already failed before JS ran */
    if (img.complete && img.naturalWidth === 0 && img.src.indexOf('data:') !== 0) {
      img.src = FALLBACK;
      img.removeAttribute('srcset');
    }
  }
  document.querySelectorAll('img[data-photo]').forEach(armFallback);

  /* ---------- reveal on scroll ---------- */
  var reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var revealEls = document.querySelectorAll('.reveal');
  if (reduced || !('IntersectionObserver' in window)) {
    revealEls.forEach(function (el) { el.classList.add('in'); });
  } else {
    var io = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (entry) {
          if (entry.isIntersecting) {
            entry.target.classList.add('in');
            io.unobserve(entry.target);
          }
        });
      },
      { threshold: 0.12, rootMargin: '0px 0px -40px 0px' }
    );
    revealEls.forEach(function (el) { io.observe(el); });
  }

  /* ---------- services carousel counter + next button ---------- */
  document.querySelectorAll('[data-carousel]').forEach(function (root) {
    var track = root.querySelector('.carousel');
    var count = root.querySelector('.carousel-count');
    var next = root.querySelector('.carousel-next');
    if (!track) return;
    var cards = track.children.length;
    function update() {
      if (!count) return;
      var cardW = track.children[0] ? track.children[0].offsetWidth + 26 : 1;
      var idx = Math.min(cards, Math.round(track.scrollLeft / cardW) + 1);
      count.textContent = idx + ' / ' + cards;
    }
    track.addEventListener('scroll', update, { passive: true });
    window.addEventListener('resize', update);
    if (next) {
      next.addEventListener('click', function () {
        var cardW = track.children[0] ? track.children[0].offsetWidth + 26 : 300;
        var max = track.scrollWidth - track.clientWidth;
        track.scrollBy({
          left: track.scrollLeft >= max - 10 ? -max : cardW,
          behavior: reduced ? 'auto' : 'smooth'
        });
      });
    }
    update();
  });

  /* ---------- forms: validation + honeypot ---------- */
  document.querySelectorAll('form[data-validate]').forEach(function (form) {
    var status = form.querySelector('.form-status');
    form.addEventListener('submit', function (e) {
      /* honeypot: bots fill the hidden field — silently drop */
      var hp = form.querySelector('.hp-field input');
      if (hp && hp.value) { e.preventDefault(); return; }

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
        if (status) {
          status.className = 'form-status fail';
          status.textContent = 'Please fix the highlighted fields and try again.';
        }
        var firstBad = form.querySelector('[aria-invalid="true"]');
        if (firstBad) firstBad.focus();
        return;
      }

      /* No backend wired yet: show confirmation instead of navigating to "#".
         Remove this block once the form action points at a real endpoint
         (Netlify Forms, Formspree, Web3Forms, etc. — see README). */
      if (form.getAttribute('action') === '#') {
        e.preventDefault();
        if (status) {
          status.className = 'form-status ok';
          status.textContent = 'Thanks! Your request is saved locally for demo purposes — connect a form service to receive it by email (see README).';
        }
        form.reset();
      }
    });
  });

  /* ---------- cookie consent (Canada/EU) ---------- */
  var banner = document.querySelector('.cookie-banner');
  if (banner) {
    var choice = null;
    try { choice = localStorage.getItem('plumbo-cookie-choice'); } catch (err) { /* storage blocked */ }
    if (!choice) banner.classList.add('show');
    banner.querySelectorAll('[data-cookie]').forEach(function (btn) {
      btn.addEventListener('click', function () {
        try { localStorage.setItem('plumbo-cookie-choice', btn.getAttribute('data-cookie')); } catch (err) { /* ignore */ }
        banner.classList.remove('show');
        /* Analytics/marketing scripts must only be injected here when
           choice === 'accept'. None are bundled by default. */
      });
    });
  }

  /* ---------- footer year ---------- */
  document.querySelectorAll('[data-year]').forEach(function (el) {
    el.textContent = String(new Date().getFullYear());
  });
})();
