"""Regroupement des produits Sauthon en variantes (couleur, taille, autres) + composition (commode / duo / trio)."""
import json, re, unicodedata, collections

rows = json.load(open('rows.json'))
BASE = 'https://www.sauthon.com/fr/'


def norm(s):
    s = unicodedata.normalize('NFD', s.lower())
    s = ''.join(ch for ch in s if unicodedata.category(ch) != 'Mn')
    s = s.replace('&', ' et ')
    s = re.sub(r"[’'`]", ' ', s)
    return re.sub(r'\s+', ' ', s).strip()


# ---------- Familles ----------
COLLECTION_VARIANT = {
    'UNI ECRU': ('UNI', 'Vanilla'), 'UNI PETALE': ('UNI', 'Pétale'), 'UNI SAUGE': ('UNI', 'Sauge'),
    'UNI TERRACOTTA': ('UNI', 'Terracotta'),
    'ORIGINAL BLANC CRISTAL': ('ORIGINAL', 'Blanc cristal'), 'ORIGINAL BLEU AQUA': ('ORIGINAL', 'Bleu aqua'),
    'ORIGINAL BLEU SAPHIR': ('ORIGINAL', 'Bleu saphir'), 'ORIGINAL JAUNE TOPAZE': ('ORIGINAL', 'Jaune topaze'),
    'ORIGINAL ROSE QUARTZ': ('ORIGINAL', 'Rose quartz'),
    'LILYGREY': ('LILY', 'Gris'), 'LILYMINT': ('LILY', 'Mint'), 'LILYPOUDREE': ('LILY', 'Rose poudré'),
    'BOREALE BLEU NUIT': ('BOREALE', 'Bleu nuit'), 'BOREALE CORAIL': ('BOREALE', 'Corail'),
    'BOREALE GRIS VOLCAN': ('BOREALE', 'Gris volcan'),
    'ACCESS BOIS': ('ACCESS', 'Bois'), 'ACCESS BOIS BLANC': ('ACCESS', 'Bois blanc'),
    'LOFTBLANC': ('LOFT', 'Blanc'), 'LOFTBOIS': ('LOFT', 'Bois'),
    'SCANDI GRIS': ('SCANDI', 'Gris'), 'SCANDI NATUREL': ('SCANDI', 'Naturel'),
    'SMILE': ('SMILE', 'Hêtre cendré'), 'SMILE CHENE SILEX': ('SMILE', 'Chêne silex'),
    'UP CHENE DORE': ('UP', 'Chêne doré'), 'UP CHENE SILEX': ('UP', 'Chêne silex'),
    'PALOMA': ('PALOMA', 'Blanc'), 'PALOMA BOIS': ('PALOMA', 'Bois'),
    'PETIT COEUR': ('PETIT', 'Petit Coeur'), 'PETIT NUAGE': ('PETIT', 'Petit Nuage'),
    'PETIT SOLEIL': ('PETIT', 'Petit Soleil'),
    'PURE BLANC': ('PURE', 'Blanc'), 'PURE BLANC ET SILEX': ('PURE', 'Blanc et silex'),
    'GALOPIN BLANC': ('GALOPIN', 'Blanc'),
}
FAMILY_ALIAS = {'MISTER BOUH': 'MISTERBOUH', 'MOKKA': 'MOKKA', 'LEOPARD': 'LEOPARD'}
MOTIF_FAMILIES = {'PETIT'}
# mots de famille à retirer des titres
FAMILY_WORDS = {
    'MISTERBOUH': ['mister bouh'], 'LILY': ['lily grey', 'lily mint', 'lily poudree', 'mintlily', 'lily'],
    'MISSFLEURDELUNE': ['miss fleur de lune'], 'CHAOCHAO': ['chao chao'], 'BLUEBALEINE': ['blue baleine'],
    'HELLOTEXTILE': ['hello'], 'LAZARE': ['new lazare', 'lazare'], 'PROMENONSNOUS': ['promenons nous', 'promenons-nous'],
    'BABYSAILOR': ['baby sailor'], 'ORIGINAL': ['sauthon original'], 'ELEONOREKAKI': ['eleonore kaki', 'eleonore'],
    'PLUCHEETPOMPON': ['pluche et pompon'], 'PETIT': ['petit coeur', 'petit nuage', 'petit soleil'],
    'UNI': ['uni'], 'NOVA': ['nova colors', 'nova'], 'BOREALE': ['boreale'], 'ACCESS': ['access bois blanc', 'access bois', 'access'],
    'SCANDI': ['scandi'], 'SMILE': ['smile'], 'UP': ['up'], 'LOFT': ['loft'], 'PALOMA': ['paloma bois', 'paloma'],
    'GALOPIN': ['galopin'], 'PURE': ['pure'], 'MYLOVE': ['my love'], 'ILOTBEBE': ['ilot bebe'],
}
TITLE_FAMILIES = ['sunlight', 'seventies', 'basic', 'arty', 'camille', 'galopin', 'bambin', 'boreale', 'eclipse',
                  'orsino', 'esmee', 'botanica']

