"""Versions espagnole et italienne des données de la balise « Variantes » : docs/variantes-es.json et variantes-it.json.

Lancé APRÈS verifier.py, qui vient de publier ../docs/variantes.json (version française contrôlée) : mêmes groupes et
mêmes compositions, dans le même ordre (la balise prend le 1er groupe qui contient la fiche), par identifiant de produit
PrestaShop, avec
  - l'adresse de chaque produit dans la langue : catégorie et fin d'adresse du lien du flux de la langue (rows-es.json,
    rows-it.json, écrits par flux_langues.py), même codage que donnees.py ; image : même identifiant qu'en français ;
  - les noms des sélecteurs, les valeurs et les compositions traduits (traductions.py), dans l'ordre français ;
  - « sw » (champ inconnu de la balise française, qui l'ignore) : index dans « v » des sélecteurs affichés en vignettes
    photo, que la balise française reconnaît à leur nom français (SELECTEURS_VIGNETTES).
Rien n'est recalculé à partir des titres ou des collections espagnols et italiens (traductions automatiques).

N'écrit aucun fichier français : seulement ../docs/variantes-<langue>.json et ../docs/status-langues.json.
« Pour compléter » n'a pas de version par langue : la balise lit pour toutes les langues pour-completer.json
(identifiants et rôles ; nom, prix et adresse sont lus en direct sur PrestaShop, dans la langue de la page).
status-langues.json liste aussi, pour information, les produits de l'encart absents, sans nom ou au titre provisoire
dans la langue, et les produits publiés dont le titre de la langue est encore le titre français.

Écarts par rapport au français, listés dans status-langues.json :
  - produit absent du flux de la langue, sans nom, au titre provisoire (« new », « copia de… » : copie PrestaShop pas
    encore traduite) ou dont l'adresse serait refusée par la balise (IT 3442 : « 3442-.html ») : retiré de cette langue ;
    un groupe ou une composition qui n'offre plus de choix n'est pas publié ;
  - texte sans traduction : le produit (ou le choix de composition) qui l'affiche est retiré de cette langue, le reste
    est publié ; deux valeurs d'un même sélecteur, deux sélecteurs d'un même groupe ou deux compositions traduits de la
    même façon : ce groupe ou cette composition n'est pas publié, le reste l'est.
Avertissement (e-mail) seulement pour ce qui est NOUVEAU par rapport à la dernière publication de la langue (« reference »
de status-langues.json) : un produit retiré, un texte sans traduction ou une traduction en double déjà signalés ne le
sont plus à chaque génération (IT 3039, 3442 : une seule fois).
Une langue dont le flux manque ou dont un contrôle échoue garde son fichier de la veille (les balises masquent les
données de plus de 7 jours, date « t »). La couverture minimale (90 % du français) ne compte que les produits perdus
par le flux de la langue (absents, sans nom, adresse refusée : signe d'un flux cassé) ; des textes sans traduction ou des
produits pas encore traduits dans PrestaShop (titre provisoire) ne bloquent pas toute la langue, sauf plus de 25 % des
produits du français au titre provisoire (MAX_PROVISOIRES : flux cassé, comptés comme perdus). Sortie en erreur, et
e-mail de GitHub par la dernière étape de regenerer.yml, si une langue est en erreur ou a de nouveaux avertissements ;
le français est déjà publié et ne dépend jamais de ce script.
"""
import collections, datetime, json, os, re, sys
from traductions import LANGUES, libelle_selecteur, traduire

