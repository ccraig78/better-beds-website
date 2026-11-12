// Original-image links remain usable if JavaScript or dialog support is absent.
(() => {
  const viewer = document.querySelector('.work-viewer');
  const links = [...document.querySelectorAll('[data-work-photo]')];
  if (!viewer || typeof viewer.showModal !== 'function' || !links.length) return;
  const full = viewer.querySelector('[data-work-full]');
  const caption = viewer.querySelector('figcaption');
  const original = viewer.querySelector('[data-work-original]');
  let current = 0;
  let opener;
  let previousOverflow = '';
  function show(index) {
    current = (index + links.length) % links.length;
    const link = links[current];
    full.src = link.href;
    full.alt = link.querySelector('img').alt;
    original.href = link.href;
    caption.textContent = `${current + 1} of ${links.length} · ${link.closest('figure').querySelector('figcaption').textContent} · Historical photo`;
  }
  links.forEach((link, index) => link.addEventListener('click', event => {
    if (event.ctrlKey || event.metaKey || event.shiftKey || event.altKey || event.button !== 0) return;
    event.preventDefault();
    opener = link;
    show(index);
    previousOverflow = document.body.style.overflow;
    document.body.style.overflow = 'hidden';
    viewer.showModal();
  }));
  viewer.querySelector('[data-work-close]').addEventListener('click', () => viewer.close());
  viewer.querySelector('[data-work-prev]').addEventListener('click', () => show(current - 1));
  viewer.querySelector('[data-work-next]').addEventListener('click', () => show(current + 1));
  viewer.addEventListener('keydown', event => {
    if (event.key === 'Tab') {
      const controls = [...viewer.querySelectorAll('button, a[href]')];
      const first = controls[0];
      const last = controls[controls.length - 1];
      if (event.shiftKey && document.activeElement === first) {
        event.preventDefault();
        last.focus();
      } else if (!event.shiftKey && document.activeElement === last) {
        event.preventDefault();
        first.focus();
      }
    }
    if (event.key === 'ArrowRight' || event.key === 'ArrowLeft') {
      event.preventDefault();
      show(current + (event.key === 'ArrowRight' ? 1 : -1));
    }
  });
  viewer.addEventListener('click', event => { if (event.target === viewer) viewer.close(); });
  viewer.addEventListener('close', () => {
    document.body.style.overflow = previousOverflow;
    opener?.focus({ preventScroll: true });
  });
})();