# ---------- Attributs ----------
COLORS = [
    ('decor bois chene sepia', 'Chêne sépia'), ('chene sepia', 'Chêne sépia'), ('blanc cristal', 'Blanc cristal'),
    ('bleu aqua', 'Bleu aqua'), ('bleu saphir', 'Bleu saphir'), ('jaune topaze', 'Jaune topaze'),
    ('rose quartz', 'Rose quartz'), ('bleu nuit', 'Bleu nuit'), ('gris volcan', 'Gris volcan'),
    ('chene dore', 'Chêne doré'), ('chene silex', 'Chêne silex'), ('argile douce', 'Argile douce'),
    ('blanc lin', 'Blanc lin'), ('bois blanc', 'Bois blanc'), ('blanc bois', 'Blanc bois'), ('dark grey', 'Gris foncé'),
    ('gris clair', 'Gris clair'), ('gris fonce', 'Gris foncé'),
    ('blanc/bleu marine', 'Blanc / bleu marine'), ('bleu marine', 'Bleu marine'), ('jaune rose', 'Jaune rose'),
    ('hetre cendre', 'Hêtre cendré'), ('rose poudree', 'Rose poudré'),
    ('blanc gris', 'Blanc / gris'), ('blanc jaune', 'Blanc / jaune'), ('blanc noir', 'Blanc / noir'),
    ('blanc rose', 'Blanc / rose'), ('blanc bleu', 'Blanc / bleu'), ('blanc beige', 'Blanc / beige'),
    ('blanc turquoise', 'Blanc / turquoise'), ('blanc-ours', 'Blanc'),
    ('sauge', 'Sauge'), ('terracotta', 'Terracotta'), ('vanille', 'Vanille'), ('vanilla', 'Vanilla'),
    ('ecrue', 'Écru'), ('ecru', 'Écru'), ('creme', 'Crème'), ('petale', 'Pétale'), ('corail', 'Corail'),
    ('tilleul', 'Tilleul'), ('caramel', 'Caramel'), ('kaki', 'Kaki'), ('naturel', 'Naturel'), ('mint', 'Mint'),
    ('grey', 'Gris'), ('gris', 'Gris'), ('poudree', 'Rose poudré'), ('rose', 'Rose'), ('bleu', 'Bleu'),
    ('jaune', 'Jaune'), ('vertes', 'Vert'), ('verte', 'Vert'), ('vert', 'Vert'), ('nude', 'Nude'), ('noir', 'Noir'),
    ('beige', 'Beige'), ('blanche', 'Blanc'), ('blanc', 'Blanc'), ('bois', 'Bois'), ('moutarde', 'Moutarde'),
    ('figue', 'Figue'), ('taupe', 'Taupe'), ('ocre', 'Ocre'), ('camel', 'Camel'),
]
SIZE_PATTERNS = [
    (r'\b(\d{2,3})\s*x\s*(\d{2,3})(?:\s*x\s*\d+(?:[.,]\d+)?)?\s*(?:cm)?\b', 'dim'),
    (r'\b(\d{1,2})\s*-\s*(\d{1,2})\s*m(?:ois)?\b\.?', 'range_m'),
    (r'\b(\d{1,2})\s*-\s*(\d{1,2})\s*ans\b', 'range_a'),
    (r'\b(\d{1,2})\s*mois', 'mois'),
    (r'\b(\d{1,2})\s*ans\b', 'ans'),
    (r'\bnaissance\b', 'naiss'),
    (r'\b(petit|grand) modele\b', 'modele'),
]
# autres dimensions : (clé, libellé, [(motif, valeur)], valeur par défaut si absent)
FEATURES = [
    ('forme', 'Forme', [(r'\bovales?\b', 'Ovale'), (r'\brectangulaires?\b', 'Rectangulaire')], None),
    ('col', 'Col', [(r'\bsans col\b', 'Sans col'), (r'\b(avec )?col\b', 'Avec col')], 'Sans col'),
    ('manches', 'Manches', [(r'\bmanches courtes\b', 'Courtes')], 'Longues'),
    ('saison', 'Saison', [(r'\bete\b', 'Été'), (r'\bouatinee?s?\b|\bhiver\b', 'Hiver (ouatinée)')], None),
]
DIM_LABELS = {'c': 'Couleur', 's': 'Taille', 'forme': 'Forme', 'col': 'Col', 'manches': 'Manches', 'saison': 'Saison'}
SIZE_ORDER = ['Naissance', '1 mois', '0-3 mois', '3 mois', '0-6 mois', '3-6 mois', '6 mois', '6-18 mois', '6-24 mois',
              '9 mois', '12 mois', '18 mois', '24 mois', 'Petit modèle', 'Grand modèle']
