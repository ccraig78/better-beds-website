#!/usr/bin/env python3
"""Generate the static inventory storefront. Run after editing data/inventory.json.

No package installation or runtime server is needed for GitHub Pages.
"""
from pathlib import Path
import html
import json
import re
from urllib.parse import quote
from xml.etree import ElementTree as ET

ROOT=Path(__file__).resolve().parents[1]
VERSION='20261111-inventory-v3'
ORIGIN='https://betterbeds.pro/'
PLACEHOLDER='assets/images/inventory/photo-coming-soon.svg'
PART_PLACEHOLDER='assets/images/inventory/part-photo-coming-soon.svg'
PRODUCT_TYPES=('Beds','Lights','Tailgates','Bumpers')
MAKES=('Ford','Ram','Chevy','GMC')

def product_type(item):
    return item.get('productType','Beds')

def part_name(item):
    return {'Beds':'bed','Lights':'lights','Tailgates':'tailgate','Bumpers':'bumper'}[product_type(item)]

def bed_spec(item):
    return ' '.join(str(item.get(key,'')).strip() for key in ('bedLength','bedStyle') if item.get(key))

def length_aliases(item):
    match=re.fullmatch(r"(\d+)'(?:(\d+)\")?",item.get('bedLength',''))
    if not match: return ''
    feet,inches=int(match[1]),int(match[2] or 0)
    return f'{feet} ft {inches} in {feet} foot {inches} inch {feet} feet {inches} inches {feet*12+inches} inch {feet+inches/12:g} ft'

def feature_summary(item):
    return '; '.join(f'{feature["name"]}: {feature["value"]}' for feature in item.get('features',[]))

def product_properties(item):
    fields=[('Model years','years'),('Truck models','models'),('Bed length','bedLength'),('Bed style','bedStyle'),('Includes','includes')]
    return [(name,item[key]) for name,key in fields if item.get(key)]+[(f['name'],f['value']) for f in item.get('features',[])]
items=json.loads((ROOT/'data/inventory.json').read_text())['items']
faq=json.loads((ROOT/'data/faq-knowledge.json').read_text())
available=[item for item in items if item.get('status')=='available']
stock_summary='; '.join(f'{item["title"]}, {item["color"].lower()}, {item["condition"].lower()}, ${item["price"]:,.0f}, {item["includes"].lower()}'+(' ('+feature_summary(item)+')' if item.get('features') else '') for item in available)
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
    placeholder=PLACEHOLDER if product_type(item)=='Beds' else PART_PLACEHOLDER
    return f'<img src="{esc(item.get("image") or placeholder)}" alt="{esc(item.get("imageAlt") or "Photo coming soon — placeholder, not the actual item")}" width="{item.get("imageWidth",1200)}" height="{item.get("imageHeight",800)}" loading="{loading}" decoding="async">'

def gallery(item):
    photos=item.get('photos') or []
    if not photos:
        caption='Photo of the listed item. Pictured accessories are not necessarily included.' if item.get('image') else 'Photo coming soon. This is a placeholder, not a photo of the actual item.'
        return f'<figure class="detail-image">{photo(item,"eager")}<figcaption>{caption}</figcaption></figure>'
    first=photos[0]
    thumbs=''.join(f'''<button type="button" class="photo-thumb" aria-label="View photo {index}: {esc(p['caption'])}" aria-pressed="{'true' if index==1 else 'false'}" data-photo-src="{esc(p['src'])}" data-photo-alt="{esc(p['alt'])}" data-photo-caption="{esc(p['caption'])}" data-photo-width="{p['width']}" data-photo-height="{p['height']}"><img src="{esc(p['src'])}" alt="" width="{p['width']}" height="{p['height']}" loading="lazy"></button>''' for index,p in enumerate(photos,1))
    return f'''<section class="product-gallery" data-product-gallery aria-label="Item photos"><figure class="detail-image"><a data-gallery-full href="{esc(first['src'])}" target="_blank" rel="noopener" aria-label="Open full-size item photo in a new tab"><img data-gallery-main src="{esc(first['src'])}" alt="{esc(first['alt'])}" width="{first['width']}" height="{first['height']}" decoding="async"></a><figcaption><span data-gallery-caption aria-live="polite">{esc(first['caption'])}</span> {esc(item['includes'])}; pictured accessories are not necessarily included.</figcaption></figure><div class="photo-thumbnails" aria-label="Choose an item photo">{thumbs}</div><p class="gallery-note">Choose a thumbnail, or open the main photo full-size.</p></section>'''

