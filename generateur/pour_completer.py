"""Table de l'encart « Pour compléter » : fiche commode / duo / trio -> plan à langer proposé sous le bouton panier.

Part de TABLE_VALIDEE (pour_completer_regles.py), puis :
- retire les fiches ou plans à langer sortis du flux (ils reviennent tout seuls quand ils y reviennent) ;
- ajoute les nouvelles fiches reliables sans ambiguïté :
  1. un seul plan à langer présent dans les accessoires PrestaShop de la fiche ;
  2. duo / trio dont la commode (contenu réel du pack) a déjà son plan.
Écrit pc_data.json (données publiées) et pc_status.json (ajouts / retraits pour status.json).
Les fiches de A_VALIDER, d'EXCLUS et les entrées validées retirées ne sont jamais ajoutées automatiquement.
"""
import json, os, re
exec(open('regroupement.py').read().split("if __name__")[0])
from pour_completer_regles import PLANS_NOMS, TABLE_VALIDEE, A_VALIDER, EXCLUS

acc_raw = json.load(open('accessoires.json')) if os.path.exists('accessoires.json') else {}
ACC = {int(k): v['acc'] for k, v in acc_raw.items() if 'acc' in v}
GONE_PAGES = {int(k) for k, v in acc_raw.items() if v.get('gone')}
TARGET = {'commode', 'duo', 'trio'}
PLAN_RE = re.compile(r'(grand )?(dispositif|plan) a langer\b')


def available(pid):
    return pid in items and pid not in GONE_PAGES


def is_plan(pid):
    return available(pid) and bool(PLAN_RE.match(title_of(items[pid]['t'])))


def plan_name(pid):
    return PLANS_NOMS.get(pid) or items[pid]['t']


entries, sources, retraits, ajouts = {}, {}, [], []
for pid, plan in TABLE_VALIDEE.items():
    if available(pid) and is_plan(plan):
        entries[pid], sources[pid] = plan, 'validée'
    else:
        retraits.append({'fiche': pid, 'plan': plan,
                         'raison': 'fiche absente du flux' if not available(pid) else 'plan à langer absent du flux'})

blocked = set(EXCLUS) | set(A_VALIDER) | set(TABLE_VALIDEE)


def add(pid, plan, source):
    entries[pid], sources[pid] = plan, source
    ajouts.append({'fiche': pid, 'titre': items[pid]['t'], 'plan': plan, 'nom_plan': plan_name(plan), 'source': source})


# 1. accessoires PrestaShop : un seul plan à langer lié à la fiche
for pid in sorted(ACC):
    if pid in blocked or pid in entries or not available(pid) or items[pid]['comp'] not in TARGET:
        continue
    cands = sorted({a for a in ACC[pid] if is_plan(a)})
    if len(cands) == 1:
        add(pid, cands[0], 'accessoire PrestaShop')

# 2. duo / trio dont la commode a déjà son plan à langer
for sid in sorted(PACKS):
    if sid in blocked or sid in entries or not available(sid) or pack_type(sid) not in ('duo', 'trio'):
        continue
    plans = {entries[i] for i in PACKS[sid] if piece_type(i) == 'commode' and i in entries}
    if len(plans) == 1:
        add(sid, plans.pop(), 'commode du pack')

used = sorted(set(entries.values()))
data = {'plans': {str(p): plan_name(p) for p in used}, 'map': {str(k): v for k, v in sorted(entries.items())}}
json.dump(data, open('pc_data.json', 'w'), ensure_ascii=False, separators=(',', ':'))
json.dump({'fiches': len(entries), 'plans': len(used), 'ajouts_auto': ajouts, 'retraits': retraits,
           'a_valider': sorted(A_VALIDER)}, open('pc_status.json', 'w'), ensure_ascii=False, indent=2)

if __name__ == '__main__':
    print(f'Pour compléter : {len(entries)} fiches ({sum(1 for s in sources.values() if s == "validée")} validées, '
          f'{len(ajouts)} ajouts automatiques), {len(used)} plans, {len(retraits)} retraits')
    for a in ajouts:
        print('  +', a['fiche'], a['titre'][:60], '->', a['plan'], a['nom_plan'], f"({a['source']})")
    for r in retraits:
        print('  -', r)
