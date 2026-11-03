"""Lignes de l'encart « Pour compléter », fiche par fiche : plan à langer, matelas (matelas.py), puis compléments
demandés par Sauthon (complements_regles.py, par référence PrestaShop ; règles de la cliente par référence : layette de
même taille, housses des lits combinés ; les duos et trios peuvent aussi recevoir ceux de leurs pièces), dans cet ordre et
sans doublon, MAX_LIGNES au plus ; un matelas à langer par défaut est suivi des autres unis s'il reste de la place.
Ajoute « l » et « r » à pc_data.json et écrit
encart_status.json (comptes, références introuvables, fiches illisibles) repris par verifier.py dans status.json.

Seules les lignes dont la règle est validée sont publiées (PUBLIER) ; les autres restent des propositions, montrées
« à valider » dans le tableau de validation (validation-client/generer_tableau.py appelle lignes()).

Format publié (lu par le tag GTM, version 2026-10-30 et suivantes ; les versions précédentes ne lisent que « map ») :
  "l": {"<fiche>": [[<id produit>, "<rôle>"], ...]}
  "r": empreinte des règles (verifier.py ne compare les listes d'une génération à l'autre qu'à règles égales)
Rôles : pl plan à langer, ml matelas de lit ou de berceau, ma matelas à langer, so sommier, ho housse de matelas à langer,
dr draps housse, pa panière, co autre complément. Le tag vérifie chaque rôle sur le titre lu en direct sur PrestaShop.

Fiche illisible pendant la lecture des pages (lire_fiches_matelas.py), elle ou une pièce de son pack, ou son plan :
elle garde sa liste de la veille si les règles n'ont pas changé (le plan à langer suit toujours « map » du jour) ; sinon
elle ne publie que ce qui ne dépend pas des pages (plan, compléments). Lecture dégradée (plus de 5 % de fiches
illisibles, ou pages lues mais vides, par exemple après un changement de thème) : listes de la veille ; sans veille
utilisable, rien n'est publié (arrêt, la version en ligne reste).
"""
import hashlib, json, os, re
exec(open('regroupement.py').read().split("if __name__")[0])
from pour_completer_regles import A_VALIDER
from complements_regles import COMPLEMENTS, COMPLEMENTS_PAR_REF, COMPLEMENTS_MOTIFS, HOUSSES_LIT_COMBINE

MAX_LIGNES = 3
ROLES = ('pl', 'ml', 'ma', 'so', 'ho', 'dr', 'pa', 'co')