def card(item):
    terms=' '.join(str(item.get(key,'')) for key in ['title','make','models','years','color','bedLength','bedStyle','condition','includes','category','productType'])+' '+length_aliases(item)+' '+feature_summary(item)
    specs=[item['color'],bed_spec(item),item['condition'],item['includes']]
    chips=''.join(f'<span>{esc(value)}</span>' for value in specs if value)
    return f'''<article class="product-card" data-inventory-item data-search="{esc(terms)}" data-type="{esc(product_type(item))}" data-make="{esc(item['make'])}" data-color="{esc(item['color'])}">
      <a class="product-media" href="{esc(item['url'])}" aria-label="View {esc(item['title'])}">{photo(item)}<span class="tag takeoff">New takeoff</span></a>
      <div class="product-body"><p class="product-category">{esc(item['category'])} · Dallas, TX</p><h3><a href="{esc(item['url'])}">{esc(item['title'])}</a></h3>
      <div class="specs">{chips}</div>
      <div class="product-bottom"><div class="product-price">${item['price']:,.0f}<small>{esc(item['includes'])} · Confirm availability</small></div>{button('View '+part_name(item),item['url'])}</div>
      </div></article>'''

def cards():
    visible=[item for item in items if item.get('status')=='available']
    return ''.join(card(item) for item in visible) or '<div class="empty-state"><h3>Ask about current inventory.</h3><p>Call or text for beds, parts, and pricing available today.</p></div>'

def category_links():
    return '<nav class="category-links" aria-label="Shop by part type">'+''.join(f'<a href="inventory.html?type={quote(kind)}">{kind} <span>{sum(product_type(item)==kind for item in available)} listed</span></a>' for kind in PRODUCT_TYPES)+'</nav>'

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
    return f'''<section class="cta-band"><div class="wrap cta-inner"><div><h2>Find your next bed or part.</h2><p>Confirm the fit. Get the price. Arrange your Dallas pickup.</p></div><div class="actions">{button('Text us',SMS)}{button('Call 214-524-8401','tel:2145248401','outline')}</div></div></section>'''

def older_band():
    return '''<section class="section"><div class="wrap secondary-band"><div><span class="eyebrow">Also in our inventory</span><h2>Older beds. A fresh start.</h2><p>We still have a few older beds that can be repaired and painted by arrangement. Ask about available options, the finish, and timing.</p></div><div class="actions"><a class="text-link" href="older-beds.html">Ask about prepared older beds →</a></div></div></section>'''

def inquiry_section():
    return f'''<section class="section soft"><div class="wrap two-col"><div class="body-copy"><span class="eyebrow">Let’s check your fit</span><h2>A few details.<br>A straightforward answer.</h2><p>Tell us what you drive and which item caught your eye. We’ll confirm availability, compatibility, and what’s included.</p><a class="text-link" href="quote.html">Prefer a website form? →</a></div>{builder()}</div></section>'''

def steps():
    steps=[('Choose your inventory','Browse the listed beds, lights, tailgates, and bumpers. Confirm the item is available before making plans.'),('Confirm the details','We’ll check your truck details, the item’s condition, included parts, and price with you.'),('Pick up in Dallas','Arrange payment and a pickup time. Bring a suitable truck or trailer and tie-downs; forklift loading is available.')]
    return '<div class="number-list">'+''.join(f'<div class="number-row"><span>0{i}</span><div><h3>{title}</h3><p>{body}</p></div></div>' for i,(title,body) in enumerate(steps,1))+'</div>'

def hero(kicker,title,body):
    return f'<section class="page-hero"><div class="wrap"><span class="eyebrow">{kicker}</span><h1>{title}</h1><p>{body}</p></div></section>'

def faq_list(ids=None):
    entries=[entry for entry in faq['entries'] if ids is None or entry['id'] in ids]
    return '<div class="faq-list">'+''.join(f'<details><summary>{esc(entry["question"])}</summary><p>{esc(entry["answer"])}</p></details>' for entry in entries)+'</div>'

