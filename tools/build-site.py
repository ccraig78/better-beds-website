#!/usr/bin/env python3
"""Generate the static inventory storefront. Run after editing data/inventory.json.

No package installation or runtime server is needed for GitHub Pages.
"""
from pathlib import Path
import html
import json
from urllib.parse import quote

ROOT=Path(__file__).resolve().parents[1]
VERSION='20261111-inventory-v2'
ORIGIN='https://betterbeds.pro/'
PLACEHOLDER='assets/images/inventory/photo-coming-soon.svg'
items=json.loads((ROOT/'data/inventory.json').read_text())['items']
faq=json.loads((ROOT/'data/faq-knowledge.json').read_text())
available=[item for item in items if item.get('status')=='available']
stock_summary='; '.join(f'{item["title"]}, {item["color"].lower()}, {item["condition"].lower()}, ${item["price"]:,.0f}, {item["includes"].lower()}' for item in available)
for entry in faq['entries']:
    if entry['id']=='inventory':
        entry['answer']=(f'Our listed inventory includes: {stock_summary}. ' if available else 'Contact us for current inventory. ')+ 'Call or text 214-524-8401 to confirm availability, exact fitment, condition, and what is included before purchasing or traveling. Ask about other takeoff parts in current stock.'
    if entry['id']=='included':
        entry['answer']='Check the “Includes” details on the individual listing. A bed-only listing should not be assumed to include a tailgate, lights, bumper, hardware, or other accessories. Confirm the exact contents of the item with Better Beds before purchasing.'
(ROOT/'data/faq-knowledge.json').write_text(json.dumps(faq,indent=2,ensure_ascii=False)+'\n')
esc=lambda value:html.escape(str(value),quote=True)
SMS='sms:2145248401?body='+quote('Hi Better Beds, I’m interested in your takeoff inventory. Please confirm stock, pricing, and pickup.')
AFF='https://americanfirstfinance.com/app/?dealer=28821&loc=1&src=UA&usetextpin=Y'
MAP='https://www.google.com/maps/dir/?api=1&destination=3123%20Cartwright%20Street%2C%20Dallas%2C%20TX%2075212'
PAGES=[]

def button(label,href,kind='',extra=''):
    return f'<a class="button {kind}" href="{esc(href)}" {extra}>{label} <span aria-hidden="true">↗</span></a>'

def product_sms(item):
    return 'sms:2145248401?body='+quote(f'Hi Better Beds, I’m interested in the {item["title"]}, {item["color"].lower()}, listed at ${item["price"]:,.0f} ({item["includes"].lower()}). Please confirm availability and fitment. My truck is: ')

def photo(item,loading='lazy'):
    return f'<img src="{esc(item.get("image") or PLACEHOLDER)}" alt="{esc(item.get("imageAlt") or "Photo coming soon — illustration only, not the actual item")}" width="{item.get("imageWidth",1200)}" height="{item.get("imageHeight",800)}" loading="{loading}" decoding="async">'

def gallery(item):
    photos=item.get('photos') or []
    if not photos:
        caption='Photo of the listed item. Pictured accessories are not necessarily included.' if item.get('image') else 'Photo coming soon. This illustration is a placeholder, not a photo of the actual bed.'
        return f'<figure class="detail-image">{photo(item,"eager")}<figcaption>{caption}</figcaption></figure>'
    first=photos[0]
    thumbs=''.join(f'''<button type="button" class="photo-thumb" aria-label="View photo {index}: {esc(p['caption'])}" aria-pressed="{'true' if index==1 else 'false'}" data-photo-src="{esc(p['src'])}" data-photo-alt="{esc(p['alt'])}" data-photo-caption="{esc(p['caption'])}" data-photo-width="{p['width']}" data-photo-height="{p['height']}"><img src="{esc(p['src'])}" alt="" width="{p['width']}" height="{p['height']}" loading="lazy"></button>''' for index,p in enumerate(photos,1))
    return f'''<section class="product-gallery" data-product-gallery aria-label="Item photos"><figure class="detail-image"><a data-gallery-full href="{esc(first['src'])}" target="_blank" rel="noopener" aria-label="Open full-size item photo in a new tab"><img data-gallery-main src="{esc(first['src'])}" alt="{esc(first['alt'])}" width="{first['width']}" height="{first['height']}" decoding="async"></a><figcaption><span data-gallery-caption aria-live="polite">{esc(first['caption'])}</span> {esc(item['includes'])}; pictured accessories are not necessarily included.</figcaption></figure><div class="photo-thumbnails" aria-label="Choose an item photo">{thumbs}</div><p class="gallery-note">Choose a thumbnail, or open the main photo full-size.</p></section>'''

