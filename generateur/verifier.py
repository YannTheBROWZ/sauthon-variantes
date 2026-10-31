"""Contrôle la génération avant publication.

Si le flux ou le site ont mal répondu (flux vide, packs illisibles, chute brutale du nombre de
produits reliés…), le script échoue : rien n'est publié, la version en ligne reste celle de la
veille et GitHub envoie un e-mail d'échec au propriétaire du dépôt.
"""
import datetime
import json
import os
import re
import sys

SEUIL_BAISSE = 0.75          # on refuse une baisse de plus de 25 % d'une nuit sur l'autre
MIN_FLUX = 800               # le flux compte ~1 550 produits
MIN_GROUPES = 100            # ~205 groupes aujourd'hui
MIN_POUR_COMPLETER = 50      # ~92 fiches avec l'encart « Pour compléter » aujourd'hui
MIN_COMPOSITIONS = 120       # ~203 fiches avec composition aujourd'hui
MIN_ENCART = 200             # ~305 fiches avec au moins une ligne publiée dans l'encart (plan, matelas, compléments)
MAX_CHANGEMENT_ENCART = 0.2  # à règles égales, plus de 20 % des listes (et 30 fiches) qui changent d'un coup : anomalie
MAX_LIGNES_ENCART = 3
ROLES_ENCART = {'pl', 'ml', 'ma', 'so', 'ho', 'dr', 'pa', 'co'}

# Mêmes règles de format et mêmes plafonds que les balises GTM : un fichier qu'elles refuseraient
# n'est jamais publié (la version de la veille reste en ligne). Toujours fullmatch, jamais match avec « $ ».
RE_SEG = re.compile(r'[A-Za-z0-9_-]{1,200}')
RE_BAD = re.compile(r'[\x00-\x1f\x7f-\x9f\u200b-\u200f\u2028-\u202e\u2060-\u2069\ufeff<>@]|://|www\.', re.I)
MAX_DIMS, MAX_MEMBRES, MAX_VALEURS, MAX_OPTIONS = 6, 60, 30, 10
MAX_CARACTERES_VARIANTES, MAX_CARACTERES_PC = 300000, 50000


def est_id(n):
    return isinstance(n, int) and not isinstance(n, bool) and 0 < n < 10**7


def est_txt(s):
    return isinstance(s, str) and 1 <= len(s) <= 40 and not RE_BAD.search(s)

new = json.load(open('variants_data.json'))
rows = json.load(open('rows.json'))
packs = json.load(open('packs.json')) if os.path.exists('packs.json') else {}
prev_path = '../docs/variantes.json'
prev = json.load(open(prev_path)) if os.path.exists(prev_path) else None
# table « Pour compléter » (absente si pour_completer.py n'a pas tourné : on garde alors la version en ligne)
pc = json.load(open('pc_data.json')) if os.path.exists('pc_data.json') else None
pc_status = json.load(open('pc_status.json')) if os.path.exists('pc_status.json') else None
prev_pc_path = '../docs/pour-completer.json'
prev_pc = json.load(open(prev_pc_path)) if os.path.exists(prev_pc_path) else None
prev_status = json.load(open('../docs/status.json')) if os.path.exists('../docs/status.json') else {}
encart_status = json.load(open('encart_status.json')) if os.path.exists('encart_status.json') else None

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

if pc is not None:
    if len(pc['map']) < MIN_POUR_COMPLETER:
        errors.append(f'Pour compléter : trop peu de fiches ({len(pc["map"])}, minimum {MIN_POUR_COMPLETER}).')
    if prev_pc and len(pc['map']) < len(prev_pc['map']) * SEUIL_BAISSE:
        errors.append(f'Pour compléter : baisse anormale des fiches : {len(prev_pc["map"])} -> {len(pc["map"])}.')
    sans_nom = sorted({v for v in pc['map'].values() if str(v) not in pc['plans']})
    if sans_nom:
        errors.append(f'Pour compléter : plans à langer sans nom : {sans_nom}')

# format attendu par les balises
hors_format = [c for c in new['c'] if not (isinstance(c, str) and RE_SEG.fullmatch(c))]
hors_format += [t for t in new['v'] + new['l'] if not est_txt(t)]
hors_format += [k for k, p in new['p'].items() if not (
    re.fullmatch(r'\d{1,7}', k) and isinstance(p[0], int) and 0 <= p[0] < len(new['c'])
    and (est_id(p[1]) or (isinstance(p[1], str) and RE_SEG.fullmatch(p[1])))
    and (p[2] == 0 or est_id(p[2])))]
if hors_format:
    errors.append(f'Données hors format (la balise refuserait tout le fichier) : {hors_format[:10]}')
trop = [i for i, g in enumerate(new['g'])
        if len(g[0]) > MAX_DIMS or len(g[2]) > MAX_MEMBRES or any(len(o) > MAX_VALEURS for o in g[1])]
if trop:
    errors.append(f'Groupes hors plafonds (ignorés par la balise) : {trop[:10]}')
if any(len(lst) > MAX_OPTIONS for lst in new['xl']):
    errors.append('Composition hors plafond (ignorée par la balise).')