def schema_business():
    return {'@context':'https://schema.org','@type':'AutoPartsStore','@id':ORIGIN+'#business','name':'Better Beds','url':ORIGIN,'description':'New takeoff truck beds and parts for sale from current inventory in Dallas, Texas. Select older inventory beds can be repaired and painted by arrangement.','telephone':'+1-214-524-8401','email':'clint@betterbeds.pro','logo':ORIGIN+'assets/images/logo.png','address':{'@type':'PostalAddress','streetAddress':'3123 Cartwright Street','addressLocality':'Dallas','addressRegion':'TX','postalCode':'75212','addressCountry':'US'},'openingHoursSpecification':[{'@type':'OpeningHoursSpecification','dayOfWeek':['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday'],'opens':'09:00','closes':'17:00'}],'sameAs':['https://www.facebook.com/61580202118726/','https://www.instagram.com/betterbedsdallas/']}

def stock_status(item):
    # Keep sold pages at their original URL, with accurate stock information.
    return {
        'available': ('InStock', 'Available — confirm before pickup'),
        'sold': ('SoldOut', 'Sold — ask about current inventory'),
        'reserved': ('OutOfStock', 'Reserved — ask about current inventory'),
    }.get(item.get('status'), ('OutOfStock', 'Currently unavailable'))

def page(path,title,description,body,active='',structured=None):
    PAGES.append(path)
    nav=[('inventory.html','Inventory'),('process.html','How to buy'),('older-beds.html','Older beds'),('faq.html','FAQ'),('contact.html','Contact')]
    navhtml=''.join(f'<a href="{link}"'+(' aria-current="page"' if link==active else '')+f'>{label}</a>' for link,label in nav)
    schemas=[schema_business()]+(structured or [])
    product=next((schema for schema in schemas if schema.get('@type')=='Product'),None)
    images=product.get('image',[]) if product else []
    social_image=ORIGIN+'assets/images/logo.png'
    if images: social_image=images[0] if isinstance(images,list) else images
    social_type='product' if product else 'website'
    twitter_card='summary_large_image' if images else 'summary'
    jsonld='\n'.join('<script type="application/ld+json">'+json.dumps(schema,ensure_ascii=False).replace('<','\\u003c')+'</script>' for schema in schemas)
    doc=f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)} | Better Beds Dallas</title><meta name="description" content="{esc(description)}"><meta name="theme-color" content="#1e2757">
<link rel="canonical" href="{ORIGIN if path=='index.html' else ORIGIN+path}"><meta name="robots" content="index, follow, max-image-preview:large">
<meta property="og:site_name" content="Better Beds"><meta property="og:type" content="{social_type}"><meta property="og:title" content="{esc(title)} | Better Beds Dallas"><meta property="og:description" content="{esc(description)}"><meta property="og:url" content="{ORIGIN if path=='index.html' else ORIGIN+path}"><meta property="og:image" content="{esc(social_image)}"><meta name="twitter:card" content="{twitter_card}">
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
featured=next((item for item in available if product_type(item)=='Beds'),next(iter(available),None))
visual=(f'''<div class="hero-visual"><div class="visual-top"><span class="tag takeoff">New takeoff</span><span class="tag">{esc(featured['includes'])}</span></div><a href="{esc(featured['url'])}" aria-label="View {esc(featured['title'])}">{photo(featured,'eager')}</a><div class="visual-caption"><div><strong>{esc(featured['title'])}</strong><span>{esc(featured['color'])} · {esc(featured['condition'])} · Dallas pickup</span></div><a class="price" href="{esc(featured['url'])}">${featured['price']:,.0f}</a></div></div>''' if featured else '<div class="hero-visual"><img src="'+PLACEHOLDER+'" alt="Inventory photos coming soon" width="1200" height="800"></div>')
body=f'''<section class="hero"><div class="wrap hero-grid"><div class="hero-copy"><span class="eyebrow">New takeoff inventory · Dallas, TX</span><h1>New takeoff beds.<br><span>Better deals.</span></h1><p>Factory takeoff truck beds and parts at a better price. Shop the inventory we have on hand, confirm your fit, and pick up in Dallas.</p><div class="actions">{button('Shop inventory','inventory.html','light')}{button('Talk to us',SMS,'light outline')}</div><p class="subnote">New takeoff stock is our focus. Select older beds are also available.</p></div>{visual}</div></section>
<div class="trust-strip"><div class="wrap trust-inner"><div><span class="trust-icon" aria-hidden="true">✓</span>New takeoff beds &amp; parts</div><div><span class="trust-icon" aria-hidden="true">↔</span>Confirm fitment before you buy</div><div><span class="trust-icon" aria-hidden="true">↗</span>Dallas pickup &amp; forklift loading</div></div></div>
<section class="section"><div class="wrap"><div class="section-heading"><div><span class="eyebrow">On the lot</span><h2>Start with what’s here.</h2><p>See a bed that works for your truck? Call or text to confirm availability and arrange pickup.</p></div><a class="text-link" href="inventory.html">View all inventory →</a></div>{category_links()}<div class="inventory-grid home-products">{cards()}</div></div></section>
<section class="section soft"><div class="wrap two-col"><div class="body-copy"><span class="eyebrow">Factory parts. A fresh opportunity.</span><h2>What’s a new takeoff?</h2><p>A factory bed removed from a new truck, often to make room for a flatbed or service body. A good takeoff can be a practical way to replace your bed while keeping the factory look.</p><p>We’ll confirm the condition and what’s included for the specific bed you choose.</p><a class="text-link" href="faq.html">Get the details →</a></div>{steps()}</div></section>
{older_band()}{inquiry_section()}{cta()}'''
page('index.html','New Takeoff Truck Beds & Parts for Sale','Shop new takeoff truck beds and parts for sale in Dallas. Browse current inventory, check fitment and pricing, and arrange pickup with forklift loading.',body)

