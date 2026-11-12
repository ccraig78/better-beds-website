// Roadie uses the published FAQ answers, so the inventory policy stays consistent.
function betterBedsFaqAnswer(question, entries, id) {
  const fallback = 'Call or text 214-524-8401 with your truck year, make, model, bed length, and the item you’re interested in. Better Beds will confirm current stock, fitment, condition, what’s included, and pricing.';
  const q = question.toLowerCase();
  let match = id ? entries.find(entry => entry.id === id) : null;
  const preferred = /\b(install|installation|remove|removal|swap)\b/.test(q) ? 'installation'
    : /\b(repair|repairs|repaired|painting|paint|repaint|refinish|restoration)\b/.test(q) ? 'stock-preparation'
    : /available[ -]to[ -]order|\bpre[ -]?order\b|order(?:ing)?\s+(?:a\s+)?bed|expected arrival|not (?:at|picked up)/.test(q) ? 'available-to-order'
    : /\b(pickup|loading|forklift|trailer)\b/.test(q) ? 'pickup'
    : /\b(stock|available|inventory|ford|f.?250|f.?350|chevy|gmc|ram|price|cost|how much)\b/.test(q) ? 'inventory'
    : /\b(takeoff|take-off)\b/.test(q) ? 'takeoff' : null;
  if (!match && preferred) match = entries.find(entry => entry.id === preferred);
  if (!match) {
    const scored = entries.map(entry => ({ entry, score: entry.keywords.reduce((n, keyword) => n + (q.includes(keyword.toLowerCase()) ? keyword.length : 0), 0) })).sort((a, b) => b.score - a.score);
    if (scored[0]?.score >= 4) match = scored[0].entry;
  }
  return match?.answer || fallback;
}
if (typeof module !== 'undefined' && module.exports) module.exports = { betterBedsFaqAnswer };
if (typeof document !== 'undefined') (() => {
  const widget = document.createElement('aside');
  widget.className = 'roadie';
  widget.setAttribute('aria-label', 'Better Beds quick answers');
  widget.innerHTML = `<button type="button" class="roadie-toggle" aria-expanded="false" aria-controls="roadie-panel">Questions? <span aria-hidden="true">↗</span></button>
    <section id="roadie-panel" class="roadie-panel" aria-label="Roadie quick answers" hidden>
      <div class="roadie-header"><div><strong>Roadie</strong><small>Better Beds · Quick answers</small></div><button type="button" class="roadie-close" aria-label="Close quick answers">×</button></div>
      <div class="roadie-body"><p>Ask about takeoff beds, pricing, fitment, or pickup. Call or text to confirm a specific item.</p>
      <div class="roadie-chips"><button type="button" data-question="takeoff">What’s a takeoff?</button><button type="button" data-question="inventory">Current stock</button><button type="button" data-question="installation">Pickup & installation</button></div>
      <form class="roadie-form"><label for="roadie-question">Your question</label><div><input id="roadie-question" maxlength="500" placeholder="e.g. Do you have a Ford bed?" required><button type="submit">Ask</button></div></form>
      <p class="roadie-answer" aria-live="polite"></p><a class="text-link" href="sms:2145248401?body=Hi%20Better%20Beds%2C%20I%20have%20an%20inventory%20question.">Text Better Beds →</a></div>
    </section>`;
  document.body.append(widget);
  const toggle = widget.querySelector('.roadie-toggle');
  const panel = widget.querySelector('.roadie-panel');
  const input = widget.querySelector('input');
  const answer = widget.querySelector('.roadie-answer');
  let knowledge;
  let pending;
  const load = async () => {
    if (knowledge) return knowledge;
    if (pending) return pending;
    pending = fetch('data/faq-knowledge.json?v=20261112-stock-preparation').then(response => {
      if (!response.ok) throw new Error('FAQ unavailable');
      return response.json();
    }).then(data => { knowledge = data; return data; }).catch(() => ({ entries: [] })).finally(() => { pending = null; });
    return pending;
  };
  const close = () => { panel.hidden = true; toggle.hidden = false; toggle.setAttribute('aria-expanded', 'false'); toggle.focus(); };
  toggle.addEventListener('click', () => { panel.hidden = false; toggle.hidden = true; toggle.setAttribute('aria-expanded', 'true'); input.focus(); load(); });
  widget.querySelector('.roadie-close').addEventListener('click', close);
  widget.addEventListener('keydown', event => { if (event.key === 'Escape') close(); });
  let latest = 0;
  const respond = async (question, id) => {
    const request = ++latest;
    answer.textContent = 'Checking…';
    const data = await load();
    if (request !== latest) return;
    answer.textContent = betterBedsFaqAnswer(question, data.entries, id);
  };
  widget.querySelector('form').addEventListener('submit', event => { event.preventDefault(); respond(input.value); });
  widget.querySelectorAll('[data-question]').forEach(button => button.addEventListener('click', () => respond('', button.dataset.question)));
})();
