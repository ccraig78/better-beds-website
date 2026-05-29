(() => {
  const CONFIG = {
    knowledgeUrl: 'data/faq-knowledge.json?v=20260529-chat-ux-v2',
    chatEndpoint: 'https://chat.betterbeds.pro/better-beds-chat',
    unansweredEndpoint: 'api/faq-unanswered.php',
    guardrailVersion: 'website-chatbot-live-guardrails-2026-05-14',
    smsHref: 'sms:2145248401?body=Hi%20Better%20Beds%2C%20I%27d%20like%20a%20quote.%20I%27ll%20send%20truck%20photos%20and%20details.',
    phoneHref: 'tel:2145248401',
    quoteHref: 'quote.html'
  };

  const styles = `
    .bb-faq-widget * { box-sizing: border-box; }
    .bb-faq-widget { position: fixed; right: clamp(14px, 2.2vw, 28px); bottom: 112px; z-index: 9999; font-family: Inter, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; color: #07182e; }
    .bb-faq-toggle { border: 0; border-radius: 999px; background: linear-gradient(135deg, #0b4f9c, #0d7dd8); color: white; box-shadow: 0 14px 35px rgba(0, 30, 80, .35); padding: 13px 18px; font-weight: 900; cursor: pointer; display: inline-flex; align-items: center; gap: 8px; letter-spacing: .01em; }
    .bb-faq-toggle:hover, .bb-faq-toggle:focus { transform: translateY(-1px); outline: 3px solid rgba(13, 125, 216, .25); }
    .bb-faq-toggle.bb-faq-intro-hidden { visibility: hidden; }
    .bb-faq-toggle.bb-faq-intro-pulse { animation: bb-faq-button-pulse 1.05s ease-out 1; }
    .bb-faq-intro-ghost { position: fixed; z-index: 10000; border: 0; border-radius: 999px; background: linear-gradient(135deg, #0b4f9c, #0d7dd8); color: white; box-shadow: 0 24px 70px rgba(0, 30, 80, .36); font-family: Inter, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; font-weight: 950; letter-spacing: .01em; display: inline-flex; align-items: center; justify-content: center; gap: 10px; pointer-events: none; overflow: hidden; white-space: nowrap; }
    .bb-faq-intro-ghost small { display: block; font-size: .72em; font-weight: 800; opacity: .82; margin-left: 4px; }
    @keyframes bb-faq-button-pulse { 0% { transform: scale(1); box-shadow: 0 14px 35px rgba(0, 30, 80, .35); } 45% { transform: scale(1.08); box-shadow: 0 18px 48px rgba(13, 125, 216, .48); } 100% { transform: scale(1); box-shadow: 0 14px 35px rgba(0, 30, 80, .35); } }
    .bb-faq-panel { width: min(620px, calc(100vw - 32px)); height: min(720px, calc(100vh - 120px)); min-height: 560px; display: none; flex-direction: column; overflow: hidden; border-radius: 22px; background: #fff; box-shadow: 0 22px 70px rgba(2, 12, 30, .38); border: 1px solid rgba(9, 35, 70, .14); }
    .bb-faq-widget.is-open { bottom: clamp(18px, 3vh, 36px); }
    .bb-faq-widget.is-open .bb-faq-panel { display: flex; }
    .bb-faq-widget.is-open .bb-faq-toggle { display: none; }
    .bb-faq-header { background: linear-gradient(135deg, #061a35, #0b4f9c); color: white; padding: 18px 20px; display: flex; justify-content: space-between; gap: 12px; align-items: flex-start; }
    .bb-faq-header strong { display: block; font-size: 1.16rem; }
    .bb-faq-header span { display: block; color: rgba(255,255,255,.86); font-size: .92rem; margin-top: 3px; }
    .bb-faq-close { background: rgba(255,255,255,.14); color: white; border: 1px solid rgba(255,255,255,.22); width: 36px; height: 36px; border-radius: 999px; cursor: pointer; font-size: 22px; line-height: 1; flex: 0 0 auto; }
    .bb-faq-messages { padding: 18px; overflow-y: auto; background: #f4f7fb; display: grid; gap: 12px; align-content: start; flex: 1 1 auto; min-height: 260px; }
    .bb-faq-message { border-radius: 16px; padding: 12px 14px; line-height: 1.42; font-size: .98rem; max-width: 88%; }
    .bb-faq-message.bot { background: white; border: 1px solid rgba(9, 35, 70, .10); justify-self: start; }
    .bb-faq-message.user { background: #0b4f9c; color: white; justify-self: end; }
    .bb-faq-message.thinking { display: inline-flex; align-items: center; gap: 8px; }
    .bb-faq-spinner { width: 14px; height: 14px; border: 2px solid rgba(11,79,156,.22); border-top-color: #0b4f9c; border-radius: 999px; animation: bb-faq-spin .8s linear infinite; flex: 0 0 auto; }
    @keyframes bb-faq-spin { to { transform: rotate(360deg); } }
    .bb-faq-quick { display: flex; flex-wrap: wrap; gap: 8px; padding: 0 18px 14px; background: #f4f7fb; }
    .bb-faq-chip { border: 1px solid rgba(11,79,156,.20); background: white; color: #0b376b; border-radius: 999px; padding: 9px 12px; cursor: pointer; font-weight: 850; font-size: .84rem; }
    .bb-faq-chip:hover { background: #eaf4ff; }
    .bb-faq-form { border-top: 1px solid rgba(9, 35, 70, .12); padding: 14px; display: grid; gap: 10px; background: white; flex: 0 0 auto; }
    .bb-faq-row { display: flex; gap: 9px; }
    .bb-faq-input { flex: 1; min-width: 0; border: 1px solid rgba(9, 35, 70, .20); border-radius: 14px; padding: 12px 13px; font: inherit; }
    .bb-faq-send { border: 0; border-radius: 14px; background: #0b4f9c; color: white; font-weight: 900; padding: 0 16px; cursor: pointer; }
    .bb-faq-escalation { display: none; gap: 8px; grid-template-columns: 1fr; border-top: 1px dashed rgba(9,35,70,.18); padding-top: 10px; }
    .bb-faq-escalation.is-visible { display: grid; }
    .bb-faq-escalation input, .bb-faq-escalation textarea { width: 100%; border: 1px solid rgba(9, 35, 70, .20); border-radius: 12px; padding: 9px 10px; font: inherit; }
    .bb-faq-actions { display: flex; gap: 8px; flex-wrap: wrap; align-items: center; }
    .bb-faq-actions a, .bb-faq-actions button { text-decoration: none; border: 0; border-radius: 999px; padding: 9px 12px; font-weight: 900; cursor: pointer; font-size: .84rem; }
    .bb-faq-actions a { background: #eaf4ff; color: #073b73; }
    .bb-faq-actions .bb-faq-primary-link { background: #0b4f9c; color: white; }
    .bb-faq-submit-question { background: #0b4f9c; color: white; }
    .bb-faq-small { color: #526070; font-size: .8rem; line-height: 1.35; }
    .bb-faq-footer-cta { color: #526070; font-size: .8rem; line-height: 1.35; display: flex; gap: 8px; flex-wrap: wrap; align-items: center; }
    .bb-faq-footer-cta a { color: #0b4f9c; font-weight: 900; text-decoration: underline; text-underline-offset: .16em; }
    .bb-faq-cta-card { justify-self: start; max-width: 92%; background: #eef7ff; border: 1px solid rgba(11,79,156,.16); border-radius: 16px; padding: 12px; display: grid; gap: 9px; }
    .bb-faq-cta-card strong { color: #09284a; }
    @media (max-width: 760px) { .bb-faq-widget { left: 8px; right: 8px; bottom: calc(112px + env(safe-area-inset-bottom)); transform: none; display: block; width: auto; } .bb-faq-widget.is-open { bottom: calc(8px + env(safe-area-inset-bottom)); } .bb-faq-toggle { margin-left: auto; padding: 12px 16px; justify-content: center; width: max-content; max-width: 100%; } .bb-faq-panel { width: calc(100vw - 16px); height: min(760px, calc(100dvh - 18px)); min-height: 0; max-height: none; border-radius: 18px; } .bb-faq-message { max-width: 94%; } .bb-faq-header { padding: 15px; } .bb-faq-messages { padding: 14px; } }
  `;

  const state = {
    knowledge: null,
    lastQuestion: '',
    escalationVisible: false,
    sessionId: (globalThis.crypto?.randomUUID ? globalThis.crypto.randomUUID() : `bb-${Date.now()}-${Math.random().toString(16).slice(2)}`),
    conversationHistory: []
  };

  const escapeHtml = (value) => String(value).replace(/[&<>'"]/g, (char) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#39;', '"': '&quot;' }[char]));
  const normalize = (value) => String(value || '').toLowerCase().replace(/[^a-z0-9\s]/g, ' ').replace(/\s+/g, ' ').trim();

  const addMessage = (messages, text, type = 'bot') => {
    const bubble = document.createElement('div');
    bubble.className = `bb-faq-message ${type}`;
    bubble.innerHTML = escapeHtml(text).replace(/\n/g, '<br>');
    messages.appendChild(bubble);
    messages.scrollTop = messages.scrollHeight;
    return bubble;
  };

  const scoreEntry = (query, entry) => {
    const normalizedQuery = normalize(query);
    if (!normalizedQuery) return 0;
    let score = 0;
    const haystack = normalize(`${entry.question} ${(entry.keywords || []).join(' ')}`);
    (entry.keywords || []).forEach((keyword) => {
      const normalizedKeyword = normalize(keyword);
      if (!normalizedKeyword) return;
      if (normalizedQuery.includes(normalizedKeyword)) score += Math.min(8, normalizedKeyword.split(' ').length * 2 + 1);
    });
    normalizedQuery.split(' ').forEach((word) => {
      if (word.length > 2 && haystack.includes(word)) score += 1;
    });
    return score;
  };

  const shouldRoadieReview = (question, match) => {
    const q = normalize(question);
    if (!match?.entry) return true;
    const hasSpecificTruck = /\b(19\d{2}|20\d{2}|chevy|gmc|ford|ram|dodge|toyota|nissan|jeep|silverado|sierra|f150|f-150|f250|f-250|f350|f-350|1500|2500|3500|dually)\b/.test(q);
    const asksExactInventory = /\b(in stock|inventory|available|do you have|have a|have any|currently have|ready now)\b/.test(q);
    const asksExactFitment = /\b(fit|fits|compatible|interchange|bolt on|work on my)\b/.test(q) && hasSpecificTruck;
    const asksFinalQuote = /\b(final quote|exact price|firm price|out the door|total price)\b/.test(q);
    const mentionsPhotosOrDamage = /\b(photo|picture|damage|damaged|wreck|collision|rusted out|repair this|estimate this)\b/.test(q) && hasSpecificTruck;
    return asksExactInventory || asksExactFitment || asksFinalQuote || mentionsPhotosOrDamage;
  };

  const classifyMatch = (question) => {
    const entries = state.knowledge?.entries || [];
    let best = null;
    let bestScore = 0;
    entries.forEach((entry) => {
      const score = scoreEntry(question, entry);
      if (score > bestScore) {
        best = entry;
        bestScore = score;
      }
    });
    if (!best || bestScore < 3) return { entry: null, score: bestScore, level: 'none', roadieNeeded: true };
    const level = bestScore >= 7 ? 'high' : 'medium';
    return { entry: best, score: bestScore, level, roadieNeeded: shouldRoadieReview(question, { entry: best, score: bestScore, level }) };
  };

  const conversationalFaqAnswer = (match) => {
    if (!match?.entry?.answer) return '';
    if (match.level === 'medium') {
      return `${match.entry.answer}\n\nIf you want, send your truck details/photos and Better Beds can get more specific.`;
    }
    return match.entry.answer;
  };

  const findAnswer = (question) => {
    const match = classifyMatch(question);
    return match.entry ? match.entry : null;
  };

  const shouldShowLeadPrompt = (question, answer = '') => {
    const text = normalize(`${question} ${answer}`);
    return /\b(quote|estimate|price|cost|how much|repair|replace|replacement|in stock|available|inventory|damage|damaged|collision|rust|rusted|paint|bedliner|install|photos|pictures)\b/.test(text);
  };

  const logLowConfidenceQuestion = (question, match) => {
    if (match?.level === 'high' && !match.roadieNeeded) return;
    try {
      fetch(CONFIG.unansweredEndpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          question,
          source: 'roadie-low-confidence-log',
          faqMatchId: match?.entry?.id || null,
          faqScore: match?.score || 0,
          faqLevel: match?.level || 'none',
          roadieNeeded: Boolean(match?.roadieNeeded),
          page: window.location.href,
          userAgent: navigator.userAgent,
          submittedAt: new Date().toISOString()
        })
      }).catch(() => {});
    } catch (error) {
      // Best-effort improvement log only.
    }
  };

  const rememberTurn = (role, content) => {
    state.conversationHistory.push({ role, content: String(content || '').slice(0, 2000), timestamp: new Date().toISOString() });
    if (state.conversationHistory.length > 12) state.conversationHistory = state.conversationHistory.slice(-12);
  };

  const callRoadie = async (question, fallbackMatch = null) => {
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 45000);
    try {
      const response = await fetch(CONFIG.chatEndpoint, {
        method: 'POST',
        signal: controller.signal,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          sessionId: state.sessionId,
          messageId: `turn-${Date.now()}-${Math.random().toString(16).slice(2, 10)}`,
          timestamp: new Date().toISOString(),
          page: window.location.href,
          message: question,
          conversationHistory: state.conversationHistory.slice(-10),
          guardrailVersion: CONFIG.guardrailVersion,
          sourceFallbackMatch: fallbackMatch
        })
      });
      if (!response.ok) throw new Error(`Roadie HTTP ${response.status}`);
      const data = await response.json();
      const reply = data.reply || data.answer;
      if (!reply) throw new Error('Roadie empty reply');
      return { ok: true, data, reply };
    } catch (error) {
      return { ok: false, error };
    } finally {
      clearTimeout(timeout);
    }
  };

  const showEscalation = (root, question = '') => {
    state.escalationVisible = true;
    const escalation = root.querySelector('.bb-faq-escalation');
    const textarea = root.querySelector('[name="bbFaqQuestionDetails"]');
    if (textarea && question) textarea.value = question;
    escalation?.classList.add('is-visible');
  };

  const hideEscalation = (root) => {
    state.escalationVisible = false;
    root.querySelector('.bb-faq-escalation')?.classList.remove('is-visible');
    root.querySelectorAll('.bb-faq-cta-card').forEach((card) => card.remove());
  };

  const showQuoteCta = (messages) => {
    if (messages.querySelector('.bb-faq-cta-card')) return;
    const card = document.createElement('div');
    card.className = 'bb-faq-cta-card';
    card.innerHTML = `
      <strong>Need a real quote?</strong>
      <div class="bb-faq-small">Roadie can answer quick questions here. For an accurate quote, photos and truck details help most.</div>
      <div class="bb-faq-actions">
        <a class="bb-faq-primary-link" href="${CONFIG.quoteHref}">Open photo quote form</a>
        <a href="${CONFIG.smsHref}">Text photos</a>
        <a href="${CONFIG.phoneHref}">Call</a>
      </div>
    `;
    messages.appendChild(card);
    messages.scrollTop = messages.scrollHeight;
  };

  const buildWidget = () => {
    if (document.querySelector('.bb-faq-widget')) return;

    const styleEl = document.createElement('style');
    styleEl.textContent = styles;
    document.head.appendChild(styleEl);

    const root = document.createElement('section');
    root.className = 'bb-faq-widget';
    root.setAttribute('aria-label', 'Better Beds Roadie chat assistant');
    root.innerHTML = `
      <button class="bb-faq-toggle" type="button" aria-expanded="false">💬 Ask Better Beds</button>
      <div class="bb-faq-panel" role="dialog" aria-modal="false" aria-label="Better Beds Roadie chat assistant">
        <div class="bb-faq-header">
          <div><strong>Roadie</strong><span>Better Beds AI helper for truck beds, repair, paint, installs, and quotes.</span></div>
          <button class="bb-faq-close" type="button" aria-label="Close Roadie chat assistant">×</button>
        </div>
        <div class="bb-faq-messages" aria-live="polite"></div>
        <div class="bb-faq-quick" aria-label="Common questions">
          <button class="bb-faq-chip" type="button">How much does a bed cost?</button>
          <button class="bb-faq-chip" type="button">Do you install beds?</button>
          <button class="bb-faq-chip" type="button">Where are you located?</button>
          <button class="bb-faq-chip" type="button">Will paint match?</button>
        </div>
        <form class="bb-faq-form">
          <div class="bb-faq-row">
            <input class="bb-faq-input" name="bbFaqQuestion" autocomplete="off" placeholder="Ask a truck bed question…" aria-label="Ask a truck bed question" />
            <button class="bb-faq-send" type="submit">Send</button>
          </div>
          <div class="bb-faq-escalation" aria-label="Send unanswered question to Better Beds">
            <div class="bb-faq-small">Want Better Beds to answer this? Leave your name and the best phone/email. Please don’t send payment info here.</div>
            <input name="bbFaqName" autocomplete="name" placeholder="Your name" />
            <input name="bbFaqContact" autocomplete="email tel" placeholder="Phone or email for reply" />
            <textarea name="bbFaqQuestionDetails" rows="3" placeholder="Question or truck details"></textarea>
            <div class="bb-faq-actions">
              <button class="bb-faq-submit-question" type="button">Send to Better Beds</button>
              <a href="${CONFIG.smsHref}">Text photos instead</a>
              <a href="${CONFIG.phoneHref}">Call now</a>
            </div>
          </div>
          <div class="bb-faq-footer-cta">Ask Roadie here first. Ready for an estimate? <a href="${CONFIG.quoteHref}">Open the photo quote form</a>.</div>
        </form>
      </div>
    `;
    document.body.appendChild(root);

    const toggle = root.querySelector('.bb-faq-toggle');
    const close = root.querySelector('.bb-faq-close');
    const messages = root.querySelector('.bb-faq-messages');
    const form = root.querySelector('.bb-faq-form');
    const questionInput = root.querySelector('[name="bbFaqQuestion"]');
    const detailsInput = root.querySelector('[name="bbFaqQuestionDetails"]');
    const submitQuestion = root.querySelector('.bb-faq-submit-question');

    addMessage(messages, 'Hi — I’m Roadie, the Better Beds AI helper. I can help with truck beds, repair, paint, installs, bedliners, and quote questions.');

    toggle.addEventListener('click', () => {
      root.classList.add('is-open');
      toggle.setAttribute('aria-expanded', 'true');
      setTimeout(() => questionInput.focus(), 50);
    });
    close.addEventListener('click', () => {
      root.classList.remove('is-open');
      toggle.setAttribute('aria-expanded', 'false');
    });

    root.querySelectorAll('.bb-faq-chip').forEach((chip) => {
      chip.addEventListener('click', () => {
        questionInput.value = chip.textContent.trim();
        form.dispatchEvent(new Event('submit', { cancelable: true }));
      });
    });

    form.addEventListener('submit', async (event) => {
      event.preventDefault();
      const question = questionInput.value.trim();
      if (!question) return;
      state.lastQuestion = question;
      addMessage(messages, question, 'user');
      rememberTurn('customer', question);
      questionInput.value = '';
      hideEscalation(root);

      const faqMatch = classifyMatch(question);
      const faqAnswer = faqMatch.entry ? conversationalFaqAnswer(faqMatch) : '';
      const fallbackMatch = faqMatch.entry ? {
        matched: true,
        source: 'faq',
        questionId: faqMatch.entry.id || null,
        confidence: faqMatch.score || 0,
        approvedAnswer: faqMatch.entry.answer,
        level: faqMatch.level
      } : { matched: false, source: 'none', questionId: null, confidence: faqMatch.score || 0, approvedAnswer: null };

      if (faqMatch.entry && !faqMatch.roadieNeeded && faqMatch.level === 'high') {
        addMessage(messages, faqAnswer);
        rememberTurn('assistant', faqAnswer);
        if (shouldShowLeadPrompt(question, faqAnswer)) showQuoteCta(messages);
        return;
      }

      if (faqMatch.entry && !faqMatch.roadieNeeded && faqMatch.level === 'medium') {
        addMessage(messages, faqAnswer);
        rememberTurn('assistant', faqAnswer);
        logLowConfidenceQuestion(question, faqMatch);
        if (shouldShowLeadPrompt(question, faqAnswer)) showQuoteCta(messages);
        return;
      }

      logLowConfidenceQuestion(question, faqMatch);
      const thinking = addMessage(messages, 'Roadie is thinking…');
      thinking.classList.add('thinking');
      thinking.insertAdjacentHTML('afterbegin', '<span class="bb-faq-spinner" aria-hidden="true"></span>');
      const roadie = await callRoadie(question, fallbackMatch);
      thinking.remove();

      if (roadie.ok) {
        addMessage(messages, roadie.reply);
        rememberTurn('assistant', roadie.reply);
        if (roadie.data?.escalate) showEscalation(root, question);
        else if (shouldShowLeadPrompt(question, roadie.reply)) showQuoteCta(messages);
        return;
      }

      if (faqMatch.entry) {
        addMessage(messages, `${faqAnswer}

Roadie is having trouble connecting right now, so I used a saved Better Beds answer.`);
        rememberTurn('assistant', faqAnswer);
        if (shouldShowLeadPrompt(question, faqAnswer)) showQuoteCta(messages);
      } else {
        const fallback = "I’m not fully sure on that one, and I don’t want to guess. Send it to Better Beds and someone can follow up with the right answer.";
        addMessage(messages, `${fallback}

Roadie is having trouble connecting right now.`);
        rememberTurn('assistant', fallback);
        showEscalation(root, question);
      }
    });

    const playHomepageIntro = () => {
      const isHomePage = ['/', '/index.html', ''].includes(window.location.pathname);
      if (!isHomePage || root.classList.contains('is-open')) return;
      if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
      try {
        if (sessionStorage.getItem('betterBedsRoadieIntroSeen') === 'true') return;
        sessionStorage.setItem('betterBedsRoadieIntroSeen', 'true');
      } catch (error) {
        // If storage is unavailable, still show the intro once for this page load.
      }
      if (!toggle.animate) return;

      window.setTimeout(() => {
        if (!document.body.contains(toggle) || root.classList.contains('is-open')) return;
        const target = toggle.getBoundingClientRect();
        if (!target.width || !target.height) return;

        const startWidth = Math.min(window.innerWidth - 28, 820);
        const startHeight = Math.max(target.height * 1.75, 74);
        const startLeft = (window.innerWidth - startWidth) / 2;
        const startTop = Math.max(86, Math.min(window.innerHeight * 0.28, 220));
        const ghost = document.createElement('div');
        const startFontSize = Math.min(24, Math.max(18, window.innerWidth / 26));
        const targetFontSize = parseFloat(window.getComputedStyle(toggle).fontSize) || 16;
        ghost.className = 'bb-faq-intro-ghost';
        ghost.textContent = '💬 Ask Better Beds…';
        ghost.style.left = `${startLeft}px`;
        ghost.style.top = `${startTop}px`;
        ghost.style.width = `${startWidth}px`;
        ghost.style.height = `${startHeight}px`;
        ghost.style.fontSize = `${startFontSize}px`;
        document.body.appendChild(ghost);
        toggle.classList.add('bb-faq-intro-hidden');

        const animation = ghost.animate([
          { left: `${startLeft}px`, top: `${startTop}px`, width: `${startWidth}px`, height: `${startHeight}px`, fontSize: `${startFontSize}px`, opacity: 0, transform: 'scale(.98)' },
          { left: `${startLeft}px`, top: `${startTop}px`, width: `${startWidth}px`, height: `${startHeight}px`, fontSize: `${startFontSize}px`, opacity: 1, transform: 'scale(1)', offset: .18 },
          { left: `${startLeft}px`, top: `${startTop}px`, width: `${startWidth}px`, height: `${startHeight}px`, fontSize: `${startFontSize}px`, opacity: 1, transform: 'scale(1)', offset: .52 },
          { left: `${target.left}px`, top: `${target.top}px`, width: `${target.width}px`, height: `${target.height}px`, fontSize: `${targetFontSize}px`, opacity: 1, transform: 'scale(1)' }
        ], { duration: 2550, easing: 'cubic-bezier(.2,.8,.2,1)', fill: 'forwards' });

        animation.addEventListener('finish', () => {
          ghost.remove();
          toggle.classList.remove('bb-faq-intro-hidden');
          toggle.classList.add('bb-faq-intro-pulse');
          window.setTimeout(() => toggle.classList.remove('bb-faq-intro-pulse'), 1200);
        });
      }, 650);
    };

    playHomepageIntro();

    submitQuestion.addEventListener('click', async () => {
      const payload = {
        question: detailsInput.value.trim() || state.lastQuestion,
        name: root.querySelector('[name="bbFaqName"]').value.trim(),
        contact: root.querySelector('[name="bbFaqContact"]').value.trim(),
        page: window.location.href,
        userAgent: navigator.userAgent,
        submittedAt: new Date().toISOString()
      };
      if (!payload.question) {
        addMessage(messages, 'Please type the question first.');
        return;
      }

      submitQuestion.disabled = true;
      submitQuestion.textContent = 'Sending…';
      try {
        const response = await fetch(CONFIG.unansweredEndpoint, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        });
        if (!response.ok) throw new Error('Bad response');
        addMessage(messages, 'Got it — Better Beds received your question. If you left contact info, someone can follow up directly.');
        hideEscalation(root);
        form.reset();
      } catch (error) {
        const subject = encodeURIComponent('Unanswered Better Beds website question');
        const body = encodeURIComponent(`Question: ${payload.question}\nName: ${payload.name}\nContact: ${payload.contact}\nPage: ${payload.page}`);
        addMessage(messages, 'I could not send that automatically from this page. You can still email it to Better Beds with the button that just appeared.');
        const actionRow = document.createElement('div');
        actionRow.className = 'bb-faq-actions';
        actionRow.innerHTML = `<a href="mailto:info@betterbeds.pro?subject=${subject}&body=${body}">Email this question</a>`;
        messages.appendChild(actionRow);
      } finally {
        submitQuestion.disabled = false;
        submitQuestion.textContent = 'Send to Better Beds';
      }
    });
  };

  const init = async () => {
    try {
      const response = await fetch(CONFIG.knowledgeUrl, { cache: 'no-store' });
      if (response.ok) state.knowledge = await response.json();
    } catch (error) {
      // Use empty state; unanswered path will still work.
    }
    buildWidget();
  };

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
