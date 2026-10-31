"""Matelas associés aux meubles (extension de « Pour compléter ») : toutes les propositions, avec leur règle.
Le site n'affiche que celles dont la règle est validée (PUBLIER dans encart.py) ; le tableau de validation
montre les autres « à valider ». La coupe à 3 lignes se fait dans encart.py, après ce filtre.

Règles (3 lignes au plus dans l'encart, plan à langer compris ; décision du 28/10 : 3 au lieu de 2) :
- commode avec plan à langer : plan + matelas à langer ;
- plan à langer seul, pack commode + plan, commode ou combiné à surface à langer intégrée : matelas à langer ;
- duo / trio : plan à langer + matelas de lit + matelas à langer (sans plan, si une surface à langer existe : matelas de lit +
  matelas à langer) ;
- lit, berceau : matelas de lit ; lit combiné (surface à langer accolée, y compris dans un duo lit + armoire) :
  matelas de lit + matelas à langer ;
  lit junior : matelas + sommier quand la fiche dit que le sommier n'est pas fourni ;
- rien si le matelas est déjà fourni (titre, ou description : « matelas à langer fourni / inclus », couffin vendu garni).
- matelas à langer : la housse vendue à part, de la même collection et couleur (« housse de rechange » s'il a déjà la sienne).
Preuves : description et caractéristiques de la fiche (et des pièces du pack), accessoires liés par Sauthon dans
PrestaShop, dimensions des matelas. Écrit matelas_data.json (pid -> lignes, noms courts) et matelas_review.json (détail).
"""
import json, re, collections
exec(open('regroupement.py').read().split("if __name__")[0])
FICHES = {int(k): v for k, v in json.load(open('fiches-matelas.json')).items()}
PC = json.load(open('pc_data.json'))
from pour_completer_regles import EXCLUS, A_VALIDER
_src = open('pour_completer_regles.py').read()
RAISON = {int(m.group(1)): m.group(2) for m in re.finditer(r'^\s*(\d+),\s*#\s*(.+?)\s:\s', _src[_src.index('EXCLUS = {'):], re.M)}

# ---------------------------------------------------------------- matelas du catalogue
LIT_PAR_TAILLE = {(120, 60): 2274, (140, 70): 11, (100, 50): 4120, (190, 90): 9, (200, 90): 8}
SOMMIER_PAR_TAILLE = {(190, 90): 6, (200, 90): 7}
BERCEAU = {'bambin': 2484, 'galopin': 2482, 'eclipse': 2487, 'lune': 2485}
MATELAS_LANGER_DEFAUT = 3194          # Matelas à langer + housse + serviette uni Vanilla, 52x68x6 cm
MATELAS_BOREALE = 2628                # « Matelas à langer commodes Boréale. Bambin. Galopin »
NOMS_COURTS = {4120: 'Matelas 100x50x10 Confort Baby', 9: 'Matelas Montana 90x190', 8: 'Matelas Montana 90x200',
               6: 'Sommier à lattes 90x190', 7: 'Sommier à lattes 90x200', 2274: 'Matelas 120x60 Confort Baby',
               11: 'Matelas 140x70x10 Confort Baby'}
MAX_LIGNES = 3                        # lignes de l'encart « Pour compléter », plan à langer compris
NUM = r'(\d{2,3})\s*(?:cm\s*)?[x×]\s*l?\s*(\d{2,3})\b'


def nom(pid):
    return NOMS_COURTS.get(pid) or (re.sub(r'\s+', ' ', items[pid]['t']).strip() if pid in items else str(pid))


def texte(pid):
    f = FICHES.get(pid, {})
    return ' '.join([f.get('description', ''), f.get('court', '')] + [f'{a} : {b}' for a, b in f.get('caracteristiques', {}).items()])


def taille(a, b):
    a, b = int(float(a)), int(float(b))
    return (max(a, b), min(a, b))


def pieces(pid):
    return FICHES.get(pid, {}).get('pack') or PACKS.get(pid, [])


def titre_n(pid):
    return title_of(items[pid]['t']) if pid in items else ''


# ---------------------------------------------------------------- matelas à langer du catalogue et leurs dimensions
def est_matelas_langer(pid):
    t = titre_n(pid)
    return 'matelas a langer' in t and not re.match(r'housse|pack toilette', t) and not re.search(r'voyage|grand modele', t)


