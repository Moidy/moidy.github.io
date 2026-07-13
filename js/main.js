/* ── Sticky nav ──────────────────────────────────────────────── */
(function () {
  const nav = document.getElementById('site-nav');
  const onScroll = () => nav.classList.toggle('scrolled', window.scrollY > 40);
  window.addEventListener('scroll', onScroll, { passive: true });
})();

/* ── Project filter ──────────────────────────────────────────── */
(function () {
  const buttons = document.querySelectorAll('.filter-btn');
  const cards   = document.querySelectorAll('.project-card');

  buttons.forEach(btn => {
    btn.addEventListener('click', () => {
      const filter = btn.dataset.filter;

      // Update active state
      buttons.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');

      // Show / hide cards
      cards.forEach(card => {
        const tags = card.dataset.tags || '';
        const visible = filter === 'all' || tags.includes(filter);
        card.classList.toggle('hidden', !visible);
      });
    });
  });
})();

/* ── Smooth reveal on scroll ─────────────────────────────────── */
(function () {
  if (!('IntersectionObserver' in window)) return;

  const observer = new IntersectionObserver(
    entries => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.style.opacity  = '';
          entry.target.style.transform = '';
          observer.unobserve(entry.target);
        }
      });
    },
    { threshold: 0.08, rootMargin: '0px 0px -40px 0px' }
  );

  document.querySelectorAll('.project-card, .stat-card').forEach(el => {
    el.style.opacity  = '0';
    el.style.transform = 'translateY(24px)';
    el.style.transition = 'opacity 0.45s ease, transform 0.45s ease';
    observer.observe(el);
  });
})();
