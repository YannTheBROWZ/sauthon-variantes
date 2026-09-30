"""Télécharge le flux produits et le convertit en rows.json."""
import json, urllib.request, xml.etree.ElementTree as ET
URL = 'https://www.sauthon.com/fr/module/xmlfeeds/api?id=8'
NS = {'g': 'http://base.google.com/ns/1.0'}
raw = urllib.request.urlopen(urllib.request.Request(URL, headers={'User-Agent': 'Mozilla/5.0'}), timeout=120).read()
root = ET.fromstring(raw)
def g(it, t):
    e = it.find('g:' + t, NS)
    return (e.text or '').strip() if e is not None else ''
rows = [dict(id=g(i, 'id'), t=g(i, 'title'), col=g(i, 'custom_label_3'), c0=g(i, 'custom_label_0'), c1=g(i, 'custom_label_1'),
             c2=g(i, 'custom_label_2'), p=g(i, 'price'), sp=g(i, 'sale_price'), av=g(i, 'availability'), link=g(i, 'link'),
             img=g(i, 'image_link')) for i in root.findall('.//item')]
json.dump(rows, open('rows.json', 'w'), ensure_ascii=False)
print(len(rows), 'produits')
