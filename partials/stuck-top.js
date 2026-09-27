  // Brave on the iPhone: pulling to refresh and pushing the page back up before the reload ends can
  // leave the page parked below the top of the screen, a blank band above the header. The iOS refresh
  // control removes its space but not the scroll offset, so the page sits at a negative scrollY and
  // nothing moves. A normal bounce never stays there (it keeps moving back to 0), so a negative scrollY
  // that holds still between two checks, with no finger on the screen, is that state: a 1 px scroll and
  // back makes the browser put the page in place. After a load and after every touch, for 2.4 s.
  (function () {
    var touching = false, timer = null;
    function watch() {
      clearTimeout(timer);
      var last = null, left = 12;
      (function check() {
        var y = window.scrollY;
        if (!touching && y < 0 && y === last) {
          window.scrollTo(0, 1);
          requestAnimationFrame(function () { window.scrollTo(0, 0); });
          return;
        }
        last = touching ? null : y;
        if (--left > 0) timer = setTimeout(check, 200);
      })();
    }
    function release(e) { touching = e.touches.length > 0; if (!touching) watch(); }
    addEventListener('touchstart', function () { touching = true; }, { passive: true });
    addEventListener('touchend', release, { passive: true });
    addEventListener('touchcancel', release, { passive: true });
    addEventListener('load', watch);
    addEventListener('pageshow', function (e) { if (e.persisted) watch(); });
  })();
