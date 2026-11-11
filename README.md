# Better Beds inventory website

Static GitHub Pages site for https://betterbeds.pro/. GitHub Pages publishes the repository root on `main`. The site now focuses on new takeoff truck beds and parts, with select older inventory beds prepared by arrangement.

## Add or update inventory

1. Edit `data/inventory.json`. Each item needs a unique `id` and root-level `.html` `url`, title, `productType` (Beds, Lights, Tailgates or Bumpers), make, models, years, color, condition, category, numeric price, currency, includes, and status. Beds also need `bedLength` (the actual measurement, such as `6'9"` or `8'`) and `bedStyle` (Short bed, Long bed or Dually). Include both in the bed title. Use Ford, Ram, Chevy or GMC consistently as the make. Add part-specific facts in `features`, an array of `{ "name": "Release", "value": "Manual release" }` entries. Use `status: "available"` for active inventory.
2. Leave `image` and `imageAlt` as `null` until actual photos are available. The site shows an explicitly labeled placeholder. Do not use old damaged-bed photos as takeoff photos.
3. For real photos, save an optimized image under `assets/images/inventory/` and set `image` to its relative path, `imageAlt` to an accurate description, and `imageWidth` / `imageHeight` to its dimensions. Add a `photos` array for multiple views; each entry uses `src`, `alt`, `caption`, `width`, and `height`. The first view should match `image`. Photos are presented unchanged, and the listing contents determine what is included.
4. Run `python tools/build-site.py` from any directory. This generates the homepage, inventory, individual product pages, shared pages, legacy redirects, structured data and sitemap. Generated HTML is committed for GitHub Pages, which does not require Python at runtime.
5. Review the pages, commit the JSON/photo/template changes along with generated HTML, and publish through the normal repository process.

The product templates support beds, lights, tailgates and bumpers. Bed-only measurements are omitted from other parts. Set the exact included contents and features for every item; no camera, step, wiring, modules, brackets or hardware should be assumed included. Condition schema is emitted only for recognized condition values. Do not invent quantities, accessories, stock or fitment. Inventory filters use the part type, make and actual listed colors; empty categories are shown as having zero listings.

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

## Product search visibility

Each inventory item gets a unique static product page, a descriptive title and canonical URL, visible specifications and price, and Product/Offer structured data generated from the same inventory record. Actual photos are included in the product markup, social preview and image sitemap. Product details and metadata are present in the initial HTML, so reading them does not require JavaScript.

Run `python tools/check-product-seo.py` after generating pages. The check verifies product data, stock markup, crawler rules, sitemap images, internal links and social previews.

Use `status: "sold"` when a bed sells. Keep its original ID and URL: the item leaves available-inventory lists while its page remains accessible and shows SoldOut in structured data. `reserved` and other unavailable statuses use OutOfStock. Update the record promptly; do not reuse a sold item's URL for a different item. New product types need their condition and included-parts copy checked as described above.

`robots.txt` explicitly permits Googlebot, Googlebot-Image, Bingbot, OAI-SearchBot and ChatGPT-User. Cloudflare can add its own crawler policy ahead of the source file; verify the public robots.txt and crawler access after hosting changes. OpenAI search and model-training crawlers are separate. Allowing search does not require changing the existing Cloudflare training policy.

Search Console ownership verification, sitemap submission, URL inspection and monitoring happen in the Google account, outside this repository. The sitemap URL is `https://betterbeds.pro/sitemap.xml`. A Merchant Center feed or direct ChatGPT merchant feed is a separate account integration, not something this website claims to have submitted. Structured data and crawl access support discovery; search engines control indexing and appearance.

The inventory accepts shared filter links such as `inventory.html?type=Tailgates&make=Ford&color=White`. These use the canonical inventory page; each actual product retains its own indexable URL. Bed measurements are searchable using feet/inches punctuation, spelled-out feet/inches, total inches, and familiar style names. These aliases help onsite search; exact measurements and style are also present in the visible product page, title and structured data.

Use an optional `itemLabel` for a specific singular part name, such as `taillight`, so product buttons and inquiries describe an individual light correctly. For separate driver/passenger listings, use distinct IDs, URLs and correctly matched photos; state the side, halogen/LED type, included sensor/module, and whether the price is for one light or a pair. Sensor presence does not claim operational testing.

When an inventory search includes a measurement, it compares the actual bed length numerically. For example, `8'` / `8 ft` / `96 inch` selects an eight-foot bed, while `6'9"` / `6.75 ft` / `81 inch` selects the short bed. Other search words and filters still apply.

Condition labels also control badges and offer markup. `Gently used` maps to `UsedCondition` and gets a gently-used badge. Product descriptions use the stated category/condition instead of assuming every item is new. Use damage and bedliner features to record confirmed details; storage orientation in photo captions describes the photo, not damage.
