"""Lit les fiches meubles et matelas : accessoires PrestaShop (sections et ordre), description, caractéristiques.
Écrit fiches-matelas.json, lu par matelas.py (matelas proposés dans l'encart « Pour compléter »)."""
import json, re, html, time, urllib.request, urllib.error, concurrent.futures
exec(open('regroupement.py').read().split("if __name__")[0])
# fiches sorties du flux depuis le calcul des cibles : ignorées
cibles = [(p, k) for p, k in json.load(open('cibles-matelas.json')) if p in items and not (k == 'lit?' and re.search(r'tiroir', title_of(items[p]['t'])))]
deja = {p for p, _ in cibles}
for p, it in items.items():
    t = title_of(it['t'])
    if p not in deja and ((re.search(r'a langer|little big bed|combine|berceau|couffin|\blit\b', t) and it['c0'] in ('MEUBLES', 'MEUBLE', ''))
                          or re.match(r'(pack toilette .*)?matelas a langer', t)):   # matelas à langer : housses
        cibles.append((p, 'autre'))

def texte(s):
    s = re.sub(r'<(script|style)[\s\S]*?</\1>', ' ', s)
    s = re.sub(r'<br\s*/?>|</p>|</li>|</dd>|</dt>|</h\d>', '\n', s)
    s = re.sub(r'<[^>]+>', ' ', s)
    return re.sub(r'[ \t\xa0]+', ' ', html.unescape(s)).strip()

def lire(pk):
    pid, kind = pk
    req = urllib.request.Request(items[pid]['link'], headers={'User-Agent': 'Mozilla/5.0 Chrome/128'})
    for essai in range(3):
        try:
            s = urllib.request.urlopen(req, timeout=40).read().decode('utf-8', 'replace'); break
        except urllib.error.HTTPError as e:
            if e.code in (404, 410): return pid, {'kind': kind, 'gone': True}
        except Exception: pass
        time.sleep(4 * (essai + 1))
    else:
        return pid, {'kind': kind, 'err': True}
    out = {'kind': kind, 'sections': []}
    # carrousels de produits liés : titre de section + ids dans l'ordre
    for m in re.finditer(r'<section class="(product-accessories|block-product-list-slider|featured-products)[^"]*"[\s\S]*?</section>\s*</section>', s):
        bloc = m.group(0)
        t = re.search(r'<(?:h2|p|div)[^>]*class="[^"]*(?:block-title|h2|title)[^"]*"[^>]*>([\s\S]*?)</', bloc)
        ids = list(dict.fromkeys(int(x) for x in re.findall(r'data-id-product="(\d+)"', bloc)))
        out['sections'].append({'type': m.group(1), 'titre': texte(t.group(1))[:80] if t else '', 'ids': ids})
    # description de la fiche seule : du bloc #product-description jusqu'aux détails (sans les carrousels)
    d = re.search(r'id="product-description"[\s\S]*?(?=id="product-details")', s) or re.search(r'id="product-description"[\s\S]{0,30000}?</section>', s)
    out['description'] = texte(d.group(0))[:6000] if d else ''
    court = re.search(r'class="product-description-short[^"]*"[^>]*>([\s\S]*?)</div>', s)
    out['court'] = texte(court.group(1))[:1500] if court else ''
    feats = re.findall(r'detail[_-]+title">([\s\S]*?)</span>[\s\S]*?detail[_-]+right">\s*([\s\S]*?)</div>', s)
    out['caracteristiques'] = {texte(a): texte(b) for a, b in feats}
    out['pack'] = [int(x) for x in re.findall(r'class="product-pack-item[\s\S]*?/(\d+)-[^"/]*\.html', s[s.find('class="product-pack '):s.find('class="product-pack ') + 20000])] if 'class="product-pack ' in s else []
    return pid, out

res = {}
with concurrent.futures.ThreadPoolExecutor(4) as ex:
    for pid, v in ex.map(lire, cibles):
        res[pid] = v
json.dump(res, open('fiches-matelas.json', 'w'), ensure_ascii=False)
print(len(res), 'fiches lues |', sum(1 for v in res.values() if v.get('err')), 'erreurs |', sum(1 for v in res.values() if v.get('gone')), 'disparues')
# site indisponible pendant la lecture : on n'invente pas de matelas sur des fiches illisibles, rien n'est publié
erreurs = sum(1 for v in res.values() if v.get('err'))
if erreurs > 0.05 * max(len(res), 1):
    raise SystemExit(f'{erreurs} fiches illisibles sur {len(res)} : rien n\'est publié, la version précédente reste en ligne.')
