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
  const normalize = text => text.toLowerCase().replace(/[^a-z0-9]+/g, '');
  const filter = () => {
    const terms = search.value.toLowerCase().trim().split(/\s+/).filter(Boolean).map(normalize);
    let count = 0;
    cards.forEach(card => {
      card.hidden = !terms.every(term => normalize(card.dataset.search).includes(term));
      if (!card.hidden) count++;
    });
    document.querySelector('[data-inventory-count]').textContent = `${count} ${count === 1 ? 'listing' : 'listings'}`;
    document.querySelector('[data-inventory-empty]').hidden = count !== 0;
  };
  search.addEventListener('input', filter);
  document.querySelector('[data-clear-search]').addEventListener('click', () => { search.value = ''; filter(); search.focus(); });
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
