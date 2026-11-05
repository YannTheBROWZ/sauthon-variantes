"""Traductions des textes publiés dans variantes-es.json et variantes-it.json (variantes_langues.py).

Textes PROVISOIRES, à faire valider par Sauthon : proposés le 05/11/2026 d'après les titres, menus et fiches espagnols et
italiens du site. Les titres du flux, traduits automatiquement (« Lazarus », « Hola sonajero », « SETTE ANNI »), ne
sont pas repris.

Clé : le texte français exact que donnees.py publie dans « v » (noms des sélecteurs, valeurs) ou « l » (compositions)
de variantes.json. traduire() cherche, dans cet ordre :
  1. TABLE (et SELECTEURS pour les noms des sélecteurs) : traduction exacte des textes simples ;
  2. tailles : « 3 mois », « 0-6 mois », « 2 ans », « 120x60 cm », « 90x190 et 140x190 cm » ;
  3. noms propres gardés tels quels : NOMS_PROPRES (une nouvelle collection s'y ajoute à la main : un nom de collection
     n'est jamais gardé « parce qu'il est dans le flux », des mots courants comme « Nature » ou « Cannelle » en sont) ;
  4. composés : « A / B », « <nom propre ou Maille> <reste> » (« Babyfan blanc / gris », « Maille bleue »),
     « Duo M évolutif » (gammes Paloma) ; un mot en minuscule se traduit comme le même mot avec une majuscule ;
sinon None : variantes_langues.py retire le produit (ou le choix de composition) de cette langue et le signale (e-mail,
une seule fois par texte).
Pour ajouter ou corriger une traduction : une ligne (français, espagnol, italien) dans TABLE ou SELECTEURS, puis pousser
sur main ; « python traductions.py » (dans generateur/, après une génération) liste chaque texte publié et sa traduction.

Choix : couleurs, matières, tailles et meubles traduits ; noms de collections, de modèles et de motifs de gamme gardés
(Babyfan, Lazare, Seventies, Petit Coeur, Léopard…) ; plan à langer = cambiador / fasciatoio (vocabulaire de la balise
d'habillage) ; matelas à langer = colchón cambiador / materassino fasciatoio. Formes féminines (couvertures « Maille … »)
seulement quand la traduction ne s'accorde pas (bleue, verte = azul / blu, verde) : « Maille blanche » attend une
traduction écrite à la main.
Aucun fichier de la génération française n'importe ce module (empreinte « r » d'encart.py inchangée).
"""
import re

LANGUES = ('es', 'it')

# Collections, modèles, motifs de gamme : gardés tels quels (les titres et menus espagnols et italiens les gardent)
NOMS_PROPRES = {
    'Arty', 'Babyfan', 'Blue Baleine', 'Botanica', 'Chao Chao', 'Esmée', 'Hello', 'Lazare', 'Léopard', 'Lilibelle',
    'Merlin', 'Mila', 'Miss Fleur de Lune', 'Mister Bouh', 'Mokka', 'My Love', 'Orsino', 'Petit Chou', 'Petit Coeur',
    'Petit Nuage', 'Petit Soleil', 'Pluche et Pompon', 'Promenons-nous', 'Seventies', 'Sunlight', 'Timouki',
}

# Noms des sélecteurs (g[0] de variantes.json) : (français, espagnol, italien)
SELECTEURS = [
    ('Couleur', 'Color', 'Colore'),
    ('Coloris', 'Color', 'Colore'),                     # jamais dans le même groupe que « Couleur »
    ('Motif', 'Motivo', 'Motivo'),                      # brodés (Orsino, Petit Coeur) autant qu'imprimés
    ('Modèle', 'Modelo', 'Modello'),
    ('Forme', 'Forma', 'Forma'),
    ('Col', 'Cuello', 'Colletto'),
    ('Manches', 'Manga', 'Maniche'),                    # es : « manga larga / corta »
    ('Saison', 'Temporada', 'Stagione'),
    ('Taille du lit', 'Medidas de la cama', 'Misura del letto'),   # « medidas » : mot des mesures en cm ; lits Nova 90x190…
    ('Taille du lit@bebe', 'Medidas de la cuna', 'Misura del lettino'),   # lits bébé et packs (120x60, 140x70 cm) : comme les
                                                                         # compositions « cuna » / « lettino » (libelle_selecteur)
    # « Taille » selon les valeurs du groupe (libelle_selecteur) : âges (vêtements), mesures en cm (matelas, édredons),
    # autres (petit / grand modèle)
    ('Taille@age', 'Talla', 'Taglia'),
    ('Taille@cm', 'Medidas', 'Misura'),
    ('Taille', 'Tamaño', 'Misura'),
]

