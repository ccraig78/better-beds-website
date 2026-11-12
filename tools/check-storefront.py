#!/usr/bin/env python3
"""Guard production indexing and data-driven storefront builds."""
from copy import deepcopy
from html.parser import HTMLParser
from pathlib import Path
from tempfile import TemporaryDirectory
from urllib.parse import urlsplit
import json
from storefront import build_storefront

ROOT=Path(__file__).resolve().parents[1]
class Page(HTMLParser):
    def __init__(self,source):
        super().__init__(); self.metas={}; self.canonical=None; self.cards=[]; self.current=None; self.schemas=[]; self.in_json=False; self.json=''; self.feed(source)
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if tag=='meta': self.metas[a.get('name') or a.get('property')]=a.get('content','')
        if tag=='link' and a.get('rel')=='canonical': self.canonical=a.get('href')
        if tag=='article' and 'data-inventory-item' in a:
            self.current={'id':a['data-id'],'text':'','links':[],'image':None};self.cards.append(self.current)
        if self.current and tag=='a': self.current['links'].append(a.get('href'))
        if self.current and tag=='img': self.current['image']=a.get('src')
        if tag=='script' and a.get('type')=='application/ld+json':self.in_json=True;self.json=''
    def handle_data(self,data):
        if self.current:self.current['text']+=data+' '
        if self.in_json:self.json+=data
    def handle_endtag(self,tag):
        if tag=='article':self.current=None
        if tag=='script' and self.in_json:self.schemas.append(json.loads(self.json));self.in_json=False

items=json.loads((ROOT/'data/inventory.json').read_text())['items']
stock={i['id']:i for i in items if i['status']=='available'}
for path in ['index.html','inventory.html']:
    source=(ROOT/path).read_text(); page=Page(source)
    url='https://betterbeds.pro/' if path=='index.html' else 'https://betterbeds.pro/'+path
    assert page.canonical==url and page.metas['og:url']==url,path+': canonical/social URL'
    assert 'index' in page.metas['robots'] and 'noindex' not in page.metas['robots'],path+': preview indexing restriction'
    assert page.metas['description'] and page.metas['og:description'],path+': missing search metadata'
    assert 'local design preview' not in source and 'preview/storefront.css' not in source
    assert 'uzvvg1g1vl' in source and 'www.clarity.ms/tag/' in source,path+': analytics missing'
    assert 'storefront.css?v=' in source
    assert sum(s.get('@type')=='AutoPartsStore' for s in page.schemas)==1
    if path=='index.html': assert len(page.cards)<=3
    else: assert {c['id'] for c in page.cards}==set(stock)
    for card in page.cards:
        item=stock[card['id']]
        assert card['image']==item['image'],item['id']+': incorrect photo'
        assert all(link==item['url'] for link in card['links']),item['id']+': incorrect detail link'
        for value in [item['years'],item['color'],item['condition'],item['includes'],'$'+format(item['price'],',.0f')]:
            assert value in card['text'],(item['id'],value)
        if item['productType']=='Beds': assert item['bedLength'] in card['text']
    if path=='index.html': business=next(s for s in page.schemas if s['@type']=='AutoPartsStore')

# Future sales and missing photos must regenerate safely without stale featured stock.
with TemporaryDirectory(prefix='betterbeds-storefront-') as folder:
    root=Path(folder); changed=deepcopy(items)
    featured_ids={c['id'] for c in Page((ROOT/'index.html').read_text()).cards}
    for item in changed:
        if item['id'] in featured_ids:item['status']='sold'
    active=next(i for i in changed if i['status']=='available')
    active.update(price=1735,image=None,imageAlt=None,photos=[])
    build_storefront(root,changed,business)
    home=Page((root/'index.html').read_text());catalog=Page((root/'inventory.html').read_text())
    assert not featured_ids.intersection(c['id'] for c in home.cards)
    card=next(c for c in catalog.cards if c['id']==active['id'])
    assert '$1,735' in card['text'] and 'photo-coming-soon.svg' in card['image']
    for item in changed:item['status']='sold'
    build_storefront(root,changed,business)
    assert not Page((root/'index.html').read_text()).cards
    assert not Page((root/'inventory.html').read_text()).cards
    assert 'Inventory is being updated' in (root/'index.html').read_text()
print('PASS: production metadata/canonicals/analytics, exact on-hand cards, featured selection, safe stock/price/photo updates and empty catalog.')
