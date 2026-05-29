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

const modalOpeners = document.querySelectorAll('[data-modal-open]');
const modalClosers = document.querySelectorAll('[data-modal-close]');
let activeModal = null;
let lastModalTrigger = null;

const openHelpModal = (modalId, trigger) => {
  const modal = document.getElementById(modalId);
  if (!modal) return;
  lastModalTrigger = trigger;
  activeModal = modal;
  modal.classList.add('is-open');
  modal.setAttribute('aria-hidden', 'false');
  document.body.classList.add('modal-open');
  const closeButton = modal.querySelector('.help-modal-close');
  if (closeButton) closeButton.focus();
};

const closeHelpModal = () => {
  if (!activeModal) return;
  activeModal.classList.remove('is-open');
  activeModal.setAttribute('aria-hidden', 'true');
  document.body.classList.remove('modal-open');
  if (lastModalTrigger) lastModalTrigger.focus();
  activeModal = null;
  lastModalTrigger = null;
};

modalOpeners.forEach((button) => {
  button.addEventListener('click', () => openHelpModal(button.dataset.modalOpen, button));
});
modalClosers.forEach((closer) => {
  closer.addEventListener('click', closeHelpModal);
});
document.addEventListener('keydown', (event) => {
  if (event.key === 'Escape') closeHelpModal();
});

const collapsiblePanelSelectors = [
  'body.about-page .about-card-grid > article',
  'body.about-page .about-services-list > article'
];

const collapsiblePanels = document.querySelectorAll(collapsiblePanelSelectors.join(','));
collapsiblePanels.forEach((panel, index) => {
  if (panel.dataset.collapsibleReady === 'true') return;

  const existingTop = panel.querySelector(':scope > .service-card-top');
  const title = existingTop ? existingTop.querySelector('h3') : panel.querySelector(':scope > h3');
  if (!title) return;

  const panelId = panel.id || `collapsible-panel-${index + 1}`;
  const bodyId = `${panelId}-details`;
  panel.id = panelId;
  panel.dataset.collapsibleReady = 'true';
  panel.classList.add('collapsible-panel', 'is-collapsed');

  let header = existingTop;
  if (!header) {
    header = document.createElement('div');
    header.className = 'collapsible-panel-header';
    panel.insertBefore(header, title);
    header.appendChild(title);
  } else {
    header.classList.add('collapsible-panel-header');
  }

  const button = document.createElement('button');
  button.type = 'button';
  button.className = 'collapsible-panel-toggle';
  button.setAttribute('aria-expanded', 'false');
  button.setAttribute('aria-controls', bodyId);
  button.innerHTML = '<span>More info</span><b aria-hidden="true">?</b>';
  header.appendChild(button);

  const body = document.createElement('div');
  body.className = 'collapsible-panel-body';
  body.id = bodyId;
  body.hidden = true;

  let node = header.nextSibling;
  while (node) {
    const next = node.nextSibling;
    body.appendChild(node);
    node = next;
  }
  panel.appendChild(body);

  button.addEventListener('click', () => {
    const isOpen = panel.classList.toggle('is-open');
    panel.classList.toggle('is-collapsed', !isOpen);
    body.hidden = !isOpen;
    button.setAttribute('aria-expanded', String(isOpen));
    button.querySelector('span').textContent = isOpen ? 'Hide info' : 'More info';
    button.querySelector('b').textContent = isOpen ? '−' : '?';
  });
});

const quoteCaptureEndpoint = 'https://chat.betterbeds.pro/better-beds-chat';
const quoteSessionStorageKey = 'betterBedsQuoteFields';
const quoteSessionTimestampKey = 'betterBedsQuoteFieldsUpdatedAt';

const quoteFieldLabels = {
  customerName: 'Name',
  customerPhone: 'Phone',
  customerLocation: 'Location',
  travelPlan: 'Travel / pickup plan',
  truck: 'Truck',
  bedLength: 'Bed length/style',
  rearWheel: 'Rear wheel setup',
  quoteType: 'Quote type',
  paymentType: 'Payment type',
  paint: 'Paint code/color',
  preferredContact: 'Preferred contact',
  callWindow: 'Best time to call',
  timing: 'Timing',
  needs: 'What I need'
};

const quoteFieldOrder = ['customerName', 'customerPhone', 'customerLocation', 'travelPlan', 'truck', 'bedLength', 'rearWheel', 'quoteType', 'paymentType', 'paint', 'preferredContact', 'callWindow', 'timing', 'needs'];

const getQuoteSessionId = () => {
  const key = 'betterBedsQuoteSessionId';
  try {
    const existing = window.localStorage.getItem(key);
    if (existing) return existing;
    const created = `quote-${Date.now()}-${Math.random().toString(36).slice(2, 10)}`;
    window.localStorage.setItem(key, created);
    return created;
  } catch (error) {
    return `quote-${Date.now()}-${Math.random().toString(36).slice(2, 10)}`;
  }
};