def dims_matelas(pid):
    t = items[pid]['t'] + ' ' + texte(pid)
    if re.search(r'petit mod[eè]le', t, re.I):
        return (68, 52)
    m = re.search(r'\b(\d{2})\s*[x×]\s*(\d{2})(?:\s*[x×]\s*\d{1,2})?\s*cm', t)
    if m:
        return taille(m.group(1), m.group(2))
    if re.search(r'matelas a langer (plus|\+|avec)', titre_n(pid)):
        return (68, 52)      # gamme « plus serviette éponge » / « avec sa housse » : 52 x 68 x 6 cm (relu sur les fiches)
    return None


MATELAS_LANGER = {p: dims_matelas(p) for p in items if est_matelas_langer(p)}


def accessoires(pid):
    out = []
    for s in FICHES.get(pid, {}).get('sections', []):
        out += [i for i in s['ids'] if i not in out]
    return out


# ---------------------------------------------------------------- type de meuble
def type_meuble(pid):
    it = items[pid]
    t = title_of(it['t'])
    if re.match(r'(matelas|sommier|housse|drap|lot de|couvre|support|tour de lit|parure|gigoteuse|tiroir|option)', t):
        return None
    if re.match(r'(grand )?(di?s?positif|plan) a langer', t):
        return 'plan'
    if re.match(r'(pack )?(berceau|couffin)\b', t):
        return 'berceau'
    if pid in PACKS and pack_type(pid):
        return pack_type(pid)
    if it['comp'] in ('lit', 'commode', 'duo', 'trio', 'duo_armoire', 'pack'):
        return it['comp']
    if t.startswith('pack') and re.search(r'\blit\b', t) and re.search(r'(meuble|combine)[^.]{0,25}a langer', t):
        return 'duo'
    if re.match(r'(combine commode a langer|commode[- ]ilot|meuble a langer)', t):
        return 'commode'
    if re.match(r'little big bed', t) or (re.match(r'lit\b', t) and not re.search(r'tiroir', t)):
        return 'lit'
    return None


# ---------------------------------------------------------------- matelas déjà fournis
def matelas_lit_inclus(pid):
    t, tx = titre_n(pid), texte(pid)
    if re.search(r'\+ ?matelas|avec (son|le|un) matelas', t):
        return True
    if type_meuble(pid) == 'berceau' and t.startswith(('couffin', 'pack couffin')):
        return not re.search(r'matelas[^.\n]{0,40}non fourni', tx, re.I)
    return False


def matelas_langer_inclus(pid):
    for p in [pid] + list(pieces(pid)):
        if re.search(r'matelas à langer (imperméable )?(est )?(fourni|inclus)|matelas à langer imperméable est inclus', texte(p), re.I):
            return True
    return False


# ---------------------------------------------------------------- besoins
def taille_lit(pid):
    tx = texte(pid)
    sz = [s for s in items[pid]['sizes'] if re.fullmatch(r'\d+x\d+', s or '')]
    if sz:
        dim = taille(*sz[0].split('x'))
        m = re.search(r'compatible avec un matelas de lit\s*L\s*(\d+)\s*x\s*l\s*(\d+)', tx)
        note = '' if not m or taille(m.group(1), m.group(2)) == dim else f' (la description annonce {m.group(1)}x{m.group(2)} : à corriger)'
        return dim, f'titre : {sz[0]}' + note
    for motif in (r'compatible avec un matelas(?: de lit)?\s*L?\s*' + NUM, r'pour matelas\s*' + NUM, r'couchage(?: bébé)?\s*:?\s*' + NUM,
                  r'matelas\s*' + NUM + r'\s*cm\s*non fourni'):
        m = re.search(motif, tx, re.I)
        if m:
            return taille(m.group(1), m.group(2)), 'description : matelas ' + m.group(1) + ' x ' + m.group(2)
    tm = FICHES.get(pid, {}).get('caracteristiques', {}).get('Taille et modèle', '')
    m = re.search(r'(\d{2,3})\s*[x×]\s*(\d{2,3})', tm)
    if m:
        return taille(m.group(1), m.group(2)), f'caractéristique « Taille et modèle » : {tm}'
    for p in pieces(pid):
        if p in items and p != pid and re.match(r'(lit|little big bed)', titre_n(p)):
            d, pr = taille_lit(p)
            if d:
                return d, f'lit du pack ({p}) : {pr}'
    return None, 'taille de couchage introuvable'


