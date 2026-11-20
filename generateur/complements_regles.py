"""Compléments demandés par Sauthon pour l'encart « Pour compléter » (commentaires de la cliente du 29/10/2026 dans le
tableau de validation) : draps housse, housses de matelas à langer, panières… par référence produit PrestaShop.

Ils s'ajoutent après le plan à langer et les matelas, dans l'ordre donné, dans la limite de 3 lignes au total.
Les duos et trios reçoivent aussi les compléments de leurs pièces (décision du 29/10/2026).
Publiés dans « l » (encart.py) et affichés par le tag « Pour compléter » à partir de sa version 2026-10-30.
"""

COMPLEMENTS = {
    2107: ['PPDR1', 'BWDR1', 'XEDR1'],  # Lit bébé 120x60 Basic — « drap housse références PPDR1 et BWDR1 et XEDR1 »
    2594: ['ECDR5'],  # Lit bébé 120x60 Arty — « draps housse ECDR5 »
    2595: ['ECDR5'],  # Lit bébé évolutif 140x70 Arty — « draps housse ECDR5 »
    2597: ['PRHM5', 'ESHM5'],  # Dispositif à langer dessus intégral 15kg Arty — « housse de matelas à langer complémentaires PRHM5 et esHM5 »
    2599: ['XCCR1'],  # Bibliothèque 2 portes. 1 penderie Arty — « cube de rangement » : XCCR1 (Yann, 30/10)
    2610: ['PPDR1', 'BWDR1'],  # Lit bébé 120x60 Antonin Bois — « drap housse PPDR1 et BWDR1 »
    2611: ['PPDR1', 'BWDR1'],  # Lit bébé 120x60 Antonin Bois Blanc — « drap housse PPDR1 et BWDR1 »
    2613: ['PPDR1', 'BWDR1'],  # Lit bébé évolutif 140x70 Antonin Bois — « drap housse PPDR1 et BWDR1 »
    2783: ['PRDR1', 'RLDH1'],  # Lit bébé 120 x 60 Access Bois — « drap housse PRDR1 et RLDR1 »
    2784: ['PRDR1', 'RLDH1'],  # Lit bébé évolutif 140x70 Access Bois — « drap housse PRDR1 et RLDR1 »
    2789: ['PRHM5', 'WVHM5'],  # Dispositif à langer 15kg dessus intégral 555  — « housse de matelas à langer complémentaires PRHM5 et WVHM5 »
    2808: ['ESDR1', 'RLDH1'],  # Lit bébé 120 x 60 Access Bois Blanc — « drap housse ESDR1 et RLDR1 »
    2809: ['ESDR1', 'RLDH1'],  # Lit bébé évolutif 140x70 Access Bois Blanc — « drap housse ESDR1 et RLDR1 »
    2810: ['ESHM5', 'WVHM5'],  # Commode 3 tiroirs Bois Blanc Access Bois Blan — « housse de matelas à langer complémentaires esHM5 et WVHM5 »
    2814: ['PRHM5', 'ESHM5'],  # Dispositif à langer 15kg dessus intégral 555  — « housse de matelas à langer complémentaires PRHM5 et esHM5 »
    3178: ['PPDR1', 'BWDR1'],  # Lit bébé 120 x 60 Azur — « drap housse PPDR1 et BWDR1 »
    3179: ['PPDR1', 'BWDR1'],  # Lit chambre évolutif commode 1 porte Azur — « drap housse PPDR1 et BWDR1 »
    3180: ['PPDR1', 'BWDR1'],  # Lit bébé évolutif 140x70 - Type Montessori -  — « drap housse PPDR1 et BWDR1 »
    3181: ['PRHM5', 'ESHM5'],  # Commode 2 portes 1 niche dal integre Azur — « housse de matelas à langer complémentaires PRHM5 et esHM5 »
    3433: ['PPDR1', 'BWDR1'],  # Trio lit 120x60 + commode + armoire Azur — « drap housse PPDR1 et BWDR1 »
    3749: ['ESPN1'],  # Pack Commode 3 tiroirs et Plan à langer Arty — « panière de rangement ESPN1 »
    3861: ['TBDR5'],  # Lit au sol jeune enfant 70x140cm – Type Monte — « drap housse TBDR5 »
    3929: ['ECPN1'],  # Commode à langer évolutive en bureau - Arche  — « panière vanille ECPN1 »
    3930: ['ECPN1'],  # Commode à langer évolutive en bureau - Arche  — « panière vanille ECPN1 »
    3931: ['ECPN1'],  # Commode à langer évolutive en bureau - Arche  — « panière vanille ECPN1 »
    3932: ['ECPN1'],  # Commode à langer évolutive en bureau - Arche  — « panière vanille ECPN1 »
    3933: ['WVDR1'],  # Lit bébé évolutif 120x60 en 90x190 - Arche -  — « drap housse WVdR1 »
    3934: ['WVDR1'],  # Lit bébé évolutif 120x60 en 90x190 - Arche -  — « drap housse WVdR1 »
    3935: ['SADR5'],  # Lit bébé évolutif 120x60 en 90x190 - Arche -  — « drap housse SAdr5 »
    3936: ['TBDR5'],  # Lit bébé évolutif 120x60 en 90x190 - Arche -  — « drap housse TBDR5 »
    3950: ['ECDR5'],  # Lit combiné 120x60 évolutif en 90x190 Arty — « draps housse ECDR5 »
    3993: ['PRHM5', 'ESHM5'],  # Commode à langer 2 tiroirs et une niche poign — « housse de matelas à langer complémentaires PRHM5 et esHM5 »
    4134: ['PRHM5', 'ESHM5'],  # DISPOSITIF A LANGER COULISSANT - 15KG ARTY — « housse de matelas à langer complémentaires PRHM5 et esHM5 »
    4157: ['ESPN1'],  # Commode XXL 6 tiroirs et dispositif à langer  — « panière de rangement ESPN1 »
    4158: ['ESPN1'],  # Commode 3 tiroirs et dispositif à langer ARTY — « panière de rangement ESPN1 »
    4162: ['ESPN1'],  # Commode 3 tiroirs et dispositif à langer ACCE — « panière de rangement ESPN1 »
    4163: ['PRHM5', 'WVHM5'],  # Commode 3 tiroirs et dispositif à langer ACCE — « housse de matelas à langer complémentaires PRHM5 et WVHM5 »
    # commentaires de la cliente du 30/10/2026
    2274: ['ECDR5', 'SADR5', 'TBDR5'],
    11: ['ECDR5', 'SADR5', 'TBDR5'],  # Matelas 140x70 Confort Baby — 02/11 : « les mêmes draps housse que le matelas 120*60 »  # Matelas 120x60 Confort Baby — « drap housse Unis les 4 références » (3 au catalogue)
    4136: ['ECDR5', 'SADR5', 'TBDR5'],  # LITTLE BIG BED 140x70 BASILE — « drap housse Unis les 4 références »
    4140: ['ECPN1', 'TBPN1', 'SAPN1'],  # Commode 6 tiroirs et dispositif à langer BOHÈME — « panière ECPN1 ou TBPN1 ou SAPN1 »
    3756: ['PK025'],  # Trousseau maternité pour le bain - Promenons-nous — « Trousseau 1 mois - Promenons-nous »
    3770: ['PK013'],  # Trousseau 1 mois - Promenons-nous — « Trousseau maternité pour le bain - Promenons-nous »
    4164: ['ECML1'],  # Commode 3 tiroirs et dispositif à langer SOLÈNE — « Matelas à langer … uni Vanilla »
    4167: ['899663'],  # Pack duo lit bébé 120x60 et commode SOLÈNE — « Matelas de lit : Matelas 120x60 Confort Baby »
}

