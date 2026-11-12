#!/usr/bin/env python3
"""Check original gallery provenance, own-stock scope and search exclusions."""
from html.parser import HTMLParser
from pathlib import Path
import hashlib
import json
import subprocess

ROOT = Path(__file__).resolve().parents[1]
archive = json.loads((ROOT/'data/work-gallery.json').read_text())


class Page(HTMLParser):
    def __init__(self, source):
        super().__init__()
        self.photos = []
        self.links = []
        self.metas = {}
        self.scripts = []
        self.feed(source)

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == 'a':
            self.links.append(a.get('href'))
            if 'data-work-photo' in a:
                self.photos.append(a)
        if tag == 'meta':
            self.metas[a.get('name') or a.get('property')] = a.get('content')
        if tag == 'script' and a.get('src'):
            self.scripts.append(a['src'].split('?')[0])


expected = {f'assets/images/gallery/gallery-{n:03}.jpg' for n in range(1, 72)}
assert len(archive['photos']) == len(expected) == 71
assert {p['src'] for p in archive['photos']} == expected
assert len(archive['featured']) == len(set(archive['featured']))
assert set(archive['featured']) <= {p['id'] for p in archive['photos']}
for photo in archive['photos']:
    original = subprocess.check_output(['git', 'show', archive['source_tag'] + ':' + photo['src']], cwd=ROOT)
    assert hashlib.sha256(original).digest() == hashlib.sha256((ROOT/photo['src']).read_bytes()).digest(), photo['src'] + ': altered archive photo'
    assert photo['width'] > 0 and photo['height'] > 0 and photo['alt']

for name in ['services.html', 'gallery.html']:
    source = (ROOT/name).read_text()
    page = Page(source)
    assert page.metas['robots'] == 'noindex, follow', name
    assert name not in (ROOT/'sitemap.xml').read_text(), name
    assert 'Only beds we own and have in stock.' in source
    assert 'not accepting customer-owned beds or trucks' in source
    assert 'Installation and removal are not offered' in source
    assert 'timing' in source and 'for each bed' in source
    assert not any(term in source for term in ['"@type": "Product"', '"@type": "Offer"', 'data-inventory-item', 'name="quote_type[]"'])
    assert 'gallery.html' in page.links and 'services.html' in page.links and 'used-beds.html' in page.links
    assert page.metas['og:image'] == 'https://betterbeds.pro/assets/images/gallery/gallery-039.jpg'
    assert 'storefront.css?v=' in source
gallery = Page((ROOT/'gallery.html').read_text())
assert len(gallery.photos) == len({p['href'] for p in gallery.photos}) == 71
assert {p['href'] for p in gallery.photos} == expected
assert all(p.get('target') == '_blank' and 'noopener' in p['rel'] for p in gallery.photos)
assert 'work-gallery.js' in gallery.scripts
assert 'historical gallery, not current inventory' in (ROOT/'gallery.html').read_text()
assert 'no standard turnaround promise' in (ROOT/'services.html').read_text()
for name in ['index.html', 'inventory.html', 'used-beds.html', 'contact.html']:
    page = Page((ROOT/name).read_text())
    assert 'services.html' in page.links and 'gallery.html' in page.links, name
print('PASS: 71 unchanged original archive photos, no duplicates, no-JS links, own-stock scope, navigation and noindex search policy.')