# Valeurs et compositions : (français, espagnol, italien)
TABLE = [
    # tailles sans chiffre (les autres : _taille)
    ('Naissance', 'Recién nacido', 'Nascita'),
    ('Petit modèle', 'Pequeño', 'Piccola'),             # sous « Tamaño » / « Misura » (accord : la misura)
    ('Grand modèle', 'Grande', 'Grande'),
    # options (FEATURES de regroupement.py, nids d'ange, couvertures)
    ('Avec col', 'Con cuello', 'Con colletto'),
    ('Sans col', 'Sin cuello', 'Senza colletto'),
    ('Longues', 'Larga', 'Lunghe'),
    ('Courtes', 'Corta', 'Corte'),
    ('Été', 'Verano', 'Estate'),
    ('Hiver (ouatinée)', 'Invierno (acolchado)', 'Inverno (imbottito)'),
    ('Classique', 'Clásico', 'Classico'),               # nids d'ange Classique / Hiver
    ('Hiver', 'Invierno', 'Invernale'),
    ('Polaire', 'Polar', 'Pile'),                       # couvertures Polaire / Maille
    ('Maille', 'Punto', 'Maglia'),
    ('Ovale', 'Oval', 'Ovale'),
    ('Rectangulaire', 'Rectangular', 'Rettangolare'),
    ('Carré', 'Cuadrado', 'Quadrato'),
    ('Triangle', 'Triangular', 'Triangolare'),
    # couleurs et finitions (COLORS, COLLECTION_VARIANT, OVERRIDES de regroupement.py)
    ('Blanc', 'Blanco', 'Bianco'),
    ('Beige', 'Beige', 'Beige'),
    ('Bleu', 'Azul', 'Blu'),
    ('Bleue', 'Azul', 'Blu'),                           # « Chao Chao bleue », « Maille bleue » (couvertures)
    ('Gris', 'Gris', 'Grigio'),
    ('Jaune', 'Amarillo', 'Giallo'),
    ('Noir', 'Negro', 'Nero'),
    ('Rose', 'Rosa', 'Rosa'),
    ('Vert', 'Verde', 'Verde'),
    ('Verte', 'Verde', 'Verde'),
    ('Turquoise', 'Turquesa', 'Turchese'),
    ('Bois', 'Madera', 'Legno'),
    ('Naturel', 'Natural', 'Naturale'),
    ('Nude', 'Nude', 'Nude'),
    ('Écru', 'Crudo', 'Ecrù'),
    ('Crème', 'Crema', 'Crema'),
    ('Caramel', 'Caramelo', 'Caramello'),
    ('Citron', 'Limón', 'Limone'),
    ('Corail', 'Coral', 'Corallo'),
    ('Mint', 'Menta', 'Menta'),                         # gamme Lily, en anglais sur le site français
    ('Pétale', 'Rosa pétalo', 'Rosa petalo'),
    ('Sauge', 'Salvia', 'Salvia'),
    ('Terracotta', 'Terracota', 'Terracotta'),
    ('Tilleul', 'Verde tilo', 'Verde tiglio'),          # vert pâle (photos 2434, 2463), pas le bois de tilleul
    ('Vanilla', 'Vainilla', 'Vaniglia'),                # gamme Uni, en anglais sur le site français
    ('Vanille', 'Vainilla', 'Vaniglia'),                # coloris Seventies
    ('Argile douce', 'Arcilla suave', 'Argilla tenue'),
    ('Blanc bois', 'Blanco madera', 'Bianco legno'),
    ('Blanc cristal', 'Blanco cristal', 'Bianco cristallo'),
    ('Blanc et silex', 'Blanco y sílex', 'Bianco e silex'),
    ('Blanc lin', 'Blanco lino', 'Bianco lino'),
    ('Bleu aqua', 'Azul agua', 'Blu acqua'),
    ('Bleu marine', 'Azul marino', 'Blu navy'),
    ('Bleu nuit', 'Azul noche', 'Blu notte'),
    ('Bleu saphir', 'Azul zafiro', 'Blu zaffiro'),
    ('Bleu tilleul', 'Verde tilo', 'Verde tiglio'),     # même teinte que « Tilleul » (berceau Eclipse 2421, pack 3560)
    ('Bois blanc', 'Madera blanca', 'Legno bianco'),
    ('Chêne doré', 'Roble dorado', 'Rovere dorato'),
    ('Chêne sépia', 'Roble sepia', 'Rovere seppia'),
    ('Chêne silex', 'Roble sílex', 'Rovere silex'),
    ('Gris clair', 'Gris claro', 'Grigio chiaro'),
    ('Gris foncé', 'Gris oscuro', 'Grigio scuro'),
    ('Gris volcan', 'Gris volcán', 'Grigio vulcano'),
    ('Hêtre cendré', 'Haya ceniza', 'Faggio cenere'),
    ('Jaune rose', 'Amarillo y rosa', 'Giallo e rosa'), # deux couleurs (imprimé jaune et rose, photo 2718)
    ('Jaune topaze', 'Amarillo topacio', 'Giallo topazio'),
    ('Rose poudré', 'Rosa empolvado', 'Rosa cipria'),
    ('Rose quartz', 'Rosa cuarzo', 'Rosa quarzo'),
    ('Tout bois', 'Todo madera', 'Tutto legno'),
    # couleurs du regroupement pas encore publiées (prochains produits)
    ('Camel', 'Camel', 'Cammello'),
    ('Figue', 'Higo', 'Fico'),
    ('Kaki', 'Caqui', 'Cachi'),
    ('Moutarde', 'Mostaza', 'Senape'),
    ('Ocre', 'Ocre', 'Ocra'),
    ('Taupe', 'Topo', 'Tortora'),
    # motifs (Orsino, Esmée, Promenons-nous, Miss Fleur de Lune, Chao Chao) et boutons Basic (libellés du 29/10/2026)
    ('Motif floral', 'Estampado floral', 'Motivo floreale'),
    ('Motif végétal', 'Estampado vegetal', 'Motivo vegetale'),
    ('Maison', 'Casita', 'Casetta'),
    ('Nuages', 'Nubes', 'Nuvole'),
    ('Ours', 'Osito', 'Orsetto'),                       # un seul ourson brodé (3298, 3299)
    ('Nuage', 'Nube', 'Nuvola'),
    ('Oiseau', 'Pájaro', 'Uccellino'),
    ('Lettres', 'Letras', 'Lettere'),
    ('Panda', 'Panda', 'Panda'),
    ('Boutons boule blanc', 'Pomos de bola blancos', 'Pomelli a sfera bianchi'),
    ('Boutons cœur rose', 'Pomos de corazón rosa', 'Pomelli a cuore rosa'),
    ('Boutons étoile gris', 'Pomos de estrella grises', 'Pomelli a stella grigi'),
    # compositions (COMP_LABEL, PIECE_LABEL_OVERRIDE de regroupement.py ; gammes Paloma « Duo M évolutif » : traduire())
    # es « cuna » : le lit bébé en Espagne (menu ES « Cunas », titres « Cuna… » des lits seuls ; fiches des lits combinés et
    # lits chambre : « cuna combinada », « cuna de 60x120 cm »), comme « Medidas de la cuna » (Taille du lit@bebe).
    ('Lit seul', 'Solo cuna', 'Solo lettino'),
    ('Commode seule', 'Solo cómoda', 'Solo cassettiera'),
    ('Armoire seule', 'Solo armario', 'Solo armadio'),
    ('Meuble à langer seul', 'Solo mueble cambiador', 'Solo mobile fasciatoio'),
    ('Commode + plan à langer', 'Cómoda + cambiador', 'Cassettiera + fasciatoio'),
    ('Duo lit + commode', 'Dúo cuna + cómoda', 'Duo lettino + cassettiera'),
    ('Duo lit + armoire', 'Dúo cuna + armario', 'Duo lettino + armadio'),
    ('Trio lit + commode + armoire', 'Trío cuna + cómoda + armario', 'Trio lettino + cassettiera + armadio'),
    ('Duo', 'Dúo', 'Duo'),
    ('Trio', 'Trío', 'Trio'),
    ('évolutif', 'convertible', 'trasformabile'),
]
# mots qui commencent un texte composé sans être des noms propres (« Maille bleue » -> « Punto azul »)
PREFIXES_TRADUITS = ('Maille',)
MOIS = {'es': ('mes', 'meses'), 'it': ('mese', 'mesi')}
ANS = {'es': ('año', 'años'), 'it': ('anno', 'anni')}
ET = {'es': 'y', 'it': 'e'}
RE_AGE = re.compile(r'\d+(?:-\d+)? (?:mois|ans)|Naissance')     # une taille en âge (vêtements)
RE_CM = re.compile(r'\d+x\d+(?: et \d+x\d+)?(?: cm)?')            # une mesure (matelas, édredons…)
RE_LIT_BEBE = re.compile(r'(?:120x60|140x70|60x120|70x140|100x50|50x100)(?: cm)?')   # « Taille du lit » d'un lit bébé