# Ce que le site affiche. Décision du 31/10/2026 (consultant, pour la cliente) : « seulement le demandé ».
# Passer une règle à True quand la cliente la valide (questions « Matelas (règle générale) » du tableau).
# Réponses de la cliente du 02/11/2026 : matelas à langer reliés dans PrestaShop, matelas à langer par défaut (« les unis,
# EC, SA, TB »), lits combinés (sauf EW101 et BJ101, matelas fourni), lits 100x50 et berceaux (« le bon matelas ») validés.
PUBLIER = {
    'plan': True,                        # plans à langer validés (map)
    'plan_propose': False,               # plan en attente de validation (A_VALIDER) : jamais publié
    'matelas_lit_demande': True,         # matelas de lit des lits 120x60 et 140x70, des duos et des trios (demande du 30/10)
    'matelas_lit_junior': True,          # lits junior 90x190 / 90x200 (demande du 02/11)
    'matelas_lit_autre': True,           # berceaux (matelas du même modèle), lits 100x50 (réponse du 02/11)
    'matelas_lit_a_corriger': False,     # titre et description de la fiche en désaccord sur la taille
    'sommier': True,                     # lits junior dont la fiche dit « sommier non fourni » (demande du 02/11)
    'matelas_langer_accessoire': True,   # matelas à langer que Sauthon relie en accessoire dans PrestaShop (réponse du 02/11)
    'matelas_langer_defaut': True,       # surface 68x52 connue, aucun matelas relié : unis Vanilla, Sauge, Terracotta (02/11)
    'matelas_langer_a_confirmer': True,  # surface non indiquée (68x52 supposée) : unis ; commodes Boréale : leur matelas (02/11)
    'matelas_langer_lit_combine': True,  # lit combiné : matelas à langer en plus du matelas de lit (réponse du 02/11)
    'housse': True,                      # housse de matelas à langer, sur la fiche du matelas (demande du 28/10)
    'complement_demande': True,          # références demandées par la cliente pour la fiche (complements_regles.py)
    'complement_herite': True,           # duo / trio : compléments demandés sur ses pièces (décision du 29/10 : comme les matelas)
}
MATELAS_LIT_DEMANDES = {2274, 11}         # Confort Baby 120x60 et 140x70
MATELAS_LIT_JUNIOR = {9, 8}               # Montana 90x190 et 90x200
# Matelas à langer par défaut (aucun relié dans PrestaShop) : « les unis, EC, SA, TB » (réponse du 02/11). Le 1er (uni
# Vanilla, calculé par matelas.py) garde la place du matelas. Un seul coloris de matelas à langer (réponse du 02/11 au
# soir : « là où il y a plusieurs coloris de matelas à langer, en laisser un seul et mettre un drap à la place ») : le drap
# housse uni du même coloris (60x120 / 70x140) le suit s'il reste de la place (les compléments demandés passent avant).
UNIS_DEFAUT = ('ECML1', 'SAML1', 'TBML1')
DRAP_UNI = {'ECML1': 'ECDR5', 'SAML1': 'SADR5', 'TBML1': 'TBDR5'}
SEUIL_DEGRADE = 0.05                      # part de fiches illisibles au-delà de laquelle toute la liste de la veille est reprise
SEUIL_PAGES_VIDES = 0.2                   # part de pages lues mais sans texte (extraction cassée) qui rend la lecture dégradée

PC = json.load(open('pc_data.json'))
MAT = json.load(open('matelas_review.json')) if os.path.exists('matelas_review.json') else {}
FICHES = json.load(open('fiches-matelas.json')) if os.path.exists('fiches-matelas.json') else {}
FEED = {int(r['id']): r for r in rows}
PAR_REF = {}
for r_ in rows:
    if r_.get('ref'):
        PAR_REF.setdefault(r_['ref'].strip().upper(), int(r_['id']))
ROLE_MATELAS = {'matelas_lit': 'ml', 'matelas_langer': 'ma', 'sommier': 'so', 'housse': 'ho', 'housse_rechange': 'ho'}
EN_ERREUR = {int(k) for k, v in FICHES.items() if v.get('err')}
_lues = [v for v in FICHES.values() if not v.get('err') and not v.get('gone')]
PAGES_VIDES = sum(1 for v in _lues if not v.get('description') and not v.get('court'))
DEGRADE = bool(FICHES) and (len(EN_ERREUR) > SEUIL_DEGRADE * len(FICHES) or PAGES_VIDES > SEUIL_PAGES_VIDES * max(len(_lues), 1))


def empreinte():
    """Empreinte des règles et du code qui font les listes : à règles égales, une liste ne change que si le site change."""
    h = hashlib.sha1(json.dumps(PUBLIER, sort_keys=True).encode())
    for f in ('encart.py', 'matelas.py', 'complements_regles.py', 'pour_completer_regles.py', 'pour_completer.py',
              'regroupement.py', 'lire_fiches_matelas.py'):
        h.update(open(f, 'rb').read())
    return h.hexdigest()[:12]


EMPREINTE = empreinte()
_prec = '../docs/pour-completer.json'
PRECEDENT = json.load(open(_prec)) if os.path.exists(_prec) else {}
VEILLE = PRECEDENT.get('l', {}) if PRECEDENT.get('r') == EMPREINTE else {}   # liste de la veille, mêmes règles seulement


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


def ref_id(ref):
    return PAR_REF.get(str(ref).strip().upper())


def ref_de(pid):
    return (FEED[pid].get('ref') or '').strip().upper() if pid in FEED else ''