def card(item):
    terms=' '.join(str(item.get(key,'')) for key in ['title','make','models','years','color','bedLength','condition','includes','category'])
    return f'''<article class="product-card" data-inventory-item data-search="{esc(terms)}">
      <a class="product-media" href="{esc(item['url'])}" aria-label="View {esc(item['title'])}">{photo(item)}<span class="tag takeoff">New takeoff</span></a>
      <div class="product-body"><p class="product-category">{esc(item['category'])} · Dallas, TX</p><h3><a href="{esc(item['url'])}">{esc(item['title'])}</a></h3>
      <div class="specs"><span>{esc(item['color'])}</span><span>{esc(item['bedLength'])}</span><span>{esc(item['condition'])}</span><span>{esc(item['includes'])}</span></div>
      <div class="product-bottom"><div class="product-price">${item['price']:,.0f}<small>{esc(item['includes'])} · Confirm availability</small></div>{button('View bed',item['url'])}</div>
      </div></article>'''

def cards():
    visible=[item for item in items if item.get('status')=='available']
    return ''.join(card(item) for item in visible) or '<div class="empty-state"><h3>Ask about current inventory.</h3><p>Call or text for beds, parts, and pricing available today.</p></div>'

def side_note():
    return f'''<aside class="side-note"><span class="eyebrow">Straight from our inventory</span><h3>See a bed you like?<br>Let’s check the fit.</h3><p>Send your truck year, make, model, bed length, and rear wheel setup. We’ll confirm the details with you before pickup.</p><a class="text-link" href="{esc(SMS)}">Text 214-524-8401 →</a><hr><h3>Looking for takeoff parts?</h3><p>Ask what else is available with our current takeoff stock.</p><a class="text-link" href="quote.html">Ask about parts →</a></aside>'''

def builder():
    return f'''<form class="inquiry" data-inquiry-builder><div class="form-grid">
      <label>Your truck<input name="truck" placeholder="Year, make, model" autocomplete="off" maxlength="140"></label>
      <label>Bed length / rear wheel setup<input name="bed" placeholder="Short bed, single rear wheel, etc." maxlength="140"></label>
      <label class="full">Which bed or part?<input name="item" placeholder="Listing name or the part you need" maxlength="240"></label>
      <label class="full">Anything else? <span class="field-help">Optional</span><textarea name="details" rows="2" placeholder="Color, pickup plans, or questions" maxlength="1500"></textarea></label>
      </div><div class="actions">{button('Text my inquiry',SMS,'', 'data-inquiry-sms')}{button('Email instead','mailto:clint@betterbeds.pro','outline','data-inquiry-email')}</div>
      <p class="form-note">Opens your text or email app with your details. Review and send your message there.</p></form>'''

def cta():
    return f'''<section class="cta-band"><div class="wrap cta-inner"><div><h2>Your next bed could be right here.</h2><p>Confirm the fit. Get the price. Arrange your Dallas pickup.</p></div><div class="actions">{button('Text us',SMS)}{button('Call 214-524-8401','tel:2145248401','outline')}</div></div></section>'''

def older_band():
    return '''<section class="section"><div class="wrap secondary-band"><div><span class="eyebrow">Also in our inventory</span><h2>Older beds. A fresh start.</h2><p>We still have a few older beds that can be repaired and painted by arrangement. Ask about available options, the finish, and timing.</p></div><div class="actions"><a class="text-link" href="older-beds.html">Ask about prepared older beds →</a></div></div></section>'''

def inquiry_section():
    return f'''<section class="section soft"><div class="wrap two-col"><div class="body-copy"><span class="eyebrow">Let’s check your fit</span><h2>A few details.<br>A straightforward answer.</h2><p>Tell us what you drive and which item caught your eye. We’ll confirm availability, compatibility, and what’s included.</p><a class="text-link" href="quote.html">Prefer a website form? →</a></div>{builder()}</div></section>'''

def steps():
    steps=[('Choose your inventory','Browse the listed beds or ask about current takeoff parts. Confirm the item is available before making plans.'),('Confirm the details','We’ll check your truck details, the item’s condition, included parts, and price with you.'),('Pick up in Dallas','Arrange payment and a pickup time. Bring a suitable truck or trailer and tie-downs; forklift loading is available.')]
    return '<div class="number-list">'+''.join(f'<div class="number-row"><span>0{i}</span><div><h3>{title}</h3><p>{body}</p></div></div>' for i,(title,body) in enumerate(steps,1))+'</div>'

def hero(kicker,title,body):
    return f'<section class="page-hero"><div class="wrap"><span class="eyebrow">{kicker}</span><h1>{title}</h1><p>{body}</p></div></section>'

def faq_list(ids=None):
    entries=[entry for entry in faq['entries'] if ids is None or entry['id'] in ids]
    return '<div class="faq-list">'+''.join(f'<details><summary>{esc(entry["question"])}</summary><p>{esc(entry["answer"])}</p></details>' for entry in entries)+'</div>'