FILLER = {'taille', 'version', 'de', 'en', 'et', 'le', 'la', 'les', 'du', 'des', 'avec', 'pour', 'cm', 'sauthon', 'new',
          'a', 'au', 'x2'}

# ---------- Corrections manuelles ----------
MERGES = [  # (ids, commentaire)
    ([3383, 3385, 3384], 'Armoire Tokyo : la blanche n’a pas de couleur dans son titre'),
    ([2099, 2098, 3272, 3273, 3271], 'Commode Seventies : même modèle, titres différents selon le coloris'),
    ([3171, 3172], 'Trio Seventies 120x60 (titre 3172 : « commode + commode »)'),
    ([2470, 2468, 2469], 'Commode Galopin : titres différents selon le coloris'),
    ([2442, 2441], 'Commode Bambin : titres différents selon le coloris'),
    ([2028, 2062], 'Trousse de toilette Lily'),
    ([3654, 3657], 'Duo Paloma lit 120x60 + commode 3 tiroirs (Blanc = « Duo M »)'),
    ([3667, 3665, 3669], 'Trio Paloma lit + commode 3 tiroirs + armoire (Blanc = « Trio M »)'),
    ([3636, 3627], 'Armoire 2 portes Paloma'),
    ([3161, 4033], 'Trio Access Bois 120x60 / 140x70'),
]
OVERRIDES = {3383: {'c': 'Blanc'}, 3172: {'c': 'Blanc'}, 3171: {'c': 'Bois blanc'}, 2098: {'c': 'Bois'}, 2099: {'c': 'Blanc'},
             3657: {'c': 'Blanc'}, 3669: {'c': 'Blanc'}, 3627: {'c': 'Blanc'}, 4033: {'s': '140x70'},
             2462: {'c': 'Blanc / bois'}, 2463: {'c': 'Tilleul'}, 2434: {'c': 'Tilleul'},
             3900: {'s': '0-6 mois'}, 3901: {'s': '6-24 mois'}, 3974: {'c': 'Rose'}, 3975: {'c': 'Vert'},
             3976: {'c': 'Citron'}, 2896: {'c': 'Écru'}, 2421: {'c': 'Bleu tilleul'},
             2362: {'s': '90x190 et 140x190'}, 2361: {'s': '90x190 et 140x190'},
             2366: {'s': '90x200 et 140x200'}, 2365: {'s': '90x200 et 140x200'}}
EXCLUDE = {4034}  # doublon de 4033 (même prix, titre différent) : à valider avant d’inclure


def family_of(r):
    col = r['col'].strip()
    cu = norm(col).upper()
    if cu in COLLECTION_VARIANT:
        return COLLECTION_VARIANT[cu]
    if col:
        return FAMILY_ALIAS.get(cu, cu.replace(' ', '')), None
    nt = norm(r['t'])
    for f in TITLE_FAMILIES:
        if re.search(rf'\b{f}\b', nt):
            return f.upper(), None
    return '', None


def size_label(kind, m):
    if kind == 'dim':
        a, b = int(m.group(1)), int(m.group(2))
        return f'{min(a, b)}x{max(a, b)}' if max(a, b) >= 180 else f'{max(a, b)}x{min(a, b)}'
    if kind == 'range_m':
        return f'{m.group(1)}-{m.group(2)} mois'
    if kind == 'range_a':
        return f'{m.group(1)}-{m.group(2)} ans'
    if kind == 'mois':
        return f'{m.group(1)} mois'
    if kind == 'ans':
        return f'{m.group(1)} ans'
    if kind == 'naiss':
        return 'Naissance'
    if kind == 'modele':
        return m.group(1).capitalize() + ' modèle'