def besoin_lit(pid):
    """(matelas de lit, sommier, preuve) ou (None, None, raison). La règle se déduit de la preuve par regle_lit()."""
    t, tx = titre_n(pid), texte(pid)
    acc = accessoires(pid)
    if type_meuble(pid) == 'berceau':
        for k, mid in BERCEAU.items():
            if k in t:
                return mid, None, f'berceau {k.capitalize()}' + (' + accessoire PrestaShop' if mid in acc else '')
        lie = [a for a in acc if a in BERCEAU.values()]
        return (lie[0], None, 'accessoire PrestaShop') if lie else (None, None, 'aucun matelas de berceau correspondant au catalogue')
    dim, preuve = taille_lit(pid)
    if not dim:
        return None, None, preuve
    mid = LIT_PAR_TAILLE.get(dim)
    if not mid:
        return None, None, f'aucun matelas {dim[0]}x{dim[1]} au catalogue'
    if mid in acc:
        preuve += ' + accessoire PrestaShop'
    som = None
    if dim in SOMMIER_PAR_TAILLE and re.search(r'sommier[^.\n]{0,40}non fourni|non fournis?[^.\n]{0,40}sommier|sans sommier|sommier non fourni', tx, re.I):
        som = SOMMIER_PAR_TAILLE[dim]
    return mid, som, preuve


SURFACE = [r'matelas à langer,?\s*de\s*dimension\s*:?\s*(\d{2})\s*[x×]\s*(\d{2})\b',
           r'dimensions conseillées\s*:?\s*(\d{2})\s*[x×]\s*(\d{2})\b',
           r'\b(\d{2})\s*[x×]\s*(\d{2})\s*cm\s*-\s*H\s*<=',
           r'compatible avec un matelas à langer[^.\n]{0,40}?\b(\d{2})\s*[x×]\s*(\d{2})\b',
           r'matelas (?:à langer )?compatible[^.\n]{0,40}?\b(\d{2})\s*[x×]\s*(\d{2})\b',
           r'dimensions utiles[^.\n]{0,60}?\b(\d{2})\s*[x×]\s*(\d{2})\b',
           r'(?:prévue pour|pour recevoir) un matelas à langer[^.\n]{0,40}?\b(\d{2})\s*[x×]\s*(\d{2})\b',
           r'matelas à langer de\s*(\d{2})\s*[x×]\s*(\d{2})\b']


def est_lit_combine(pid):
    """Lit avec commode et surface à langer accolées (lit combiné, « lit chambre évolutif commode »)."""
    return pid in items and type_meuble(pid) == 'lit' and (surface_propre(pid) or 'combine' in titre_n(pid))


def surface_langer(pid):
    """Dimensions de la surface à langer et preuve : fiche, plan relié, ou pièce du pack."""
    plan = PC['map'].get(str(pid)) or A_VALIDER.get(pid)
    sources = [(pid, 'description')] + ([(int(plan), f'description du plan {plan}')] if plan else []) + \
              [(p, f'description de la pièce {p}') for p in pieces(pid) if p in items and p != pid and
               (type_meuble(p) in ('commode', 'plan') or est_lit_combine(p))]
    for src, lab in sources:
        tx = texte(src)
        for motif in SURFACE:
            m = re.search(motif, tx, re.I)
            if m and 40 <= int(m.group(1)) <= 90 and 40 <= int(m.group(2)) <= 90:
                return taille(m.group(1), m.group(2)), lab
    return None, ''