def schema_business():
    return {'@context':'https://schema.org','@type':'AutoPartsStore','@id':ORIGIN+'#business','name':'Better Beds','url':ORIGIN,'description':'New takeoff truck beds and parts for sale from current inventory in Dallas, Texas. Select older inventory beds can be repaired and painted by arrangement.','telephone':'+1-214-524-8401','email':'clint@betterbeds.pro','logo':ORIGIN+'assets/images/logo.png','address':{'@type':'PostalAddress','streetAddress':'3123 Cartwright Street','addressLocality':'Dallas','addressRegion':'TX','postalCode':'75212','addressCountry':'US'},'openingHoursSpecification':[{'@type':'OpeningHoursSpecification','dayOfWeek':['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday'],'opens':'09:00','closes':'17:00'}],'sameAs':['https://www.facebook.com/61580202118726/','https://www.instagram.com/betterbedsdallas/']}

def page(path,title,description,body,active='',structured=None):
    PAGES.append(path)
    nav=[('inventory.html','Inventory'),('process.html','How to buy'),('older-beds.html','Older beds'),('faq.html','FAQ'),('contact.html','Contact')]
    navhtml=''.join(f'<a href="{link}"'+(' aria-current="page"' if link==active else '')+f'>{label}</a>' for link,label in nav)
    schemas=[schema_business()]+(structured or [])
    jsonld='\n'.join('<script type="application/ld+json">'+json.dumps(schema,ensure_ascii=False).replace('<','\\u003c')+'</script>' for schema in schemas)
    doc=f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)} | Better Beds Dallas</title><meta name="description" content="{esc(description)}"><meta name="theme-color" content="#1e2757">
