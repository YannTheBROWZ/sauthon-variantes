"""Contrôle la génération avant publication.

Si le flux ou le site ont mal répondu (flux vide, packs illisibles, chute brutale du nombre de
produits reliés…), le script échoue : rien n'est publié, la version en ligne reste celle de la
veille et GitHub envoie un e-mail d'échec au propriétaire du dépôt.
"""
import datetime
import json
import os
import sys

SEUIL_BAISSE = 0.75          # on refuse une baisse de plus de 25 % d'une nuit sur l'autre
MIN_FLUX = 800               # le flux compte ~1 550 produits
MIN_GROUPES = 100            # ~205 groupes aujourd'hui

new = json.load(open('variants_data.json'))
rows = json.load(open('rows.json'))
packs = json.load(open('packs.json')) if os.path.exists('packs.json') else {}
prev_path = '../docs/variantes.json'
prev = json.load(open(prev_path)) if os.path.exists(prev_path) else None

errors = []
if len(rows) < MIN_FLUX:
    errors.append(f'Flux trop court : {len(rows)} produits (minimum {MIN_FLUX}).')
packs_lus = sum(1 for v in packs.values() if v.get('items'))
if packs and packs_lus < 0.5 * len(packs):
    errors.append(f'Contenu des packs illisible : {packs_lus}/{len(packs)} pages lues (site indisponible ?).')
packs_err = sorted(k for k, v in packs.items() if 'err' in v)
if packs_err:
    errors.append(f'Pages de packs en erreur après 3 essais : {packs_err[:10]} '
                  f'(si durable, ajouter ces produits à EXCLUDE dans regroupement.py).')
if len(new['g']) < MIN_GROUPES:
    errors.append(f'Trop peu de groupes de variantes : {len(new["g"])} (minimum {MIN_GROUPES}).')
if prev:
    for key, label in (('p', 'produits reliés'), ('g', 'groupes de variantes'), ('x', 'fiches avec composition')):
        before, after = len(prev[key]), len(new[key])
        if after < before * SEUIL_BAISSE:
            errors.append(f'Baisse anormale des {label} : {before} -> {after}.')

# cohérence interne : tout produit référencé doit avoir son URL
refs = {m[0] for g in new['g'] for m in g[2]} | {t for lst in new['xl'] for _, t in lst} | {int(k) for k in new['x']}
missing = sorted(i for i in refs if str(i) not in new['p'])
if missing:
    errors.append(f'Produits référencés sans URL : {missing[:10]}')

status = {
    'genere_le': datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
    'produits_flux': len(rows),
    'produits_relies': len(new['p']),
    'groupes_variantes': len(new['g']),
    'fiches_composition': len(new['x']),
    'packs_lus': f'{packs_lus}/{len(packs)}',
    'packs_supprimes': sorted(k for k, v in packs.items() if v.get('gone')),
    'statut': 'erreur' if errors else 'ok',
    'erreurs': errors,
}
print(json.dumps(status, ensure_ascii=False, indent=2))
if errors:
    sys.exit(1)

with open('../docs/variantes.json', 'w') as f:
    json.dump(new, f, ensure_ascii=False, separators=(',', ':'))
with open('../docs/status.json', 'w') as f:
    json.dump(status, f, ensure_ascii=False, indent=2)
