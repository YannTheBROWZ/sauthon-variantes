"""Règles de l'encart « Pour compléter » (plan à langer proposé sous le bouton panier).

TABLE_VALIDEE : correspondances validées (fiche commode / duo / trio -> plan à langer).
A_VALIDER     : suggestions en attente de validation client : NON publiées tant qu'elles restent ici.
                Pour en activer une, la déplacer dans TABLE_VALIDEE ; pour en refuser une, la déplacer dans EXCLUS.
EXCLUS        : fiches qui ne doivent jamais avoir l'encart (plan déjà inclus, commode à langer…).
                ATTENTION : seul EXCLUS bloque l'ajout automatique. Une ligne simplement SUPPRIMÉE de TABLE_VALIDEE
                ou d'A_VALIDER est republiée la nuit suivante si les accessoires PrestaShop ou la commode du pack
                la relient à un plan. Pour retirer ou refuser une correspondance : la déplacer dans EXCLUS.
PLANS_NOMS    : nom affiché dans l'encart pour chaque plan à langer (sinon : titre du flux).

Chaque nuit, pour_completer.py part de TABLE_VALIDEE, retire les fiches ou plans sortis du flux, et ajoute
automatiquement les nouveautés sûres (plan présent dans les accessoires PrestaShop d'une nouvelle fiche,
nouveau duo / trio dont la commode a déjà son plan). Les ajouts et retraits sont listés dans status.json.
"""

PLANS_NOMS = {
    2789: 'Dispositif à langer Access Bois',
    2814: 'Dispositif à langer Access Bois Blanc',
    2597: 'Dispositif à langer Arty',
    2590: 'Dispositif à langer Boréale Bleu nuit',
    3208: 'Dispositif à langer Cannelle',
    2799: 'Dispositif à langer Eléonore Kaki',
    1583: 'Dispositif à langer Happy',
    3649: 'Dispositif à langer Mokka',
    3644: 'Dispositif à langer Mélinée',
    3221: 'Dispositif à langer Nature',
    3632: 'Dispositif à langer Paloma',
    3638: 'Dispositif à langer Paloma Bois',
    3631: 'Dispositif à langer Paloma grande commode',
    2094: 'Dispositif à langer Serena',
    2101: 'Dispositif à langer Seventies',
    3388: 'Dispositif à langer Tokyo',
    3215: 'Dispositif à langer Vanille',
    2618: 'Dispositif à langer multi-positions Antonin',
    3275: 'Grand dispositif à langer Seventies',
    3866: 'Plan à langer Camille',
    3921: 'Plan à langer coulissant My Love',
    3922: 'Plan à langer coulissant My Love XXL',
    3927: 'Plan à langer multiposition Îlot bébé',
}