# Pyjamas, lots de bodies, bonnets et trousseaux de la même taille, dans toutes les collections (cliente : Orsino le 02/11,
# puis « pour les pyjamas de toutes les autres collections, suivre la même logique de terminaison de références ») :
#   pyjama xxPY1 / xxPY5 (naissance) -> bodies xxBD1, bonnet xxBN1, « Trousseau maternité - Taille naissance - <collection> »
#   pyjama xxPY2 / xxPY6 (1 mois)    -> bodies xxBD2, « Trousseau 1 mois - <collection> »
#   pyjama xxPY3 / xxPY7 (3 mois)    -> bodies xxBD3
#   et inversement (bodies, bonnet xxBN1 et trousseau -> pyjamas de la même taille).
# La taille est lue dans le titre (quelques références ne suivent pas la règle : LMBD3 = bodies naissance, SJPY4 = pyjama
# 3 mois), à défaut déduite de la terminaison. Bodies à manches courtes et autres bonnets laissés de côté, comme pour Orsino.
TAILLE_PAR_FIN = {'PY': {'1': 'naissance', '5': 'naissance', '2': '1 mois', '6': '1 mois', '3': '3 mois', '7': '3 mois'},
                  'BD': {'1': 'naissance', '2': '1 mois', '3': '3 mois'}}


def taille_layette(ref, titre):
    t = title_of(titre)
    if re.search(r'\bnaissance\b', t):
        return 'naissance'
    m = re.search(r'(?<![\w-])(\d{1,2})\s*mois', t)
    if m:
        return f'{int(m.group(1))} mois'
    fin = re.fullmatch(r'[A-Z0-9]{2}(PY|BD)(\d+)', ref)
    return TAILLE_PAR_FIN[fin.group(1)].get(fin.group(2)) if fin else None


def cle_collection(s):
    return re.sub(r'[^a-z0-9]', '', norm(s or ''))


def liens_layette():
    """{référence: [références proposées]} pour les pyjamas, bodies, bonnets et trousseaux (voir ci-dessus)."""
    coll = collections.defaultdict(lambda: {'PY': [], 'BD': [], 'BN': [], 'nom': ''})
    for r in rows:
        ref = (r.get('ref') or '').strip().upper()
        m = re.fullmatch(r'([A-Z0-9]{2})(PY|BD|BN)(\d+)', ref)
        if not m or int(r['id']) not in items:
            continue
        p, k, n = m.groups()
        coll[p]['nom'] = coll[p]['nom'] or cle_collection(r.get('col'))
        if k == 'BN':
            if n == '1':
                coll[p]['BN'].append((ref, 'naissance'))
        elif not (k == 'BD' and re.search(r'manches? courtes?', title_of(r['t']))):
            taille = taille_layette(ref, r['t'])
            if taille:
                coll[p][k].append((ref, taille))
    trousseaux = collections.defaultdict(list)       # (collection, taille) -> références
    for r in rows:
        m = re.fullmatch(r'trousseau (?:maternite - taille (naissance)|(1 mois)) - (.+)', title_of(r['t']))
        if m and r.get('ref') and int(r['id']) in items:
            trousseaux[(cle_collection(m.group(3)), m.group(1) or m.group(2))].append(r['ref'].strip().upper())
    out = collections.defaultdict(list)
    for p, c in coll.items():
        pyjamas = lambda taille: sorted(py for py, t in c['PY'] if t == taille)
        for py, taille in c['PY']:
            out[py] += sorted(b for b, t in c['BD'] if t == taille)
            out[py] += sorted(b for b, _ in c['BN']) if taille == 'naissance' else []
            out[py] += sorted(trousseaux.get((c['nom'], taille), [])) if c['nom'] else []
        for ref, taille in c['BD'] + c['BN']:
            out[ref] += pyjamas(taille)
        for (nom, taille), pks in trousseaux.items():
            if nom and nom == c['nom']:
                for pk in pks:
                    out[pk] += pyjamas(taille)
    return {k: list(dict.fromkeys(v)) for k, v in out.items() if v}


LAYETTE = liens_layette()