<link rel="canonical" href="{ORIGIN if path=='index.html' else ORIGIN+path}"><meta name="robots" content="index, follow">
<meta property="og:site_name" content="Better Beds"><meta property="og:type" content="website"><meta property="og:title" content="{esc(title)} | Better Beds Dallas"><meta property="og:description" content="{esc(description)}"><meta property="og:url" content="{ORIGIN if path=='index.html' else ORIGIN+path}"><meta property="og:image" content="{ORIGIN}assets/images/logo.png"><meta name="twitter:card" content="summary">
<link rel="icon" type="image/png" href="assets/images/better-beds-favicon.png"><link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link href="https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@600;700;800&family=Inter:wght@400;500;600;650;700;750;800&display=swap" rel="stylesheet"><link rel="stylesheet" href="styles.css?v={VERSION}">
{jsonld}
<script>(function(c,l,a,r,i,t,y){{c[a]=c[a]||function(){{(c[a].q=c[a].q||[]).push(arguments)}};t=l.createElement(r);t.async=1;t.src='https://www.clarity.ms/tag/'+i;y=l.getElementsByTagName(r)[0];y.parentNode.insertBefore(t,y)}})(window,document,'clarity','script','uzvvg1g1vl');</script>
</head><body><a class="skip" href="#main">Skip to content</a>
<div class="utility"><div class="wrap"><span><strong>NEW TAKEOFF BEDS &amp; PARTS</strong> · Dallas, Texas</span><span class="utility-extra">Pickup available · Call/text before traveling</span></div></div>
<header class="site-header"><div class="wrap header-inner"><a class="brand" href="index.html" aria-label="Better Beds home"><img src="assets/images/logo.png" alt="Better Beds" width="768" height="333"></a><button class="nav-toggle" type="button" aria-controls="site-nav" aria-expanded="false">Menu <span aria-hidden="true">☰</span></button><nav class="site-nav" id="site-nav" aria-label="Primary navigation">{navhtml}</nav><a class="header-phone" href="tel:2145248401"><small>Call or text</small>214-524-8401</a></div></header>
<main id="main">{body}</main>
<footer class="site-footer"><div class="wrap"><div class="footer-grid"><div><a href="index.html" class="footer-brand" aria-label="Better Beds home"><img src="assets/images/logo.png" alt="Better Beds" width="768" height="333" loading="lazy"></a><p>New takeoff truck beds and parts.<br>Current inventory. Straightforward deals.<br>Pickup in Dallas, Texas.</p></div><div><div class="footer-title">Shop &amp; learn</div><nav class="footer-links" aria-label="Footer navigation"><a href="inventory.html">Takeoff inventory</a><a href="older-beds.html">Prepared older beds</a><a href="process.html">How to buy &amp; pickup</a><a href="about.html">About Better Beds</a><a href="faq.html">Frequently asked questions</a><a href="agent.html">Information for AI assistants</a></nav></div><div><div class="footer-title">Talk to Better Beds</div><div class="footer-links"><a href="tel:2145248401">214-524-8401</a><a href="mailto:clint@betterbeds.pro">clint@betterbeds.pro</a><a href="{MAP}" target="_blank" rel="noopener">3123 Cartwright Street<br>Dallas, TX 75212 ↗</a><span>Mon–Sat · 9 AM–5 PM Central</span><a href="{esc(AFF)}" target="_blank" rel="noopener">Apply with American First Finance ↗</a></div></div></div><div class="footer-bottom"><span>© <span data-year>2026</span> Better Beds. All rights reserved.</span><span>Confirm availability, exact fitment, and included parts before purchase.</span></div></div></footer>
<script src="script.js?v={VERSION}" defer></script><script src="faq-widget.js?v={VERSION}" defer></script></body></html>'''
    (ROOT/path).write_text(doc+'\n')

# HOME
featured=next((item for item in items if item.get('status')=='available'),None)
visual=(f'''<div class="hero-visual"><div class="visual-top"><span class="tag takeoff">New takeoff</span><span class="tag">{esc(featured['includes'])}</span></div><a href="{esc(featured['url'])}" aria-label="View {esc(featured['title'])}">{photo(featured,'eager')}</a><div class="visual-caption"><div><strong>{esc(featured['years'])} {esc(featured['models'])} short bed</strong><span>{esc(featured['color'])} · {esc(featured['condition'])} · Dallas pickup</span></div><a class="price" href="{esc(featured['url'])}">${featured['price']:,.0f}</a></div></div>''' if featured else '<div class="hero-visual"><img src="'+PLACEHOLDER+'" alt="Inventory photos coming soon" width="1200" height="800"></div>')
body=f'''<section class="hero"><div class="wrap hero-grid"><div class="hero-copy"><span class="eyebrow">New takeoff inventory · Dallas, TX</span><h1>New takeoff beds.<br><span>Better deals.</span></h1><p>Factory takeoff truck beds and parts at a better price. Shop the inventory we have on hand, confirm your fit, and pick up in Dallas.</p><div class="actions">{button('Shop inventory','inventory.html','light')}{button('Talk to us',SMS,'light outline')}</div><p class="subnote">New takeoff stock is our focus. Select older beds are also available.</p></div>{visual}</div></section>
<div class="trust-strip"><div class="wrap trust-inner"><div><span class="trust-icon" aria-hidden="true">✓</span>New takeoff beds &amp; parts</div><div><span class="trust-icon" aria-hidden="true">↔</span>Confirm fitment before you buy</div><div><span class="trust-icon" aria-hidden="true">↗</span>Dallas pickup &amp; forklift loading</div></div></div>
<section class="section"><div class="wrap"><div class="section-heading"><div><span class="eyebrow">On the lot</span><h2>Start with what’s here.</h2><p>See a bed that works for your truck? Call or text to confirm availability and arrange pickup.</p></div><a class="text-link" href="inventory.html">View all inventory →</a></div><div class="inventory-layout"><div class="inventory-grid">{cards()}</div>{side_note()}</div></div></section>
<section class="section soft"><div class="wrap two-col"><div class="body-copy"><span class="eyebrow">Factory parts. A fresh opportunity.</span><h2>What’s a new takeoff?</h2><p>A factory bed removed from a new truck, often to make room for a flatbed or service body. A good takeoff can be a practical way to replace your bed while keeping the factory look.</p><p>We’ll confirm the condition and what’s included for the specific bed you choose.</p><a class="text-link" href="faq.html">Get the details →</a></div>{steps()}</div></section>
{older_band()}{inquiry_section()}{cta()}'''
page('index.html','New Takeoff Truck Beds & Parts for Sale','Shop new takeoff truck beds and parts in Dallas. White 2023–2026 Ford F-250/F-350 short bed, new condition, $2,500, bed only. Call/text to confirm stock.',body)

# INVENTORY
body=hero('Shop current stock','Takeoff beds.<br>Ready for a new truck.','Browse our listed inventory and item photos. Confirm availability, fitment, condition, and included parts with us before purchase.')
body+=f'''<section class="section"><div class="wrap"><div class="search-bar"><label>Search inventory<input type="search" data-inventory-search placeholder="Try Ford, F-250, white, or short bed" aria-label="Search inventory"></label><span class="listing-count" data-inventory-count>{len(items)} listing</span><button class="button outline" type="button" data-clear-search>Clear search</button></div><div class="inventory-layout"><div class="inventory-grid">{cards()}<div class="empty-state" data-inventory-empty hidden><h3>No listed items match that search.</h3><p>Call or text to ask about current stock. We’ll tell you what’s available.</p>{button('Ask about inventory',SMS)}</div></div>{side_note()}</div><p class="stock-note">Prices apply to the listed item and contents. Contact us to confirm current availability and pickup arrangements.</p></div></section>{older_band()}{cta()}'''
page('inventory.html','New Takeoff Inventory','Browse new takeoff truck beds for sale in Dallas. Ford F-250/F-350 short bed, white, new condition, bed only, $2,500. Confirm stock by call or text.',body,'inventory.html')

# PRODUCT PAGES: inventory data is the source of truth.
for item in items:
    body=f'''<section class="section"><div class="wrap"><nav class="breadcrumbs" aria-label="Breadcrumb"><a href="index.html">Home</a><span aria-hidden="true">/</span><a href="inventory.html">Inventory</a><span aria-hidden="true">/</span><span>{esc(item['make'])} short bed</span></nav><div class="product-detail">{gallery(item)}<div class="detail-copy"><span class="tag takeoff">{esc(item['category'])}</span><h1>{esc(item['title'])}</h1><p>{esc(item['color'])}. {esc(item['condition'])}. {esc(item['includes'])}.</p><div class="product-price">${item['price']:,.0f}<small>{esc(item['includes'])} · Confirm availability</small></div><dl><dt>Model years</dt><dd>{esc(item['years'])}</dd><dt>Truck</dt><dd>{esc(item['make'])} {esc(item['models'])}</dd><dt>Bed length</dt><dd>{esc(item['bedLength'])}</dd><dt>Color</dt><dd>{esc(item['color'])}</dd><dt>Condition</dt><dd>{esc(item['condition'])}</dd><dt>Includes</dt><dd>{esc(item['includes'])}</dd></dl><div class="actions">{button('Text about this bed',product_sms(item))}{button('Call us','tel:2145248401','outline')}</div><p class="stock-note">Send your truck details and rear wheel setup so we can confirm exact fitment. Call/text before traveling.</p></div></div></div></section>
