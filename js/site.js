/* Beyond Summit Expeditions - shared behaviour. No dependencies, no scroll listeners. */
(() => {
  const d = document, root = d.documentElement;
  root.classList.remove('no-js'); root.classList.add('js');
  const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
  const io = (cb, opts) => ('IntersectionObserver' in window ? new IntersectionObserver(cb, opts) : null);
  const store = {
    get: k => { try { return localStorage.getItem(k); } catch (e) { return null; } },
    set: (k, v) => { try { localStorage.setItem(k, v); } catch (e) {} }
  };

  /* Theme toggle (light by default) */
  d.querySelectorAll('[data-theme-toggle]').forEach(btn => {
    const label = () => {
      const t = root.dataset.theme || 'light';
      btn.querySelector('span').textContent = t === 'dark' ? 'Light mode' : 'Dark mode';
    };
    label();
    btn.addEventListener('click', () => {
      const cur = root.dataset.theme || 'light';
      root.dataset.theme = cur === 'dark' ? 'light' : 'dark';
      store.set('theme', root.dataset.theme); label();
    });
  });

  /* Header: transparent while the photo hero is on screen */
  const header = d.getElementById('header');
  const hero = d.querySelector('.photo-hero');
  if (header && hero) {
    header.classList.add('over');
    const o = io(([e]) => header.classList.toggle('over', e.isIntersecting), { rootMargin: `-${header.offsetHeight}px 0px 0px 0px` });
    o ? o.observe(hero) : header.classList.remove('over');
  }

  /* Mobile menu */
  const menuBtn = d.getElementById('menuBtn');
  if (menuBtn) {
    const set = open => {
      d.body.classList.toggle('menu-open', open);
      menuBtn.setAttribute('aria-expanded', open);
      menuBtn.setAttribute('aria-label', open ? 'Close menu' : 'Open menu');
      d.body.style.overflow = open ? 'hidden' : '';
    };
    menuBtn.addEventListener('click', () => set(!d.body.classList.contains('menu-open')));
    d.querySelectorAll('#mobileMenu a').forEach(a => a.addEventListener('click', () => set(false)));
    d.addEventListener('keydown', e => { if (e.key === 'Escape') set(false); });
  }

  /* Fade lazy images in once decoded */
  d.querySelectorAll('img[loading="lazy"]').forEach(img => {
    const done = () => img.classList.add('loaded');
    img.complete && img.naturalWidth ? done() : (img.addEventListener('load', done), img.addEventListener('error', done));
  });

  /* Reveal on scroll, staggered within a group */
  const rv = io(entries => entries.forEach(e => {
    if (!e.isIntersecting) return;
    const el = e.target, sibs = [...el.parentElement.children].filter(c => c.classList.contains('reveal'));
    el.style.setProperty('--d', Math.min(sibs.indexOf(el), 5) * 70 + 'ms');
    el.classList.add('in'); rv.unobserve(el);
  }), { rootMargin: '0px 0px -6% 0px', threshold: .04 });
  d.querySelectorAll('.reveal').forEach(el => (rv && !reduce ? rv.observe(el) : el.classList.add('in')));

  /* Card filters (listing pages) */
  d.querySelectorAll('[data-filters]').forEach(bar => {
    const grid = d.getElementById(bar.dataset.filters);
    const empty = grid.parentElement.querySelector('.empty');
    const apply = val => {
      bar.querySelectorAll('button').forEach(b => b.setAttribute('aria-pressed', b.dataset.f === val));
      let shown = 0;
      grid.querySelectorAll('[data-tags]').forEach(c => {
        const ok = val === 'all' || c.dataset.tags.split(' ').includes(val);
        c.hidden = !ok; if (ok) shown++;
      });
      if (empty) empty.hidden = shown > 0;
    };
    bar.addEventListener('click', e => { const b = e.target.closest('button'); if (b) apply(b.dataset.f); });
    const q = new URLSearchParams(location.search).get('f');
    if (q && bar.querySelector(`[data-f="${CSS.escape(q)}"]`)) apply(q);
  });

  /* Home trip finder -> listing filter */
  const finder = d.getElementById('finder');
  if (finder) finder.addEventListener('submit', e => {
    e.preventDefault();
    const f = new FormData(finder);
    const type = f.get('type'), region = f.get('region'), len = f.get('length'), level = f.get('level');
    const page = type === 'climb' ? '/expeditions.html' : '/trekking.html';
    const pick = [region, level, len].find(v => v && v !== 'all') || 'all';
    location.href = page + (pick !== 'all' ? '?f=' + encodeURIComponent(pick) : '') + '#trips';
  });

  /* Trip page: section nav + day highlight on the sticky route map */
  const tnav = d.querySelector('.trip-nav');
  if (tnav) {
    const links = [...tnav.querySelectorAll('a')];
    const secs = links.map(a => d.querySelector(a.getAttribute('href'))).filter(Boolean);
    const so = io(entries => entries.forEach(e => {
      if (!e.isIntersecting) return;
      links.forEach(a => a.classList.toggle('active', a.getAttribute('href') === '#' + e.target.id));
      const act = tnav.querySelector('a.active');
      if (act) act.scrollIntoView({ block: 'nearest', inline: 'center', behavior: reduce ? 'auto' : 'smooth' });
    }), { rootMargin: '-45% 0px -50% 0px' });
    so && secs.forEach(s => so.observe(s));
  }
  const itin = d.getElementById('itinerary');
  if (itin) {
    const ia = io(([e]) => d.body.classList.toggle('itin-active', e.isIntersecting), { rootMargin: '-30% 0px -40% 0px' });
    ia && ia.observe(itin);
  }
  const big = d.querySelector('.map-big');
  const days = [...d.querySelectorAll('.day[data-day]')];
  if (days.length) {
    const label = d.getElementById('mapDay');
    const setDay = idx => {
      days.forEach((x, i) => x.classList.toggle('in-view', i === idx));
      if (!big) return;
      big.querySelectorAll('.seg').forEach(s => {
        const i = +s.dataset.i;
        s.classList.toggle('on', i === idx);
        s.classList.toggle('done', i < idx);
      });
      big.querySelectorAll('.stop[data-i]').forEach(s => s.classList.toggle('on', +s.dataset.i === idx));
      if (label) label.textContent = days[idx].dataset.label;
    };
    const dobs = io(entries => entries.forEach(e => { if (e.isIntersecting) setDay(days.indexOf(e.target)); }), { rootMargin: '-40% 0px -55% 0px' });
    dobs && days.forEach(x => dobs.observe(x));
  }

  /* Altitude profile tooltip */
  d.querySelectorAll('.profile-wrap').forEach(wrap => {
    const tip = wrap.querySelector('.tip'), cur = wrap.querySelector('.cursor'), svg = wrap.querySelector('svg');
    const show = h => {
      const r = svg.getBoundingClientRect(), vb = svg.viewBox.baseVal, k = r.width / vb.width;
      const x = +h.dataset.x, y = +h.dataset.y;
      tip.innerHTML = h.dataset.tip; tip.classList.add('show');
      tip.style.left = x * k + 'px'; tip.style.top = y * k + 'px';
      if (cur) { cur.setAttribute('x1', x); cur.setAttribute('x2', x); cur.style.opacity = 1; }
    };
    const hide = () => { tip.classList.remove('show'); if (cur) cur.style.opacity = 0; };
    wrap.querySelectorAll('.hit').forEach(h => {
      h.addEventListener('pointerenter', () => show(h));
      h.addEventListener('focus', () => show(h));
      h.addEventListener('click', () => { const t = d.getElementById('day-' + h.dataset.day); if (t) t.scrollIntoView({ behavior: reduce ? 'auto' : 'smooth' }); });
    });
    svg.addEventListener('pointerleave', hide);
    wrap.addEventListener('focusout', hide);
  });

  /* Enquiry form: validates, then sends by WhatsApp or e-mail (no server needed) */
  const form = d.getElementById('enquiry');
  if (form) {
    const qs = new URLSearchParams(location.search);
    const tripSel = form.querySelector('[name="trip"]');
    if (qs.get('trip') && tripSel) {
      const opt = [...tripSel.options].find(o => o.value === qs.get('trip'));
      if (opt) opt.selected = true;
    }
    const status = d.getElementById('formStatus');
    const check = () => {
      let ok = true;
      form.querySelectorAll('[required]').forEach(inp => {
        const f = inp.closest('.field');
        const bad = !inp.value.trim() || (inp.type === 'email' && !/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(inp.value.trim()));
        f.classList.toggle('invalid', bad); inp.setAttribute('aria-invalid', bad);
        if (bad && ok) { inp.focus(); ok = false; }
      });
      return ok;
    };
    form.querySelectorAll('input, select, textarea').forEach(i => i.addEventListener('input', () => i.closest('.field')?.classList.remove('invalid')));
    const compose = () => {
      const f = new FormData(form), tripText = tripSel ? tripSel.options[tripSel.selectedIndex].text : '';
      return [
        `Hello Beyond Summit, I'd like to plan a trip.`,
        `Name: ${f.get('name')}`, `Email: ${f.get('email')}`,
        f.get('country') ? `Country: ${f.get('country')}` : '',
        `Trip: ${tripText}`,
        f.get('month') ? `Preferred month: ${f.get('month')}` : '',
        f.get('people') ? `Travellers: ${f.get('people')}` : '',
        f.get('message') ? `\n${f.get('message')}` : ''
      ].filter(Boolean).join('\n');
    };
    form.addEventListener('submit', e => {
      e.preventDefault();
      if (!check()) return;
      const via = e.submitter?.value || 'whatsapp', text = compose();
      const url = via === 'email'
        ? `mailto:${form.dataset.email}?subject=${encodeURIComponent('Trip enquiry: ' + (tripSel?.options[tripSel.selectedIndex].text || ''))}&body=${encodeURIComponent(text)}`
        : `https://wa.me/${form.dataset.wa}?text=${encodeURIComponent(text)}`;
      window.open(url, via === 'email' ? '_self' : '_blank', 'noopener');
      status.textContent = via === 'email'
        ? 'Your e-mail app should now be open with your message ready. Press send and we will reply within one working day.'
        : 'WhatsApp should now be open with your message ready. Press send and we will reply within one working day.';
      status.classList.add('show');
    });
  }
})();