def housses_lit_combine(pid):
    """Lits combinés dont le matelas à langer est fourni : housses de matelas à langer des collections demandées."""
    return [r for coll in HOUSSES_LIT_COMBINE.get(ref_de(pid), [])
            for r in sorted(r for r in PAR_REF if re.fullmatch(coll + r'HM\d+', r))]


# Gigoteuses (et douillettes) naissance ou 0-6 mois (demande du 03/11/2026) : pyjama 1 mois (xxPY2) et bodies 1 mois
# (xxBD2) de la collection. Collection = 2 premiers caractères de la référence ; pour un pack sans référence de ce type
# (GI001…), le préfixe le plus courant des articles de la même collection PrestaShop.
def _prefixes_collection():
    par_col = collections.defaultdict(collections.Counter)
    for r in rows:
        ref = (r.get('ref') or '').strip().upper()
        if re.fullmatch(r'[A-Z0-9]{2}[A-Z]{2}\d+', ref) and r['col'].strip():
            par_col[norm(r['col'])][ref[:2]] += 1
    return {c: n.most_common(1)[0][0] for c, n in par_col.items()}


PREFIXE_COLLECTION = _prefixes_collection()


def layette_gigoteuse(pid):
    if pid not in FEED:
        return []
    t, ref = title_of(FEED[pid]['t']), ref_de(pid)
    if not (re.search(r'\b(gigoteuses?|douillettes?)\b', t) and re.search(r'\bnaissance\b|\b0\s*-\s*6\s*m', t)):
        return []
    p = ref[:2] if re.fullmatch(r'[A-Z0-9]{2}[A-Z]{2}\d+', ref) else PREFIXE_COLLECTION.get(norm(FEED[pid]['col']), '')
    return [c for c in (p + 'PY2', p + 'BD2') if p and ref_id(c)]


def demandes(pid):
    """Références demandées pour une fiche, dans l'ordre : par id (COMPLEMENTS), par référence de la fiche
    (COMPLEMENTS_PAR_REF, housses des lits combinés, layette), puis règles par motif de référence (COMPLEMENTS_MOTIFS,
    cibles absentes ignorées)."""
    out = list(COMPLEMENTS.get(pid, [])) + list(COMPLEMENTS_PAR_REF.get(ref_de(pid), [])) + housses_lit_combine(pid) + \
        LAYETTE.get(ref_de(pid), []) + layette_gigoteuse(pid)
    for motif, cibles in COMPLEMENTS_MOTIFS:
        m = re.fullmatch(motif, ref_de(pid))
        if m:
            out += [c.format(p=m.group(1)) for c in cibles if ref_id(c.format(p=m.group(1)))]
    return list(dict.fromkeys(str(r).strip().upper() for r in out))


def complements_de(pid):
    """[(id produit, origine)] : demandés pour la fiche (origine « demandé »), puis, pour un duo ou un trio, ceux de ses
    pièces (origine = id de la pièce), sans doublon ; références absentes du flux ignorées (voir refs_inconnues())."""
    out, vus = [], set()
    for ref in demandes(pid):
        cid = ref_id(ref)
        if cid and cid not in vus and cid != pid:
            out.append((cid, 'demandé')); vus.add(cid)
    if pid in PACKS and pid in items and pack_type(pid) in ROOM_SETS:
        for piece in PACKS[pid]:
            for ref in demandes(piece):
                cid = ref_id(ref)
                if cid and cid not in vus and cid != pid:
                    out.append((cid, piece)); vus.add(cid)
    return out


def refs_inconnues():
    """{référence: [fiches ou références qui la demandent]} pour les références explicites absentes du flux (produit
    hors ligne, coquille). Les règles par motif ne comptent pas : une collection sans spirale n'est pas une erreur."""
    out = {}
    for pid, refs in COMPLEMENTS.items():
        for ref in refs:
            if not ref_id(ref):
                out.setdefault(str(ref).strip().upper(), []).append(pid)
    for src, refs in COMPLEMENTS_PAR_REF.items():
        for ref in refs:
            if not ref_id(ref):
                out.setdefault(str(ref).strip().upper(), []).append(ref_id(src) or src)
    return out


