#!/usr/bin/env python3
"""Exercise order status and collection transitions without editing real inventory."""
from copy import deepcopy
from pathlib import Path
from tempfile import TemporaryDirectory
import json
import re
import shutil
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]

def product(root,url):
    return next(schema for block in re.findall(r'<script type="application/ld\+json">(.*?)</script>',(root/url).read_text(),re.S) if (schema:=json.loads(block)).get('@type')=='Product')

with TemporaryDirectory(prefix='betterbeds-order-check-') as folder:
    root=Path(folder)
    shutil.copytree(ROOT/'data',root/'data')
    shutil.copytree(ROOT/'tools',root/'tools')
    shutil.copy(ROOT/'robots.txt',root/'robots.txt')
    (root/'assets').symlink_to(ROOT/'assets',target_is_directory=True)
    data=json.loads((root/'data/inventory.json').read_text())
    fixture=deepcopy(data['items'][0])
    fixture.update(id='order-check-fixture',url='order-check-fixture.html',title="Test Ford 8' long bed",bedLength="8'",bedStyle='Long bed',status='available_to_order',price=None,image=None,imageAlt=None,photos=[])
    data['items'].append(fixture)

    def build():
        (root/'data/inventory.json').write_text(json.dumps(data))
        subprocess.run([sys.executable,str(root/'tools/build-site.py')],check=True,capture_output=True,text=True)
        check=subprocess.run([sys.executable,str(root/'tools/check-product-seo.py')],capture_output=True,text=True)
        assert check.returncode==0,check.stdout+check.stderr

    build()
    source=(root/fixture['url']).read_text()
    assert 'Contact for pricing' in source and 'not at our shop yet' in source
    assert 'offers' not in product(root,fixture['url']), 'Unknown price must not create a fake offer'
    assert fixture['url'] in (root/'available-to-order.html').read_text()
    assert fixture['url'] not in (root/'inventory.html').read_text()
    assert fixture['url'] not in (root/'index.html').read_text()
    faq=json.loads((root/'data/faq-knowledge.json').read_text())
    assert fixture['title'] not in next(x['answer'] for x in faq['entries'] if x['id']=='inventory')

    fixture['price']=1800
    build()
    assert product(root,fixture['url'])['offers']['availability']=='https://schema.org/PreOrder'

    fixture['status']='available'
    build()
    assert product(root,fixture['url'])['offers']['availability']=='https://schema.org/InStock'
    assert fixture['url'] not in (root/'available-to-order.html').read_text()
    assert fixture['url'] in (root/'inventory.html').read_text()
    assert fixture['url'] in (root/'index.html').read_text()
    assert 'not at our shop yet' not in (root/fixture['url']).read_text()

    for item in data['items']:
        if item['status']=='available_to_order': item['status']='sold'
    build()
    assert 'Order listings are being added.' in (root/'available-to-order.html').read_text()
    assert '"@type": "Product"' not in (root/'available-to-order.html').read_text()

print('PASS: unknown-price order, priced PreOrder, collection to InStock at the same URL, separate catalogs/stock answers, and empty order page.')
