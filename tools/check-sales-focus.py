#!/usr/bin/env python3
"""Check the public product focus, used-bed catalog and retired page indexing."""
from html.parser import HTMLParser
from pathlib import Path
from urllib.robotparser import RobotFileParser
import json
import re

ROOT=Path(__file__).resolve().parents[1]
retired={'older-beds.html','before-after.html','repair-example.html','truck-bed-repair.html'}
showcase={'services.html','gallery.html'}
sitemap=(ROOT/'sitemap.xml').read_text()
robots=RobotFileParser()
robots.parse((ROOT/'robots.txt').read_text().splitlines())

class Links(HTMLParser):
    def __init__(self,source):
        super().__init__(); self.links=[]; self.feed(source)
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if tag=='a': self.links.append(a.get('href'))

terms=r'\brepair(?:s|ed|ing)?\b|\brepaint(?:ed|ing)?\b|prepared older|older inventory|paint by arrangement'
for path in ROOT.glob('*.html'):
    source=path.read_text()
    if path.name in retired:
        assert '<meta name="robots" content="noindex, follow">' in source,path.name
        assert 'http-equiv="refresh"' not in source,path.name+': crawlers must see noindex'
        assert path.name not in sitemap,path.name+': retired URL in sitemap'
        assert 'used-beds.html' in Links(source).links,path.name+': no useful destination'
        for agent in ['Googlebot','Bingbot','OAI-SearchBot']:
            assert robots.can_fetch(agent,'https://betterbeds.pro/'+path.name), 'Allow crawling of noindex pages'
    elif path.name in showcase:
        assert '<meta name="robots" content="noindex, follow">' in source,path.name
        assert 'http-equiv="refresh"' not in source,path.name
        assert path.name not in sitemap,path.name+': showcase must stay out of search sitemap'
        assert 'Only beds we own and have in stock.' in source,path.name
        assert 'not accepting customer-owned beds or trucks' in source,path.name
        assert not retired.intersection(Links(source).links),path.name
    else:
        assert not re.search(terms,source,re.I),path.name+': obsolete service promotion'
        assert not retired.intersection(Links(source).links),path.name+': retired service link'

for name in ['data/faq-knowledge.json','.well-known/agent.json','llms.txt']:
    assert not re.search(terms,(ROOT/name).read_text(),re.I),name+': obsolete service metadata'

items=json.loads((ROOT/'data/inventory.json').read_text())['items']
expected={item['url'] for item in items if item['status']=='available' and item.get('productType','Beds')=='Beds' and item['condition'] in ['Gently used','Used condition','Refurbished']}
source=(ROOT/'used-beds.html').read_text()
actual=set(Links(source).links).intersection({item['url'] for item in items})
assert actual==expected,(actual,expected)
assert 'https://betterbeds.pro/used-beds.html' in sitemap
assert '<meta name="robots" content="index, follow, max-image-preview:large">' in source
assert 'used-beds.html' in Links((ROOT/'index.html').read_text()).links
profile=json.loads((ROOT/'.well-known/agent.json').read_text())
assert profile['used_beds_url']=='https://betterbeds.pro/used-beds.html'
assert any(service['name']=='Used truck bed sales' for service in profile['services'])
assert (ROOT/'_config.yml').read_text().count('exclude:')==1
print(f'PASS: product-focused indexed content/metadata, {len(retired)} retired and {len(showcase)} own-stock showcase noindex URLs, and {len(expected)} correctly filtered used-bed listing(s).')