TABLE_VALIDEE = {
    2785: 2789,  # Commode 3 tiroirs Bois Access Bois
    3139: 2789,  # Duo lit 120x60 + commode Access Bois
    3437: 2789,  # Duo lit 140x70 + commode Access Bois
    4033: 2789,  # Chambre bébé trio: Lit bébé 70x140 évolutif, commode 3 tiroirs et armoire 2 portes
    3161: 2789,  # Trio lit 120x60 + commode + armoire Access Bois
    2810: 2814,  # Commode 3 tiroirs Bois Blanc Access Bois Blanc
    3138: 2814,  # Duo lit 120x60 + commode Access Bois Blanc
    3434: 2814,  # Duo lit 140x70 + commode Access Bois Blanc
    3160: 2814,  # Trio lit 120x60 + commode + armoire Access Bois Blanc
    2616: 2618,  # Commode 3 tiroirs Antonin Bois
    2617: 2618,  # Commode 3 tiroirs Antonin Bois Blanc
    3158: 2618,  # Duo lit 120x60 + commode Antonin Bois
    3157: 2618,  # Duo lit 120x60 + commode Antonin Bois Blanc
    2596: 2597,  # Commode 3 tiroirs Arty
    3153: 2597,  # Duo lit 120x60 + commode Arty
    3607: 2597,  # Duo lit 140x70 + commode Arty
    3174: 2597,  # Trio lit 120x60 + commode + armoire Arty
    3869: 2597,  # Trio lit évolutif 140x70 + commode + armoire Arty
    2591: 2590,  # Commode 1 porte 3 tiroirs 1 niche version Bleu nuit Boréale
    3515: 2590,  # Duo lit 140x70 + commode Boréale Bleu Nuit
    3516: 2590,  # Trio lit 140x70 + commode + armoire Boréale Bleu Nuit
    3865: 3866,  # Commode 3 tiroirs avec pieds bois décor vanille
    3868: 3866,  # Chambre bébé complète Camille, Lit 120x60 et Commode à langer - décor vanille
    3204: 3208,  # Commode 3 tiroirs Cannelle
    3422: 3208,  # Duo lit 120x60 + commode Cannelle
    3557: 3208,  # Duo lit 140x70 + commode Cannelle
    3428: 3208,  # Trio lit 120x60 + commode + armoire Cannelle
    2797: 2799,  # Commode 1 tiroir 2 portes Eléonore Kaki
    3140: 2799,  # Duo lit 120x60 + commode Eléonore Kaki
    3609: 2799,  # Duo lit 140x70 + commode Eleonore Kaki
    3162: 2799,  # Trio lit 120x60 + commode + armoire Eléonore Kaki
    2602: 1583,  # Petite commode 3 tiroirs Happy
    3926: 3927,  # Commode-îlot bébé décor bois chêne suave avec rangements 3 faces
    3646: 3649,  # Commode 3 tiroirs 1 porte Mokka
    3653: 3649,  # Duo lit 140x70+ commode Mokka
    3664: 3649,  # Trio lit 140x70cm + commode + armoire Mokka
    3919: 3921,  # Commode 2 tiroirs et 1 niche décor chêne vintage poignées dorées My Love
    3918: 3922,  # Commode 5 tiroirs et 2 portes décor chêne vintage poignées dorées My Love
    4036: 3921,  # Chambre bébé trio évolutive My Love, Lit 140x70 évolutif Commode 2 tiroirs et armoire
    4035: 3922,  # Chambre bébé trio évolutive My Love, Lit 140x70 évolutif Commode XXL et armoire
    4013: 3922,  # Chambre bébé évolutive My Love, Lit 140x70 évolutif et Commode - Chêne Vintage
    3641: 3644,  # Commode 3 tiroirs Mélinée
    3651: 3644,  # Duo lit 120x60cm transformable + commode Mélinée
    3652: 3644,  # Duo lit 140x70 + commode Mélinée
    3663: 3644,  # Trio lit 140x70cm + commode + armoire Mélinée
    3662: 3644,  # Trio évolutif lit 120x60cm transformable + commode + armoire Mélinée
    3218: 3221,  # Commode 3 tiroirs Nature
    3420: 3221,  # Duo lit 120x60 + commode Nature
    3556: 3221,  # Duo lit 140x70 + commode Nature
    3427: 3221,  # Trio lit 120x60 + commode + armoire Nature
    3625: 3631,  # Commode 3 tiroirs 1 porte Paloma
    3626: 3632,  # Commode 3 tiroirs Paloma
    3657: 3632,  # Duo M Paloma lit 120x60cm + commode 3 tiroirs
    3658: 3632,  # Duo M évolutif Paloma lit 120x60cm transformable + commode 3 tiroirs
    3659: 3631,  # Duo XL Paloma évolutif lit 120x60cm transformable + grande commode
    3660: 3631,  # Duo XL Paloma évolutif lit 140x70cm + grande commode
    3669: 3632,  # Trio M Paloma lit 120x60cm + commode 3 tiroirs + armoire
    3670: 3632,  # Trio M évolutif Paloma lit 120x60cm transformable + commode 3 tiroirs + armoire
    3674: 3631,  # Trio XL Paloma évolutif lit 120x60cm transformable + grande commode + armoire
    3675: 3631,  # Trio XL Paloma évolutif lit 140x70cm + grande commode + armoire
    3635: 3638,  # Commode 3 tiroirs Paloma Bois
    3654: 3638,  # Duo lit 120x60cm + commode Paloma Bois
    3655: 3638,  # Duo lit 140x70cm évolutif + commode Paloma Bois
    3667: 3638,  # Trio lit 120x60cm + commode + armoire Paloma Bois
    3665: 3638,  # Trio lit 140x70 + commode + armoire Paloma Bois
    2092: 2094,  # Commode 3 tiroirs Serena
    3152: 2094,  # Duo lit 120x60 + commode Serena
    3610: 2094,  # Duo lit 140x70 + commode Serena
    3173: 2094,  # Trio lit 120x60 + commode + armoire Serena
    2099: 2101,  # Commode 1 porte et 3 tiroirs Seventies version Blanc
    3272: 3275,  # Commode 3 tiroirs 1 porte Sauge Seventies
    3273: 3275,  # Commode 3 tiroirs 1 porte Terracotta Seventies
    3271: 3275,  # Commode 3 tiroirs 1 porte Vanille Seventies
    3151: 2101,  # Duo lit 120x60 + commode Seventies Blanc
    3150: 2101,  # Duo lit 120x60 + commode Seventies Bois Blanc
    3449: 3275,  # Duo lit 140x70 + commode Seventies Sauge
    3450: 3275,  # Duo lit 140x70 + commode Seventies Terracotta
    3448: 3275,  # Duo lit 140x70 + commode Seventies Vanille
    3171: 2101,  # Trio lit 120x60 + commode + armoire Seventies Bois Blanc
    3172: 2101,  # Trio lit 120x60 + commode + commode Seventies Blanc
    3380: 3388,  # Commode 1 porte 3 niches porte Blanche Tokyo
    3382: 3388,  # Commode 1 porte 3 niches porte Sauge Tokyo
    3381: 3388,  # Commode 1 porte 3 niches porte Terracotta Tokyo
    3424: 3388,  # Duo lit 120x60 + commode Tokyo Blanc
    3426: 3388,  # Duo lit 120x60 + commode Tokyo Sauge
    3425: 3388,  # Duo lit 120x60 + commode Tokyo Terracotta
    3553: 3388,  # Duo lit 140x70 + commode Tokyo Blanc
    3555: 3388,  # Duo lit 140x70 + commode Tokyo Sauge
    3554: 3388,  # Duo lit 140x70 + commode Tokyo Terracotta
    3430: 3388,  # Trio lit 120x60 + commode + armoire Tokyo Blanc
    3432: 3388,  # Trio lit 120x60 + commode + armoire Tokyo Sauge
    3431: 3388,  # Trio lit 120x60 + commode + armoire Tokyo Terracotta
    3211: 3215,  # Commode 3 tiroirs Vanille
    3423: 3215,  # Duo lit 120x60 + commode Vanille
    3558: 3215,  # Duo lit 140x70 + commode Vanille
    3429: 3215,  # Trio lit 120x60 + commode + armoire Vanille
}

