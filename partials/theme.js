  // Theme: follows the system until the viewer picks one (saved, applied before paint by theme-head.html).
  // Picking the system's own theme clears the choice, so the page follows the system again.
  var themeQuery = window.matchMedia ? window.matchMedia('(prefers-color-scheme: dark)') : null;
  function systemTheme() { return themeQuery && themeQuery.matches ? 'dark' : 'light'; }
  function currentTheme() { return root.getAttribute('data-theme') || systemTheme(); }
  function paintTheme() {
    var t = currentTheme();
    // the browser bar (and the space above the page when it is pulled down) takes the page's color
    document.querySelectorAll('meta[name="theme-color"]').forEach(function (m) { m.setAttribute('content', t === 'dark' ? '#060b1f' : '#f8fafc'); });
    document.querySelectorAll('[data-set-theme]').forEach(function (b) { b.setAttribute('aria-pressed', String(b.getAttribute('data-set-theme') === t)); });
    document.querySelectorAll('[data-toggle-theme]').forEach(function (b) {
      b.setAttribute('aria-pressed', String(t === 'dark'));
      b.setAttribute('aria-label', t === 'dark' ? 'Switch to the light theme' : 'Switch to the dark theme');
    });
  }
  function setTheme(t) {
    if (t === systemTheme()) {
      root.removeAttribute('data-theme');
      try { localStorage.removeItem('theme'); } catch (e) {}
    } else {
      root.setAttribute('data-theme', t);
      try { localStorage.setItem('theme', t); } catch (e) {}
    }
    paintTheme();
  }
  document.querySelectorAll('[data-set-theme]').forEach(function (b) {
    b.addEventListener('click', function () { setTheme(b.getAttribute('data-set-theme')); });
  });
  document.querySelectorAll('[data-toggle-theme]').forEach(function (b) {
    b.addEventListener('click', function () { setTheme(currentTheme() === 'dark' ? 'light' : 'dark'); });
  });
  if (themeQuery && themeQuery.addEventListener) themeQuery.addEventListener('change', paintTheme);
  paintTheme();