if len(new['x']) < MIN_COMPOSITIONS:
    errors.append(f'Trop peu de fiches avec composition : {len(new["x"])} (minimum {MIN_COMPOSITIONS}).')
if len(json.dumps(new, ensure_ascii=False, separators=(',', ':'))) > MAX_CARACTERES_VARIANTES:
    errors.append(f'variantes.json dépasserait {MAX_CARACTERES_VARIANTES} caractères (refusé par la balise).')
if pc is not None:
    bad = [k for k, v in pc['map'].items() if not (re.fullmatch(r'\d{1,7}', k) and re.fullmatch(r'\d{1,7}', str(v)))]
    if bad:
        errors.append(f'Pour compléter : identifiants hors format : {bad[:10]}')
    if len(json.dumps(pc, ensure_ascii=False, separators=(',', ':'))) > MAX_CARACTERES_PC:
        errors.append(f'pour-completer.json dépasserait {MAX_CARACTERES_PC} caractères (refusé par la balise).')
    # lignes de l'encart (encart.py) : [[id produit, rôle], ...] par fiche, MAX_LIGNES_ENCART au plus
    lignes = pc.get('l')
    if lignes is not None:
        mal = [k for k, v in lignes.items() if not (
            re.fullmatch(r'\d{1,7}', k) and isinstance(v, list) and 1 <= len(v) <= MAX_LIGNES_ENCART
            and all(isinstance(x, list) and len(x) == 2 and est_id(x[0]) and x[1] in ROLES_ENCART and str(x[0]) != k for x in v)
            and len({x[0] for x in v}) == len(v))]
        if mal:
            errors.append(f'Encart : lignes hors format : {mal[:10]}')
        if len(lignes) < MIN_ENCART:
            errors.append(f'Encart : trop peu de fiches avec des lignes ({len(lignes)}, minimum {MIN_ENCART}).')
        meme_regles = bool(prev_pc and prev_pc.get('l') and prev_pc.get('r') and prev_pc.get('r') == pc.get('r'))
        if meme_regles and len(lignes) < len(prev_pc['l']) * SEUIL_BAISSE:   # baisse voulue si les règles ont changé
            errors.append(f'Encart : baisse anormale des fiches avec des lignes : {len(prev_pc["l"])} -> {len(lignes)}.')
        # le tag lit « l » en priorité : chaque plan de « map » doit être la première ligne de sa fiche
        sans_plan = [k for k, v in pc['map'].items() if not lignes.get(k) or lignes[k][0] != [int(v), 'pl']]
        if sans_plan:
            errors.append(f'Encart : plans à langer de « map » absents de « l » (ils disparaîtraient du site) : {sans_plan[:10]}')
        # à règles égales (même empreinte « r »), un changement massif d'une génération à l'autre trahit une lecture
        # ratée du site (pages vides, thème modifié…) plutôt qu'un vrai changement du catalogue
        # (lecture dégradée : les listes publiées sont celles de la veille, ce contrôle ne s'applique pas)
        if meme_regles and encart_status and not encart_status.get('lecture_degradee') and \
                (prev_status.get('encart') or {}).get('publiees_par_regle'):
            av_r, ap_r = prev_status['encart']['publiees_par_regle'], encart_status['publiees_par_regle']
            for regle, n_av in av_r.items():
                if n_av - ap_r.get(regle, 0) > max(10, 0.05 * n_av):
                    errors.append(f'Encart : baisse anormale des lignes « {regle} » à règles égales : {n_av} -> '
                                  f'{ap_r.get(regle, 0)} (lecture du site ratée ?).')
        if meme_regles:
            avant = prev_pc['l']
            changes = sorted((set(avant) | set(lignes)) - {k for k in set(avant) & set(lignes) if avant[k] == lignes[k]}, key=int)
            if len(changes) > max(30, MAX_CHANGEMENT_ENCART * len(avant)):
                errors.append(f'Encart : {len(changes)} listes changent d\'un coup à règles égales (lecture du site ratée ?) : '
                              f'{changes[:10]}')

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
    'pour_completer': pc_status,
    'encart_fiches': len(pc.get('l', {})) if pc else None,
    'encart': encart_status,
    'statut': 'erreur' if errors else 'ok',
    'erreurs': errors,
}
print(json.dumps(status, ensure_ascii=False, indent=2))
if errors:
    sys.exit(1)

# Date de génération lue par les balises : au-delà de 7 jours (variantes) ou 14 jours (Pour compléter),
# elles n'affichent plus rien et le site revient seul à son état d'origine si la tâche nocturne s'arrête.
genere = int(datetime.datetime.now(datetime.timezone.utc).timestamp())
new['t'] = genere
if pc is not None:
    pc['t'] = genere

with open('../docs/variantes.json', 'w') as f:
    json.dump(new, f, ensure_ascii=False, separators=(',', ':'))
if pc is not None:
    with open('../docs/pour-completer.json', 'w') as f:
        json.dump(pc, f, ensure_ascii=False, separators=(',', ':'))
with open('../docs/status.json', 'w') as f:
    json.dump(status, f, ensure_ascii=False, indent=2)