const sendQuoteCapture = (payload) => {
  const body = JSON.stringify(payload);

  try {
    if (navigator.sendBeacon) {
      const blob = new Blob([body], { type: 'application/json' });
      if (navigator.sendBeacon(quoteCaptureEndpoint, blob)) return;
    }
  } catch (error) {
    // Fall back to keepalive fetch below.
  }

  try {
    fetch(quoteCaptureEndpoint, {
      method: 'POST',
      mode: 'cors',
      keepalive: true,
      headers: { 'Content-Type': 'application/json' },
      body
    }).catch(() => {});
  } catch (error) {
    // Do not block opening the customer's text/email/call app if capture fails.
  }
};

const buildQuoteMessageFromFields = (fieldValues) => {
  const lines = ['Hi Better Beds, I would like a truck bed quote.'];
  quoteFieldOrder.forEach((name) => {
    const value = fieldValues[name];
    if (!value) return;
    lines.push(`${quoteFieldLabels[name] || name}: ${value}`);
  });
  lines.push('I can attach photos after this message opens.');
  return lines.join('\n');
};

const makeQuoteCapturePayload = ({ action, fieldValues, source, linkHref = '', linkText = '' }) => {
  const filledFields = Object.entries(fieldValues || {}).filter(([, value]) => value);
  if (!filledFields.length) return null;

  const quoteMessage = buildQuoteMessageFromFields(fieldValues);
  const fieldLines = filledFields.map(([name, value]) => `${quoteFieldLabels[name] || name}: ${value}`);

  return {
    sessionId: getQuoteSessionId(),
    messageId: `quote-${action}-${Date.now()}`,
    timestamp: new Date().toISOString(),
    page: window.location.href,
    message: [
      'WEBSITE QUOTE / CONTACT LEAD COPY',
      `Customer action: ${action}`,
      `Page: ${window.location.href}`,
      linkText ? `Button text: ${linkText}` : '',
      linkHref ? `Button href: ${linkHref}` : '',
      ...fieldLines,
      'Customer-facing message:',
      quoteMessage
    ].filter(Boolean).join('\n'),
    conversationHistory: [],
    knownCustomerFields: fieldValues,
    currentLeadSummary: fieldLines.join('; '),
    guardrailVersion: 'website-quote-lead-copy-2026-05-25-any-contact-v2',
    source
  };
};

const rememberQuoteFields = (fieldValues) => {
  if (!fieldValues || !Object.keys(fieldValues).length) return;
  try {
    window.sessionStorage.setItem(quoteSessionStorageKey, JSON.stringify(fieldValues));
    window.sessionStorage.setItem(quoteSessionTimestampKey, new Date().toISOString());
  } catch (error) {
    // Some browsers block storage; capture still works from live fields.
  }
};

const getStoredQuoteFields = () => {
  try {
    const raw = window.sessionStorage.getItem(quoteSessionStorageKey);
    if (!raw) return {};
    const parsed = JSON.parse(raw);
    return parsed && typeof parsed === 'object' ? parsed : {};
  } catch (error) {
    return {};
  }
};

const getLiveQuoteFields = () => {
  const fields = Array.from(document.querySelectorAll('[data-quote-builder] input, [data-quote-builder] textarea, [data-quote-builder] select'));
  return quoteFieldOrder.reduce((values, name) => {
    const matchingFields = fields.filter((field) => field.name === name);
    if (!matchingFields.length) return values;
    const fieldValues = matchingFields
      .filter((field) => field.type !== 'checkbox' || field.checked)
      .map((field) => field.value.trim())
      .filter(Boolean);
    if (fieldValues.length) values[name] = fieldValues.join(', ');
    return values;
  }, {});
};

const getBestKnownQuoteFields = () => ({
  ...getStoredQuoteFields(),
  ...getLiveQuoteFields()
});