# demandes sans référence exploitable (question posée à la cliente)
SANS_REFERENCE = {}

# Demandes de la cliente du 02/11/2026 (hors tableau), par référence de la fiche : référence -> références proposées.
# Les pyjamas, lots de bodies, bonnets et trousseaux de toutes les collections sont reliés par taille dans encart.py
# (liens_layette : règle d'Orsino étendue aux autres collections, réponse du 02/11 ; pack Orsino 1 mois = PK028).
COMPLEMENTS_PAR_REF = {
    # 2e message du 02/11 : berceaux ovales Galopin -> matelas berceau ovale et draps housse ovales (5 coloris) ;
    # berceaux Bambin -> matelas berceau et draps housse rectangulaires ; meuble à langer Galopin -> housses ovales
    **{r: ['899666', 'JZDH1', 'KHDH1', 'QNDH1', 'VGDH1', 'XYDH1'] for r in ('68152', '68154', '68155', '68156')},
    **{r: ['899669', 'JZDH2', 'KHDH2', 'QNDH2', 'VGDH2', 'XYDH2'] for r in ('19152', '19154', '19155', '19156')},
    '68437': ['JZHM2', 'KHHM2', 'QNHM2', 'VGHM2', 'XYHM2'],   # Meuble à langer blanc pieds bois Galopin
    # réponse du 02/11 au soir : meubles à langer Bambin (matelas fourni) -> housses rectangulaires 76x55 JZHM3 et KHHM3
    **{r: ['JZHM3', 'KHHM3'] for r in ('19431', '19434', '19435', '19436')},
    # demandes du 04/11 : lits FIRST 2H035 / 2H038 et lit Azur AF031 -> tour de lit et douillette Babyfan ; lit UP UI101 ->
    # protections de barreaux Terracotta (photo d'ambiance) et douillette Babyfan
    **{r: ['BWTL1', 'BWDO1'] for r in ('2H035', '2H038', 'AF031')},
    'UI101': ['TBPB1', 'BWDO1'],
    'DU111': ['XEML1', 'XEPB1'],   # duo lit chambre + armoire UP chêne silex : matelas à langer et protections Baby Sailor (04/11)
    'LXTL5': ['LXED5', 'LXED6', 'LXDO5'],   # tour de lit Lazare : édredons 120x60 / 140x70 et gigoteuse 0-6 mois (04/11)
    # demandes du 09/11 (encart sur toutes les langues ; 3 lignes au plus, lits : matelas, 1er drap, puis la demande)
    # lit Choco 140x70 : en plus du matelas ; RLPB1 ne rentre pas (4e ligne). 20/11 : « remplacer le drap housse par le
    # TBDR1 », absent du catalogue : TBDR5, le drap housse uni Terracotta (le seul TBDR), à la place de RLDH1
    'HO111': ['SCPB1', 'RLPB1', 'TBDR5'],
    'HO955': ['ECML1', 'SCML1'],   # dispositif Choco : SCML1 « en plus du matelas à langer proposé » (l'uni ECML1 gardé)
    'DU207': ['SCML1', 'RLML1'],   # commode + dispositif Choco : matelas à langer Emmy et Léopard
    'BD111': ['SVPB4', 'SVDN2'],   # lit Bohème : demandés « SVPB1 et SVDN1 », absents du catalogue ; protections et
                                   # gigoteuse naissance Petit Écossais, les seules de la collection (SV)
    # demandes du 19/11 : compléments « normaux » donnés avec un coup de cœur (voir COUPS_DE_COEUR_PAR_REF)
    **{r: ['SJML1'] for r in ('DU219', 'TR046')},   # Solène duo et trio : matelas à langer Sunlight, en plus du matelas
    **{r: ['BWML1'] for r in ('DU216', 'DU217')},   # New York duo 120x60, commode + dispositif : matelas à langer Babyfan
    'RLDN1': ['RLDO1'],   # gigoteuse naissance Léopard : gigoteuse hiver Léopard
    'RLDO1': ['RLTT1'],   # gigoteuse hiver Léopard : trousse de toilette Léopard
    'WVDN1': ['WVCV1'],   # gigoteuse naissance Orsino : couverture Orsino
    # demandes du 20/11, lits : entre le matelas (et le drap housse) et le coup de cœur. Ordre des lits (encart.ordre_lit) :
    # matelas, 1er drap housse, tour de lit, puis le reste, 3 lignes au plus
    'MO111': ['WVTL1', 'WVPB1'],   # lit Mokka 140x70 : demandé « drap housse WVTL1 », qui est le tour de lit Orsino ;
                                   # protections de barreaux Orsino
    'LV111': ['RLDH1', 'RLPB1'],   # lit My Love 70x140 : demandé « RLDR1 », absent : RLDH1, le drap housse Léopard
                                   # (comme pour les lits Access le 29/10) ; protections de barreaux Léopard
    **{r: ['ESTL1'] for r in ('1J111', '1J031')},   # lits Arty 140x70 et 120x60 : tour de lit Esmée après le drap ECDR5
    'PK152': ['ECDR5', 'WVTL1'],   # lit Opaline 70x140 : demandé « ECDR1 », absent : ECDR5, drap housse uni Vanilla ;
                                   # tour de lit Orsino
    'CC111': ['WVCM1', 'WVPB1'],   # lit décor vanille 140x70 : couvre-lit et protections de barreaux Orsino
    'EW101': ['WVPB1'],            # lit combiné Paloma : protections de barreaux Orsino, après la housse WVHM5
    # 2e message du 20/11, lits (le tour de lit relié dans PrestaShop ne prend pas la place d'un complément demandé :
    # encart.ordre_lit)
    'HK111': ['SADR5', 'PRPB2'],   # lit Eléonore Kaki 140x70 : demandé « SADR1 », absent : SADR5, le drap housse uni Sauge ;
                                   # puis protections de barreaux Tilleul Promenons-nous
    'MH111': ['ESPB1', 'TBPB1'],   # lit Mélinée 140x70 : protections de barreaux Esmée et uni Terracotta
    'XV111': ['TBDR5', 'WVPB1'],   # lit Tokyo 140x70 : demandé « TBDR1 », absent : TBDR5 (comme HO111) ; protections Orsino
}
# Lits combinés dont le matelas à langer est fourni (réponse du 02/11 : matelas à langer « sauf EW101 et BJ101 », « ajouter
# housse de matelas à langer EC, WV, SA, TB ») : pas de matelas à langer, mais les housses de matelas à langer (références
# xxHMn) des collections EC (uni Vanilla), WV (Orsino), SA (uni Sauge) et TB (uni Terracotta), dans cet ordre. Aujourd'hui
# seule la housse Orsino (WVHM5) est vendue seule ; les autres s'ajouteront d'elles-mêmes si elles arrivent au catalogue.
HOUSSES_LIT_COMBINE = {
    'EW101': ['EC', 'WV', 'SA', 'TB'],   # Lit bébé combiné évolutif 140x70 Paloma
    'BJ101': ['EC', 'WV', 'SA', 'TB'],   # Lit bébé combiné 140x70 évolutif Balloon
}

