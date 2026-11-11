'use strict';
const toggle = document.querySelector('.nav-toggle');
const nav = document.querySelector('.site-nav');
const closeNav = () => { nav?.classList.remove('open'); toggle?.setAttribute('aria-expanded', 'false'); };
toggle?.addEventListener('click', () => toggle.setAttribute('aria-expanded', String(nav.classList.toggle('open'))));
nav?.addEventListener('click', event => { if (event.target.closest('a')) closeNav(); });
document.addEventListener('keydown', event => { if (event.key === 'Escape') closeNav(); });
document.querySelectorAll('[data-year]').forEach(node => { node.textContent = new Date().getFullYear(); });

// Compose a customer-reviewed message in the customer's own text/email app.
document.querySelectorAll('[data-inquiry-builder]').forEach(form => {
  const sms = form.querySelector('[data-inquiry-sms]');
  const email = form.querySelector('[data-inquiry-email]');
  const update = () => {
    const fields = new FormData(form);
    const parts = ['Hi Better Beds, I’m interested in your current inventory.'];
    for (const [label, name] of [['Truck', 'truck'], ['Bed length / wheel setup', 'bed'], ['Item', 'item'], ['Details', 'details']]) {
      const value = String(fields.get(name) || '').trim();
      if (value) parts.push(`${label}: ${value}`);
    }
    parts.push('Please confirm fitment, availability, price, and pickup.');
    const body = encodeURIComponent(parts.join('\n'));
    sms.href = `sms:2145248401?body=${body}`;
    email.href = `mailto:clint@betterbeds.pro?subject=Better%20Beds%20inventory%20inquiry&body=${body}`;
  };
  form.addEventListener('input', update);
  form.addEventListener('change', update);
  form.addEventListener('submit', event => { event.preventDefault(); update(); sms.click(); });
  update();
});