/* Photo gallery: category filter and a full-screen viewer (lightbox) */
(() => {
  const d = document;
  const grid = d.getElementById('gGrid');
  const bar = d.querySelector('.g-filters');
  if (grid && bar) bar.addEventListener('click', e => {
    const b = e.target.closest('button[data-g]'); if (!b) return;
    bar.querySelectorAll('button').forEach(x => x.setAttribute('aria-pressed', String(x === b)));
    grid.querySelectorAll('.g-item').forEach(it => { it.hidden = b.dataset.g !== 'all' && it.dataset.cat !== b.dataset.g; });
  });

  const lb = d.getElementById('lightbox');
  if (!lb || typeof lb.showModal !== 'function') return; // without <dialog> support, links open the photo directly
  const im = lb.querySelector('img'), cap = lb.querySelector('figcaption'), count = lb.querySelector('.lb-count');
  let list = [], i = 0, opener = null;
  const show = n => {
    i = (n + list.length) % list.length;
    const a = list[i];
    im.src = a.href; im.alt = a.querySelector('img')?.alt || '';
    cap.textContent = a.dataset.caption || '';
    count.textContent = `${i + 1} / ${list.length}`;
    lb.classList.toggle('lb-solo', list.length < 2);
    const nx = list[(i + 1) % list.length]; if (nx) new Image().src = nx.href; // preload next
  };
  d.addEventListener('click', e => {
    const a = e.target.closest('a[data-lightbox]'); if (!a) return;
    e.preventDefault();
    const scope = a.closest('.g-grid, .g-strip') || d;
    list = [...scope.querySelectorAll('a[data-lightbox]')].filter(x => !x.closest('[hidden]'));
    opener = a; show(list.indexOf(a)); lb.showModal();
  });
  lb.addEventListener('click', e => {
    const b = e.target.closest('[data-lb]');
    if (b) { b.dataset.lb === 'close' ? lb.close() : show(i + (b.dataset.lb === 'next' ? 1 : -1)); return; }
    if (e.target === lb || e.target.tagName === 'FIGURE') lb.close();
  });
  lb.addEventListener('keydown', e => {
    if (e.key === 'ArrowRight') show(i + 1);
    else if (e.key === 'ArrowLeft') show(i - 1);
  });
  let x0 = null;
  lb.addEventListener('touchstart', e => { x0 = e.touches[0].clientX; }, { passive: true });
  lb.addEventListener('touchend', e => {
    if (x0 === null) return;
    const dx = e.changedTouches[0].clientX - x0; x0 = null;
    if (Math.abs(dx) > 50) show(i + (dx < 0 ? 1 : -1));
  });
  lb.addEventListener('close', () => { im.removeAttribute('src'); opener?.focus(); });
})();
