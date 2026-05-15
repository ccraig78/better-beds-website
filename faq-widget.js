(() => {
  const CONFIG = {
    knowledgeUrl: 'data/faq-knowledge.json?v=20260515-roadie-fallback',
    chatEndpoint: 'https://chat.betterbeds.pro/better-beds-chat',
    unansweredEndpoint: 'api/faq-unanswered.php',
    guardrailVersion: 'website-chatbot-live-guardrails-2026-05-14',
    smsHref: 'sms:2145248401?body=Hi%20Better%20Beds%2C%20I%27d%20like%20a%20quote.%20I%27ll%20send%20truck%20photos%20and%20details.',
    phoneHref: 'tel:2145248401'
  };

  const styles = `
    .bb-faq-widget * { box-sizing: border-box; }
    .bb-faq-widget { position: fixed; right: clamp(14px, 2.2vw, 28px); bottom: 96px; z-index: 9999; font-family: Inter, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; color: #07182e; }
    .bb-faq-toggle { border: 0; border-radius: 999px; background: linear-gradient(135deg, #0b4f9c, #0d7dd8); color: white; box-shadow: 0 14px 35px rgba(0, 30, 80, .35); padding: 13px 18px; font-weight: 900; cursor: pointer; display: inline-flex; align-items: center; gap: 8px; letter-spacing: .01em; }
    .bb-faq-toggle:hover, .bb-faq-toggle:focus { transform: translateY(-1px); outline: 3px solid rgba(13, 125, 216, .25); }
    .bb-faq-panel { width: min(380px, calc(100vw - 28px)); max-height: min(680px, calc(100vh - 100px)); display: none; flex-direction: column; overflow: hidden; border-radius: 22px; background: #fff; box-shadow: 0 22px 70px rgba(2, 12, 30, .38); border: 1px solid rgba(9, 35, 70, .14); }
    .bb-faq-widget.is-open .bb-faq-panel { display: flex; }
    .bb-faq-widget.is-open .bb-faq-toggle { display: none; }
    .bb-faq-header { background: linear-gradient(135deg, #061a35, #0b4f9c); color: white; padding: 16px; display: flex; justify-content: space-between; gap: 12px; align-items: flex-start; }
    .bb-faq-header strong { display: block; font-size: 1.05rem; }
    .bb-faq-header span { display: block; color: rgba(255,255,255,.82); font-size: .86rem; margin-top: 2px; }
    .bb-faq-close { background: rgba(255,255,255,.14); color: white; border: 1px solid rgba(255,255,255,.22); width: 32px; height: 32px; border-radius: 999px; cursor: pointer; font-size: 20px; line-height: 1; }
    .bb-faq-messages { padding: 14px; overflow-y: auto; background: #f4f7fb; display: grid; gap: 10px; }
    .bb-faq-message { border-radius: 16px; padding: 10px 12px; line-height: 1.35; font-size: .94rem; max-width: 92%; }
    .bb-faq-message.bot { background: white; border: 1px solid rgba(9, 35, 70, .10); justify-self: start; }
    .bb-faq-message.user { background: #0b4f9c; color: white; justify-self: end; }
    .bb-faq-quick { display: flex; flex-wrap: wrap; gap: 7px; padding: 0 14px 12px; background: #f4f7fb; }
    .bb-faq-chip { border: 1px solid rgba(11,79,156,.20); background: white; color: #0b376b; border-radius: 999px; padding: 7px 10px; cursor: pointer; font-weight: 800; font-size: .78rem; }
    .bb-faq-chip:hover { background: #eaf4ff; }
    .bb-faq-form { border-top: 1px solid rgba(9, 35, 70, .12); padding: 12px; display: grid; gap: 8px; background: white; }
    .bb-faq-row { display: flex; gap: 8px; }
    .bb-faq-input { flex: 1; min-width: 0; border: 1px solid rgba(9, 35, 70, .20); border-radius: 14px; padding: 11px 12px; font: inherit; }
    .bb-faq-send { border: 0; border-radius: 14px; background: #0b4f9c; color: white; font-weight: 900; padding: 0 14px; cursor: pointer; }
    .bb-faq-escalation { display: none; gap: 8px; grid-template-columns: 1fr; }
    .bb-faq-escalation.is-visible { display: grid; }
    .bb-faq-escalation input, .bb-faq-escalation textarea { width: 100%; border: 1px solid rgba(9, 35, 70, .20); border-radius: 12px; padding: 9px 10px; font: inherit; }
    .bb-faq-actions { display: flex; gap: 8px; flex-wrap: wrap; }
    .bb-faq-actions a, .bb-faq-actions button { text-decoration: none; border: 0; border-radius: 999px; padding: 9px 12px; font-weight: 900; cursor: pointer; font-size: .84rem; }
    .bb-faq-actions a { background: #eaf4ff; color: #073b73; }
    .bb-faq-submit-question { background: #0b4f9c; color: white; }
    .bb-faq-small { color: #526070; font-size: .78rem; line-height: 1.3; }
    @media (max-width: 560px) { .bb-faq-widget { left: 50%; right: auto; bottom: calc(72px + env(safe-area-inset-bottom)); transform: translateX(-50%); display: flex; justify-content: center; width: min(360px, calc(100vw - 24px)); } .bb-faq-toggle { padding: 12px 16px; justify-content: center; width: max-content; max-width: 100%; } .bb-faq-panel { width: min(380px, calc(100vw - 24px)); max-height: calc(100vh - 116px); } }
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

  const findAnswer = (question) => {
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
    return bestScore >= 3 ? best : null;
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
          <div class="bb-faq-small">For quotes, photos help a lot: truck year/make/model, bed length, SRW/dually, color or paint code, and what you need done.</div>
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

      const match = findAnswer(question);
      const fallbackMatch = match ? {
        matched: true,
        source: 'faq',
        questionId: match.id || null,
        confidence: 1,
        approvedAnswer: match.answer
      } : { matched: false, source: 'none', questionId: null, confidence: 0, approvedAnswer: null };

      const thinking = addMessage(messages, 'Roadie is checking that…');
      const roadie = await callRoadie(question, fallbackMatch);
      thinking.remove();

      if (roadie.ok) {
        addMessage(messages, roadie.reply);
        rememberTurn('assistant', roadie.reply);
        if (roadie.data?.escalate) showEscalation(root, question);
        return;
      }

      if (match) {
        addMessage(messages, `${match.answer}

Roadie is having trouble connecting right now, so I used a saved Better Beds answer.`);
        rememberTurn('assistant', match.answer);
      } else {
        const fallback = "I’m not fully sure on that one, and I don’t want to guess. Send it to Better Beds and someone can follow up with the right answer.";
        addMessage(messages, `${fallback}

Roadie is having trouble connecting right now.`);
        rememberTurn('assistant', fallback);
        showEscalation(root, question);
      }
    });

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
