// Астро-таро: по дате рождения — положение Солнца, его декан и карты. Всё считается здесь, ничего не уходит на сервер.
(function () {
  var D = window.ASTRO;
  var form = document.getElementById('astro-form');
  var out = document.getElementById('astro-result');
  var me = document.currentScript || document.querySelector('script[data-cards]');
  var CARDS = me.getAttribute('data-cards');
  var TG = me.getAttribute('data-tg');
  if (!D || !form) return;

  // Барабаны даты, как в iPhone: прокрутка со щелчком на строку, значение — в скрытом #astro-date.
  var MONTHS = ['января', 'февраля', 'марта', 'апреля', 'мая', 'июня', 'июля', 'августа', 'сентября', 'октября', 'ноября', 'декабря'];
  var ROW = 40;
  var YEAR_MAX = new Date().getFullYear(), YEAR_MIN = 1930;
  var field = document.getElementById('astro-date');
  var cols = {};
  var sel = { d: 1, m: 0, y: 1990 };
  var values = {
    d: Array.from({ length: 31 }, function (_, i) { return i + 1; }),
    m: MONTHS.map(function (_, i) { return i; }),
    y: Array.from({ length: YEAR_MAX - YEAR_MIN + 1 }, function (_, i) { return YEAR_MIN + i; })
  };
  function label(kind, v) { return kind === 'm' ? MONTHS[v] : String(v); }
  function daysIn(m, y) { return new Date(Date.UTC(y, m + 1, 0)).getUTCDate(); }

  function sync() {
    var max = daysIn(sel.m, sel.y);
    cols.d.querySelectorAll('.wheel__item').forEach(function (el, i) { el.classList.toggle('wheel__item--off', i + 1 > max); });
    if (sel.d > max) { sel.d = max; scrollTo('d', max - 1, true); }
    field.value = sel.y + '-' + String(sel.m + 1).padStart(2, '0') + '-' + String(sel.d).padStart(2, '0');
  }
  function scrollTo(kind, i, smooth) {
    cols[kind].scrollTo({ top: i * ROW, behavior: smooth ? 'smooth' : 'auto' });
  }
  // Строки дальше от центра — бледнее и повёрнуты, как на барабане.
  function shade(col) {
    var mid = col.scrollTop + 80;
    col.querySelectorAll('.wheel__item').forEach(function (el, i) {
      var dist = (i * ROW - (mid - 80)) / ROW;
      var a = Math.max(-2.5, Math.min(2.5, dist));
      el.style.transform = 'rotateX(' + (-a * 18) + 'deg) scale(' + (1 - Math.abs(a) * 0.06) + ')';
      el.style.opacity = String(Math.max(0.25, 1 - Math.abs(a) * 0.3));
    });
  }

  document.querySelectorAll('#astro-wheel .wheel__col').forEach(function (col) {
    var kind = col.getAttribute('data-kind');
    cols[kind] = col;
    var html = '<div class="wheel__pad"></div>';
    values[kind].forEach(function (v, i) { html += '<div class="wheel__item" data-i="' + i + '">' + label(kind, v) + '</div>'; });
    col.innerHTML = html + '<div class="wheel__pad"></div>';
    col.style.perspective = '600px';

    var timer, frame;
    col.addEventListener('scroll', function () {
      if (!frame) frame = requestAnimationFrame(function () { frame = 0; shade(col); });
      clearTimeout(timer);
      timer = setTimeout(function () {
        var i = Math.max(0, Math.min(values[kind].length - 1, Math.round(col.scrollTop / ROW)));
        sel[kind] = values[kind][i];
        col.setAttribute('aria-valuetext', label(kind, sel[kind]));
        sync();
      }, 90);
    }, { passive: true });
    col.addEventListener('click', function (e) {
      var it = e.target.closest('.wheel__item');
      if (it) scrollTo(kind, +it.getAttribute('data-i'), true);
    });
    col.addEventListener('keydown', function (e) {
      if (e.key !== 'ArrowUp' && e.key !== 'ArrowDown') return;
      e.preventDefault();
      var i = Math.round(col.scrollTop / ROW) + (e.key === 'ArrowDown' ? 1 : -1);
      scrollTo(kind, Math.max(0, Math.min(values[kind].length - 1, i)), true);
    });
  });
  document.querySelectorAll('.wheel-arrow').forEach(function (btn) {
    btn.addEventListener('click', function () {
      var kind = btn.getAttribute('data-kind'), col = cols[kind];
      var i = Math.round(col.scrollTop / ROW) + (+btn.getAttribute('data-step'));
      scrollTo(kind, Math.max(0, Math.min(values[kind].length - 1, i)), true);
    });
  });
  requestAnimationFrame(function () {
    scrollTo('d', sel.d - 1); scrollTo('m', sel.m); scrollTo('y', sel.y - YEAR_MIN);
    Object.keys(cols).forEach(function (k) { shade(cols[k]); });
    sync();
    // Ссылка на результат: #1990-03-25 — сразу показать карту этой даты.
    var h = /^#(\d{4})-(\d{2})-(\d{2})$/.exec(location.hash);
    if (h && +h[1] >= YEAR_MIN && +h[1] <= YEAR_MAX && +h[2] >= 1 && +h[2] <= 12 && +h[3] >= 1 && +h[3] <= daysIn(+h[2] - 1, +h[1])) {
      sel = { d: +h[3], m: +h[2] - 1, y: +h[1] };
      scrollTo('d', sel.d - 1); scrollTo('m', sel.m); scrollTo('y', sel.y - YEAR_MIN);
      sync();
      form.requestSubmit ? form.requestSubmit() : form.dispatchEvent(new Event('submit', { cancelable: true }));
    }
  });

  // Долгота Солнца, точность около 0,01° (формула Астрономического ежегодника).
  function sunLon(ms) {
    var n = ms / 86400000 + 2440587.5 - 2451545;
    var L = 280.460 + 0.9856474 * n;
    var g = (357.528 + 0.9856003 * n) * Math.PI / 180;
    var lon = L + 1.915 * Math.sin(g) + 0.020 * Math.sin(2 * g);
    return ((lon % 360) + 360) % 360;
  }
  function decanAt(ms) { return Math.floor(sunLon(ms) / 10) % 36; }

  // Сутки берутся по Москве: если в этот день Солнце перешло границу, находим примерное время перехода.
  function whenChanged(a, b) {
    var d0 = decanAt(a);
    for (var i = 0; i < 30; i++) { var m = (a + b) / 2; if (decanAt(m) === d0) a = m; else b = m; }
    var t = new Date(b + 3 * 3600000);
    var hh = t.getUTCHours(), mm = t.getUTCMinutes();
    return (hh < 10 ? '0' : '') + hh + ':' + (mm < 10 ? '0' : '') + mm;
  }
  // Знак — по 30°, карта двора — по 30° со сдвигом: от 20° Рыб (350°). Обе границы совпадают с границами деканов.
  function signOf(dec) { return D.signs[Math.floor(dec / 3)]; }
  function courtOf(dec) { return D.courts[Math.floor((((dec * 10 + 5 - 350) % 360) + 360) % 360 / 30)]; }

  function esc(s) { return String(s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }
  function pic(id, alt, cls) {
    return id ? '<img class="' + cls + '" src="' + CARDS + id + '.webp" alt="' + esc(alt) + '" loading="lazy" width="360" height="604" />'
              : '<div class="' + cls + ' astro__noimg"><span>' + esc(alt) + '</span></div>';
  }
  function card(n, label, id, name, text, shadow) {
    return '<div class="astro__main">' + pic(id, name, 'astro__card') +
      '<div><span class="tag">' + n + ' · ' + esc(label) + '</span>' +
      '<h2 class="astro__title">' + esc(name) + '</h2>' +
      '<p>' + esc(text) + '</p><p class="astro__shadow"><b>Тень.</b> ' + esc(shadow) + '</p></div></div>';
  }
  // Три главные карты: знак, покровитель знака, карта двора.
  function main(dec) {
    var s = signOf(dec), pl = D.planets[s.ruler], c = courtOf(dec);
    return '<div class="astro__three">' +
      card(1, 'Знак — ' + s.sign, s.img, s.arcanum, s.text, s.shadow) +
      card(2, 'Покровитель — ' + s.ruler, pl.img, pl.arcanum, pl.text, pl.shadow) +
      card(3, 'Карта двора', c.img, c.card, c.text, c.shadow) +
      '</div>';
  }
  // Младший аркан «Солнце в знаке» — только дополняет, и есть не у всех знаков.
  function extra(dec) {
    var d = signOf(dec).minor;
    if (!d) return '';
    return '<div class="astro__more"><h3 class="astro__h3">Дополняет</h3>' +
      '<p class="astro__hint">Младший аркан, где Солнце стоит в вашем знаке: он уточняет портрет, но не главный.</p>' +
      '<div class="astro__mini">' + pic(d.img, d.card, 'astro__card astro__card--sm') +
      '<div><span class="astro__label">' + esc(d.where) + '</span><b>' + esc(d.card) + '</b>' +
      '<p>' + esc(d.text) + '</p></div></div></div>';
  }

  form.addEventListener('submit', function (e) {
    e.preventDefault();
    var v = document.getElementById('astro-date').value.split('-');
    if (v.length !== 3) return;
    var start = Date.UTC(+v[0], +v[1] - 1, +v[2], 0, 0) - 3 * 3600000;   // 00:00 по Москве
    var end = start + 86400000 - 60000;
    var a = decanAt(start), b = decanAt(end);
    var html;
    // Карты меняются только на границе знака или карты двора; смена декана внутри них ничего не меняет.
    if (signOf(a) === signOf(b) && courtOf(a) === courtOf(b)) {
      html = main(a) + extra(a);
    } else {
      var t = whenChanged(start, end);
      html = '<p class="astro__note">В этот день Солнце перешло границу около ' + t + ' по Москве. Если вы родились раньше — первый вариант, позже — второй.</p>' +
        '<h3 class="astro__h3">Если раньше ' + t + '</h3>' + main(a) + extra(a) +
        '<hr class="astro__hr" /><h3 class="astro__h3">Если позже ' + t + '</h3>' + main(b) + extra(b);
    }
    html += '<div class="astro__cta"><p>Это общий портрет. Что он значит в вашей ситуации, видно только на раскладе.</p>' +
      '<a class="btn" href="' + TG + '">Записаться на расклад</a></div>';
    if (history.replaceState) history.replaceState(null, '', '#' + field.value);
    out.innerHTML = html;
    out.hidden = false;
    out.scrollIntoView({ behavior: 'smooth', block: 'start' });
    if (window.ym && window.METRIKA_ID) window.ym(window.METRIKA_ID, 'reachGoal', 'tool_result');
  });
})();