def categorie(pid, cid, origine, ligne_matelas=None):
    """Règle qui produit la ligne (clé de PUBLIER)."""
    if origine == 'plan':
        return 'plan'
    if origine == 'proposition':
        return 'plan_propose'
    if origine == 'demandé':
        return 'complement_demande'
    if origine != 'matelas':
        return 'complement_herite'
    l, tm = ligne_matelas, MAT.get(str(pid), {}).get('type')
    role, regle = l['role'], l.get('regle')
    if role == 'matelas_lit':
        if regle == 'a_corriger':
            return 'matelas_lit_a_corriger'
        if regle != 'berceau' and (tm in ('duo', 'trio', 'duo_armoire') or cid in MATELAS_LIT_DEMANDES):
            return 'matelas_lit_demande'
        if regle != 'berceau' and cid in MATELAS_LIT_JUNIOR:
            return 'matelas_lit_junior'
        return 'matelas_lit_autre'
    if role == 'sommier':
        return 'sommier'
    if role == 'matelas_langer':
        return {'accessoire': 'matelas_langer_accessoire', 'defaut': 'matelas_langer_defaut',
                'lit_combine': 'matelas_langer_lit_combine'}.get(regle, 'matelas_langer_a_confirmer')
    return 'housse'


def candidates(pid, proposition=False):
    """Toutes les lignes possibles, dans l'ordre de l'encart : [(id produit, rôle, origine, catégorie)]."""
    out = []
    plan = PC['map'].get(str(pid))
    if plan:
        out.append((int(plan), 'pl', 'plan', 'plan'))
    elif proposition and pid in A_VALIDER:
        out.append((A_VALIDER[pid], 'pl', 'proposition', 'plan_propose'))
    for l in MAT.get(str(pid), {}).get('lignes', []):
        if l['role'] == 'matelas_langer' and ref_de(pid) in HOUSSES_LIT_COMBINE:
            continue          # matelas à langer fourni avec ce lit combiné (réponse du 02/11 : « sauf EW101 et BJ101 »)
        out.append((l['id'], ROLE_MATELAS[l['role']], 'matelas', categorie(pid, l['id'], 'matelas', l)))
    for cid, origine in complements_de(pid):
        if cid in items:
            out.append((cid, role_titre(cid), origine, categorie(pid, cid, origine)))
    return [c for c in out if c[0] != pid]


def defaut_langer(pid, cid):
    """Le matelas à langer cid est-il proposé par défaut sur la fiche (aucun matelas relié dans PrestaShop) ?"""
    return any(l['id'] == cid and l['role'] == 'matelas_langer' and l.get('defaut')
               for l in MAT.get(str(pid), {}).get('lignes', []))


def lignes(pid, proposition=False):
    """(publiées, coupées, à valider), listes de (id produit, rôle, origine, catégorie) sans doublon d'un produit :
    publiées = ce que le site affiche (règles PUBLIER), MAX_LIGNES au plus ; coupées = publiables mais au-delà de
    MAX_LIGNES ; à valider = propositions dont la règle n'est pas encore validée (proposition=True : avec le plan en
    attente de validation). Matelas à langer par défaut publié : le drap housse uni du même coloris (origine « uni ») le
    suit si une place est restée libre."""
    pub, a_valider, vus = [], [], set()
    cands = candidates(pid, proposition)
    for c in cands:
        if PUBLIER[c[3]] and c[0] not in vus:
            pub.append(c); vus.add(c[0])
    for c in cands:
        if not PUBLIER[c[3]] and c[0] not in vus:
            a_valider.append(c); vus.add(c[0])
    pub, coupees = pub[:MAX_LIGNES], pub[MAX_LIGNES:]
    k = next((i for i, c in enumerate(pub) if c[2] == 'matelas' and c[1] == 'ma' and defaut_langer(pid, c[0])), None)
    if k is not None and len(pub) < MAX_LIGNES:
        drap = ref_id(DRAP_UNI.get(ref_de(pub[k][0]), ''))
        if drap in items and drap not in vus and drap != pid:
            pub = pub[:k + 1] + [(drap, 'dr', 'uni', pub[k][3])] + pub[k + 1:]
    return pub, coupees, a_valider


