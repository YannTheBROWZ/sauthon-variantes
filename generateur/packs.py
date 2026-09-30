import json, re, time, urllib.error, urllib.request, concurrent.futures
exec(open('regroupement.py').read().split("if __name__")[0])
targets = [it for it in items.values() if it['comp'] in SETS]
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
    i = s.find('class="product-pack ')
    if i < 0:
        return it['id'], {'items': []}
    seg = s[i:i + 20000]
    blocks = re.findall(r'class="product-pack-item.*?(?=class="product-pack-item|</section>|$)', seg, re.S)
    ids = []
    for b in blocks:
        m = re.search(r'/(\d+)-[^"/]*\.html', b)
        if m:
            ids.append(int(m.group(1)))
    return it['id'], {'items': ids}
res = {}
with concurrent.futures.ThreadPoolExecutor(4) as ex:
    for k, v in ex.map(fetch, targets):
        res[k] = v
json.dump(res, open('packs.json', 'w'))
print(len(targets), 'fiches', sum(1 for v in res.values() if v.get('items')), 'avec contenu', sum(1 for v in res.values() if 'err' in v), 'erreurs', sum(1 for v in res.values() if v.get('gone')), 'supprimées')
