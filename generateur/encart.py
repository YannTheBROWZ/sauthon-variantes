"""Lignes de l'encart « Pour compléter », fiche par fiche : plan à langer, matelas (matelas.py), puis compléments
demandés par Sauthon (complements_regles.py, par référence PrestaShop ; les duos et trios peuvent aussi recevoir ceux de
leurs pièces), dans cet ordre et sans doublon, MAX_LIGNES au plus. Ajoute « l » et « r » à pc_data.json et écrit
encart_status.json (comptes, références introuvables, fiches illisibles) repris par verifier.py dans status.json.

Seules les lignes dont la règle est validée sont publiées (PUBLIER) ; les autres restent des propositions, montrées
« à valider » dans le tableau de validation (validation-client/generer_tableau.py appelle lignes()).

Format publié (lu par le tag GTM, version 2026-10-30 et suivantes ; les versions précédentes ne lisent que « map ») :
  "l": {"<fiche>": [[<id produit>, "<rôle>"], ...]}
  "r": empreinte des règles (verifier.py ne compare les listes d'une génération à l'autre qu'à règles égales)
Rôles : pl plan à langer, ml matelas de lit ou de berceau, ma matelas à langer, so sommier, ho housse de matelas à langer,
dr draps housse, pa panière, co autre complément. Le tag vérifie chaque rôle sur le titre lu en direct sur PrestaShop.

Fiche illisible pendant la lecture des pages (lire_fiches_matelas.py), elle ou une pièce de son pack, ou son plan :
elle garde sa liste de la veille (si les règles n'ont pas changé). Plus de 5 % de fiches illisibles : toute la liste de
la veille est reprise.
"""
import hashlib, json, os, re
exec(open('regroupement.py').read().split("if __name__")[0])
from pour_completer_regles import A_VALIDER
from complements_regles import COMPLEMENTS

MAX_LIGNES = 3
ROLES = ('pl', 'ml', 'ma', 'so', 'ho', 'dr', 'pa', 'co')

# Ce que le site affiche. Décision du 31/10/2026 (consultant, pour la cliente) : « seulement le demandé ».
# Passer une règle à True quand la cliente la valide (questions « Matelas (règle générale) » du tableau).
PUBLIER = {
    'plan': True,                        # plans à langer validés (map)
    'plan_propose': False,               # plan en attente de validation (A_VALIDER) : jamais publié
    'matelas_lit_demande': True,         # matelas de lit des lits 120x60 et 140x70, des duos et des trios (demande du 30/10)
    'matelas_lit_autre': False,          # berceaux, lits junior 90x190 / 90x200, lits 100x50
    'matelas_lit_a_corriger': False,     # titre et description de la fiche en désaccord sur la taille
    'sommier': False,                    # lits junior dont la fiche dit « sommier non fourni »
    'matelas_langer_accessoire': False,  # matelas à langer que Sauthon relie en accessoire dans PrestaShop
    'matelas_langer_defaut': False,      # surface 68x52 connue, aucun matelas relié : matelas neutre 3194
    'matelas_langer_a_confirmer': False,  # taille de la surface non indiquée (68x52 supposée), commodes Boréale
    'matelas_langer_lit_combine': False,  # lit combiné : matelas à langer en plus du matelas de lit
    'housse': True,                      # housse de matelas à langer, sur la fiche du matelas (demande du 28/10)
    'complement_demande': True,          # références demandées par la cliente pour la fiche (complements_regles.py)
    'complement_herite': True,           # duo / trio : compléments demandés sur ses pièces (décision du 29/10 : comme les matelas)
}
MATELAS_LIT_DEMANDES = {2274, 11}         # Confort Baby 120x60 et 140x70
SEUIL_DEGRADE = 0.05                      # part de fiches illisibles au-delà de laquelle toute la liste de la veille est reprise

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
DEGRADE = bool(FICHES) and len(EN_ERREUR) > SEUIL_DEGRADE * len(FICHES)


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