def _par_langue(table):
    """{langue: {français: traduction}} ; une ligne en double serait une erreur silencieuse : refusée."""
    out = {}
    for i, L in enumerate(LANGUES, start=1):
        out[L] = {}
        for ligne in table:
            if len(ligne) != len(LANGUES) + 1 or ligne[0] in out[L]:
                raise ValueError(f'traductions.py : ligne en double ou incomplète : {ligne}')
            out[L][ligne[0]] = ligne[i]
    return out


TEXTES = _par_langue(TABLE)
NOMS_SELECTEURS = _par_langue(SELECTEURS)


def _taille(s, L):
    m = re.fullmatch(r'(\d+)(?:-(\d+))? (mois|ans)', s)
    if m:
        a, b, unite = m.groups()
        un, plusieurs = (MOIS if unite == 'mois' else ANS)[L]
        return f'{a}-{b} {plusieurs}' if b else f'{a} {un if a == "1" else plusieurs}'
    if re.fullmatch(r'\d+x\d+(?: cm)?', s):
        return s
    m = re.fullmatch(r'(\d+x\d+) et (\d+x\d+)( cm)?', s)
    if m:
        return f'{m.group(1)} {ET[L]} {m.group(2)}{m.group(3) or ""}'
    return None


def traduire(s, L):
    """Traduction de s (texte français publié) en langue L, ou None."""
    if not s:
        return None
    T = TEXTES[L]
    if s in T:
        return T[s]
    t = _taille(s, L)
    if t is not None:
        return t
    if s in NOMS_PROPRES:
        return s
    if ' / ' in s:
        parts = [traduire(p, L) for p in s.split(' / ')]
        return None if None in parts else ' / '.join(parts)
    u = s[0].upper()
    if s[0].islower() and len(u) == 1 and u.isupper():   # « gris foncé » dans « Babyfan gris foncé » ; jamais « º »
        t = traduire(u + s[1:], L)
        return t[0].lower() + t[1:] if t else None
    debuts = [p for p in NOMS_PROPRES | set(PREFIXES_TRADUITS) if s.startswith(p + ' ')]
    for p in sorted(debuts, key=lambda p: (-len(p), p)):   # le plus long d'abord : « Petit Coeur » avant « Petit »
        tete, reste = traduire(p, L), traduire(s[len(p) + 1:], L)
        if tete and reste:
            return f'{tete} {reste}'
    m = re.fullmatch(r'(Duo|Trio) (XS|M|XL|XXL)( évolutif)?', s)              # gammes Paloma (LINE)
    if m:
        return f'{T[m.group(1)]} {m.group(2)}' + (f' {T["évolutif"]}' if m.group(3) else '')
    return None


