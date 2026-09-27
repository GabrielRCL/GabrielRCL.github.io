  // Pull to refresh, the site's own (the gesture and its numbers come from Mar & Minas' lib/puxar.js).
  // The browser's is off on touch screens (overscroll-behavior, base.css): on the iPhone, in Safari and
  // in Brave, it could leave the page parked under a blank band after the reload. The indicator follows
  // half of the finger (the resistance that makes it feel pulled) up to 100 px; from 64 px a release
  // reloads the page, and the circle fills with the sunset to say so. A touch becomes a pull only with
  // the page at the top, one finger, a move down and mostly vertical (the screenshot thumbnails scroll
  // sideways), and never on the open phone menu or in a dialog.
  (function () {
    if (!('ontouchstart' in window)) return;
    var THRESHOLD = 64, MAX = 100;
    var bar = document.querySelector('.topbar');
    var el = document.createElement('div');
    el.className = 'ptr';
    el.setAttribute('role', 'status');
    el.setAttribute('aria-live', 'polite');
    el.innerHTML = '<span class="ptr-dot"><svg class="ic"><use href="#lu-refresh-cw"/></svg></span><span class="ptr-msg"></span>';
    document.body.appendChild(el);
    var icon = el.querySelector('.ic'), msg = el.querySelector('.ptr-msg');
    var touch = null, dist = 0, busy = false;

    function show(d, dragging) {
      dist = d;
      el.classList.toggle('dragging', dragging);
      el.classList.toggle('armed', d >= THRESHOLD);
      el.style.transform = 'translateY(' + (d - 52) + 'px)';
      el.style.opacity = String(Math.min(1, d / (THRESHOLD * 0.6)));
      icon.style.transform = 'rotate(' + d * 3 + 'deg)';
    }
    function blocked(target) {
      return (bar && bar.classList.contains('open')) || Boolean(target.closest && target.closest('dialog'));
    }
    addEventListener('touchstart', function (e) {
      touch = null;
      if (busy || e.touches.length !== 1 || window.scrollY > 0 || blocked(e.target)) return;
      touch = { x: e.touches[0].clientX, y: e.touches[0].clientY, pulling: false };
    }, { passive: true });
    addEventListener('touchmove', function (e) {
      if (!touch) return;
      var dx = e.touches[0].clientX - touch.x, dy = e.touches[0].clientY - touch.y, side = Math.abs(dx);
      if (!touch.pulling) {
        if (dy < -4 || (side > 8 && side >= dy)) { touch = null; return; }
        if (!(dy > 8 && dy > side * 1.5)) return;
        touch.pulling = true;
        el.style.top = (bar ? Math.max(0, bar.getBoundingClientRect().bottom) : 0) + 'px';
      }
      show(Math.min(MAX, Math.max(0, dy) * 0.5), true);
    }, { passive: true });
    addEventListener('touchend', function () {
      var t = touch;
      touch = null;
      if (!t || !t.pulling) return;
      if (dist < THRESHOLD) { show(0, false); return; }
      busy = true;
      show(THRESHOLD, false);
      el.classList.add('busy');
      msg.textContent = document.documentElement.getAttribute('data-lang') === 'pt' ? 'Atualizando' : 'Refreshing';
      setTimeout(function () { location.reload(); }, 300);
    });
    addEventListener('touchcancel', function () {
      var t = touch;
      touch = null;
      if (t && t.pulling) show(0, false);
    });
    // back to a page kept in memory (the browser's back button): the indicator was left spinning
    addEventListener('pageshow', function (e) {
      if (!e.persisted) return;
      busy = false;
      el.classList.remove('busy');
      msg.textContent = '';
      show(0, false);
    });
  })();