DOCS = '../docs/'
SITE = 'https://www.sauthon.com/'
EAN_PREFIX = '3500760'                     # donnees.py ; la balise reconstruit « product-3500760 » + 6 chiffres
SELECTEURS_VIGNETTES = {'Couleur', 'Motif', 'Coloris', 'Modèle'}   # tag-gtm-variantes.html, isColor (noms français)
MIN_FLUX = 800                             # même seuil que flux.py et verifier.py
MIN_PART = 0.9                             # part minimale du français : produits reliés, groupes, fiches avec composition
MAX_PROVISOIRES = 0.25                     # au-delà (part des produits du français), titres provisoires = flux cassé
# Mêmes règles de format et mêmes plafonds que la balise et verifier.py : un fichier qu'elle refuserait n'est jamais
# publié (la version de la veille reste en ligne). Toujours fullmatch, jamais match avec « $ ».
RE_SEG = re.compile(r'[A-Za-z0-9_-]{1,200}')
RE_BAD = re.compile(r'[\x00-\x1f\x7f-\x9f\u200b-\u200f\u2028-\u202e\u2060-\u2069\ufeff<>@]|://|www\.', re.I)
MAX_DIMS, MAX_MEMBRES, MAX_VALEURS, MAX_OPTIONS = 6, 60, 30, 10
MAX_CARACTERES_VARIANTES = 300000
# titre PrestaShop provisoire d'un produit pas encore traduit : même idée que titresProvisoires de la balise de l'encart,
# un peu plus large (« nuevo », « nuovo », « copia de », « copia di » dans les deux langues)
RE_PROVISOIRE = re.compile(r'\s*(new|nuevo|nuovo)\s*([|–-]\s*sauthon\s*)?|\s*copia d[ei]\b.*', re.I | re.S)
# listes comparées à la dernière publication de la langue (avertissement seulement pour ce qui est nouveau)
REFERENCES = ('produits_retires', 'sans_traduction', 'collisions')


def longueur_js(s):
    """Longueur d'un texte vue par la balise (JavaScript compte en unités UTF-16)."""
    return len(s.encode('utf-16-le')) // 2


def est_id(n):
    return isinstance(n, int) and not isinstance(n, bool) and 0 < n < 10**7


def est_index(n, liste):
    return isinstance(n, int) and not isinstance(n, bool) and 0 <= n < len(liste)


def est_date(t):
    """Date de génération « t » (secondes depuis 1970), comme la teste la balise."""
    return isinstance(t, int) and not isinstance(t, bool) and t > 0


def est_txt(s):
    return isinstance(s, str) and 1 <= longueur_js(s) <= 40 and not RE_BAD.search(s)


def charger(chemin):
    return json.load(open(chemin)) if os.path.exists(chemin) else None


def ecrire(chemin, texte):
    """Écrit d'un seul coup (fichier temporaire puis renommage) : jamais de fichier à moitié écrit dans docs/."""
    tmp = os.path.basename(chemin) + '.tmp'
    with open(tmp, 'w', encoding='utf-8') as f:
        f.write(texte)
    os.replace(tmp, chemin)