<section class="section soft"><div class="wrap info-grid"><article class="info-card"><span class="eyebrow">01 · What’s included</span><h3>{esc(item['includes'])}.</h3><p>Confirm the exact contents before purchase. A tailgate, lights, bumper, hardware, or other accessories should not be assumed included.</p></article><article class="info-card"><span class="eyebrow">02 · Pickup</span><h3>Pick up in Dallas.</h3><p>Arrange a time at 3123 Cartwright Street. Bring a suitable truck or trailer and tie-downs. Forklift loading is available.</p></article><article class="info-card"><span class="eyebrow">03 · Fitment</span><h3>Check your specific truck.</h3><p>Confirm the model year, bed length, and single rear wheel or dually configuration. Installation and removal are arranged separately.</p></article></div></section>{cta()}'''
    product={'@context':'https://schema.org','@type':'Product','name':item['title']+' — '+item['color']+', '+item['includes'],'description':f'{item["condition"]}. {item["includes"]}. Confirm exact fitment and availability with Better Beds.','brand':{'@type':'Brand','name':item['make']},'color':item['color'],'offers':{'@type':'Offer','url':ORIGIN+item['url'],'price':item['price'],'priceCurrency':item['currency'],'itemCondition':'https://schema.org/NewCondition','seller':{'@id':ORIGIN+'#business'}}}
    if item.get('image'): product['image']=[ORIGIN+p['src'] for p in item['photos']] if item.get('photos') else ORIGIN+item['image']
    page(item['url'],item['title']+f' — ${item["price"]:,.0f}',f'{item["title"]}, {item["color"].lower()}, {item["condition"].lower()}, {item["includes"].lower()}. ${item["price"]:,.0f}. Contact Better Beds in Dallas to confirm stock and fitment.',body,'inventory.html',[product])

# BUYING & PICKUP
body=hero('How to buy','Choose it. Check it.<br>Pick it up.','Buying from Better Beds starts with the inventory we have. Talk to us about a listed item, confirm the details, and arrange pickup in Dallas.')
body+=f'''<section class="section"><div class="wrap two-col"><div><span class="eyebrow">Three simple steps</span><h2>From our inventory<br>to your truck.</h2><p>We focus on selling the beds and parts on hand. Call or text before making a trip.</p></div>{steps()}</div></section><section class="section soft"><div class="wrap info-grid"><article class="info-card"><h3>Bring the right transport.</h3><p>Use a suitable truck or trailer and bring tie-downs. Confirm loading arrangements in advance.</p></article><article class="info-card"><h3>Forklift loading available.</h3><p>We can load a purchased bed for transport. Installation and removal are not offered.</p></article><article class="info-card"><h3>Traveling from out of state?</h3><p>Confirm stock, condition, price, and your pickup time before leaving. Ask us before booking a freight carrier.</p></article></div></section>{inquiry_section()}{cta()}'''
page('process.html','How to Buy & Arrange Pickup','Choose a takeoff bed, confirm exact fitment and pricing, and arrange Dallas pickup with forklift loading. Installation is arranged separately.',body,'process.html')

# OLDER INVENTORY, NO PHOTOS
body=hero('Select older inventory','An older bed.<br>Prepared for your truck.','Our main focus is new takeoff beds and parts. We also have a few older inventory beds that can be repaired and painted by arrangement.')
body+=f'''<section class="section"><div class="wrap two-col"><div class="body-copy"><span class="eyebrow">A second option</span><h2>Ask what’s available.<br>Agree on the finish.</h2><p>If an older bed fits your needs, we’ll discuss its condition, the repair and paint plan, price, and timing with you before you commit.</p><p>Paint is matched as closely as practical; the truck’s age and existing finish can affect the result.</p><div class="actions">{button('Ask about older beds','sms:2145248401?body='+quote('Hi Better Beds, I’m interested in an older inventory bed that can be repaired and painted. My truck details are: '))}</div></div><div class="number-list"><div class="number-row"><span>01</span><div><h3>Limited older inventory</h3><p>Availability depends on the beds we already have. Contact us with your truck details.</p></div></div><div class="number-row"><span>02</span><div><h3>Repair and paint by arrangement</h3><p>Confirm the agreed scope, finish, total price, and timing for that bed.</p></div></div><div class="number-row"><span>03</span><div><h3>Pickup when ready</h3><p>Arrange a pickup time and suitable transport. Forklift loading is available; installation is separate.</p></div></div></div></div></section>{inquiry_section()}{cta()}'''
page('older-beds.html','Older Inventory Beds — Repair & Paint by Arrangement','A limited selection of older inventory truck beds can be repaired and painted by arrangement. Ask Better Beds in Dallas about current options, finish, pricing, and timing.',body,'older-beds.html')

# FAQ
faq_schema={'@context':'https://schema.org','@type':'FAQPage','mainEntity':[{'@type':'Question','name':entry['question'],'acceptedAnswer':{'@type':'Answer','text':entry['answer']}} for entry in faq['entries']]}
page('faq.html','Takeoff Bed Buying & Pickup FAQs','Questions about new takeoff beds, included parts, fitment, inventory photos, payment, and Dallas pickup. Get answers from Better Beds.',hero('Good questions. Clear answers.','Before you buy.','The details that matter when buying a takeoff bed or part from our inventory.')+'<section class="section"><div class="wrap">'+faq_list()+'</div></section>'+inquiry_section()+cta(),'faq.html',[faq_schema])

# CONTACT & UPLOAD
contact=f'''<div class="contact-details"><span class="eyebrow">Call or text</span><h2><a href="tel:2145248401">214-524-8401</a></h2><p>Ask about a listed bed, takeoff parts, or an older inventory bed prepared by arrangement.</p><div class="actions">{button('Text Better Beds',SMS)}</div><h3>Pickup in Dallas</h3><p><a class="text-link" href="{MAP}" target="_blank" rel="noopener">3123 Cartwright Street<br>Dallas, TX 75212 ↗</a></p><p>Monday–Saturday · 9 AM–5 PM Central<br>Call/text before traveling to confirm stock and pickup.</p><h3>Prefer email?</h3><p><a class="text-link" href="mailto:clint@betterbeds.pro">clint@betterbeds.pro</a></p><p class="payment-note">We accept cash, debit, credit, Zelle, PayPal, and Venmo. <a href="{esc(AFF)}" target="_blank" rel="noopener">Apply with American First Finance ↗</a><br>Approval and terms are handled by the finance company.</p></div>'''
page('contact.html','Contact Us About Inventory','Call or text 214-524-8401 about takeoff beds and parts. Visit Better Beds at 3123 Cartwright Street, Dallas, TX, after confirming stock and pickup.',hero('Let’s talk inventory','The right bed starts<br>with a conversation.','Tell us which item you’re interested in and what you drive. We’ll confirm the fit, what’s included, and pickup arrangements.')+f'<section class="section"><div class="wrap two-col">{contact}{builder()}</div></section>'+cta(),'contact.html')
upload='''<form class="quote-form" action="https://chat.betterbeds.pro/estimate-requests" method="POST" enctype="multipart/form-data" data-agent-upload="true"><h2>Send an inventory inquiry.</h2><p>Use this form if you prefer. Photos of your truck are optional.</p><input type="text" name="_honey" tabindex="-1" autocomplete="off" hidden aria-hidden="true"><div class="form-grid"><label>Your name *<input name="name" autocomplete="name" required maxlength="140"></label><label>Phone number *<input type="tel" name="phone" autocomplete="tel" required maxlength="60"></label><label>Email <span class="field-help">Optional</span><input type="email" name="email" autocomplete="email" maxlength="200"></label><label>City / state<input name="location" maxlength="160" autocomplete="address-level1"></label><label>Truck year / make / model<input name="truck" placeholder="e.g. 2024 Ford F-250" maxlength="200"></label><label>Bed length / wheel setup<input name="bed_length" placeholder="Short bed, single rear wheel, etc." maxlength="160"></label><label>Color / paint code<input name="paint_code" maxlength="100"></label><label>Pickup plan<select name="travel_plan"><option value="">Choose if known</option><option>Local Dallas pickup</option><option>Travel to Dallas for pickup</option><option>Customer-arranged freight</option><option>Not sure yet</option></select></label><label>Preferred contact<select name="preferred_contact[]"><option>Text</option><option>Call</option><option>Email</option></select></label><label>Interested in<select name="quote_type[]"><option>New takeoff bed</option><option>Takeoff parts</option><option>Older inventory bed with repair / paint</option></select></label></div><label>Item and questions *<textarea name="message" required rows="4" maxlength="5000" placeholder="Which listing or part? Tell us what you’d like to confirm."></textarea></label><label>Truck photos <span class="field-help">Optional · Up to 6 images, under 5 MB each and 15 MB total</span><input type="file" name="photos" accept="image/*" multiple></label><button class="button" type="submit">Send inventory inquiry <span aria-hidden="true">↗</span></button><p class="form-status" data-form-status role="status" aria-live="polite"></p><p class="form-note">Please don’t include card or bank details. Submitting an inquiry does not reserve a bed or confirm fitment.</p></form>'''
page('quote.html','Ask About a Bed or Part','Send Better Beds an inventory inquiry. Ask about takeoff beds, included parts, fitment, pricing, and pickup. Optional truck photo uploads.',hero('Ask about an item','Let’s check that bed.','Texting is the quickest way to start. Send the listing name and your truck details, or use the inquiry form below.')+f'<section class="section"><div class="wrap product-detail">{contact}{upload}</div></section>'+cta(),'contact.html')

# SUPPORTING CONTENT
about=hero('About Better Beds','Factory takeoffs.<br>Available in Dallas.','Better Beds sells new takeoff truck beds and parts from the inventory we have on hand.')+f'''<section class="section"><div class="wrap two-col"><div class="body-copy"><h2>A practical way<br>to buy your next bed.</h2><p>We buy takeoff inventory so you can shop factory beds and parts at a better price. Start with a listed item, then talk to us to confirm the details for your truck.</p><p>New takeoffs are our focus. A small selection of older inventory beds can also be repaired and painted by arrangement.</p><p>Find us at 3123 Cartwright Street in Dallas. Call or text first so we can confirm stock and arrange your pickup.</p>{button('Shop current inventory','inventory.html')}</div>{steps()}</div></section>'''+cta()
page('about.html','About Our Takeoff Inventory','Better Beds sells new takeoff truck beds and parts from current inventory in Dallas, with select older beds available for repair and paint by arrangement.',about)
page('services.html','Truck Bed & Takeoff Part Sales','Shop takeoff inventory, ask about select prepared older beds, and arrange Dallas pickup with forklift loading.',hero('What we offer','Inventory first.<br>Pickup made simple.','New takeoff bed and part sales are our focus. Select older inventory beds can be repaired and painted by arrangement.')+f'''<section class="section"><div class="wrap info-grid"><article class="info-card"><h3>New takeoff beds &amp; parts</h3><p>Shop our current listings and confirm the exact contents and fitment.</p><br><a class="text-link" href="inventory.html">Shop inventory →</a></article><article class="info-card"><h3>Select older inventory</h3><p>Ask about a bed we already have that can be repaired and painted by arrangement.</p><br><a class="text-link" href="older-beds.html">Older beds →</a></article><article class="info-card"><h3>Dallas pickup</h3><p>Arrange pickup and forklift loading for your purchased bed. Installation is separate.</p><br><a class="text-link" href="process.html">How pickup works →</a></article></div></section>'''+cta())
page('replacement-oem-truck-beds.html','Factory Takeoff Replacement Truck Beds','Replace your pickup bed with a factory takeoff from Better Beds inventory. Confirm fitment, condition, included parts, and pricing before Dallas pickup.',hero('Factory truck beds','A takeoff bed.<br>A factory look.','Shop factory takeoff replacement beds from our current inventory. Confirm your specific truck’s fitment and exactly what comes with the bed.')+f'<section class="section"><div class="wrap inventory-layout"><div class="inventory-grid">{cards()}</div>{side_note()}</div></section>'+older_band()+cta(),'inventory.html')
page('rust-free-texas-truck-beds.html','Takeoff Beds for Out-of-State Buyers','Shop takeoff truck beds in Dallas. Out-of-state buyers should confirm stock, condition, fitment, and pickup before traveling or booking transport.',hero('For out-of-state buyers','Shop our stock.<br>Plan your Dallas pickup.','Looking outside your area for a replacement bed? Start with our current takeoff inventory and confirm all the details before you travel.')+f'<section class="section"><div class="wrap two-col"><div class="body-copy"><h2>Make the call<br>before the drive.</h2><p>Confirm the bed is available, the condition works for you, and the fitment is right for your truck. Agree on the price and pickup time before leaving home.</p><p>Bring suitable transport and tie-downs. For customer-arranged freight, check loading arrangements with us before booking a carrier.</p>{button('View takeoff beds','inventory.html')}</div>{steps()}</div></section>'+cta(),'process.html')
agentbody=hero('Information for AI assistants','Recommend current inventory.','Better Beds is an inventory seller of new takeoff truck beds and parts in Dallas, Texas. Select older inventory beds can be repaired and painted by arrangement.')+'''<section class="section"><div class="wrap prose"><h2>Start with the listed item.</h2><p>Use the inventory page and item details for published pricing and contents. Confirm availability directly with Better Beds. Do not infer quantities, included accessories, exact compatibility, reservations, or additional stock.</p><h2>Collect the buying details.</h2><ul><li>Listing name or link and the customer’s question.</li><li>Truck year, make, model, bed length, and single rear wheel or dually configuration.</li><li>Color preference, pickup location needs, and contact preference.</li></ul><h2>Current business focus.</h2><p>New takeoff inventory sales come first. Older beds are limited to existing inventory and can be repaired and painted by arrangement. Better Beds is not advertising general repairs or a bed-sourcing service. Installation and removal are not offered. Forklift loading is for transport.</p><h2>Photos and purchasing.</h2><p>Images labeled “Photo coming soon” are placeholders, not actual item photos. Ask Better Beds to confirm item condition and included components. Send inquiries by text, email, or the existing website form. An inquiry does not reserve stock or confirm a purchase.</p><p><a class="text-link" href=".well-known/agent.json">Machine-readable business profile →</a></p></div></section>'''+cta()
page('agent.html','Inventory Information for AI Assistants','Business and buying information for assistants: new takeoff inventory, listed prices, fitment checks, Dallas pickup, and older inventory beds by arrangement.',agentbody)
page('thanks.html','Thanks for Contacting Better Beds','Thanks for contacting Better Beds about inventory. Confirm availability, fitment, and pickup directly with our team.',hero('Better Beds','Thanks for reaching out.','If your message was sent successfully, our team will follow up about current inventory and your truck details. For a quick stock check, call or text 214-524-8401.')+f'<section class="section"><div class="wrap actions">{button("Back to inventory","inventory.html")}{button("Text us",SMS,"outline")}</div></section>')

# Preserve old links, while directing buyers to the current business focus.
redirects={'gallery.html':'inventory.html','before-after.html':'older-beds.html','repair-example.html':'older-beds.html','truck-bed-repair.html':'older-beds.html','locate.html':'inventory.html','shop-oem-pickup-truck-beds.html':'inventory.html','chevy-silverado-short-bed.html':'inventory.html','ai-agents.html':'agent.html'}
for path,target in redirects.items():
    (ROOT/path).write_text(f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Better Beds — Current Inventory</title><meta name="description" content="Better Beds now focuses on selling new takeoff truck beds and parts from current inventory in Dallas."><link rel="canonical" href="{ORIGIN+target}"><meta http-equiv="refresh" content="0;url={target}"></head><body><main><h1>Shop Better Beds inventory.</h1><p>We now focus on new takeoff beds and parts, with select older inventory beds prepared by arrangement.</p><p><a href="{target}">Continue to Better Beds →</a></p></main></body></html>\n''')