def analyse(r):
    t = norm(r['t'])
    fam, col_val = family_of(r)
    work = ' ' + t + ' '
    words = set(FAMILY_WORDS.get(fam, [])) | {norm(r['col'])} | {w for w in norm(r['col']).split() if len(w) > 2}
    for w in sorted(words, key=len, reverse=True):
        if w:
            work = re.sub(rf'(?<![a-z]){re.escape(w)}(?![a-z])', ' ', work)
    sizes = []
    for pat, kind in SIZE_PATTERNS:
        for m in re.finditer(pat, work):
            sizes.append((m.start(), size_label(kind, m)))
        work = re.sub(pat, ' ', work)
    sizes = [s for _, s in sorted(sizes)]
    feats = {}
    for key, _, pats, default in FEATURES:
        for pat, val in pats:
            if re.search(pat, work):
                feats[key] = val
                work = re.sub(pat, ' ', work)
                break
        else:
            feats[key] = default
    found = []
    for key, label in COLORS:
        pat = rf'(?<![a-z]){re.escape(key)}(?![a-z])'
        m = re.search(pat, work)
        if m:
            found.append((m.start(), label))
            work = re.sub(pat, ' ', work)
    labels = []
    for _, lab in sorted(found):
        if not any(norm(lab) in norm(o) or norm(o) in norm(lab) for o in labels):
            labels.append(lab)
    color = ' / '.join(labels[:2]) if labels else None
    if col_val:
        color = f'{col_val} {labels[0].lower()}' if (fam in MOTIF_FAMILIES and labels) else col_val
    skel = ' '.join(w for w in re.split(r'[^a-z0-9]+', work) if w and w not in FILLER)
    return dict(fam=fam, c=color, sizes=sizes, s=sizes[0] if sizes else None, skel=skel, **feats)


def comp_of(r):
    t = norm(r['t'])
    if r['c0'] not in ('MEUBLES', 'MEUBLE') and r['c1'] != 'MEUBLES' and not re.search(r'\b(duo|trio|commode|lit|armoire)\b', t):
        return None
    has_bed = re.search(r'\blit\b|\bchambre\b', t)
    if has_bed and re.search(r'\btrio\b|3 pieces', t):
        return 'trio'
    if has_bed and re.search(r'\bduo\b|2 pieces', t):
        return 'duo_armoire' if ('armoire' in t and 'commode' not in t) else 'duo'
    if t.startswith('pack commode') and 'plan a langer' in t:
        return 'pack'
    if re.match(r'(petite )?commode\b', t) and 'ilot' not in t:
        return 'commode'
    if re.match(r'(lit bebe|lit \d|little big bed|lit combine|lit evolutif)', t):
        return 'lit'
    if re.match(r'armoire\b', t):
        return 'armoire'
    return None


try:
    GONE = {int(k) for k, v in json.load(open('packs.json')).items() if v.get('gone')}
except FileNotFoundError:
    GONE = set()

items = {}
for r in rows:
    price = float(r['sp'].split()[0]) if r['sp'] else 0
    pid = int(r['id'])
    if price <= 0 or price > 20000 or pid in EXCLUDE or pid in GONE:
        continue
    a = analyse(r)
    a.update(OVERRIDES.get(pid, {}))
    img = re.search(r'/(\d+)-[a-z_]+/', r['img'] or '')
    items[pid] = {**r, **a, 'id': pid, 'price': price, 'comp': comp_of(r),
                  'path': r['link'].replace(BASE, '').replace('.html', ''), 'imgid': int(img.group(1)) if img else None}

# ---------- Groupes de variantes ----------
key_of = {pid: (it['fam'], it['skel']) for pid, it in items.items() if it['fam']}
for ids, _ in MERGES:
    ids = [i for i in ids if i in items]
    if not ids:  # tous les produits de ce regroupement ont quitté le flux
        continue
    k = ('MERGE', ids[0])
    for i in ids:
        key_of[i] = k
raw = collections.defaultdict(list)
for pid, k in key_of.items():
    raw[k].append(items[pid])

