# Better Beds Website

Website files for Better Beds Dallas.

## Current setup

This is a simple static website so it can be hosted easily on Hostinger and versioned through GitHub.

## Files

- `index.html` — page content and structure
- `styles.css` — layout, colors, responsive design
- `script.js` — mobile menu and small page behaviors

## Photo workflow

Real job photos can be added later and used in the repair gallery. Best folders to add next:

```text
assets/
  images/
    jobs/
      job-01-before.jpg
      job-01-after.jpg
```

## Contact form note

The first draft uses a temporary `mailto:` form. Before launch, connect this to one of these:

- Hostinger form/email handling
- Formspree / Basin / Netlify-style form endpoint
- A small PHP form handler on Hostinger

## FAQ Assistant Widget

This site now includes a lightweight Better Beds FAQ assistant widget on every HTML page.

### Files

- `faq-widget.js` — floating chat/FAQ widget.
- `data/faq-knowledge.json` — approved FAQ answers the widget can use.
- `api/faq-unanswered.php` — PHP endpoint for questions the widget cannot answer.
- `private/faq-unanswered.jsonl` — created on the server when unanswered questions arrive.
- `tools/add-faq-answer.py` — local helper to add approved answers to the widget knowledge base.

### How unanswered questions work

If the widget cannot confidently answer, it asks the visitor for name/contact info and sends the question to `api/faq-unanswered.php`.

The PHP endpoint:

1. saves the question to `private/faq-unanswered.jsonl`;
2. emails `info@betterbeds.pro` by default, where Euro can see it;
3. reminds Euro/Buddy to add the approved answer to `data/faq-knowledge.json` after Clint approves it.

Hostinger should run the PHP endpoint if the site is deployed on PHP-capable hosting. If the endpoint is not available, the widget falls back to a `mailto:` button so the visitor can still email the question.

### Adding Clint's approved answer to the knowledge base

From the repo root:

```bash
tools/add-faq-answer.py "Customer question?" "Approved Better Beds answer." "keyword one, keyword two, keyword three"
```

Then commit/deploy the updated `data/faq-knowledge.json`.

### Safety boundaries

The widget should not promise exact pricing, exact inventory, perfect paint match, insurance coverage, or exact completion time unless Better Beds has verified it. It should never collect card, bank, or payment information.