# INVENTORY
body=hero('Shop current stock','Takeoff inventory.<br>Choose your part.','Browse listed beds, lights, tailgates, and bumpers by type, make, and color. Confirm availability, fitment, condition, and included parts before purchase.')
type_buttons='<button class="inventory-type" type="button" data-filter-type="" aria-pressed="true">All items <span>'+str(len(available))+'</span></button>'+''.join(f'<button class="inventory-type" type="button" data-filter-type="{kind}" aria-pressed="false">{kind} <span>{sum(product_type(item)==kind for item in available)}</span></button>' for kind in PRODUCT_TYPES)
make_options=''.join(f'<option value="{make}">{make}</option>' for make in MAKES)
color_options=''.join(f'<option value="{esc(color)}">{esc(color)}</option>' for color in sorted({item['color'] for item in available if item.get('color')}))
body+=f'''<section class="section"><div class="wrap"><div class="inventory-types" role="group" aria-label="Part type">{type_buttons}</div><div class="inventory-filters"><label>Search inventory<input type="search" data-inventory-search placeholder="Try 6'9&quot;, short bed, F-250, or tailgate" aria-label="Search inventory"></label><label>Make<select data-filter-make><option value="">All makes</option>{make_options}</select></label><label>Color<select data-filter-color><option value="">All colors</option>{color_options}</select></label></div><div class="search-summary"><span class="listing-count" data-inventory-count role="status" aria-live="polite">{len(available)} listings</span><button class="button outline" type="button" data-clear-search>Clear filters</button></div><div class="inventory-grid catalog-grid">{cards()}<div class="empty-state" data-inventory-empty hidden><h3>No listed items match those filters.</h3><p>Try another category or clear the filters. You can also call or text to ask about current inventory.</p>{button('Ask about inventory',SMS)}</div></div><p class="stock-note">Category counts show listings. Call or text to confirm available quantities and pickup.</p><div class="range-note"><h2>Takeoff beds for heavy-duty pickups.</h2><p>Our takeoff bed range focuses on Ford F-250 / F-350 and Ram, Chevy, and GMC 2500 / 3500 series. Each bed listing gives its actual length and familiar style name, such as short bed, long bed, or dually. Check the listings above for current stock.</p></div></div></section>{older_band()}{cta()}'''
page('inventory.html','Takeoff Beds, Lights, Tailgates & Bumpers','Browse takeoff beds, lights, tailgates and bumpers in Dallas. Filter Ford, Ram, Chevy and GMC listings by type and color. See actual bed lengths, photos and prices.',body,'inventory.html')