DIMS = ['c', 's', 'forme', 'col', 'manches', 'saison']
groups, issues = [], []
for k, members in raw.items():
    if len(members) < 2:
        continue
    # doublons exacts de titre : indistinguables -> exclus
    sig = lambda m: (norm(m['t']), m['c'], m['s'])
    tc = collections.Counter(sig(m) for m in members)
    dup_titles = {t for t, n in tc.items() if n > 1}
    if dup_titles:
        issues.append(('Titres identiques', [m['id'] for m in members if sig(m) in dup_titles]))
        members = [m for m in members if sig(m) not in dup_titles]
    if len(members) < 2:
        continue
    # plusieurs dimensions de taille : si collision sur la 1re, on prend celles qui diffèrent
    firsts = collections.Counter((m['c'], m['s']) for m in members)
    if any(n > 1 for n in firsts.values()) and all(len(m['sizes']) > 1 for m in members):
        common = set.intersection(*(set(m['sizes']) for m in members))
        for m in members:
            m['s'] = ' / '.join(s for s in m['sizes'] if s not in common) or m['s']
    dims = [d for d in DIMS if len({m[d] for m in members if m[d]}) > 1]
    if not dims:
        continue
    # une valeur manquante sur une dimension affichée = ambigu, sauf si elle est seule à manquer (on la laisse de côté)
    kept = []
    for m in members:
        missing = [d for d in dims if not m[d]]
        if missing:
            issues.append((f'Sans valeur pour {", ".join(DIM_LABELS[d] for d in missing)}', [m['id']]))
        else:
            kept.append(m)
    combos = collections.Counter(tuple(m[d] for d in dims) for m in kept)
    clash = {c for c, n in combos.items() if n > 1}
    if clash:
        issues.append(('Combinaisons en double', [m['id'] for m in kept if tuple(m[d] for d in dims) in clash]))
        kept = [m for m in kept if tuple(m[d] for d in dims) not in clash]
    if len(kept) < 2:
        continue
    groups.append({'key': k, 'dims': dims, 'members': kept,
                   'attr': 'Motif' if kept[0]['fam'] in MOTIF_FAMILIES else 'Couleur'})

# ---------- Composition ----------
COMP_LABEL = {'lit': 'Lit seul', 'commode': 'Commode seule', 'armoire': 'Armoire seule', 'pack': 'Commode + plan à langer',
              'duo': 'Duo lit + commode', 'duo_armoire': 'Duo lit + armoire', 'trio': 'Trio lit + commode + armoire'}
SETS = {'pack', 'duo', 'duo_armoire', 'trio'}
SINGLES = {'lit', 'commode', 'armoire'}
# Sur un duo / trio, on ne propose que les autres ensembles (les pièces seules sont déjà listées
# dans « Ce pack contient ») ; sur une pièce seule, on propose la pièce + les ensembles qui la contiennent.
ROOM_SETS = {'duo', 'duo_armoire', 'trio'}
OFFER = {'commode': ['commode', 'pack', 'duo', 'trio'], 'lit': ['lit', 'duo', 'duo_armoire', 'trio'],
         'armoire': ['armoire', 'duo_armoire', 'trio'], 'duo': ['duo', 'trio'], 'trio': ['duo', 'trio'],
         'duo_armoire': ['duo_armoire', 'trio']}
OFFER_SETS = ['commode', 'pack', 'duo', 'trio']
# gammes Paloma (Blanc) : commode / duo / trio de la même gamme
LINE = {3656: 'XS', 3668: 'XS', 3628: 'XS', 3657: 'M', 3669: 'M', 3626: 'M', 3658: 'M évolutif', 3670: 'M évolutif',
        3659: 'XL évolutif', 3660: 'XL évolutif', 3674: 'XL évolutif', 3675: 'XL évolutif', 3625: 'XL évolutif'}
# appariements sans libellé (filtre uniquement) : My Love commode 2 tiroirs vs XXL
LINE_FILTER = {3918: 'XXL', 4035: 'XXL', 3919: '2T', 4036: '2T', 4037: '2T'}
SIZED = {3628: 'commode'}  # meuble à langer Paloma = « commode » de la gamme XS
for pid, comp in SIZED.items():
    if pid in items:
        items[pid]['comp'] = comp
STOP = {'lit', 'bebe', 'commode', 'armoire', 'duo', 'trio', 'et', 'de', 'la', 'le', 'avec', 'chambre', 'pieces', 'x'}