def complements_de(pid):
    """[(id produit, origine)] : demandés pour la fiche (origine « demandé »), puis, pour un duo ou un trio, ceux de ses
    pièces (origine = id de la pièce), sans doublon ; références absentes du flux ignorées (voir refs_inconnues())."""
    out, vus = [], set()
    for ref in COMPLEMENTS.get(pid, []):
        cid = ref_id(ref)
        if cid and cid not in vus and cid != pid:
            out.append((cid, 'demandé')); vus.add(cid)
    if pid in PACKS and pid in items and pack_type(pid) in ROOM_SETS:
        for piece in PACKS[pid]:
            for ref in COMPLEMENTS.get(piece, []):
                cid = ref_id(ref)
                if cid and cid not in vus and cid != pid:
                    out.append((cid, piece)); vus.add(cid)
    return out


def refs_inconnues():
    """{référence: [fiches qui la demandent]} pour les références absentes du flux (produit hors ligne, coquille)."""
    out = {}
    for pid, refs in COMPLEMENTS.items():
        for ref in refs:
            if not ref_id(ref):
                out.setdefault(str(ref).strip().upper(), []).append(pid)
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
        out.append((l['id'], ROLE_MATELAS[l['role']], 'matelas', categorie(pid, l['id'], 'matelas', l)))
    for cid, origine in complements_de(pid):
        if cid in FEED:
            out.append((cid, role_titre(cid), origine, categorie(pid, cid, origine)))
    return [c for c in out if c[0] != pid]


def lignes(pid, proposition=False):
    """(publiées, coupées, à valider), listes de (id produit, rôle, origine, catégorie) sans doublon d'un produit :
    publiées = ce que le site affiche (règles PUBLIER), MAX_LIGNES au plus ; coupées = publiables mais au-delà de
    MAX_LIGNES ; à valider = propositions dont la règle n'est pas encore validée (proposition=True : avec le plan en
    attente de validation)."""
    pub, a_valider, vus = [], [], set()
    cands = candidates(pid, proposition)
    for c in cands:
        if PUBLIER[c[3]] and c[0] not in vus:
            pub.append(c); vus.add(c[0])
    for c in cands:
        if not PUBLIER[c[3]] and c[0] not in vus:
            a_valider.append(c); vus.add(c[0])
    return pub[:MAX_LIGNES], pub[MAX_LIGNES:], a_valider


def dependances(pid):
    """Fiches dont la page a servi à calculer les matelas de la fiche : elle-même, ses pièces, son plan."""
    plan = PC['map'].get(str(pid))
    pieces = (FICHES.get(str(pid), {}).get('pack') or PACKS.get(pid, [])) if pid in items else []
    return {pid, *pieces} | ({int(plan)} if plan else set())


def liste_publiee(pid):
    """(liste [[id, rôle]], source) : 'calcul', 'veille' (page illisible, liste de la veille gardée) ou 'vide'."""
    if (DEGRADE or dependances(pid) & EN_ERREUR) and str(pid) in VEILLE:
        garde = [[x[0], x[1]] for x in VEILLE[str(pid)] if isinstance(x, list) and len(x) >= 2 and x[0] in FEED
                 and x[0] != pid and x[1] in ROLES][:MAX_LIGNES]
        if garde:
            return garde, 'veille'
    pub, _, _ = lignes(pid)
    return [[i, r] for i, r, _, _ in pub], ('calcul' if pub else 'vide')


if __name__ == '__main__':
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
        'fiches_illisibles': sorted(EN_ERREUR), 'lecture_degradee': DEGRADE,
        'listes_de_la_veille': sources['veille'], 'refs_inconnues': refs_inconnues(), 'empreinte': EMPREINTE,
    }
    json.dump(statut, open('encart_status.json', 'w'), ensure_ascii=False, indent=1)
    print(f'Encart : {statut["fiches"]} fiches, {statut["lignes"]} lignes', statut['roles'],
          '| à valider (non publiées) :', dict(a_valider), '| listes de la veille :', sources['veille'],
          '| fiches illisibles :', len(EN_ERREUR), '(lecture dégradée)' if DEGRADE else '')