def surface_integree(pid, vus=None):
    """Surface à langer qui fait partie du meuble (pas un plan vendu à part). Règle Sauthon : sauf mention dans le titre,
    le plan à langer n'est jamais inclus dans un duo ou un trio ; « commode à langer » seul ne suffit donc pas."""
    vus = (vus or set()) | {pid}
    t, tx = titre_n(pid), texte(pid)
    if re.search(r'dal integre|meuble a langer|combine', t):
        return True
    if 'intégré' in RAISON.get(pid, ''):
        return True
    for m in re.finditer(r'dispositif à langer (amovible )?(inclus|intégré)|avec dispositif à langer|plan à langer amovible|joues? du dispositif à langer', tx, re.I):
        debut, fin = tx.rfind('.', 0, m.start()) + 1, tx.find('.', m.end())
        phrase = tx[debut:fin if fin >= 0 else len(tx)]
        if not re.search(r'vendu(e|s)? séparément|en option|non (inclus|fourni)', phrase, re.I):
            return True
    return any(surface_integree(p, vus) for p in pieces(pid) if p in items and p not in vus and type_meuble(p) == 'commode')


def surface_propre(pid):
    """Dimensions de surface à langer écrites sur la fiche elle-même (pas sur un plan vendu à part)."""
    tx = texte(pid)
    for motif in SURFACE:
        m = re.search(motif, tx, re.I)
        if m and 40 <= int(m.group(1)) <= 90 and 40 <= int(m.group(2)) <= 90:
            return True
    return False


def regle_lit(pid, preuve):
    """Règle d'un matelas de lit : 'berceau', 'a_corriger' (titre et description en désaccord) ou 'taille'."""
    if type_meuble(pid) == 'berceau':
        return 'berceau'
    return 'a_corriger' if 'à corriger' in preuve else 'taille'


def matelas_langer(pid):
    """(matelas à langer, preuve, règle) ; règle : 'accessoire' (relié par Sauthon dans PrestaShop, taille compatible ou
    non indiquée), 'defaut' (surface 68x52 connue, matelas neutre), 'suppose' (surface non indiquée : 68x52 supposée),
    'boreale' (matelas des commodes Boréale, taille à confirmer)."""
    t = titre_n(pid)
    plan = PC['map'].get(str(pid))
    if 'boreale' in t and (plan or type_meuble(pid) == 'plan'):
        return MATELAS_BOREALE, 'matelas conçu pour les commodes Boréale (taille non indiquée : à confirmer)' + \
            (' + accessoire PrestaShop' if MATELAS_BOREALE in accessoires(pid) else ''), 'boreale'
    dim, preuve = surface_langer(pid)
    lies = [a for a in accessoires(pid) + (accessoires(int(plan)) if plan else []) if a in MATELAS_LANGER]
    if dim:
        comp = [a for a in lies if MATELAS_LANGER[a] == dim]
        if comp:
            return comp[0], f'surface {dim[0]}x{dim[1]} ({preuve}) + accessoire PrestaShop', 'accessoire'
        if dim == (68, 52):
            return MATELAS_LANGER_DEFAUT, f'surface {dim[0]}x{dim[1]} ({preuve}), matelas neutre par défaut', 'defaut'
        return None, f'aucun matelas {dim[0]}x{dim[1]} au catalogue', None
    comp = [a for a in lies if MATELAS_LANGER[a] in (None, (68, 52))]
    if comp:
        return comp[0], 'accessoire PrestaShop (dimensions de la surface non indiquées)', 'accessoire'
    return MATELAS_LANGER_DEFAUT, 'surface standard 68x52 supposée (non indiquée sur la fiche) : à confirmer', 'suppose'


# ---------------------------------------------------------------- trois lignes au plus (plan compris)
data, review = {}, {}
for pid in sorted(items):
    tm = type_meuble(pid)
    if not tm:
        continue
    plan = PC['map'].get(str(pid))
    notes, candidats = [], []
    integre = surface_integree(pid) or (tm == 'commode' and surface_propre(pid))
    couchage = tm in ('lit', 'berceau', 'duo', 'trio', 'duo_armoire')
    if couchage:
        if matelas_lit_inclus(pid):
            notes.append('matelas de lit déjà fourni')
        else:
            ml, som, pr = besoin_lit(pid)
            if ml:
                candidats.append({'id': ml, 'role': 'matelas_lit', 'preuve': pr, 'regle': regle_lit(pid, pr)})
                if som:
                    candidats.append({'id': som, 'role': 'sommier', 'preuve': 'description : sommier non fourni',
                                      'regle': 'sommier'})
            else:
                notes.append(f'matelas de lit : {pr}')
    lit_combine = est_lit_combine(pid) or (tm == 'duo_armoire' and any(est_lit_combine(p) for p in pieces(pid)))
    a_langer = tm in ('plan', 'pack') or lit_combine or (tm in ('commode', 'duo', 'trio', 'duo_armoire') and (bool(plan) or pid in A_VALIDER or integre))
    if a_langer:
        if matelas_langer_inclus(pid):
            notes.append('matelas à langer déjà fourni')
        else:
            mal, pr, regle = matelas_langer(pid)
            if mal:
                candidats.append({'id': mal, 'role': 'matelas_langer', 'regle': 'lit_combine' if lit_combine else regle,
                                  'preuve': pr + (' (lit combiné : règle à valider)' if lit_combine else '')})
            else:
                notes.append(f'matelas à langer : {pr}')
    retenus = candidats                  # toutes les propositions : encart.py filtre (PUBLIER) puis coupe à MAX_LIGNES
    if retenus:
        data[str(pid)] = [c['id'] for c in retenus]
    review[pid] = {'type': tm, 'plan': plan, 'integre': integre, 'lit_combine': lit_combine, 'a_langer': a_langer, 'lignes': retenus, 'notes': notes}

