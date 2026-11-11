#!/usr/bin/env python3
"""Check that product pages expose consistent, crawlable inventory information."""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit
from urllib.robotparser import RobotFileParser
from xml.etree import ElementTree as ET
import json

ROOT=Path(__file__).resolve().parents[1]
ORIGIN='https://betterbeds.pro/'
items=json.loads((ROOT/'data/inventory.json').read_text())['items']
assert len({item['id'] for item in items})==len(items), 'Duplicate inventory IDs'
assert len({item['url'] for item in items})==len(items), 'Products must have unique URLs'

class Page(HTMLParser):
    def __init__(self,source):
        super().__init__()
        self.metas={}; self.links=[]; self.schemas=[]; self.canonical=None
        self.in_json=False; self.json_buffer=''; self.title=''; self.in_title=False
        self.feed(source)
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if tag=='meta': self.metas[a.get('name') or a.get('property')]=a.get('content','')
        if tag=='link' and a.get('rel')=='canonical': self.canonical=a['href']
        if tag=='a': self.links.append(a.get('href'))
        if tag=='title': self.in_title=True
        if tag=='script' and a.get('type')=='application/ld+json': self.in_json=True; self.json_buffer=''
    def handle_data(self,text):
        if self.in_title: self.title+=text
        if self.in_json: self.json_buffer+=text
    def handle_endtag(self,tag):
        if tag=='title': self.in_title=False
        if tag=='script' and self.in_json:
            self.schemas.append(json.loads(self.json_buffer)); self.in_json=False

robots=RobotFileParser()
robots.parse((ROOT/'robots.txt').read_text().splitlines())
ns={'s':'http://www.sitemaps.org/schemas/sitemap/0.9','image':'http://www.google.com/schemas/sitemap-image/1.1'}
sitemap=ET.parse(ROOT/'sitemap.xml').getroot()
sitemap_entries={entry.find('s:loc',ns).text:entry for entry in sitemap.findall('s:url',ns)}
catalog=Page((ROOT/'inventory.html').read_text())
for item in items:
    url=ORIGIN+item['url']
    source=(ROOT/item['url']).read_text()
    page=Page(source)
    assert page.canonical==url, item['id']+': canonical URL'
    assert 'noindex' not in page.metas['robots'], item['id']+': indexability'
    assert item['title'] in page.title and 'Dallas' in page.title, item['id']+': descriptive title'
    assert '$'+format(item['price'],',.0f') in source and item['includes'] in source
    assert url in sitemap_entries, item['id']+': sitemap inclusion'
    for agent in ['Googlebot','Googlebot-Image','Bingbot','OAI-SearchBot','ChatGPT-User']:
        assert robots.can_fetch(agent,url), item['id']+': '+agent+' blocked'
    products=[schema for schema in page.schemas if schema['@type']=='Product']
    assert len(products)==1, item['id']+': must describe a single product'
    product=products[0]; offer=product['offers']
    assert product['url']==url and offer['url']==url
    assert offer['price']==item['price'] and offer['priceCurrency']==item['currency']
    condition={'New condition':'NewCondition','Gently used':'UsedCondition','Used condition':'UsedCondition','Refurbished':'RefurbishedCondition'}.get(item['condition'])
    if condition: assert offer.get('itemCondition')=='https://schema.org/'+condition, item['id']+': incorrect item condition'
    if condition=='UsedCondition': assert 'New takeoff inventory' not in product['description']
    expected={'available':'InStock','sold':'SoldOut'}.get(item['status'],'OutOfStock')
    assert offer['availability']=='https://schema.org/'+expected, item['id']+': stale stock markup'
    assert product['color']==item['color'] and product['brand']['name']==item['make']
    assert any(p['name']=='Includes' and p['value']==item['includes'] for p in product['additionalProperty'])
    assert any(schema['@type']=='BreadcrumbList' for schema in page.schemas)
    photos=item.get('photos') or ([{'src':item['image']}] if item.get('image') else [])
    actual_images=[ORIGIN+photo['src'] for photo in photos]
    schema_images=product.get('image',[])
    if isinstance(schema_images,str): schema_images=[schema_images]
    assert schema_images==actual_images, item['id']+': actual product photos only'
    sitemap_images=[image.text for image in sitemap_entries[url].findall('image:image/image:loc',ns)]
    assert sitemap_images==actual_images
    for image in actual_images:
        assert (ROOT/urlsplit(image).path.lstrip('/')).is_file()
        assert robots.can_fetch('Googlebot-Image',image)
    if actual_images: assert page.metas['og:image']==actual_images[0]
    if item['status']=='available': assert item['url'] in catalog.links, item['id']+': missing crawlable catalog link'
    assert 'aggregateRating' not in product and 'review' not in product, 'Do not fabricate reviews'
print(f'PASS: {len(items)} product page(s): indexability, canonical URLs, factual Product/Offer data, stock, image sitemap, social photo, breadcrumbs, internal links and crawler access.')

# Bed measurements and slang must stay together; part pages must not inherit
# irrelevant bed specifications or assume bed hardware is included.
for item in items:
    source=(ROOT/item['url']).read_text()
    product=next(schema for schema in Page(source).schemas if schema['@type']=='Product')
    properties={prop['name']:prop['value'] for prop in product['additionalProperty']}
    if item.get('productType','Beds')=='Beds':
        assert item['bedLength'] in item['title']
        assert item['bedStyle'].lower() in item['title'].lower()
        assert properties['Bed length']==item['bedLength']
        assert properties['Bed style']==item['bedStyle']
    else:
        assert 'Bed length' not in properties and 'Bed style' not in properties
    for feature in item.get('features',[]):
        assert properties[feature['name']]==feature['value']
print('PASS: exact bed length and style, part-specific features, and no bed-only fields on other parts.')
