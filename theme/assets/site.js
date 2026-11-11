// Тихое появление блоков при прокрутке. При «уменьшить движение» — ничего не двигается, SVG-анимации на паузе.
(function () {
  var reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var blocks = document.querySelectorAll('.reveal');
  if (reduce) {
    document.querySelectorAll('svg').forEach(function (s) { if (s.pauseAnimations) s.pauseAnimations(); });
    blocks.forEach(function (b) { b.classList.add('is-in'); });
    return;
  }
  if (!('IntersectionObserver' in window)) { blocks.forEach(function (b) { b.classList.add('is-in'); }); return; }
  var io = new IntersectionObserver(function (entries) {
    entries.forEach(function (e) {
      if (e.isIntersecting) { e.target.classList.add('is-in'); io.unobserve(e.target); }
    });
  }, { rootMargin: '0px 0px -10% 0px' });
  blocks.forEach(function (b) { io.observe(b); });
})();

// Ссылки на канал из текста страниц и статей открываются в новой вкладке (в шаблонах это задано прямо в разметке).
(function () {
  document.querySelectorAll('a[href*="t.me/everveyratarot"]').forEach(function (a) {
    a.target = '_blank';
    a.rel = 'noopener';
  });
})();

// Цели Метрики: клик по записи в личку и по каналу. Без счётчика (metrika_id пуст) — ничего.
(function () {
  document.addEventListener('click', function (e) {
    var a = e.target.closest && e.target.closest('a[href*="t.me/"]');
    if (!a || !window.ym || !window.METRIKA_ID) return;
    var goal = a.href.indexOf('t.me/everveyratarot') !== -1 ? 'channel_click'
      : a.href.indexOf('t.me/everveyra') !== -1 ? 'booking_click' : '';
    if (goal) window.ym(window.METRIKA_ID, 'reachGoal', goal);
  });
})();

// Шапка телефона: на главной появляется, когда первый экран ушёл под неё; бургер открывает боковое меню.
(function () {
  var bar = document.querySelector('.mbar');
  var drawer = document.getElementById('menu');
  if (!bar || !drawer) return;
  var hero = document.querySelector('.hero');
  if (hero && bar.classList.contains('mbar--auto')) {
    var tick = false;
    var update = function () {
      tick = false;
      bar.classList.toggle('is-shown', hero.getBoundingClientRect().bottom <= bar.offsetHeight);
    };
    window.addEventListener('scroll', function () { if (!tick) { tick = true; requestAnimationFrame(update); } }, { passive: true });
    window.addEventListener('resize', update);
    update();
  }
  var burger = bar.querySelector('.burger');
  var close = drawer.querySelector('.drawer__x');
  function set(open) {
    drawer.classList.toggle('is-open', open);
    burger.setAttribute('aria-expanded', open ? 'true' : 'false');
    document.documentElement.style.overflow = open ? 'hidden' : '';
    (open ? close : burger).focus({ preventScroll: true });
  }
  burger.addEventListener('click', function () { set(true); });
  drawer.addEventListener('click', function (e) {
    if (e.target.closest('[data-close]') || e.target.closest('a')) set(false);
  });
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape' && drawer.classList.contains('is-open')) set(false);
  });
})();