def words(t):
    return {w for w in re.split(r'[^a-z0-9]+', norm(t)) if w and w not in STOP and not re.match(r'\d+x\d+', w)}

comp_families = collections.defaultdict(list)
for it in items.values():
    if it['comp'] and it['fam']:
        comp_families[it['fam']].append(it)
compositions = {fam: m for fam, m in comp_families.items() if any(i['comp'] in SETS for i in m)}

comp_options = {}
for fam, mem in compositions.items():
    multi_color = len({i['c'] for i in mem if i['comp'] in SETS and i['c']}) > 1
    ccol = lambda i: i['c'] if multi_color else None
    size0 = lambda i: i['sizes'][0] if i['sizes'] else None
    lgrp = lambda i: LINE[i['id']].split()[0] if i['id'] in LINE else LINE_FILTER.get(i['id'])
    for P in mem:
        same = [i for i in mem if ccol(i) is None or ccol(P) is None or ccol(i) == ccol(P)]
        if lgrp(P):
            same = [i for i in same if lgrp(i) in (None, lgrp(P))]
        offer = OFFER.get(P['comp'], OFFER_SETS)
        opts = []
        for comp in offer:
            if comp == P['comp'] and comp in SINGLES:
                opts.append((COMP_LABEL[comp], P['id']))
                continue
            cands = [i for i in same if i['comp'] == comp]
            if comp in SINGLES and P['comp'] in SINGLES:
                continue
            by_line = collections.defaultdict(list)
            for i in cands:
                by_line[LINE.get(i['id'])].append(i)
            if P['comp'] in ('lit', 'armoire') and any(by_line.keys()):
                opts = []  # trop de configurations (gammes) depuis un lit / une armoire
                break
            for line in sorted(by_line, key=lambda l: (l is not None, str(l))):
                group = by_line[line]
                if P in group:
                    best = P
                else:
                    wp = words(P['t'])
                    best = sorted(group, key=lambda i: (0 if (size0(P) is None or size0(i) == size0(P)) else 1,
                                                       -len(wp & words(i['t'])), i['price'], i['id']))[0]
                label = COMP_LABEL[comp] if not line else f"{COMP_LABEL[comp].split()[0]} {line}"
                if comp == 'commode' and line:
                    label = COMP_LABEL['commode']
                opts.append((label, best['id']))
        seen, uniq = set(), []
        for lab, tid in opts:
            if tid not in seen:
                seen.add(tid); uniq.append((lab, tid))
        if len(uniq) >= 2 and any(items[t]['comp'] in SETS for _, t in uniq) and P['id'] in [t for _, t in uniq]:
            comp_options[P['id']] = uniq

# ---------- Composition fondée sur le contenu réel des packs PrestaShop ----------
PACKS = {}
try:
    PACKS = {int(k): v['items'] for k, v in json.load(open('packs.json')).items() if v.get('items')}
except FileNotFoundError:
    pass
PIECE_LABEL = {'lit': 'Lit seul', 'commode': 'Commode seule', 'armoire': 'Armoire seule'}
PIECE_LABEL_OVERRIDE = {3628: 'Meuble à langer seul'}
TYPE_ORDER = ['pack', 'duo', 'duo_armoire', 'trio']


def piece_type(pid):
    it = items.get(pid)
    if not it:
        return None
    t = norm(it['t'])
    if 'a langer' in t and re.match(r'(dispositif|plan)', t):
        return 'plan'
    if it['comp'] in SINGLES:
        return it['comp']
    if re.match(r'armoirette', t):
        return 'armoire'
    if re.match(r'lit\b', t):
        return 'lit'
    return None


def pack_type(sid):
    if any(i not in items for i in PACKS[sid]):  # une pièce a quitté le flux : pack ignoré
        return None
    kinds = {piece_type(i) for i in PACKS[sid]}
    if kinds == {'commode', 'plan'}:
        return 'pack'
    if kinds >= {'lit', 'commode', 'armoire'}:
        return 'trio'
    if kinds >= {'lit', 'commode'}:
        return 'duo'
    if kinds >= {'lit', 'armoire'}:
        return 'duo_armoire'
    return None


def pack_label(sid):
    if sid in LINE:
        return f"{COMP_LABEL[pack_type(sid)].split()[0]} {LINE[sid]}"
    return COMP_LABEL[pack_type(sid)]