A_VALIDER = {
    4034: 2789,  # Chambre bébé trio: Lit bébé 70x140 évolutif, commode + armoire — Titre « commode à langer » : vérifier que le plan n’est pas déjà inclus (même prix que 4033)
    4037: 3921,  # Chambre bébé duo évolutive My Love, Lit 140x70 évolutif et Commode à langer 2 tiroirs — Description : « commode … équipée d’un dispositif à langer coulissant » → plan peut-être inclus
    2098: 2101,  # Commode 1 porte et 3 tiroirs Seventies version Bois — Version Bois : 2101 (dessus chêne, joues blanches, comme la version Blanc) ou 3275 (tout chêne doré) ?
}

EXCLUS = {
    2368,  # Commode à langer (plan intégré), aucun plan vendu séparément : Commode à langer évolutive en bureau Nova Argile Douce
    2369,  # Commode à langer (plan intégré), aucun plan vendu séparément : Commode à langer évolutive en bureau Nova Gris Volcan
    2370,  # Commode à langer (plan intégré), aucun plan vendu séparément : Commode à langer évolutive en bureau Nova Blanc Lin
    2387,  # Non commercialisé (prix 0 €) : Commode 3 tiroirs Sixties Bois
    2392,  # Non commercialisé (prix 0 €) : Commode 3 tiroirs Sixties Blanc Bois
    2408,  # Commode à langer (plan intégré), aucun plan vendu séparément : Commode à langer 2 portes 1 niche
    3455,  # Pas de commode dans l’ensemble : DUO LIT CHAMBRE TRANSFORMABLE + ARMOIRE JOY NATUREL
    3457,  # Pas de commode dans l’ensemble : DUO LIT CHAMBRE TRANSFORMABLE + ARMOIRE SMILE HETRE CENDRE
    3458,  # Pas de commode dans l’ensemble : DUO LIT CHAMBRE TRANSFORMABLE + ARMOIRE SMILE CHENE SILEX
    3459,  # Pas de commode dans l’ensemble : DUO LIT CHAMBRE TRANSFORMABLE + ARMOIRE FIRST BLANC
    3460,  # Pas de commode dans l’ensemble : DUO LIT CHAMBRE TRANSFORMABLE + ARMOIRE FIRST BLANC BOIS
    3461,  # Pas de commode dans l’ensemble : DUO LIT CHAMBRE TRANSFORMABLE ETAGERE + ARMOIRE UP CHENE DORE
    3462,  # Pas de commode dans l’ensemble : DUO LIT CHAMBRE TRANSFORMABLE + ARMOIRE UP CHENE DORE
    3463,  # Pas de commode dans l’ensemble : DUO LIT CHAMBRE TRANSFORMABLE ETAGERE + ARMOIRE UP CHENE SILEX
    3464,  # Pas de commode dans l’ensemble : DUO LIT CHAMBRE TRANSFORMABLE + ARMOIRE UP CHENE SILEX
    3656,  # Meuble à langer intégré : Duo XS Paloma lit 120x60cm + meuble à langer
    3661,  # Pas de commode dans l’ensemble : Duo lit chambre transformable + armoire Paloma
    3668,  # Meuble à langer intégré : Trio XS Paloma lit 120x60cm + meuble à langer + armoirette
    3749,  # Plan à langer déjà inclus : Pack Commode 3 tiroirs et Plan à langer Arty
    3750,  # Plan à langer déjà inclus : Pack Commode 1 porte Sauge 3 niches et Plan à langer Tokyo
    3751,  # Plan à langer déjà inclus : Pack Commode 1 porte Terracotta 3 niches et Plan à langer Tokyo
    3752,  # Plan à langer déjà inclus : Pack Commode 1 porte Blanche 3 niches et Plan à langer Tokyo
    3929,  # Commode à langer (plan intégré), aucun plan vendu séparément : Commode à langer évolutive en bureau - Arche - décor bois chêne sépia
    3930,  # Commode à langer (plan intégré), aucun plan vendu séparément : Commode à langer évolutive en bureau - Arche - Caramel
    3931,  # Commode à langer (plan intégré), aucun plan vendu séparément : Commode à langer évolutive en bureau - Arche - Sauge
    3932,  # Commode à langer (plan intégré), aucun plan vendu séparément : Commode à langer évolutive en bureau - Arche - Terracotta
    3958,  # Commode à langer (plan intégré), aucun plan vendu séparément : Chambre bébé complète Basic, Lit 120x60 tout barreaux, Commode à lange
    3959,  # Commode à langer (plan intégré), aucun plan vendu séparément : Chambre bébé complète Basic, Lit 120x60 et Commode à langer - boutons 
    3993,  # Commode à langer (plan intégré), aucun plan vendu séparément : Commode à langer 2 tiroirs et une niche poignées métal - Angèle
    3995,  # Plan à langer déjà inclus : Chambre bébé 2 pièces Angèle, Lit bébé 60x120 à barreaux et Commode à 
    3996,  # Plan à langer déjà inclus : Chambre bébé 3 pièces Angèle, Lit bébé 120x60 à barreaux, Commode à la
    4004,  # Commode à langer (plan intégré), aucun plan vendu séparément : Commode à langer 3 tiroirs avec fronton et pieds bois laqués -  ouvert
    4006,  # Plan à langer déjà inclus : Chambre bébé 2 pièces Milann, Lit bébé 120x60 et Commode à langer + pl
    4007,  # Plan à langer déjà inclus : Chambre bébé 3 pièces Milann, Lit bébé 120x60, Commode à langer et arm
    4010,  # Commode à langer (plan intégré), aucun plan vendu séparément : Commode à langer 3 tiroirs sur pieds - décor bois hêtre cendré - Opali
    4012,  # Plan à langer déjà inclus : Chambre bébé 3 pièces Opaline, Lit bébé 120x60, Commode et Armoire 3 p
    4014,  # Plan à langer déjà inclus : Chambre bébé 2 pièces Opaline, Lit bébé 120x60, Commode + plan à lange
}
