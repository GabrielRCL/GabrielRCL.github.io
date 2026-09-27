  // ===== Motion: scroll-linked scenes (rules in partials/motion.css) ================================
  // Scrolling stays native. Each scene gets --p from 0 to 1 as it enters (the hero: as it leaves).
  // Viewers who ask for reduced motion get the static page: html.motion is never set.

  if (!reduceMotion && window.requestAnimationFrame) (function () {
    root.classList.add('motion');
    var targets = [];

    function mark(sel, mode, range) {
      document.querySelectorAll(sel).forEach(function (el) {
        el.setAttribute('data-p', mode);
        targets.push({ el: el, mode: mode, range: range || 0.45, last: -1 });
      });
    }
    function stagger(sel, child) {
      document.querySelectorAll(sel).forEach(function (box) {
        var kids = box.querySelectorAll(child);
        kids.forEach(function (k, i) { k.style.setProperty('--f', kids.length > 1 ? (i / (kids.length - 1)).toFixed(3) : '0'); });
      });
    }

    mark('.hero-band', 'leave');
    mark('.hero .link', 'enter', 0.3);
    mark('main > section', 'enter', 0.4);
    mark('.companies', 'enter', 0.35);
    mark('.case', 'enter', 0.45);
    mark('.stats', 'enter', 0.6);
    mark('.feature', 'enter', 0.5);
    mark('.product', 'enter', 0.55);
    mark('.side', 'enter', 0.6);
    mark('.timeline', 'enter', 0.85);
    mark('.tier', 'enter', 0.7);
    mark('.two', 'enter', 0.5);
    mark('.contact-grid', 'enter', 0.5);
    mark('.site-footer', 'enter', 0.35);
    stagger('.stats', '.stat');
    stagger('.roles', 'li');
    stagger('.side', ':scope > div');
    stagger('.timeline', 'li');
    stagger('.tier', '.chips li');
    stagger('.rows', 'li');
    stagger('.contact-list', 'li');

    // Stack chips start scattered; the offsets are fixed per position so every visit looks the same.
    document.querySelectorAll('.tier .chips li').forEach(function (li, i) {
      li.style.setProperty('--dx', (((i * 37) % 11) - 5) * 28 + 'px');
      li.style.setProperty('--dy', (70 + ((i * 53) % 7) * 20) + 'px');
      li.style.setProperty('--r', (((i * 29) % 9) - 4) * 8 + 'deg');
    });

    // Numbers count up once, the first time they come into view.
    var counters = [].slice.call(document.querySelectorAll('[data-count]')).map(function (el) {
      return { el: el, to: parseFloat(el.getAttribute('data-count')), locale: el.closest('.pt') ? 'pt-BR' : 'en-US', done: false };
    });
    function countUp(c) {
      c.done = true;
      var t0 = performance.now();
      (function step(now) {
        var k = Math.min(1, (now - t0) / 1400);
        c.el.textContent = Math.round(c.to * (1 - Math.pow(1 - k, 4))).toLocaleString(c.locale);
        if (k < 1) requestAnimationFrame(step);
      })(t0);
    }

    // Progress bar, the scene rail on the left and the timecode, like a video player.
    var bar = document.createElement('div');
    bar.className = 'progress';
    document.body.appendChild(bar);
    var scenes = [document.getElementById('top')].concat([].slice.call(document.querySelectorAll('main > section[id]')));
    function labelOf(sec) {
      if (sec.hasAttribute('data-label-en')) return [sec.getAttribute('data-label-en'), sec.getAttribute('data-label-pt')];
      var h = sec.querySelector('h2') || sec.querySelector('h3');
      var en = h.querySelector('.en'), pt = h.querySelector('.pt');
      return [(en || h).textContent.trim(), (pt || h).textContent.trim()];
    }
    var rail = document.createElement('nav');
    rail.className = 'rail';
    rail.setAttribute('aria-label', 'Scenes');
    rail.innerHTML = '<span class="rail-fill"></span><span class="rail-dot"></span>';
    var nodes = scenes.map(function (sec, i) {
      var l = labelOf(sec);
      var a = document.createElement('a');
      a.className = 'rail-node' + (i === scenes.length - 1 ? ' end' : '');
      a.href = '#' + sec.id;
      a.innerHTML = '<span><span class="en"></span><span class="pt"></span></span>';
      a.querySelector('.en').textContent = l[0];
      a.querySelector('.pt').textContent = l[1];
      a.addEventListener('click', function (e) {
        e.preventDefault();
        var bar = sec.id === 'top' ? 0 : document.querySelector('.topbar').offsetHeight;
        window.scrollTo({ top: sec.getBoundingClientRect().top + scrollY - bar, behavior: 'smooth' });
      });
      rail.appendChild(a);
      return a;
    });
    document.body.appendChild(rail);
    var hud = document.createElement('div');
    hud.className = 'hud';
    hud.setAttribute('aria-hidden', 'true');
    hud.innerHTML = '<span class="play"></span><b class="tc">00:00:00</b><span class="sc"></span><span class="scene"><span class="en"></span><span class="pt"></span></span>';
    document.body.appendChild(hud);
    var tc = hud.querySelector('.tc'), sc = hud.querySelector('.sc');
    var sceneEn = hud.querySelector('.scene .en'), scenePt = hud.querySelector('.scene .pt');
    var REEL = 90; // seconds: the whole page reads as a 1:30 reel
    var current = -1;

    function layout() {
      var max = Math.max(1, document.documentElement.scrollHeight - innerHeight);
      scenes.forEach(function (sec, i) {
        var y = Math.min(1, (sec.getBoundingClientRect().top + scrollY) / max);
        nodes[i].style.setProperty('--y', (y * 100).toFixed(2) + '%');
      });
    }

    function update() {
      ticking = false;
      var vh = innerHeight;
      var rects = targets.map(function (t) { return t.el.getBoundingClientRect(); });
      targets.forEach(function (t, i) {
        var r = rects[i], p;
        if (t.mode === 'leave') p = -r.top / Math.max(1, r.height);
        else p = (vh - r.top) / (vh * t.range);
        p = Math.min(1, Math.max(0, p));
        if (t.mode === 'enter') p = 1 - Math.pow(1 - p, 3);
        var v = Math.round(p * 1000) / 1000;
        if (v !== t.last) { t.el.style.setProperty('--p', v); t.last = v; }
      });

      counters.forEach(function (c) {
        if (c.done) return;
        var r = c.el.getBoundingClientRect();
        if (r.bottom > 0 && r.top < vh * 0.88 && r.height) countUp(c);
      });

      var max = Math.max(1, document.documentElement.scrollHeight - vh);
      var gp = Math.min(1, Math.max(0, scrollY / max));
      var g = gp.toFixed(4);
      bar.style.setProperty('--gp', g);
      rail.style.setProperty('--gp', g);
      var now = 0;
      scenes.forEach(function (sec, i) { if (sec.getBoundingClientRect().top <= vh * 0.45) now = i; });
      if (gp > 0.995) now = scenes.length - 1;
      if (now !== current) {
        current = now;
        nodes.forEach(function (n, i) { n.classList.toggle('on', i < now); n.classList.toggle('now', i === now); });
        var l = labelOf(scenes[now]);
        sc.textContent = String(now + 1).padStart(2, '0') + ' / ' + String(scenes.length).padStart(2, '0');
        sceneEn.textContent = l[0];
        scenePt.textContent = l[1];
      }
      var s = gp * REEL;
      tc.textContent = [Math.floor(s / 60), Math.floor(s % 60), Math.floor((s % 1) * 24)].map(function (n) { return String(n).padStart(2, '0'); }).join(':');
    }

    var ticking = false;
    function schedule() { if (!ticking) { ticking = true; requestAnimationFrame(update); } }
    addEventListener('scroll', schedule, { passive: true });
    addEventListener('resize', function () { layout(); schedule(); });
    addEventListener('load', function () { layout(); schedule(); });
    layout();
    update();
  })();