# Règles par motif de référence : (motif de la référence de la fiche, références proposées), {p} = 2 premières lettres
# (la collection). Une référence absente du catalogue est simplement ignorée.
COMPLEMENTS_MOTIFS = [
    (r'(..)NA[12]', ['{p}CV1', '{p}SL1']),   # nid d'ange : couverture et spirale de la même collection
    (r'(..)CV[12]', ['{p}NA1', '{p}SL1']),   # couverture : nid d'ange et spirale de la même collection
    (r'(..)SB1', ['{p}TT1', '{p}TT2']),      # cape de bain : trousses de toilette de la même collection (demande du 03/11)
    (r'(..)CF1', ['898505']),                # couffin : support bois pour couffin (demande du 03/11)
    # jouets d'éveil de la même collection (demandes du 03/11) : balle, cube et spirale entre eux ; tapis d'éveil -> livre, cube
    (r'(..)BA1', ['{p}CU1', '{p}SL1']),
    (r'(..)CU1', ['{p}BA1', '{p}SL1']),
    (r'(..)SL1', ['{p}BA1', '{p}CU1']),
    (r'(..)TS1', ['{p}LI1', '{p}CU1']),
    (r'(..)DO3', ['{p}HC1', '{p}DD1']),      # gigoteuse ouatinée 6-24 mois : housse de couette et peluche (demande du 03/11)
    # tours de lit (demande du 04/11) : couvre-lit et draps housse de la collection ; Babyfan, Miss Fleur de Lune et Chao Chao :
    # édredons 120x60 / 140x70 et gigoteuse 0-6 mois (Lazare LXTL5 : COMPLEMENTS_PAR_REF)
    (r'(?!BW|XC|QJ)(..)TL[12]', ['{p}CM1', '{p}DR1']),
    (r'(BW|XC|QJ)TL[12]', ['{p}ED1', '{p}ED2', '{p}DO1']),
]
# Collections textiles Emmy (SC) et Petit Écossais (SV), nouveautés de novembre (demande du 20/11/2026 : « reprendre les
# mêmes associations au sein de la collection que pour les autres collections textiles ») : leurs références ne suivent
# pas la numérotation des autres (SVNA5, SVCV4, SCSL2…). Pour les règles par motif ci-dessus, une fiche y est lue comme
# l'article habituel de son type (SVNA5 comme xxNA1 ; gigoteuse 6-24 mois, reconnue à son titre, comme xxDO3), et une
# cible xxTTn y désigne un article de ce type de la collection : celui qui a le même numéro que la fiche d'abord (même
# motif : nid d'ange SVNA5 sherpa / carreaux caramel -> couverture SVCV5 carreaux caramel), sinon le plus petit numéro.
COLLECTIONS_NUMEROTATION_LIBRE = ['SC', 'SV']
# Pas de pyjama ni de bodies dans ces deux collections : leurs gigoteuses naissance et 0-6 mois proposent un doudou
# mouchoir et la spirale d'activités au lieu du pyjama et des bodies 1 mois (« DM1 et SL1 », 20/11). Emmy : doudou
# mouchoir rose fleur SCDM1, assorti aux gigoteuses ; Petit Écossais : SVDM4 (plus petit numéro, ours sherpa).
GIGOTEUSE_SANS_LAYETTE = ['DM1', 'SL1']

