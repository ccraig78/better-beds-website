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
const businessCardFlip = document.querySelector('.contact-card-flip');
if (businessCard) {
  const flipBusinessCard = () => {
    businessCard.classList.add('is-locked');
    businessCard.classList.toggle('is-flipped');
  };

  businessCard.addEventListener('click', (event) => {
    if (event.target instanceof HTMLAnchorElement || event.target.closest('a')) return;
    flipBusinessCard();
  });

  businessCard.addEventListener('keydown', (event) => {
    if (event.key === 'Enter' || event.key === ' ') {
      event.preventDefault();
      flipBusinessCard();
    }
  });

  if (businessCardFlip) {
    businessCardFlip.addEventListener('click', flipBusinessCard);
  }
}
