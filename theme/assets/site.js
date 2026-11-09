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
