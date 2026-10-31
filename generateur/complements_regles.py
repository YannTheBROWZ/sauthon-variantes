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
    2274: ['ECDR5', 'SADR5', 'TBDR5'],  # Matelas 120x60 Confort Baby — « drap housse Unis les 4 références » (3 au catalogue)
    4136: ['ECDR5', 'SADR5', 'TBDR5'],  # LITTLE BIG BED 140x70 BASILE — « drap housse Unis les 4 références »
    4140: ['ECPN1', 'TBPN1', 'SAPN1'],  # Commode 6 tiroirs et dispositif à langer BOHÈME — « panière ECPN1 ou TBPN1 ou SAPN1 »
    3756: ['PK025'],  # Trousseau maternité pour le bain - Promenons-nous — « Trousseau 1 mois - Promenons-nous »
    3770: ['PK013'],  # Trousseau 1 mois - Promenons-nous — « Trousseau maternité pour le bain - Promenons-nous »
    4164: ['ECML1'],  # Commode 3 tiroirs et dispositif à langer SOLÈNE — « Matelas à langer … uni Vanilla »
    4167: ['899663'],  # Pack duo lit bébé 120x60 et commode SOLÈNE — « Matelas de lit : Matelas 120x60 Confort Baby »
}

# demandes sans référence exploitable (question posée à la cliente)
SANS_REFERENCE = {}