def date(t):
    return datetime.datetime.fromtimestamp(t, datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')


# ------------------------------------------------------------------ produits de la langue
def adresses(L, rows):
    """({id: (catégorie, fin d'adresse)} des produits publiables en langue L, {id: raison} des autres, {id: lien},
    {id: (catégorie, fin d'adresse)} des produits écartés pour leur seul titre provisoire : pas encore traduits dans
    PrestaShop, ils ne comptent pas comme une perte du flux dans la couverture)."""
    ok, ecartes, liens, provisoires = {}, {}, {}, {}
    motif = re.compile(re.escape(f'{SITE}{L}/') + r'([^/]+)/(\d+)-([^/]*)\.html')
    for r in rows:
        if not re.fullmatch(r'\d{1,7}', str(r.get('id', ''))):
            continue
        pid, lien = int(r['id']), r.get('link') or ''
        if pid in liens:                          # produit en double dans le flux : gardé seulement si même adresse
            if lien != liens[pid]:
                ok.pop(pid, None)
                provisoires.pop(pid, None)
                ecartes[pid] = 'deux adresses dans le flux'
            continue
        liens[pid] = lien
        m = motif.fullmatch(lien)
        titre = (r.get('t') or '').strip()
        if not titre:
            ecartes[pid] = 'sans nom dans cette langue'
        elif not m or int(m.group(2)) != pid:
            ecartes[pid] = 'adresse illisible'
        elif not (RE_SEG.fullmatch(m.group(1)) and RE_SEG.fullmatch(m.group(3))):
            ecartes[pid] = 'adresse refusée par la balise (caractère hors [A-Za-z0-9_-] ou fin vide)'
        elif RE_PROVISOIRE.fullmatch(titre):
            ecartes[pid] = 'titre provisoire dans cette langue (« new », « copia de… »)'
            provisoires[pid] = (m.group(1), m.group(3))
        else:
            ok[pid] = (m.group(1), m.group(3))
    return ok, ecartes, liens, provisoires


# ------------------------------------------------------------------ données de la balise
def sans_traduire(s, L):
    return s


def sans_traduire_selecteur(fr, valeurs_fr, L):
    return fr


def construire(FR, L, ok, traduire_=traduire, libelle_=libelle_selecteur):
    """Données de la langue L, même format que variantes.json (plus « sw » et « lang »), et le détail des écarts.
    origine : pour chaque groupe publié, (index du groupe français, dimensions françaises gardées) (contrôles).
    Avec traduire_=sans_traduire, libelle_=sans_traduire_selecteur : le français réduit aux produits publiables de la
    langue, qui mesure ce que le flux de la langue fait perdre (couverture), sans les textes sans traduction."""
    V, vindex = [], {}

    def vid(s, vignette=False):
        # un nom de sélecteur en vignettes a sa propre entrée : « sw » (index) ne peut pas désigner aussi un sélecteur
        # en boutons ou une valeur qui porterait le même texte
        k = ('sw', s) if vignette else s
        if k not in vindex:
            vindex[k] = len(V)
            V.append(s)
        return vindex[k]

    manque = set()                       # textes français sans traduction utilisable
    non_publies = collections.Counter()  # groupes et compositions non publiés, par raison
    retires = collections.Counter()      # produits retirés d'un groupe, choix retirés d'une composition, par raison
    collisions = set()                   # groupes et compositions non publiés pour une traduction en double

    def tr(s):
        t = traduire_(s, L)
        if t is None or not est_txt(t):
            manque.add(s)
            return None
        return t

    groupes, origine, vignettes = [], [], set()
    for gi, (labs, orders, mem) in enumerate(FR['g']):
        garde = []
        for m in mem:
            if m[0] not in ok:
                retires['absent, sans nom, titre provisoire ou adresse refusée'] += 1
            elif any(tr(FR['v'][v]) is None for v in m[1:]):
                retires['valeur sans traduction'] += 1
            else:
                garde.append(m)
        if len(garde) < 2:
            non_publies['groupe de moins de 2 produits dans cette langue'] += 1
            continue
        # dimensions du français ; seule une dimension réduite à une valeur PAR les produits retirés disparaît (une
        # dimension déjà à une valeur en français reste, comme sur le site français)
        dims = [k for k in range(len(labs)) if len({m[k + 1] for m in garde}) > 1 or len({m[k + 1] for m in mem}) == 1]
        if not dims or len({tuple(m[k + 1] for k in dims) for m in garde}) < len(garde):
            non_publies['groupe sans sélecteur ou combinaisons en double'] += 1
            continue
        utiles = {k: [v for v in orders[k] if any(m[k + 1] == v for m in garde)] for k in dims}
        noms_dims = {k: libelle_(FR['v'][labs[k]], [FR['v'][v] for v in utiles[k]], L) for k in dims}
        if any(n is None or not est_txt(n) for n in noms_dims.values()):
            manque.update(FR['v'][labs[k]] for k, n in noms_dims.items() if n is None or not est_txt(n))
            non_publies['nom de sélecteur sans traduction'] += 1
            continue
        if len(set(noms_dims.values())) < len(dims):
            non_publies['deux sélecteurs traduits de la même façon'] += 1
            collisions.add(f'groupe du produit {garde[0][0]} : sélecteurs {sorted(set(noms_dims.values()))}')
            continue
        doubles = sorted({t for k in dims
                          for t, n in collections.Counter(tr(FR['v'][v]) for v in utiles[k]).items() if n > 1})
        if doubles:
            non_publies['deux valeurs traduites de la même façon'] += 1
            collisions.add(f'groupe du produit {garde[0][0]} : valeurs {doubles}')
            continue
        g0 = [vid(noms_dims[k], FR['v'][labs[k]] in SELECTEURS_VIGNETTES) for k in dims]
        vignettes |= {i for k, i in zip(dims, g0) if FR['v'][labs[k]] in SELECTEURS_VIGNETTES}
        g1 = [[vid(tr(FR['v'][v])) for v in utiles[k]] for k in dims]       # ordre français (ORDRE_VALEURS, tailles…)
        g2 = [[m[0]] + [vid(tr(FR['v'][m[k + 1]])) for k in dims] for m in garde]
        groupes.append([g0, g1, g2])
        origine.append((gi, dims))

    Lb, lindex, xl, xindex, x = [], {}, [], {}, {}
    for k, i in FR['x'].items():
        if int(k) not in ok:
            non_publies['composition d\'un produit absent, sans nom, au titre provisoire ou à l\'adresse refusée'] += 1
            continue
        opts = []
        for a, t in FR['xl'][i]:
            lab = tr(FR['l'][a]) if t in ok else None
            if lab is None:
                retires['choix de composition absent ou sans traduction'] += 1
            else:
                opts.append((lab, t))
        if len(opts) < 2 or int(k) not in [t for _, t in opts]:
            non_publies['composition de moins de 2 choix dans cette langue'] += 1
            continue
        if len({lab for lab, _ in opts}) < len(opts):
            non_publies['deux compositions traduites de la même façon'] += 1
            collisions.add(f'composition du produit {k} : '
                           f'{sorted(lab for lab, n in collections.Counter(lab for lab, _ in opts).items() if n > 1)}')
            continue
        enc = []
        for lab, t in opts:
            if lab not in lindex:
                lindex[lab] = len(Lb)
                Lb.append(lab)
            enc.append([lindex[lab], t])
        cle_ = json.dumps(enc)
        if cle_ not in xindex:
            xindex[cle_] = len(xl)
            xl.append(enc)
        x[k] = xindex[cle_]

    utilises = {m[0] for g in groupes for m in g[2]} | {t for lst in xl for _, t in lst} | {int(k) for k in x}
    cats, cindex, p = [], {}, {}
    for pid in sorted(utilises):                     # même ordre que donnees.py
        cat, fin = ok[pid]
        m = re.fullmatch(rf'product-{EAN_PREFIX}(\d{{6}})', fin)
        if cat not in cindex:
            cindex[cat] = len(cats)
            cats.append(cat)
        # codage compact de donnees.py, sauf « 000000 » : 0 serait refusé par la balise, la fin d'adresse reste en clair
        p[str(pid)] = [cindex[cat], int(m.group(1)) if m and int(m.group(1)) else fin, FR['p'][str(pid)][2]]
    data = {'c': cats, 'v': V, 'l': Lb, 'p': p, 'g': groupes, 'x': x, 'xl': xl, 'sw': sorted(vignettes), 'lang': L,
            't': FR.get('t')}
    return data, origine, {'sans_traduction': sorted(manque), 'collisions': sorted(collisions),
                           'non_publies': dict(non_publies), 'choix_retires': dict(retires)}


# ------------------------------------------------------------------ contrôles avant publication
def hors_format(D):
    """Ce que refuserait valid() de la balise (tag-gtm-variantes.html), qui ignore alors tout le fichier ; « sw » :
    contrôle de la balise multilingue."""
    if not (all(isinstance(D.get(k), list) for k in ('c', 'v', 'l', 'g', 'xl', 'sw'))
            and all(isinstance(D.get(k), dict) for k in ('p', 'x'))):
        return ['structure']
    pb = [f'catégorie {c!r}' for c in D['c'] if not (isinstance(c, str) and RE_SEG.fullmatch(c))]
    pb += [f'texte {t!r}' for t in D['v'] + D['l'] if not est_txt(t)]
    pb += [f'produit {k}' for k, q in D['p'].items() if not (
        re.fullmatch(r'\d{1,7}', k) and isinstance(q, list) and len(q) == 3 and est_index(q[0], D['c'])
        and (est_id(q[1]) or (isinstance(q[1], str) and RE_SEG.fullmatch(q[1]))) and (q[2] == 0 or est_id(q[2])))]
    for gi, g in enumerate(D['g']):
        if not (isinstance(g, list) and len(g) == 3 and all(isinstance(e, list) for e in g)
                and len(g[0]) >= 1 and len(g[1]) == len(g[0]) and all(est_index(i, D['v']) for i in g[0])
                and all(isinstance(o, list) and all(est_index(i, D['v']) for i in o) for o in g[1])
                and all(isinstance(m, list) and len(m) == len(g[0]) + 1 and est_id(m[0]) and str(m[0]) in D['p']
                        and all(est_index(i, D['v']) for i in m[1:]) for m in g[2])):
            pb.append(f'groupe {gi}')
    for li, lst in enumerate(D['xl']):
        if not (isinstance(lst, list) and all(isinstance(o, list) and len(o) == 2 and est_index(o[0], D['l'])
                                              and est_id(o[1]) and str(o[1]) in D['p'] for o in lst)):
            pb.append(f'composition {li}')
    pb += [f'fiche {k}' for k, i in D['x'].items() if not (re.fullmatch(r'\d{1,7}', k) and est_index(i, D['xl']))]
    pb += [f'sw {i}' for i in D['sw'] if not est_index(i, D['v'])]
    if not est_date(D.get('t')):
        pb.append('date « t »')
    return pb


def url_balise(D, L, pid):
    """Adresse construite exactement comme la balise (url() de tag-gtm-variantes.html, base_url + langue)."""
    q = D['p'][str(pid)]
    fin = f'product-{EAN_PREFIX}{q[1]:06d}' if isinstance(q[1], int) else q[1]
    return f'{SITE}{L}/{D["c"][q[0]]}/{pid}-{fin}.html'


def controler(D, origine, FR, L, liens, base):
    """Erreurs qui empêchent la publication de la langue L (la version de la veille reste en ligne).
    base : construire(..., sans_traduire, sans_traduire_selecteur), pour la couverture (pertes dues au flux seulement)."""
    pb = hors_format(D)
    if pb:
        return [f'Données hors format (la balise refuserait tout le fichier) : {pb[:10]}']
    err = []
    if D.get('lang') != L:
        err.append(f'Champ « lang » différent de {L!r} (la balise refuserait le fichier).')
    if [i for i, g in enumerate(D['g']) if len(g[0]) > MAX_DIMS or len(g[2]) > MAX_MEMBRES
            or any(len(o) > MAX_VALEURS for o in g[1])]:
        err.append('Groupes hors plafonds (ignorés par la balise).')
    if any(len(lst) > MAX_OPTIONS for lst in D['xl']):
        err.append('Composition hors plafond (ignorée par la balise).')
    taille = longueur_js(json.dumps(D, ensure_ascii=False, separators=(',', ':')))
    if taille > MAX_CARACTERES_VARIANTES:
        err.append(f'Fichier de {taille} caractères : la balise refuse au-delà de {MAX_CARACTERES_VARIANTES}.')
    if D['t'] != FR.get('t'):
        err.append('Date « t » différente de celle du fichier français.')
    refs = {m[0] for g in D['g'] for m in g[2]} | {t for lst in D['xl'] for _, t in lst} | {int(k) for k in D['x']}
    if refs != {int(k) for k in D['p']}:
        err.append('Produits référencés sans adresse, ou adresses inutiles.')
    # adresses : celle que construit la balise = lien du flux de la langue ; image : celle du français
    faux = [k for k in D['p'] if url_balise(D, L, int(k)) != liens.get(int(k)) or D['p'][k][2] != FR['p'][k][2]]
    if faux:
        err.append(f'Adresses ou images différentes du flux de la langue : {faux[:10]}')
    # mêmes groupes que le français : chaque produit affiche la traduction de ses valeurs françaises, le groupe garde
    # l'ordre français des produits et des valeurs, les vignettes photo sont celles du français
    sw = set(D['sw'])
    for (gi, dims), (g0, g1, g2) in zip(origine, D['g']):
        labs, orders, mem = FR['g'][gi]
        fr_de = {m[0]: m for m in mem}
        ids = [m[0] for m in g2]
        if len(dims) != len(g0) or ids != [m[0] for m in mem if m[0] in set(ids)]:
            err.append(f'Groupe du produit {ids[0]} sans équivalent français.')
            continue
        utiles = [[FR['v'][v] for v in orders[k] if any(fr_de[i][k + 1] == v for i in ids)] for k in dims]
        attendu = [[traduire(FR['v'][fr_de[i][k + 1]], L) for k in dims] for i in ids]
        if ([[D['v'][v] for v in m[1:]] for m in g2] != attendu
                or [[D['v'][v] for v in o] for o in g1] != [[traduire(v, L) for v in u] for u in utiles]
                or [D['v'][i] for i in g0] != [libelle_selecteur(FR['v'][labs[k]], u, L) for k, u in zip(dims, utiles)]
                or [i in sw for i in g0] != [FR['v'][labs[k]] in SELECTEURS_VIGNETTES for k in dims]):
            err.append(f'Groupe du produit {ids[0]} : sélecteurs, valeurs, ordre ou vignettes différents du français.')
        if any(len({D['v'][v] for v in o}) < len(o) for o in g1) or len({tuple(m[1:]) for m in g2}) < len(g2):
            err.append(f'Groupe du produit {ids[0]} : valeurs ou combinaisons en double.')
    if len(origine) != len(D['g']) or len({gi for gi, _ in origine}) != len(origine):
        err.append('Groupes sans équivalent français.')
    for k, i in D['x'].items():
        fr_opts = [(FR['l'][a], t) for a, t in FR['xl'][FR['x'][k]]] if k in FR['x'] else []
        opts = [(D['l'][a], t) for a, t in D['xl'][i]]
        if opts != [(traduire(lab, L), t) for lab, t in fr_opts if t in {t_ for _, t_ in opts}] \
                or int(k) not in [t for _, t in opts]:
            err.append(f'Composition du produit {k} différente du français.')
    if [i for i in sw if i not in {i for g in D['g'] for i in g[0]}]:
        err.append('« sw » désigne autre chose qu\'un nom de sélecteur.')
    # couverture : une langue dont le flux fait perdre beaucoup par rapport au français trahit un flux cassé (les textes
    # sans traduction, déjà signalés, n'en sont pas : le reste de la langue est publié)
    for cle_, lab in (('p', 'produits reliés'), ('g', 'groupes'), ('x', 'fiches avec composition')):
        if len(base[cle_]) < MIN_PART * len(FR[cle_]):
            err.append(f'Flux de la langue : trop peu de {lab} par rapport au français : {len(base[cle_])} / '
                       f'{len(FR[cle_])}.')
    return err[:20]


# ------------------------------------------------------------------ une langue
def _liste(x):
    """Liste (ou dict) lue dans l'état de la veille ; autre chose (état abîmé) : liste vide."""
    return x if isinstance(x, (list, dict)) else []


def publier(FR, PC, L, st, avant, titres_fr):
    """Calcule, contrôle et écrit variantes-<L>.json ; remplit st (statut de la langue dans status-langues.json).
    avant : statut de la langue à la génération précédente ; sa « reference » (listes de la dernière publication de la
    langue) dit ce qui est nouveau : avertissement seulement pour ce qui est nouveau.
    titres_fr : {id: titre français} (rows.json), pour information (titres restés en français dans la langue)."""
    ref = avant.get('reference') if isinstance(avant.get('reference'), dict) else {}
    rows = charger(f'rows-{L}.json')
    if rows is None:
        st['erreurs'].append(f'Flux {L} absent (téléchargement en échec, voir flux_langues.py) : version de la veille '
                             f'gardée (s\'il y en a une).')
        return
    if len(rows) < MIN_FLUX:
        st['erreurs'].append(f'Flux {L} trop court : {len(rows)} produits (minimum {MIN_FLUX}) : version de la veille '
                             f'gardée (s\'il y en a une).')
        return
    ok, ecartes, liens, provisoires = adresses(L, rows)
    D, origine, detail = construire(FR, L, ok)
    fr_ids = {int(k) for k in FR['p']}
    # couverture : pertes dues au flux seulement (ni textes sans traduction, ni produits pas encore traduits) ; au-delà de
    # MAX_PROVISOIRES des produits du français, des titres provisoires trahissent un flux cassé : comptés comme perdus
    prov = set(provisoires) & fr_ids
    trop_de_provisoires = len(prov) > MAX_PROVISOIRES * len(fr_ids)
    base = construire(FR, L, ok if trop_de_provisoires else {**ok, **provisoires}, sans_traduire,
                      sans_traduire_selecteur)[0]
    retires_fr = {str(k): v for k, v in sorted(ecartes.items()) if k in fr_ids}
    retires_fr.update({str(k): 'absent du flux de la langue' for k in sorted(fr_ids - set(liens))})
    titres = {int(r['id']): (r.get('t') or '').strip() for r in rows if re.fullmatch(r'\d{1,7}', str(r.get('id', '')))}
    st.update(produits_flux=len(rows), produits_relies=len(D['p']), groupes_variantes=len(D['g']),
              fiches_composition=len(D['x']),
              francais={'produits_relies': len(FR['p']), 'groupes_variantes': len(FR['g']),
                        'fiches_composition': len(FR['x'])},
              produits_retires=dict(sorted(retires_fr.items(), key=lambda kv: int(kv[0]))), **detail)
    # pour information (pas d'avertissement : un nom propre peut s'écrire pareil) : produits publiés dont le titre de la
    # langue est encore exactement le titre français (« Commode 4 tiroirs CHOCO »), à traduire dans PrestaShop.
    # Informations seulement : un rows.json ou un pour-completer.json d'un autre format ne bloque jamais la langue.
    try:
        st['titres_identiques_au_francais'] = [k for k in sorted(D['p'], key=int)
                                               if (titres_fr.get(int(k)) or '').strip() == titres.get(int(k)) != '']
    except Exception as e:
        st['titres_identiques_au_francais'] = f'illisible ({type(e).__name__})'
    if PC:   # pour information : l'encart lit en direct le nom de ces produits, absent ou provisoire dans la langue
        try:
            ids = {int(k) for k in PC.get('l', {})} | {x_[0] for v in PC.get('l', {}).values() for x_ in v} | \
                  {int(k) for k in PC.get('map', {})} | {int(v) for v in PC.get('map', {}).values()}
            st['encart_produits_a_corriger'] = {
                str(i): 'absent du flux' if i not in titres else 'sans nom' if not titres[i] else 'titre provisoire'
                for i in sorted(ids) if i not in titres or not titres[i] or RE_PROVISOIRE.fullmatch(titres[i])}
        except Exception as e:
            st['encart_produits_a_corriger'] = f'illisible ({type(e).__name__})'
    nouveaux_textes = sorted(set(detail['sans_traduction']) - set(_liste(ref.get('sans_traduction'))))
    if nouveaux_textes:
        st['avertissements'].append(f'{len(nouveaux_textes)} nouveaux textes sans traduction (traductions.py) : '
                                    f'{nouveaux_textes[:10]} ; les produits ou choix qui les affichent sont retirés de '
                                    f'cette langue, le reste est publié.')
    nouvelles_collisions = sorted(set(detail['collisions']) - set(_liste(ref.get('collisions'))))
    if nouvelles_collisions:
        st['avertissements'].append(f'Traduction en double (traductions.py), non publié dans cette langue : '
                                    f'{nouvelles_collisions[:10]}.')
    nouveaux = sorted(set(retires_fr) - set(_liste(ref.get('produits_retires'))), key=int)
    if nouveaux:
        quand = 'depuis sa dernière publication' if 'produits_retires' in ref else '(1re génération de cette langue)'
        st['avertissements'].append(f'{len(nouveaux)} produits retirés de cette langue {quand} (absents, sans nom, '
                                    f'titre provisoire ou adresse refusée, détail dans « produits_retires ») : '
                                    f'{nouveaux[:10]}.')
    err = controler(D, origine, FR, L, liens, base)
    if err:
        if trop_de_provisoires:
            err.insert(0, f'{len(prov)} produits du français sur {len(fr_ids)} au titre provisoire dans cette langue '
                          f'(plus de {MAX_PROVISOIRES * 100:.0f} %) : comptés comme perdus par le flux.')
        st['erreurs'] += [f'variantes-{L}.json : {e}' for e in err]
        return
    ecrire(f'{DOCS}variantes-{L}.json', json.dumps(D, ensure_ascii=False, separators=(',', ':')))
    st['publie'] = True


def lire(chemin, defaut):
    """Fichier d'information (état de la veille, liste de l'encart, flux français) : illisible = défaut, jamais d'arrêt
    (sinon status-langues.json ne serait jamais réécrit et l'arrêt se répéterait chaque nuit)."""
    try:
        x = charger(chemin)
    except Exception:
        return defaut
    return x if isinstance(x, type(defaut)) else defaut


if __name__ == '__main__':
    FR = json.load(open(DOCS + 'variantes.json'))          # version française que verifier.py vient de publier
    PC = lire(DOCS + 'pour-completer.json', {})
    titres_fr = {int(r['id']): r.get('t') or '' for r in lire('rows.json', [])
                 if isinstance(r, dict) and re.fullmatch(r'\d{1,7}', str(r.get('id', '')))}
    precedent = lire(DOCS + 'status-langues.json', {}).get('langues')
    precedent = precedent if isinstance(precedent, dict) else {}
    statut = {'genere_le': datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
              't': FR.get('t'), 'statut': 'ok', 'langues': {}}
    for L in LANGUES:
        st = statut['langues'][L] = {'statut': 'ok', 'publie': False, 'erreurs': [], 'avertissements': []}
        avant = precedent.get(L) if isinstance(precedent.get(L), dict) else {}
        try:
            publier(FR, PC, L, st, avant, titres_fr)
        except Exception as e:          # erreur de programme : cette langue garde sa veille, les autres continuent
            st['erreurs'].append(f'Erreur du générateur : {type(e).__name__} : {e}'[:300])
        # listes de la dernière publication : celles du jour si la langue est publiée, sinon celles d'avant (un produit
        # retiré pendant une nuit en panne sera signalé la nuit où la langue sera de nouveau publiée)
        st['reference'] = ({k: st.get(k, [] if k != 'produits_retires' else {}) for k in REFERENCES} if st['publie']
                           else avant.get('reference') if isinstance(avant.get('reference'), dict) else {})
        st['statut'] = 'erreur' if st['erreurs'] else 'avertissement' if st['avertissements'] else 'ok'
        en_ligne = lire(f'{DOCS}variantes-{L}.json', {})
        try:     # information seulement : une date hors calendrier n'empêche pas d'écrire l'état
            st['version_en_ligne'] = date(en_ligne['t']) if est_date(en_ligne.get('t')) else None
        except (OverflowError, OSError, ValueError):
            st['version_en_ligne'] = None
    statut['statut'] = 'erreur' if any(s['statut'] == 'erreur' for s in statut['langues'].values()) else \
        'avertissement' if any(s['statut'] != 'ok' for s in statut['langues'].values()) else 'ok'
    ecrire(DOCS + 'status-langues.json', json.dumps(statut, ensure_ascii=False, indent=2))
    for L, s in statut['langues'].items():
        print(f'{L} : {s["statut"]}, ' + (f'publié | produits {s["produits_relies"]} | groupes {s["groupes_variantes"]} | '
              f'compositions {s["fiches_composition"]} | retirés {len(s["produits_retires"])} | sans traduction '
              f'{len(s["sans_traduction"])}' if s['publie'] else f'version en ligne gardée ({s["version_en_ligne"] or "aucune"})'))
        for e in s['erreurs'] + s['avertissements']:
            print('   ', e)
    # étape « continue-on-error » de regenerer.yml : le français est publié quand même ; sortie en erreur = e-mail
    if statut['statut'] != 'ok':
        sys.exit(1)