def libelle_selecteur(fr, valeurs_fr, L):
    """Nom d'un sélecteur en langue L, ou None. « Taille » et « Taille du lit » dépendent des valeurs françaises affichées
    (valeurs_fr)."""
    N = NOMS_SELECTEURS[L]
    if fr == 'Taille du lit' and valeurs_fr and all(RE_LIT_BEBE.fullmatch(p) for v in valeurs_fr for p in v.split(' / ')):
        return N['Taille du lit@bebe']
    if fr == 'Taille' and valeurs_fr:
        parts = [p for v in valeurs_fr for p in v.split(' / ')]
        if all(RE_AGE.fullmatch(p) for p in parts):
            return N['Taille@age']
        if all(RE_CM.fullmatch(p) for p in parts):
            return N['Taille@cm']
    return N.get(fr)


if __name__ == '__main__':
    # Relecture (après une génération) : chaque texte publié dans ../docs/variantes.json et sa traduction (« - » : aucune)
    import json
    D = json.load(open('../docs/variantes.json'))
    lignes = set()
    for g in D['g']:
        for k, i in enumerate(g[0]):
            valeurs = [D['v'][v] for v in g[1][k]]
            lignes.add(('sélecteur', D['v'][i]) + tuple(libelle_selecteur(D['v'][i], valeurs, L) or '-' for L in LANGUES))
            lignes |= {('valeur', v) + tuple(traduire(v, L) or '-' for L in LANGUES) for v in valeurs}
    lignes |= {('composition', s) + tuple(traduire(s, L) or '-' for L in LANGUES) for s in D['l']}
    print('type | français | ' + ' | '.join(LANGUES))
    for ligne in sorted(lignes):
        print(' | '.join(ligne))
