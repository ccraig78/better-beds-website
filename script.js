const navToggle = document.querySelector('.nav-toggle');
const siteNav = document.querySelector('.site-nav');
const year = document.querySelector('#year');
const heroSlides = Array.from(document.querySelectorAll('.hero-bg'));

if (year) {
  year.textContent = new Date().getFullYear();
}

if (navToggle && siteNav) {
  navToggle.addEventListener('click', () => {
    const isOpen = siteNav.classList.toggle('open');
    navToggle.setAttribute('aria-expanded', String(isOpen));
  });

  siteNav.addEventListener('click', (event) => {
    if (event.target instanceof HTMLAnchorElement) {
      siteNav.classList.remove('open');
      navToggle.setAttribute('aria-expanded', 'false');
    }
  });
}

if (heroSlides.length > 1 && !window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
  let currentHeroSlide = 0;

  window.setInterval(() => {
    heroSlides[currentHeroSlide].classList.remove('active');
    currentHeroSlide = (currentHeroSlide + 1) % heroSlides.length;
    heroSlides[currentHeroSlide].classList.add('active');
  }, 4500);
}

const businessCard = document.querySelector('.business-card-3d');
const businessCardInner = document.querySelector('.contact-card-inner');
const businessCardFlip = document.querySelector('.contact-card-flip');
if (businessCard && businessCardInner) {
  let rotationY = 0;
  let rotationX = 0;
  let lastTime = performance.now();
  let isAutoRotating = true;
  let isDragging = false;
  let didDrag = false;
  let dragStartX = 0;
  let dragStartY = 0;
  let startRotationY = 0;
  let startRotationX = 0;

  const setBusinessCardTransform = () => {
    businessCardInner.style.transform = `rotateX(${rotationX}deg) rotateY(${rotationY}deg)`;
  };

  const setAutoRotate = (enabled) => {
    isAutoRotating = enabled;
    businessCard.classList.toggle('is-locked', !enabled);
    if (businessCardFlip) {
      businessCardFlip.textContent = enabled ? 'Pause spin' : 'Resume spin';
      businessCardFlip.setAttribute('aria-pressed', String(!enabled));
    }
  };

  const renderBusinessCard = (time) => {
    const delta = time - lastTime;
    lastTime = time;

    if (isAutoRotating && !isDragging) {
      rotationY = (rotationY + delta * 0.018) % 360;
      rotationX = Math.sin(time / 1600) * 2.5;
      setBusinessCardTransform();
    }

    window.requestAnimationFrame(renderBusinessCard);
  };

  const stopAutoForManualControl = () => {
    setAutoRotate(false);
  };

  businessCard.addEventListener('pointerdown', (event) => {
    if (event.target instanceof HTMLAnchorElement || event.target.closest('a')) return;
    stopAutoForManualControl();
    isDragging = true;
    didDrag = false;
    dragStartX = event.clientX;
    dragStartY = event.clientY;
    startRotationY = rotationY;
    startRotationX = rotationX;
    businessCard.classList.add('is-dragging');
    businessCard.setPointerCapture(event.pointerId);
  });

  businessCard.addEventListener('pointermove', (event) => {
    if (!isDragging) return;
    const deltaX = event.clientX - dragStartX;
    const deltaY = event.clientY - dragStartY;
    if (Math.abs(deltaX) + Math.abs(deltaY) > 4) didDrag = true;
    rotationY = startRotationY + deltaX * 0.45;
    rotationX = Math.max(-18, Math.min(18, startRotationX - deltaY * 0.18));
    setBusinessCardTransform();
  });

  const endDrag = (event) => {
    if (!isDragging) return;
    isDragging = false;
    businessCard.classList.remove('is-dragging');
    if (businessCard.hasPointerCapture(event.pointerId)) {
      businessCard.releasePointerCapture(event.pointerId);
    }
  };

  businessCard.addEventListener('pointerup', endDrag);
  businessCard.addEventListener('pointercancel', endDrag);

  businessCard.addEventListener('click', (event) => {
    if (event.target instanceof HTMLAnchorElement || event.target.closest('a')) return;
    if (didDrag) return;
    stopAutoForManualControl();
  });

  businessCard.addEventListener('keydown', (event) => {
    if (event.key === 'Enter' || event.key === ' ') {
      event.preventDefault();
      stopAutoForManualControl();
      rotationY += 180;
      rotationX = 0;
      setBusinessCardTransform();
    }
  });

  if (businessCardFlip) {
    businessCardFlip.textContent = 'Pause spin';
    businessCardFlip.setAttribute('aria-pressed', 'false');
    businessCardFlip.addEventListener('click', () => {
      setAutoRotate(!isAutoRotating);
      if (isAutoRotating) rotationX = 0;
      setBusinessCardTransform();
    });
  }

  setBusinessCardTransform();
  window.requestAnimationFrame(renderBusinessCard);
}