# Coups de cœur (demande du 19/11/2026) : un produit par fiche, en DERNIÈRE ligne de l'encart, en plus de ses 3 lignes, avec
# l'étiquette « Coup de ♥ » (balise 2026-11-19 et suivantes ; les précédentes l'affichent comme un complément ordinaire,
# dans la limite de leurs 3 lignes). Règle par référence de la fiche d'abord, puis par type de fiche (encart.coup_de_coeur).
COUPS_DE_COEUR_PAR_REF = {
    'CC111': 'WVMM2',     # 20/11 : « remplacer le mobile coup de cœur par le WVMM2 » (lit décor vanille 140x70)
    'HK111': 'PRMM1',     # 20/11 : « remplacer le mobile par le PRMM1 » (lit Eléonore Kaki 140x70), mobile Promenons-nous
    'MH111': 'FJMM2',     # 20/11 : « mobile FJMM2 » (lit Mélinée 140x70), mobile Petit Coeur
    **{r: 'SJMM1' for r in ('DU219', 'TR046')},   # Solène duo et trio (demandé « DU219 et TR045 » : TR045 est le trio Choco)
    **{r: 'BWMM1' for r in ('DU216', 'DU217')},   # New York duo 120x60 et commode + dispositif
    'RLDN1': 'RLCV1',     # gigoteuse naissance Léopard : couverture velours côtelé et sherpa
    'RLDO1': 'RLCV3',     # gigoteuse hiver Léopard : demandé « RLCV2 », absente du catalogue ; RLCV3, la couverture en gaze
    'WVDN1': 'RLCV1',     # gigoteuse naissance Orsino : couverture Léopard
}
COUP_DE_COEUR_DUO_TRIO = 'WVNA2'          # duos et trios (nid d'ange hiver Orsino)
# lits seuls, par collection : (famille de regroupement.py, coloris ou None) -> référence
COUPS_DE_COEUR_LITS = [
    (('ARTY', None), 'ESMM1'), (('SERENA', None), 'ESMM1'), (('ACCESS', 'Bois blanc'), 'ESMM1'),   # mobile Esmée
    (('ACCESS', 'Bois'), 'PRMM1'), (('AZUR', None), 'PRMM1'),                                     # mobile Promenons-nous
]
COUP_DE_COEUR_LIT_120_140 = 'RLMM3'       # autres lits 120x60 / 140x70 : demandé « RLMM2 », absent ; RLMM3, mobile Léopard
COUP_DE_COEUR_AUTRES_LITS = 'WVMM2'       # autres lits (100x50…) : mobile Orsino
# Lits junior 90x190 / 90x200 (demande du 20/11 : « enlever les mobiles musicaux en coup de cœur pour les lits juniors
# 90x190 » et les remplacer par « deux lignes de coussins SJCS1 et SJCS2 ») : coussin carré Sunlight en ligne normale,
# après le matelas et le sommier, puis coussin arc-en-ciel en coup de cœur (une seule ligne coup de cœur par fiche).
# Lit junior = lit dont matelas.py retient le matelas Montana 90x190 ou 90x200 (encart.est_lit_junior).
COMPLEMENTS_LITS_JUNIOR = ['SJCS1']
COUP_DE_COEUR_LITS_JUNIOR = 'SJCS2'