const search = document.querySelector('[data-inventory-search]');
if (search) {
  const cards = [...document.querySelectorAll('[data-inventory-item]')];
  const typeButtons = [...document.querySelectorAll('[data-filter-type]')];
  const make = document.querySelector('[data-filter-make]');
  const color = document.querySelector('[data-filter-color]');
  const params = new URLSearchParams(window.location.search);
  let activeType = typeButtons.find(button => button.dataset.filterType.toLowerCase() === (params.get('type') || '').toLowerCase())?.dataset.filterType || '';
  search.value = params.get('q') || '';
  for (const [select, key] of [[make, 'make'], [color, 'color']]) {
    select.value = [...select.options].find(option => option.value.toLowerCase() === (params.get(key) || '').toLowerCase())?.value || '';
  }
  const normalize = text => text.toLowerCase().replace(/[^a-z0-9]+/g, '');
  const measuredQuery = text => {
    const feet = text.match(/(?:^|\s)(\d+(?:\.\d+)?)\s*(?:['’′]|ft\b|foot\b|feet\b)(?:\s*(\d{1,2})(?!\d)\s*(?:["”″]|in\b|inch(?:es)?\b)?)?/i);
    if (feet) {
      const inches = Number(feet[2] || 0);
      if (inches < 12) return { inches: Number(feet[1]) * 12 + inches, query: text.replace(feet[0], ' ') };
    }
    const inches = text.match(/(?:^|\s)(\d+(?:\.\d+)?)\s*(?:["”″]|in\b|inch(?:es)?\b)/i);
    return inches ? { inches: Number(inches[1]), query: text.replace(inches[0], ' ') } : { inches: null, query: text };
  };
  const filter = () => {
    const measurement = measuredQuery(search.value);
    const terms = measurement.query.toLowerCase().trim().split(/\s+/).filter(Boolean).map(normalize);
    const length = measurement.inches;
    let count = 0;
    cards.forEach(card => {
      card.hidden = !terms.every(term => normalize(card.dataset.search).includes(term))
        || Boolean(length !== null && (card.dataset.bedInches === '' || Number(card.dataset.bedInches) !== length))
        || Boolean(activeType && card.dataset.type !== activeType)
        || Boolean(make.value && card.dataset.make !== make.value)
        || Boolean(color.value && card.dataset.color !== color.value);
      if (!card.hidden) count++;
    });
    document.querySelector('[data-inventory-count]').textContent = `${count} ${count === 1 ? 'listing' : 'listings'}`;
    document.querySelector('[data-inventory-empty]').hidden = count !== 0;
    typeButtons.forEach(button => button.setAttribute('aria-pressed', String(button.dataset.filterType === activeType)));
    const url = new URL(window.location.href);
    for (const [key, value] of [['type', activeType], ['make', make.value], ['color', color.value], ['q', search.value.trim()]]) {
      if (value) url.searchParams.set(key, value);
      else url.searchParams.delete(key);
    }
    window.history.replaceState(null, '', url);
  };
  search.addEventListener('input', filter);
  make.addEventListener('change', filter);
  color.addEventListener('change', filter);
  typeButtons.forEach(button => button.addEventListener('click', () => { activeType = button.dataset.filterType; filter(); }));
  document.querySelector('[data-clear-search]').addEventListener('click', () => {
    search.value = ''; make.value = ''; color.value = ''; activeType = '';
    filter(); search.focus();
  });
  filter();
}

// Preserve the existing multipart photo-inquiry endpoint and field names.
const upload = document.querySelector('[data-agent-upload]');
if (upload) {
  const status = upload.querySelector('[data-form-status]');
  const submit = upload.querySelector('button[type="submit"]');
  const report = (message, kind) => { status.textContent = message; status.dataset.kind = kind; };
  upload.addEventListener('submit', async event => {
    event.preventDefault();
    if (upload.querySelector('[name="_honey"]').value || !upload.reportValidity()) return;
    const files = [...upload.querySelector('[name="photos"]').files];
    if (files.length > 6 || files.some(file => file.size > 5 * 1024 * 1024 || !file.type.startsWith('image/')) || files.reduce((sum, file) => sum + file.size, 0) > 15 * 1024 * 1024) {
      report('Choose up to 6 images, each under 5 MB, with less than 15 MB total. You can also text photos to 214-524-8401.', 'error');
      return;
    }
    const data = new FormData(upload);
    data.delete('_honey');
    const controller = new AbortController();
    const timeout = window.setTimeout(() => controller.abort(), 25000);
    submit.disabled = true;
    upload.setAttribute('aria-busy', 'true');
    report('Sending your inventory inquiry…', 'pending');
    try {
      const response = await fetch(upload.action, { method: 'POST', body: data, mode: 'cors', signal: controller.signal });
      const result = await response.json();
      if (!response.ok || !result.ok) throw new Error('Request failed');
      report(`Inquiry received. We’ll follow up to confirm inventory and pricing.${result.id ? ` Reference: ${result.id}` : ''}`, 'success');
      upload.reset();
    } catch {
      report('We couldn’t confirm your inquiry was received. Your details are still here. Please call/text 214-524-8401 or try again.', 'error');
    } finally {
      window.clearTimeout(timeout);
      submit.disabled = false;
      upload.removeAttribute('aria-busy');
    }
  });
}

// Select an actual item photo while keeping its full-size link and caption in sync.
document.querySelectorAll('[data-product-gallery]').forEach(gallery => {
  const main = gallery.querySelector('[data-gallery-main]');
  const full = gallery.querySelector('[data-gallery-full]');
  const caption = gallery.querySelector('[data-gallery-caption]');
  const thumbnails = [...gallery.querySelectorAll('[data-photo-src]')];
  thumbnails.forEach(button => button.addEventListener('click', () => {
    main.src = button.dataset.photoSrc;
    main.alt = button.dataset.photoAlt;
    main.width = Number(button.dataset.photoWidth);
    main.height = Number(button.dataset.photoHeight);
    full.href = button.dataset.photoSrc;
    caption.textContent = button.dataset.photoCaption;
    thumbnails.forEach(thumbnail => thumbnail.setAttribute('aria-pressed', String(thumbnail === button)));
  }));
});