const quoteBuilders = document.querySelectorAll('[data-quote-builder]');
quoteBuilders.forEach((builder) => {
  const smsLink = builder.querySelector('[data-quote-sms]');
  const emailLink = builder.querySelector('[data-quote-email]');
  const fields = Array.from(builder.querySelectorAll('input, textarea, select'));

  const getFieldValue = (name) => {
    const matchingFields = fields.filter((field) => field.name === name);
    if (!matchingFields.length) return '';
    const values = matchingFields
      .filter((field) => field.type !== 'checkbox' || field.checked)
      .map((field) => field.value.trim())
      .filter(Boolean);
    return values.join(', ');
  };

  const getFieldValues = () => quoteFieldOrder.reduce((values, name) => {
    const value = getFieldValue(name);
    if (value) values[name] = value;
    return values;
  }, {});

  const buildMessage = () => buildQuoteMessageFromFields(getFieldValues());

  const captureQuoteLead = (action, link) => {
    const fieldValues = getFieldValues();
    rememberQuoteFields(fieldValues);
    const payload = makeQuoteCapturePayload({
      action,
      fieldValues,
      source: 'betterbeds.pro quote builder',
      linkHref: link?.getAttribute('href') || '',
      linkText: link?.textContent?.trim() || ''
    });
    if (payload) sendQuoteCapture(payload);
  };

  const updateLinks = () => {
    const fieldValues = getFieldValues();
    rememberQuoteFields(fieldValues);
    const message = buildQuoteMessageFromFields(fieldValues);
    const encodedMessage = encodeURIComponent(message);
    if (smsLink) smsLink.href = `sms:2145248401?body=${encodedMessage}`;
    if (emailLink) {
      emailLink.href = `mailto:info@betterbeds.pro?subject=${encodeURIComponent('Better Beds quote request')}&body=${encodedMessage}`;
    }
  };

  const validateEmailContact = (event) => {
    const preferredContact = getFieldValue('preferredContact').toLowerCase();
    const wantsCallOrText = preferredContact.includes('call') || preferredContact.includes('text');
    const phoneField = builder.querySelector('[name="customerPhone"]');
    const phone = phoneField ? phoneField.value.trim() : '';

    if (wantsCallOrText && !phone) {
      event.preventDefault();
      alert('Please enter your phone number before emailing the quote request, since you selected call or text as a preferred contact method.');
      if (phoneField) phoneField.focus();
      return false;
    }
    return true;
  };

  fields.forEach((field) => {
    field.addEventListener('input', updateLinks);
    field.addEventListener('change', updateLinks);
  });
  if (smsLink) {
    smsLink.addEventListener('click', () => captureQuoteLead('sms', smsLink));
  }
  if (emailLink) {
    emailLink.addEventListener('click', (event) => {
      if (validateEmailContact(event) === false) return;
      captureQuoteLead('email', emailLink);
    });
  }
  updateLinks();
});

document.addEventListener('click', (event) => {
  const link = event.target instanceof Element ? event.target.closest('a[href]') : null;
  if (!link) return;
  if (link.matches('[data-quote-sms], [data-quote-email]')) return;

  const href = link.getAttribute('href') || '';
  const hrefLower = href.toLowerCase();
  let action = '';
  if (hrefLower.startsWith('sms:')) action = 'sms_contact_button';
  if (hrefLower.startsWith('tel:')) action = 'call_contact_button';
  if (hrefLower.startsWith('mailto:')) action = 'email_contact_button';
  if (!action) return;

  const fieldValues = getBestKnownQuoteFields();
  if (!Object.keys(fieldValues).length) return;
  rememberQuoteFields(fieldValues);

  const payload = makeQuoteCapturePayload({
    action,
    fieldValues,
    source: 'betterbeds.pro contact button quote snapshot',
    linkHref: href,
    linkText: link.textContent.trim()
  });
  if (payload) sendQuoteCapture(payload);
});

const floatingApplyCtaHref = 'https://americanfirstfinance.com/app/?dealer=28821&loc=1&src=UA&usetextpin=Y';
if (!document.querySelector('.floating-apply-cta')) {
  const floatingApplyCta = document.createElement('a');
  floatingApplyCta.className = 'floating-apply-cta';
  floatingApplyCta.href = floatingApplyCtaHref;
  floatingApplyCta.target = '_blank';
  floatingApplyCta.rel = 'noopener';
  floatingApplyCta.setAttribute('aria-label', 'Apply with American First Finance');
  floatingApplyCta.innerHTML = '<span>Apply with AFF<small>Financing</small></span>';
  document.body.appendChild(floatingApplyCta);
}

// Better Beds secure estimate/photo upload form.
(function () {
  const form = document.querySelector('form[data-agent-upload="true"]');
  if (!form) return;
  const status = form.querySelector('[data-form-status]');
  const submit = form.querySelector('button[type="submit"]');
  const setStatus = (message, kind) => {
    if (!status) return;
    status.textContent = message;
    status.dataset.kind = kind || '';
  };
  form.addEventListener('submit', async (event) => {
    event.preventDefault();
    const honey = form.querySelector('input[name="_honey"]');
    if (honey && honey.value) return;
    const data = new FormData(form);
    data.delete('_honey');
    setStatus('Uploading your free estimate request…', 'pending');
    if (submit) submit.disabled = true;
    try {
      const response = await fetch(form.action, { method: 'POST', body: data, mode: 'cors' });
      const result = await response.json().catch(() => ({}));
      if (!response.ok || !result.ok) {
        const error = result.error || result.message || 'upload_failed';
        throw new Error(error);
      }
      setStatus(`Request received. Better Beds will review it soon. Request ID: ${result.id || result.leadId || 'received'}.`, 'success');
      form.reset();
    } catch (error) {
      setStatus('Upload did not go through. Please text photos/details to 214-524-8401 or try again in a moment.', 'error');
    } finally {
      if (submit) submit.disabled = false;
    }
  });
})();
