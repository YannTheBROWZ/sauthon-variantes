# Sauthon – variantes produits

Données des sélecteurs de variantes (couleur, taille, autres) et de composition (commode seule / duo / trio)
affichés sur les fiches produit de [sauthon.com](https://www.sauthon.com) par un tag Google Tag Manager.

## Fonctionnement

1. **Chaque nuit** (03:15 UTC, soit 05:15 l'été / 04:15 l'hiver à Paris), la tâche *Régénérer les variantes*
   ([.github/workflows/regenerer.yml](.github/workflows/regenerer.yml)) :
   - télécharge le flux produits du site (`generateur/flux.py`) ;
   - lit le contenu réel des packs duo / trio sur les fiches (`generateur/packs.py`) ;
   - regroupe les produits en variantes et compositions (`generateur/regroupement.py`, `generateur/donnees.py`) ;
   - contrôle le résultat (`generateur/verifier.py`) puis publie `docs/variantes.json`.
2. Le fichier est servi par GitHub Pages :
   <https://yannthebrowz.github.io/sauthon-variantes/variantes.json>
   (état de la dernière génération : [status.json](https://yannthebrowz.github.io/sauthon-variantes/status.json)).
3. Le tag GTM ([tag/tag-gtm-variantes.html](tag/tag-gtm-variantes.html)) charge ce fichier sur chaque fiche produit.
   Il n'y a rien à republier dans GTM quand le catalogue change.

## Garde-fous

Si le flux est vide ou tronqué, si le site ne répond pas, ou si le nombre de produits reliés chute de plus de 25 %
d'une nuit à l'autre, **rien n'est publié** : la version de la veille reste en ligne et GitHub envoie un e-mail
d'échec. Une baisse importante mais légitime du catalogue se valide en relançant la tâche après avoir ajusté
`SEUIL_BAISSE` dans `generateur/verifier.py`.

## Forcer une mise à jour

Onglet **Actions** > *Régénérer les variantes* > **Run workflow**. Toute modification de `generateur/`
relance aussi la génération.

## Corriger un regroupement

Les règles manuelles sont en tête de `generateur/regroupement.py` : `MERGES` (produits à regrouper),
`OVERRIDES` (libellé de couleur / taille forcé), `EXCLUDE` (produits à ignorer), `LINE` (gammes Paloma).
