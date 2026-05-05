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
  let angle = 0;
  let lastTime = performance.now();
  let isPaused = false;

  const renderBusinessCard = (time) => {
    const delta = time - lastTime;
    lastTime = time;

    if (!isPaused) {
      angle = (angle + delta * 0.018) % 360;
      businessCardInner.style.transform = `rotateY(${angle}deg)`;
    }

    window.requestAnimationFrame(renderBusinessCard);
  };

  const toggleBusinessCardPause = () => {
    isPaused = !isPaused;
    businessCard.classList.toggle('is-locked', isPaused);
    if (businessCardFlip) {
      businessCardFlip.textContent = isPaused ? 'Spin card' : 'Pause card';
      businessCardFlip.setAttribute('aria-pressed', String(isPaused));
    }
  };

  businessCard.addEventListener('click', (event) => {
    if (event.target instanceof HTMLAnchorElement || event.target.closest('a')) return;
    toggleBusinessCardPause();
  });

  businessCard.addEventListener('keydown', (event) => {
    if (event.key === 'Enter' || event.key === ' ') {
      event.preventDefault();
      toggleBusinessCardPause();
    }
  });

  if (businessCardFlip) {
    businessCardFlip.textContent = 'Pause card';
    businessCardFlip.setAttribute('aria-pressed', 'false');
    businessCardFlip.addEventListener('click', toggleBusinessCardPause);
  }

  window.requestAnimationFrame(renderBusinessCard);
}