def dependances(pid):
    """Fiches dont la page a servi à calculer les matelas de la fiche : elle-même, ses pièces, son plan."""
    plan = PC['map'].get(str(pid))
    pieces = (FICHES.get(str(pid), {}).get('pack') or PACKS.get(pid, [])) if pid in items else []
    return {pid, *pieces} | ({int(plan)} if plan else set())


def liste_publiee(pid):
    """(liste [[id, rôle]], source) : 'calcul', 'veille' (page illisible, liste de la veille gardée), 'sans_pages'
    (page illisible sans veille : plan et compléments seulement) ou 'vide'."""
    illisible = DEGRADE or bool(dependances(pid) & EN_ERREUR)
    if illisible and str(pid) in VEILLE:
        # liste de la veille, mais le plan à langer suit toujours « map » du jour (lu dans le flux, pas sur la page) :
        # plan ajouté ou retiré aujourd'hui pris en compte, et « map » reste la tête de « l » (contrôle de verifier.py)
        plan = PC['map'].get(str(pid))
        garde = ([[int(plan), 'pl']] if plan and PUBLIER['plan'] else []) + \
            [[x[0], x[1]] for x in VEILLE[str(pid)] if isinstance(x, list) and len(x) >= 2 and x[0] in items
             and x[0] != pid and x[1] in ROLES and x[1] != 'pl' and not (plan and x[0] == int(plan))]
        garde = garde[:MAX_LIGNES]
        if garde:
            return garde, 'veille'
    pub, coupees, _ = lignes(pid)
    if illisible:      # matelas calculés sur une page vide : pas fiables (taille « à corriger » perdue…), on les retire
        pub = [c for c in pub + coupees if c[2] not in ('matelas', 'uni')][:MAX_LIGNES]
        return [[i, r] for i, r, _, _ in pub], ('sans_pages' if pub else 'vide')
    return [[i, r] for i, r, _, _ in pub], ('calcul' if pub else 'vide')


if __name__ == '__main__':
    if DEGRADE and not VEILLE:
        raise SystemExit(f'Lecture du site dégradée ({len(EN_ERREUR)} fiches illisibles, {PAGES_VIDES} pages vides sur '
                         f'{len(FICHES)}) et pas de liste de la veille aux mêmes règles : rien n\'est publié, la version '
                         'précédente reste en ligne.')
    publie, sources = {}, collections.Counter()
    for pid in sorted(items):
        lst, src = liste_publiee(pid)
        sources[src] += 1
        if lst:
            publie[str(pid)] = lst
    PC['l'] = publie
    PC['r'] = EMPREINTE
    json.dump(PC, open('pc_data.json', 'w'), ensure_ascii=False, separators=(',', ':'))
    publiees, a_valider = collections.Counter(), collections.Counter()
    for pid in sorted(items):
        pub, coupees, av = lignes(pid)
        publiees.update(c[3] for c in pub)
        a_valider.update(c[3] for c in av)
    statut = {
        'fiches': len(publie), 'lignes': sum(len(v) for v in publie.values()),
        'roles': dict(collections.Counter(r for v in publie.values() for _, r in v)),
        'publiees_par_regle': dict(publiees), 'a_valider_par_regle': dict(a_valider),
        'fiches_illisibles': sorted(EN_ERREUR), 'pages_vides': PAGES_VIDES, 'lecture_degradee': DEGRADE,
        'listes_de_la_veille': sources['veille'], 'listes_sans_pages': sources['sans_pages'],
        'refs_inconnues': refs_inconnues(), 'empreinte': EMPREINTE,
    }
    json.dump(statut, open('encart_status.json', 'w'), ensure_ascii=False, indent=1)
    print(f'Encart : {statut["fiches"]} fiches, {statut["lignes"]} lignes', statut['roles'],
          '| à valider (non publiées) :', dict(a_valider), '| listes de la veille :', sources['veille'],
          '| fiches illisibles :', len(EN_ERREUR), '(lecture dégradée)' if DEGRADE else '')