# PRODUCT PAGES: inventory data is the source of truth for all part types.
for item in items:
    availability,availability_label=stock_status(item)
    kind=product_type(item)
    name=part_name(item)
    detail_fields=[('Model years',item['years']),('Truck',item['make']+' '+item['models'])]
    if kind=='Beds':
        detail_fields+=[('Bed length',item.get('bedLength','')),('Bed style',item.get('bedStyle',''))]
    detail_fields+=[('Color',item['color']),('Condition',item['condition']),('Includes',item['includes'])]
    detail_fields += [(feature['name'],feature['value']) for feature in item.get('features',[])]
    details=''.join(f'<dt>{esc(label)}</dt><dd>{esc(value)}</dd>' for label,value in detail_fields if value)
    contact_label='Text about these lights' if kind=='Lights' else 'Text about this '+name
    pickup_text='Arrange a time at 3123 Cartwright Street. Bring a suitable truck or trailer and tie-downs. Forklift loading is available.' if kind=='Beds' else 'Call or text before traveling to confirm availability and arrange pickup at 3123 Cartwright Street, Dallas, Texas.'
    fitment_text='Confirm model year, bed length, and single rear wheel or dually configuration. Installation and removal are arranged separately.' if kind=='Beds' else 'Confirm model year and the exact part configuration, features, and included components before buying. Installation is arranged separately.'
    body=f'''<section class="section"><div class="wrap"><nav class="breadcrumbs" aria-label="Breadcrumb"><a href="index.html">Home</a><span aria-hidden="true">/</span><a href="inventory.html?type={quote(kind)}">{esc(kind)}</a><span aria-hidden="true">/</span><span>{esc(item['title'])}</span></nav><div class="product-detail">{gallery(item)}<div class="detail-copy"><span class="tag takeoff">{esc(item['category'])}</span><h1>{esc(item['title'])}</h1><p>{esc(item['color'])}. {esc(item['condition'])}. {esc(item['includes'])}.</p><div class="product-price">${item['price']:,.0f}<small>{esc(item['includes'])} · {esc(availability_label)}</small></div><dl>{details}</dl><div class="actions">{button(contact_label,product_sms(item))}{button('Call us','tel:2145248401','outline')}</div><p class="stock-note">Send your truck details so we can confirm exact fitment. Call/text before traveling.</p></div></div></div></section>
<section class="section soft"><div class="wrap info-grid"><article class="info-card"><span class="eyebrow">01 · What’s included</span><h3>{esc(item['includes'])}.</h3><p>Confirm the listed contents and any hardware with us before purchase. Other parts are sold separately unless explicitly included.</p></article><article class="info-card"><span class="eyebrow">02 · Pickup</span><h3>Pick up in Dallas.</h3><p>{pickup_text}</p></article><article class="info-card"><span class="eyebrow">03 · Fitment</span><h3>Check your specific truck.</h3><p>{fitment_text}</p></article></div></section>{cta()}'''
    feature_text=(' '+feature_summary(item)+'.') if item.get('features') else ''
    product={'@context':'https://schema.org','@type':'Product','@id':ORIGIN+item['url']+'#product','url':ORIGIN+item['url'],'name':item['title']+' — '+item['color']+', '+item['includes'],'description':f'{item["title"]}, {item["color"].lower()}, {item["condition"].lower()}, {item["includes"].lower()}.{feature_text} New takeoff inventory at Better Beds in Dallas, Texas. {availability_label}. Confirm exact fitment.','brand':{'@type':'Brand','name':item['make']},'color':item['color'],'category':item['category'],'additionalProperty':[{'@type':'PropertyValue','name':label,'value':value} for label,value in product_properties(item)],'offers':{'@type':'Offer','url':ORIGIN+item['url'],'price':item['price'],'priceCurrency':item['currency'],'availability':'https://schema.org/'+availability,'seller':{'@id':ORIGIN+'#business'}}}
    condition_schema={'New condition':'NewCondition','Used condition':'UsedCondition','Refurbished':'RefurbishedCondition'}.get(item['condition'])
    if condition_schema: product['offers']['itemCondition']='https://schema.org/'+condition_schema
    if kind=='Beds' and bed_spec(item): product['size']=bed_spec(item)
    if item.get('image'): product['image']=[ORIGIN+p['src'] for p in item['photos']] if item.get('photos') else ORIGIN+item['image']
    breadcrumbs={'@context':'https://schema.org','@type':'BreadcrumbList','itemListElement':[{'@type':'ListItem','position':position,'name':label,'item':ORIGIN+url} for position,label,url in [(1,'Better Beds',''),(2,kind,'inventory.html?type='+quote(kind)),(3,item['title'],item['url'])]]}
    seo_title=item['title']+(' for Sale' if item.get('status')=='available' else ' — '+availability_label.split(' — ')[0])
    page(item['url'],seo_title,f'{item["title"]} in Dallas: {item["color"].lower()}, {item["condition"].lower()}, {item["includes"].lower()}. ${item["price"]:,.0f}.{feature_text} {availability_label}.',body,'inventory.html',[product,breadcrumbs])

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
upload='''<form class="quote-form" action="https://chat.betterbeds.pro/estimate-requests" method="POST" enctype="multipart/form-data" data-agent-upload="true"><h2>Send an inventory inquiry.</h2><p>Use this form if you prefer. Photos of your truck are optional.</p><input type="text" name="_honey" tabindex="-1" autocomplete="off" hidden aria-hidden="true"><div class="form-grid"><label>Your name *<input name="name" autocomplete="name" required maxlength="140"></label><label>Phone number *<input type="tel" name="phone" autocomplete="tel" required maxlength="60"></label><label>Email <span class="field-help">Optional</span><input type="email" name="email" autocomplete="email" maxlength="200"></label><label>City / state<input name="location" maxlength="160" autocomplete="address-level1"></label><label>Truck year / make / model<input name="truck" placeholder="e.g. 2024 Ford F-250" maxlength="200"></label><label>Bed length / wheel setup<input name="bed_length" placeholder="Short bed, single rear wheel, etc." maxlength="160"></label><label>Color / paint code<input name="paint_code" maxlength="100"></label><label>Pickup plan<select name="travel_plan"><option value="">Choose if known</option><option>Local Dallas pickup</option><option>Travel to Dallas for pickup</option><option>Customer-arranged freight</option><option>Not sure yet</option></select></label><label>Preferred contact<select name="preferred_contact[]"><option>Text</option><option>Call</option><option>Email</option></select></label><label>Interested in<select name="quote_type[]"><option>New takeoff bed</option><option>Takeoff lights</option><option>Takeoff tailgate</option><option>Takeoff bumper</option><option>Older inventory bed with repair / paint</option></select></label></div><label>Item and questions *<textarea name="message" required rows="4" maxlength="5000" placeholder="Which listing or part? Tell us what you’d like to confirm."></textarea></label><label>Truck photos <span class="field-help">Optional · Up to 6 images, under 5 MB each and 15 MB total</span><input type="file" name="photos" accept="image/*" multiple></label><button class="button" type="submit">Send inventory inquiry <span aria-hidden="true">↗</span></button><p class="form-status" data-form-status role="status" aria-live="polite"></p><p class="form-note">Please don’t include card or bank details. Submitting an inquiry does not reserve a bed or confirm fitment.</p></form>'''
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