# ---------------------------------------------------------------- housses des matelas à langer (demande du 28/10)
# Sur la fiche d'un matelas à langer : la housse vendue à part, de la même collection et de la même couleur (ou reliée
# dans PrestaShop). Si le matelas a déjà sa housse (« + housse », « déhoussable »…), c'est une housse de rechange.
NOMS_COURTS.update({2815: 'Housse de matelas à langer plus 2 linges Esmée',
                    2816: 'Housse de matelas à langer plus 2 linges Promenons-nous'})
HOUSSES = [p for p in items if re.match(r'housse (de )?matelas a langer', titre_n(p))]
A_SA_HOUSSE = r'd[ée]houssable|housse (100 ?% ?)?coton|\b1 housse|[ée]quip[ée] de sa housse|avec (sa|une) housse|\+ ?housse'


def meme_couleur(a, b):
    return not (items[a]['c'] and items[b]['c']) or norm(items[a]['c']) == norm(items[b]['c'])


for pid in sorted(items):
    t = titre_n(pid)
    if not t.startswith('matelas a langer'):
        continue
    notes, retenus = [], []
    a_housse = bool(re.search(r'housse|dehoussable', t) or re.search(A_SA_HOUSSE, texte(pid), re.I))
    acc = accessoires(pid)
    fam = items[pid]['fam']
    cands = sorted([h for h in HOUSSES if fam and items[h]['fam'] == fam and meme_couleur(h, pid)], key=lambda h: (h not in acc, h))
    cands = cands or [a for a in acc if a in HOUSSES]
    if 'voyage' in t:
        notes.append('housse : matelas de voyage, pas de housse vendue à part')
    elif cands:
        preuve = ('même collection' if fam and items[cands[0]]['fam'] == fam else '') + \
                 (' + accessoire PrestaShop' if cands[0] in acc else '')
        retenus.append({'id': cands[0], 'role': 'housse_rechange' if a_housse else 'housse', 'preuve': preuve.strip(' +'),
                        'regle': 'housse'})
    elif a_housse:
        notes.append('housse déjà fournie avec le matelas')
    else:
        notes.append('housse : aucune housse de la même collection au catalogue')
    if retenus:
        data[str(pid)] = [c['id'] for c in retenus]
    review[pid] = {'type': 'matelas_langer', 'plan': None, 'integre': False, 'lit_combine': False, 'a_langer': False,
                   'lignes': retenus, 'notes': notes}

noms = {str(i): nom(i) for v in data.values() for i in v}
json.dump({'map': data, 'noms': noms}, open('matelas_data.json', 'w'), ensure_ascii=False, separators=(',', ':'))
json.dump({str(k): v for k, v in review.items()}, open('matelas_review.json', 'w'), ensure_ascii=False, indent=1)
if __name__ == '__main__':
    print('meubles examinés', len(review), dict(collections.Counter(r['type'] for r in review.values())))
    print('fiches avec au moins un matelas', len(data), '| lignes', sum(len(v) for v in data.values()))
    print('matelas proposés', collections.Counter(i for v in data.values() for i in v).most_common())
    print('notes', collections.Counter(re.sub(r'\d+', 'N', n)[:70] for r in review.values() for n in r['notes']).most_common(20))
