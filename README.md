# Better Beds inventory website

Static GitHub Pages site for https://betterbeds.pro/. GitHub Pages publishes the repository root on `main`. The site now focuses on new takeoff truck beds and parts, with select older inventory beds prepared by arrangement.

## Add or update inventory

1. Edit `data/inventory.json`. Each item needs a unique `id` and root-level `.html` `url`, title, make, models, years, bedLength, color, condition, category, numeric price, currency, includes, and status. Use `status: "available"` for active inventory.
2. Leave `image` and `imageAlt` as `null` until actual photos are available. The site shows an explicitly labeled placeholder. Do not use old damaged-bed photos as takeoff photos.
3. For real photos, save an optimized image under `assets/images/inventory/` and set `image` to its relative path and `imageAlt` to an accurate description.
4. Run `python tools/build-site.py` from any directory. This generates the homepage, inventory, individual product pages, shared pages, legacy redirects, structured data and sitemap. Generated HTML is committed for GitHub Pages, which does not require Python at runtime.
5. Review the pages, commit the JSON/photo/template changes along with generated HTML, and publish through the normal repository process.

The product templates currently describe new takeoff, bed-only inventory. When adding other product types, adapt the product detail inclusion copy and condition schema in `tools/build-site.py` to match the confirmed item. Do not invent quantities, accessories, stock or fitment.

## Shared content and behavior

- `tools/build-site.py`: shared layout, page content, product cards and metadata.
- `styles.css`: responsive storefront styles.
- `script.js`: mobile menu, inventory search, SMS/email message builder and existing multipart inquiry form integration.
- `faq-widget.js`: Roadie quick answers from the published FAQ knowledge file. It does not call the old remote repair-oriented chatbot.
- `data/faq-knowledge.json`: published FAQ page and Roadie answers. The generator updates the inventory answer from the listing data. Edit the other answers when business policies change.
- `.well-known/agent.json`: assistant-facing business policies. `llms.txt` is generated with current listings. Update the profile when business policies change.

## Existing inquiry integration

The inventory inquiry form retains `https://chat.betterbeds.pro/estimate-requests`, its multipart field names, and optional image upload limits (6 images, 5 MB each, 15 MB total). The endpoint path keeps its historical name. It is managed outside this repository. Do not submit test leads to production; intercept requests in browser tests. Call/text/email remain available if the form fails.

Clarity project `uzvvg1g1vl`, the existing phone/email/address/hours, financing application link, pickup and forklift-loading policy are retained. Installation and removal are not offered.

Legacy gallery, repair-example and bed-finding URLs direct visitors to current inventory or the secondary older-bed page, without showing old damaged-bed photos.

## Restore point

The verified pre-change website backup is at commit `45efac9bffaa1100b54cd896139851c083dbf9c1`. A full bundle and source archive were saved before this change. Production restoration should use a new commit that restores that source tree, preserving history.

## Checks

Run `python tools/build-site.py`, `node --check script.js`, `node --check faq-widget.js`, and `node tools/check-service-policy.cjs` before publication.