SITEMAP_NS='http://www.sitemaps.org/schemas/sitemap/0.9'
IMAGE_NS='http://www.google.com/schemas/sitemap-image/1.1'
ET.register_namespace('',SITEMAP_NS)
ET.register_namespace('image',IMAGE_NS)
sitemap=ET.Element(f'{{{SITEMAP_NS}}}urlset')
products_by_url={item['url']:item for item in items}
for path in PAGES:
    if path=='thanks.html': continue
    url=ET.SubElement(sitemap,f'{{{SITEMAP_NS}}}url')
    ET.SubElement(url,f'{{{SITEMAP_NS}}}loc').text=ORIGIN if path=='index.html' else ORIGIN+path
    item=products_by_url.get(path,{})
    photos=item.get('photos') or ([{'src':item['image']}] if item.get('image') else [])
    for photo in photos:
        image=ET.SubElement(url,f'{{{IMAGE_NS}}}image')
        ET.SubElement(image,f'{{{IMAGE_NS}}}loc').text=ORIGIN+photo['src']
ET.indent(sitemap,space='  ')
ET.ElementTree(sitemap).write(ROOT/'sitemap.xml',encoding='utf-8',xml_declaration=True)
inventory_links='\n'.join(f'- [{item["title"]}]({ORIGIN+item["url"]}): {item["color"]}, {item["condition"].lower()}, {item["includes"].lower()}, ${item["price"]:,.0f}.'+(' '+feature_summary(item)+'.' if item.get('features') else '') for item in available)
(ROOT/'llms.txt').write_text(f'''# Better Beds — New Takeoff Inventory, Dallas

> Better Beds sells new takeoff truck beds and parts from current inventory. Select older inventory beds can be repaired and painted by arrangement. New takeoff inventory is the main business focus.

Contact: 214-524-8401 (call/text), clint@betterbeds.pro.
Pickup: 3123 Cartwright Street, Dallas, TX 75212. Monday–Saturday 9 AM–5 PM Central. Confirm stock and pickup before traveling.
Installation and removal are not offered. Forklift loading is available for purchased beds, for transport only.

Inventory categories: Beds, Lights, Tailgates and Bumpers. Takeoff beds focus on Ford F-250/F-350 and Ram, Chevy and GMC 2500/3500 series. Bed listings include the exact length and style name. Refer to current listings for confirmed stock.

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
