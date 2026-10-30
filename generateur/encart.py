"""Lignes de l'encart « Pour compléter », fiche par fiche : plan à langer, matelas (matelas.py), puis compléments
demandés par Sauthon (complements_regles.py, par référence PrestaShop ; les duos et trios reçoivent aussi ceux de
leurs pièces), dans cet ordre et sans doublon, MAX_LIGNES au plus. Ajoute « l » à pc_data.json.

Format publié (lu par le tag GTM, version 2026-10-30 et suivantes ; les versions précédentes ne lisent que « map ») :
  "l": {"<fiche>": [[<id produit>, "<rôle>"], ...]}
Rôles : pl plan à langer, ml matelas de lit ou de berceau, ma matelas à langer, so sommier, ho housse de matelas à langer,
dr draps housse, pa panière, co autre complément. Le tag vérifie chaque rôle sur le titre lu en direct sur PrestaShop.
"""
import json, os, re
exec(open('regroupement.py').read().split("if __name__")[0])
from pour_completer_regles import A_VALIDER
try:
    from complements_regles import COMPLEMENTS
except ImportError:
    COMPLEMENTS = {}

MAX_LIGNES = 3
ROLES = ('pl', 'ml', 'ma', 'so', 'ho', 'dr', 'pa', 'co')
PC = json.load(open('pc_data.json'))
MAT = json.load(open('matelas_review.json')) if os.path.exists('matelas_review.json') else {}
FEED = {int(r['id']): r for r in rows}
PAR_REF = {}
for r_ in rows:
    if r_.get('ref'):
        PAR_REF.setdefault(r_['ref'].strip().upper(), int(r_['id']))
ROLE_MATELAS = {'matelas_lit': 'ml', 'matelas_langer': 'ma', 'sommier': 'so', 'housse': 'ho', 'housse_rechange': 'ho'}


def role_titre(pid):
    """Rôle d'un produit d'après son titre (mêmes règles que le contrôle du tag)."""
    t = title_of(FEED[pid]['t'])
    if re.match(r'(grand )?(dispositif|plan) a langer\b', t):
        return 'pl'
    if t.startswith('housse') and 'langer' in t:
        return 'ho'
    if 'matelas a langer' in t:
        return 'ma'
    if t.startswith('matelas'):
        return 'ml'
    if t.startswith('sommier'):
        return 'so'
    if 'drap' in t:
        return 'dr'
    if 'panier' in t:
        return 'pa'
    return 'co'


def complements_de(pid):
    """[(id produit, origine)] : demandés pour la fiche (origine « demandé »), puis, pour un duo ou un trio, ceux de ses
    pièces (origine = id de la pièce), sans doublon ; références absentes du flux ignorées."""
    out, vus = [], set()
    for ref in COMPLEMENTS.get(pid, []):
        cid = PAR_REF.get(ref)
        if cid and cid not in vus and cid != pid:
            out.append((cid, 'demandé')); vus.add(cid)
    if pid in PACKS and pid in items and pack_type(pid) in ROOM_SETS:
        for piece in PACKS[pid]:
            for ref in COMPLEMENTS.get(piece, []):
                cid = PAR_REF.get(ref)
                if cid and cid not in vus and cid != pid:
                    out.append((cid, piece)); vus.add(cid)
    return out


def lignes(pid, proposition=False):
    """(affichées, coupées) : listes de (id produit, rôle, origine). proposition=True ajoute le plan en attente de
    validation (A_VALIDER) en tête, comme dans le tableau de validation ; jamais publié."""
    out = []
    plan = PC['map'].get(str(pid))
    if plan:
        out.append((int(plan), 'pl', 'plan'))
    elif proposition and pid in A_VALIDER:
        out.append((A_VALIDER[pid], 'pl', 'proposition'))
    for l in MAT.get(str(pid), {}).get('lignes', []):
        out.append((l['id'], ROLE_MATELAS[l['role']], 'matelas'))
    vus = {i for i, _, _ in out}
    for cid, origine in complements_de(pid):
        if cid in vus or cid not in FEED:
            continue
        vus.add(cid)
        out.append((cid, role_titre(cid), origine))
    return out[:MAX_LIGNES], out[MAX_LIGNES:]


if __name__ == '__main__':
    publie = {}
    for pid in sorted(items):
        aff, _ = lignes(pid)
        if aff:
            publie[str(pid)] = [[i, r] for i, r, _ in aff]
    PC['l'] = publie
    json.dump(PC, open('pc_data.json', 'w'), ensure_ascii=False, separators=(',', ':'))
    nb = collections.Counter(r for v in publie.values() for _, r in v)
    print(f'Encart : {len(publie)} fiches, {sum(len(v) for v in publie.values())} lignes', dict(nb))