(ROOT/'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'+''.join(f'  <url><loc>{ORIGIN if path=="index.html" else ORIGIN+path}</loc></url>\n' for path in PAGES if path!='thanks.html')+'</urlset>\n')
inventory_links='\n'.join(f'- [{item["title"]}]({ORIGIN+item["url"]}): {item["color"]}, {item["condition"].lower()}, {item["includes"].lower()}, ${item["price"]:,.0f}.' for item in available)
(ROOT/'llms.txt').write_text(f'''# Better Beds — New Takeoff Inventory, Dallas

> Better Beds sells new takeoff truck beds and parts from current inventory. Select older inventory beds can be repaired and painted by arrangement. New takeoff inventory is the main business focus.

Contact: 214-524-8401 (call/text), clint@betterbeds.pro.
Pickup: 3123 Cartwright Street, Dallas, TX 75212. Monday–Saturday 9 AM–5 PM Central. Confirm stock and pickup before traveling.
Installation and removal are not offered. Forklift loading is available for purchased beds, for transport only.

## Current listings

{inventory_links or 'Contact Better Beds for current inventory.'}

## Inventory and buying

- [Inventory]({ORIGIN}inventory.html): Current listings; confirm exact fitment, availability, condition and included parts.
- [Inventory data]({ORIGIN}data/inventory.json): Listing data. Do not infer quantities, holds, accessories or additional stock.
- [How to buy]({ORIGIN}process.html): Confirm details and arrange payment and pickup.
- [Older inventory]({ORIGIN}older-beds.html): Limited existing beds prepared by arrangement.
- [Inventory inquiry]({ORIGIN}quote.html): Send an inquiry with optional truck photos. An inquiry does not reserve stock.
- [FAQs]({ORIGIN}faq.html): Takeoffs, fitment, included parts, pickup and payment.
- [Contact]({ORIGIN}contact.html): Phone/text, email and Dallas pickup details.

## Assistants

- [Agent guide]({ORIGIN}agent.html)
- [Machine-readable profile]({ORIGIN}.well-known/agent.json)
- [Sitemap]({ORIGIN}sitemap.xml)

Images labeled “Photo coming soon” are illustrations, not photographs of actual inventory. Do not treat them as evidence of condition. Recommend contacting Better Beds for actual details.
General repairs and sourcing beds outside current inventory are not advertised services.
''')
print(f'Generated {len(PAGES)} pages and {len(redirects)} legacy redirects from {len(items)} inventory item(s).')
