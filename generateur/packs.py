"""Lit les fiches produit sur le site :
- duos / trios / packs : contenu réel du pack (« Ce pack contient ») -> packs.json
- mêmes fiches + commodes : accessoires PrestaShop (« Vous aimerez aussi ») -> accessoires.json,
  qui servent à relier automatiquement une nouvelle fiche à son plan à langer (« Pour compléter »).
"""
import json, re, time, urllib.error, urllib.request, concurrent.futures
exec(open('regroupement.py').read().split("if __name__")[0])
sets = {it['id'] for it in items.values() if it['comp'] in SETS}
targets = [it for it in items.values() if it['comp'] in SETS or it['comp'] == 'commode']


def fetch(it):
    req = urllib.request.Request(it['link'], headers={'User-Agent': 'Mozilla/5.0 Chrome/128'})
    err = ''
    for essai in range(3):
        try:
            s = urllib.request.urlopen(req, timeout=40).read().decode('utf-8', 'replace')
            break
        except urllib.error.HTTPError as e:
            if e.code in (404, 410):
                return it['id'], {'gone': True}
            err = f'HTTP {e.code}'
        except Exception as e:
            err = str(e)
        time.sleep(5 * (essai + 1))
    else:
        return it['id'], {'err': err}
    out = {'items': [], 'acc': []}
    m = re.search(r'<section class="product-accessories.*?</section>\s*</section>', s, re.S)
    if m:
        out['acc'] = list(dict.fromkeys(int(x) for x in re.findall(r'data-id-product="(\d+)"', m.group(0))))
    i = s.find('class="product-pack ')
    if i >= 0:
        seg = s[i:i + 20000]
        for b in re.findall(r'class="product-pack-item.*?(?=class="product-pack-item|</section>|$)', seg, re.S):
            mm = re.search(r'/(\d+)-[^"/]*\.html', b)
            if mm:
                out['items'].append(int(mm.group(1)))
    return it['id'], out


res = {}
with concurrent.futures.ThreadPoolExecutor(4) as ex:
    for k, v in ex.map(fetch, targets):
        res[k] = v

packs = {k: ({'items': v['items']} if 'items' in v else v) for k, v in res.items() if k in sets}
accessoires = {k: ({'acc': v['acc']} if 'acc' in v else v) for k, v in res.items()}
json.dump(packs, open('packs.json', 'w'))
json.dump(accessoires, open('accessoires.json', 'w'))
print(len(targets), 'fiches lues |', len(packs), 'duos/trios/packs,', sum(1 for v in packs.values() if v.get('items')), 'avec contenu |',
      sum(1 for v in res.values() if 'err' in v), 'erreurs |', sum(1 for v in res.values() if v.get('gone')), 'supprimées')