def bed_size(sid):
    for i in PACKS.get(sid, []):
        if piece_type(i) == 'lit' and items[i]['sizes']:
            return items[i]['sizes'][0]
    return items[sid]['sizes'][0] if items[sid]['sizes'] else None


containing = collections.defaultdict(list)
for sid, content in PACKS.items():
    if sid in items and pack_type(sid):
        for i in content:
            containing[i].append(sid)


def pick(cands, ref_size, prefer=None):
    """Un pack par libellé : celui de la page si présent, sinon même taille de lit, puis prix."""
    out = collections.OrderedDict()
    for sid in sorted(cands, key=lambda s: (TYPE_ORDER.index(pack_type(s)), pack_label(s))):
        out.setdefault(pack_label(sid), []).append(sid)
    res = []
    for lab, sids in out.items():
        if prefer in sids:
            res.append((lab, prefer)); continue
        sids.sort(key=lambda s: (0 if ref_size and bed_size(s) == ref_size else 1, items[s]['price'], s))
        res.append((lab, sids[0]))
    return res


pack_options = {}
for pid in list(containing) + list(PACKS):
    if pid not in items:
        continue
    if pid in PACKS:
        if not pack_type(pid):
            continue
        content = PACKS[pid]
        anchor = next((i for i in content if piece_type(i) == 'commode'), None) or \
            next((i for i in content if piece_type(i) == 'armoire'), None)
        if not anchor or anchor not in items:
            continue
        if pack_type(pid) in ROOM_SETS:
            opts = [o for o in pick(containing[anchor], bed_size(pid), prefer=pid) if pack_type(o[1]) in ROOM_SETS]
        else:
            opts = [(PIECE_LABEL_OVERRIDE.get(anchor, PIECE_LABEL[piece_type(anchor)]), anchor)]
            opts += pick(containing[anchor], bed_size(pid), prefer=pid)
    else:
        ptype = piece_type(pid)
        if ptype not in PIECE_LABEL:
            continue
        cands = containing[pid]
        # pièce partagée entre coloris (ex. lit Tokyo) : ambigu -> pas de composition
        colors = {items[s]['c'] for s in cands}
        if len(colors) > 1 and ptype == 'lit':
            continue
        opts = [(PIECE_LABEL_OVERRIDE.get(pid, PIECE_LABEL[ptype]), pid)]
        opts += pick(cands, items[pid]['sizes'][0] if items[pid]['sizes'] else None)
    if len(opts) >= 2:
        pack_options[pid] = opts

# fusion : les packs réels priment, l'heuristique reste pour les ensembles sans contenu lisible
heuristic_only = {pid: o for pid, o in comp_options.items()
                  if pid not in pack_options and not any(t in PACKS for _, t in o) and pid not in PACKS
                  and pid not in containing}
comp_options = {**pack_options, **heuristic_only}

# incohérences titre / contenu : le pack annonce un coloris, contient la pièce d'un autre coloris
# alors que la pièce du coloris annoncé existe (inversion probable)
catalog_issues = []
for sid, content in PACKS.items():
    if sid not in items or not items[sid]['c']:
        continue
    for i in content:
        pt = piece_type(i)
        if i not in items or pt not in SINGLES or not items[i]['c'] or items[i]['c'] == items[sid]['c']:
            continue
        twin = [j for j in items.values() if j['fam'] == items[i]['fam'] and piece_type(j['id']) == pt
                and j['c'] == items[sid]['c'] and norm(re.sub(r'bois|blanc', '', j['skel'])) == norm(re.sub(r'bois|blanc', '', items[i]['skel']))]
        if twin:
            catalog_issues.append((sid, i, twin[0]['id']))

if __name__ == '__main__':
    n = sum(len(g['members']) for g in groups)
    print('groupes', len(groups), '| produits', n)
    print('dims', collections.Counter(tuple(g['dims']) for g in groups).most_common())
    print('familles avec ensembles', len(compositions), '| fiches avec composition', len(comp_options), '(packs réels :', len(pack_options), ')')
    print('incohérences catalogue', [(a, items[a]['t'][:40], b, items[b]['t'][:40], c) for a, b, c in catalog_issues])
    print('problèmes', len(issues))
    for lab, ids in issues:
        print('  -', lab, ids, [items[i]['t'][:50] for i in ids[:2]])
