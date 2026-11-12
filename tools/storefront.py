"""Approved storefront and optional work showcase; rendered by tools/build-site.py.

Inventory JSON is the source of truth. Other pages keep their existing layout.
"""
from pathlib import Path
from urllib.parse import quote
import html,json,re

VERSION='20261112-stock-work-v1'

def build_storefront(root,items,business_schema,version=VERSION,showcase=None):
    ROOT=Path(root)
    esc=lambda x:html.escape(str(x),quote=True)
    available=[i for i in items if i['status']=='available']
    orders=[i for i in items if i['status']=='available_to_order']
    used=[i for i in available if i['productType']=='Beds' and i['condition'] in ('Gently used','Used condition','Refurbished')]
    types=['Beds','Tailgates','Bumpers','Lights']
    counts={t:sum(i['productType']==t for i in available) for t in types}
    SMS='sms:2145248401?body='+quote('Hi Better Beds, I’m interested in a bed or part from your inventory. My truck details are: ')
    MAP='https://www.google.com/maps/dir/?api=1&destination=3123%20Cartwright%20Street%2C%20Dallas%2C%20TX%2075212'
    schemas='<script type="application/ld+json">'+json.dumps(business_schema,ensure_ascii=False).replace('<',chr(92)+'u003c')+'</script>'
    icons={
     'Beds':'<path d="M3 8h18v10H3zM6 8V5h12v3M7 18v2m10-2v2M6 12h12"/>',
     'Tailgates':'<rect x="3" y="6" width="18" height="13" rx="1"/><path d="M9 6v3h6V6M6 15h12"/>',
     'Bumpers':'<path d="M3 10h6l1 3h4l1-3h6v7H3zM7 17v2m10-2v2"/>',
     'Lights':'<path d="M8 3h8v18H8zM8 9h8m-8 6h8M11 6h2m-2 6h2m-2 6h2"/>'}
    def icon(t): return '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.4" aria-hidden="true">'+icons[t]+'</svg>'
    def button(label,href,secondary=False): return f'<a class="button{" secondary" if secondary else ""}" href="{esc(href)}">{label}</a>'
    def photo(i,loading='lazy'):
     placeholder='assets/images/inventory/photo-coming-soon.svg' if i['productType']=='Beds' else 'assets/images/inventory/part-photo-coming-soon.svg'
     return f'<img src="{esc(i.get("image") or placeholder)}" alt="{esc(i.get("imageAlt") or "Photo coming soon — placeholder, not the actual item")}" width="{i.get("imageWidth") or 1200}" height="{i.get("imageHeight") or 800}" loading="{loading}" decoding="async">'
    def card_title(i):
     truck=i['make']+' '+i['models']; t=i['productType']; f={x['name']:x['value'] for x in i.get('features',[])}
     if t=='Beds': part=i['bedStyle'].lower()+' bed' if i['bedStyle']=='Dually' else i['bedStyle'].lower()
     elif t=='Tailgates': part=('Platinum ' if f.get('Trim')=='Platinum' else '')+'tailgate'
     elif t=='Lights': part=f.get('Side','').lower()+' taillight'
     else: part=f.get('Position','').lower()+' bumper'
     return truck+' '+part

    def length_inches(i):
     m=re.fullmatch(r"(\d+)'(?:(\d+)\")?",i.get('bedLength',''))
     return int(m[1])*12+int(m[2] or 0) if m else ''
    def card(i):
     meta=[i['years']]+([i['bedLength']] if i['productType']=='Beds' else [])+[i['color']]
     features={f['name']:f['value'] for f in i.get('features',[])}
     highlights=[]
     for key in ['Rear wheel setup','Damage','Bedliner','Step','Light type','Sensor holes']:
      if key in features:
       value=features[key]
       if key=='Rear wheel setup':
        if 'DRW' in value and i.get('bedStyle')=='Dually': continue
        value='Dually' if 'DRW' in value else 'Single rear wheel'
       elif key=='Step': value='Step included' if value=='Included' else value
       elif key=='Sensor holes': value='No sensor holes' if value=='None' else value
       highlights.append(value)
     search=' '.join(str(i.get(k,'')) for k in ['title','make','models','years','color','bedLength','bedStyle','condition','includes','category','productType'])+' '+' '.join(f['name']+' '+f['value'] for f in i.get('features',[]))
     return f'''<article class="product-card" data-inventory-item data-id="{esc(i['id'])}" data-search="{esc(search)}" data-type="{i['productType']}" data-make="{i['make']}" data-color="{esc(i['color'])}" data-bed-inches="{length_inches(i)}">
     <a class="product-media" href="{i['url']}" aria-label="{esc('View '+i['title'])}">{photo(i)}<span class="availability">On hand</span></a>
     <div class="product-body"><h3><a href="{i['url']}">{esc(card_title(i))}</a></h3><p class="product-meta">{esc(' · '.join(meta))}</p><p class="product-facts"><span>{esc(i['condition'])}</span><span>{esc(i['includes'])}</span></p>{'<p class="product-features">'+esc(' · '.join(highlights))+'</p>' if highlights else ''}<div class="product-bottom"><strong class="product-price">${i['price']:,.0f}</strong><a class="details-link" href="{i['url']}">View details <span aria-hidden="true">›</span></a></div></div></article>'''

    def header(active):
     links=[('inventory.html','Inventory'),('available-to-order.html','Available to order'),('used-beds.html','Used beds'),('services.html','Services'),('process.html','How to buy'),('contact.html','Contact')]
     nav=''.join(f'<a href="{p}"'+(' aria-current="page"' if p==active else '')+f'>{label}</a>' for p,label in links)
     return f'''<div class="utility"><div class="wrap"><span>Truck beds &amp; factory takeoff parts</span><span>Dallas, Texas · Pickup available</span></div></div><header class="site-header"><div class="wrap header-inner"><a class="brand" href="index.html" aria-label="Better Beds home"><img src="assets/images/logo.png" alt="Better Beds" width="768" height="333"></a><nav class="site-nav" id="site-nav" aria-label="Primary navigation">{nav}<a class="mobile-faq" href="faq.html">FAQ</a></nav><div class="header-contact"><a class="header-phone" href="tel:2145248401"><span class="desktop-phone">214-524-8401</span><span class="mobile-call">Call</span></a>{button('Text us',SMS)}<button class="nav-toggle" type="button" aria-label="Menu" aria-expanded="false" aria-controls="site-nav"><svg viewBox="0 0 24 24" width="22" height="22" stroke="currentColor" stroke-width="1.7" aria-hidden="true"><path d="M3 6h18M3 12h18M3 18h18"/></svg></button></div></div></header>'''

    def footer():
     return f'''<footer class="site-footer"><div class="wrap footer-grid"><div><a href="index.html" aria-label="Better Beds home"><img class="footer-logo" src="assets/images/logo.png" alt="Better Beds" width="768" height="333" loading="lazy"></a><p>Truck beds and factory parts.<br>New takeoffs and listed used inventory.<br>Pickup in Dallas, Texas.</p></div><div><h2>Shop</h2><a href="inventory.html">All on-hand inventory</a><a href="inventory.html?type=Beds">Truck beds</a><a href="inventory.html?type=Tailgates">Tailgates</a><a href="inventory.html?type=Bumpers">Bumpers</a><a href="inventory.html?type=Lights">Lights</a><a href="available-to-order.html">Available to order</a><a href="used-beds.html">Used beds</a></div><div><h2>Good to know</h2><a href="process.html">Buying &amp; pickup</a><a href="faq.html">Frequently asked questions</a><a href="about.html">About Better Beds</a><a href="services.html">Services</a><a href="gallery.html">Previous work gallery</a><a href="quote.html">Send an inquiry</a><a href="https://americanfirstfinance.com/app/?dealer=28821&amp;loc=1&amp;src=UA&amp;usetextpin=Y" target="_blank" rel="noopener">American First Finance</a></div><div><h2>Visit &amp; contact</h2><a href="tel:2145248401">214-524-8401</a><a href="mailto:clint@betterbeds.pro">clint@betterbeds.pro</a><a href="{MAP}" target="_blank" rel="noopener">3123 Cartwright Street<br>Dallas, TX 75212</a><p>Monday–Saturday<br>9 AM–5 PM Central</p></div></div><div class="wrap footer-bottom">© <span data-year>2026</span> Better Beds. All rights reserved.</div></footer>'''

    analytics="<script>(function(c,l,a,r,i,t,y){c[a]=c[a]||function(){(c[a].q=c[a].q||[]).push(arguments)};t=l.createElement(r);t.async=1;t.src='https://www.clarity.ms/tag/'+i;y=l.getElementsByTagName(r)[0];y.parentNode.insertBefore(t,y)})(window,document,'clarity','script','uzvvg1g1vl');</script>"
    def document(path,title,body,description=None,indexable=True,share_image='assets/images/logo.png',scripts=()):
     canonical='https://betterbeds.pro/' if path=='index.html' else 'https://betterbeds.pro/'+path
     descriptions={'index.html':'Shop new takeoff truck beds and parts, plus listed used beds, at Better Beds in Dallas. See actual photos, prices and included parts; arrange Dallas pickup.','inventory.html':'Browse on-hand truck beds, tailgates, bumpers and lights in Dallas. Filter Ford, Ram, Chevy and GMC listings by part, make, color and exact bed length.'}
     description=description or descriptions[path]
     robots='index, follow, max-image-preview:large' if indexable else 'noindex, follow'
     twitter_card='summary' if share_image=='assets/images/logo.png' else 'summary_large_image'
     extra_scripts=''.join(f'<script src="{esc(script)}?v={version}" defer></script>' for script in scripts)
     (ROOT/path).write_text(f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>{esc(title)} | Better Beds Dallas</title><meta name="description" content="{esc(description)}"><meta name="robots" content="{robots}"><meta name="theme-color" content="#303f80"><link rel="canonical" href="{canonical}"><meta property="og:site_name" content="Better Beds"><meta property="og:type" content="website"><meta property="og:title" content="{esc(title)} | Better Beds Dallas"><meta property="og:description" content="{esc(description)}"><meta property="og:url" content="{canonical}"><meta property="og:image" content="https://betterbeds.pro/{esc(share_image)}"><meta name="twitter:card" content="{twitter_card}"><link rel="icon" href="assets/images/better-beds-favicon.png"><link rel="stylesheet" href="storefront.css?v={version}">{schemas}{analytics}</head><body class="storefront"><a class="skip" href="#main">Skip to content</a>{header(path)}<main id="main">{body}</main>{footer()}<script src="script.js?v={version}" defer></script><script src="faq-widget.js?v={version}" defer></script>{extra_scripts}</body></html>\n''')

    # HOME: a compact introduction, four category links and just three featured beds.
    hero=next((i for i in available if i['productType']=='Beds'),next(iter(available),None))
    featured_ids=['ford-super-duty-short-bed-white','ford-super-duty-eight-foot-srw-white-bedliner','ram-3500-eight-foot-dually-gray']
    featured=[i for k in featured_ids for i in available if i['id']==k]
    featured += [i for i in available if i['productType']=='Beds' and i not in featured]
    featured += [i for i in available if i not in featured]
    featured=featured[:3]
    categories=''.join(f'<a class="category-card" href="inventory.html?type={t}">{icon(t)}<span><strong>{t}</strong><small>{counts[t]} {"listing" if counts[t]==1 else "listings"}</small></span><span class="category-chevron" aria-hidden="true">›</span></a>' for t in types)
    form=f'''<details class="home-inquiry"><summary>Send your truck details</summary><form data-inquiry-builder class="inquiry"><div class="form-grid"><label>Your truck<input name="truck" placeholder="Year, make, model" maxlength="140"></label><label>Bed length / wheel setup<input name="bed" placeholder="Length, single rear wheel or dually" maxlength="140"></label><label>Bed or part<input name="item" placeholder="Listing name or item" maxlength="240"></label><label>Questions<textarea name="details" rows="2" maxlength="1500"></textarea></label></div><div class="actions"><a class="button" data-inquiry-sms href="{SMS}">Prepare a text</a><a class="button secondary" data-inquiry-email href="mailto:clint@betterbeds.pro">Prepare an email</a></div><p class="form-note">Opens your text or email app. Review and send your message there.</p></form></details>'''
    hero_panel=f'''<figure class="hero-photo"><a href="{hero['url']}">{photo(hero,'eager')}</a><figcaption><div><strong>{esc(card_title(hero))}</strong><span>{esc(hero["years"]+" · "+hero["bedLength"]+" · "+hero["color"]+" · "+hero["includes"])}</span></div><a href="{hero['url']}">${hero['price']:,.0f}</a></figcaption></figure>''' if hero else '<figure class="hero-photo"><img src="assets/images/inventory/photo-coming-soon.svg" alt="Photo coming soon — placeholder, not the actual item" width="1200" height="800"><figcaption>Inventory is being updated. Contact us for current stock.</figcaption></figure>'
    home=f'''<section class="home-hero"><div class="wrap hero-grid"><div class="hero-title"><p class="eyebrow">New takeoffs. Real inventory.</p><h1>Truck beds &amp; parts.<br>Right here in Dallas.</h1></div>{hero_panel}<div class="hero-copy"><p class="hero-intro">Factory beds, tailgates, bumpers and lights. See the actual item, know the price, and find the right fit for your truck.</p><div class="actions">{button('Shop all inventory','inventory.html')}{button('Ask about a bed',SMS,True)}</div><p class="hero-note">Ford · Ram · Chevy · GMC</p></div></div></section>
    <section class="categories"><div class="wrap category-grid">{categories}</div></section>
    <section class="featured-section"><div class="wrap"><div class="section-heading"><div><p class="eyebrow">A few from the lot</p><h2>Take a look at what’s here.</h2></div><a class="text-link" href="inventory.html">See all {len(available)} listings <span aria-hidden="true">›</span></a></div><div class="product-grid featured-grid">{''.join(card(i) for i in featured)}</div></div></section>
    <section class="takeoff-section"><div class="wrap takeoff-grid"><div><p class="eyebrow">Factory parts. Another purpose.</p><h2>What’s a new takeoff?</h2></div><div><p>A factory bed or part removed from a new truck, often to make room for a flatbed or service body. It’s a practical way to keep the factory look.</p><p>Each listing shows the actual item’s condition and what’s included.</p><a class="text-link" href="faq.html">More buying questions</a></div></div></section>
    <section class="pickup-section"><div class="wrap pickup-grid"><div><p class="eyebrow">From our lot to your truck</p><h2>Pickup in Dallas.<br>We can help you load.</h2><p>Choose a listing, check the details with us, and arrange a pickup time. Forklift loading is available for transport; bring a suitable truck or trailer and tie-downs.</p><a class="text-link" href="process.html">How buying &amp; pickup works</a></div><div class="address-card"><div class="address-icon"><svg viewBox="0 0 24 24" width="28" height="28" fill="none" stroke="currentColor" stroke-width="1.5" aria-hidden="true"><path d="M19 10c0 5-7 11-7 11S5 15 5 10a7 7 0 1 1 14 0Z"/><circle cx="12" cy="10" r="2.5"/></svg></div><h3>Better Beds</h3><p>3123 Cartwright Street<br>Dallas, TX 75212</p><p>Monday–Saturday · 9 AM–5 PM Central</p><a class="text-link" href="{MAP}" target="_blank" rel="noopener">Get directions</a></div></div></section>
    <section class="contact-section"><div class="wrap contact-grid"><div><p class="eyebrow">Let’s check your fit</p><h2>Questions about a bed?</h2><p>Send your truck year, model and the listing you’re interested in. We’ll confirm availability, fitment and the details before you make the trip.</p><div class="actions">{button('Text 214-524-8401',SMS)}{button('Call us','tel:2145248401',True)}</div><a class="text-link contact-form-link" href="quote.html">Prefer the website inquiry form?</a></div><div>{form}<div class="order-link"><strong>Looking beyond on-hand stock?</strong><p>Available-to-order beds haven’t been collected yet.</p><a class="text-link" href="available-to-order.html">Browse {len(orders)} available-to-order beds</a></div></div></div></section>'''
    document('index.html','Truck beds & factory parts in Dallas',home)

    # INVENTORY: preserve existing filter hooks, semantics and shared URLs.
    tabs='<button class="inventory-type" type="button" data-filter-type="" aria-pressed="true">All items <span>'+str(len(available))+'</span></button>'+''.join(f'<button class="inventory-type" type="button" data-filter-type="{t}" aria-pressed="false">{t} <span>{counts[t]}</span></button>' for t in types)
    makes=''.join(f'<option value="{m}">{m}</option>' for m in ['Ford','Ram','Chevy','GMC'])
    colors=''.join(f'<option value="{esc(c)}">{esc(c)}</option>' for c in sorted({i['color'] for i in available}))
    ordered=sorted(available,key=lambda i:types.index(i['productType']))
    inventory=f'''<section class="catalog-intro"><div class="wrap"><nav class="breadcrumbs" aria-label="Breadcrumb"><a href="index.html">Home</a><span aria-hidden="true">/</span><span>Inventory</span></nav><div class="catalog-title-row"><div><h1>Truck beds &amp; parts in stock</h1><p>Browse by truck, bed length, or part. Dallas pickup.</p></div><a class="catalog-contact" href="{SMS}">Need a hand? Text us</a></div><div class="stock-navigation"><span aria-current="page">On-hand inventory</span><a href="available-to-order.html">Available to order <small>{len(orders)}</small></a><a href="used-beds.html">Used beds <small>{len(used)}</small></a></div></div></section>
    <section class="catalog-section"><div class="wrap"><div class="catalog-controls"><div class="inventory-types" role="group" aria-label="Part type">{tabs}</div><div class="inventory-filters"><label class="search-label">Search inventory<input type="search" data-inventory-search aria-label="Search inventory" placeholder="Try F-250, 8 foot, short bed, or tailgate"></label><label>Make<select data-filter-make><option value="">All makes</option>{makes}</select></label><label>Color<select data-filter-color><option value="">All colors</option>{colors}</select></label></div></div><div class="search-summary"><span data-inventory-count role="status" aria-live="polite">{len(available)} listings</span><button type="button" class="clear-filters" data-clear-search>Clear filters</button></div><div class="product-grid catalog-grid">{''.join(card(i) for i in ordered)}<div class="empty-state" data-inventory-empty hidden><h2>No listings match those filters.</h2><p>Try another search or clear the filters. Beds not yet collected are listed separately under Available to Order.</p><a class="text-link" href="available-to-order.html">View available-to-order beds</a></div></div><p class="catalog-note">Prices apply to the contents stated in each listing. Confirm availability and exact fitment before traveling. Counts show listings, not quantities.</p></div></section>
    <section class="catalog-help"><div class="wrap"><div><h2>Have a question about a listing?</h2><p>Send the item and your truck details. We’ll check it with you.</p></div><div class="actions">{button('Text Better Beds',SMS)}{button('How pickup works','process.html',True)}</div></div></section>'''
    document('inventory.html','On-hand truck bed & part inventory',inventory)
    pages=['index.html','inventory.html']
    if showcase is not None:
     from work_showcase import build_work_showcase
     pages.extend(build_work_showcase(document,showcase))
    return pages
