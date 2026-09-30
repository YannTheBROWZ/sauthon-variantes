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

## Encart « Pour compléter »

Le second tag GTM ([tag/tag-gtm-pour-completer.html](tag/tag-gtm-pour-completer.html)) propose le plan à langer
assorti sous le bouton panier des commodes, duos et trios. Sa table est publiée chaque nuit dans
<https://yannthebrowz.github.io/sauthon-variantes/pour-completer.json> par `generateur/pour_completer.py` :

- elle part des correspondances validées (`TABLE_VALIDEE` dans `generateur/pour_completer_regles.py`) ;
- retire automatiquement les fiches ou plans à langer sortis du flux (ils reviennent quand ils y reviennent) ;
- ajoute automatiquement les nouveautés sans ambiguïté : un seul plan à langer dans les accessoires PrestaShop
  d'une nouvelle fiche, ou nouveau duo / trio dont la commode a déjà son plan ;
- n'ajoute jamais les fiches de `A_VALIDER` (en attente du client) ni d'`EXCLUS`.

Pour refuser une suggestion ou retirer une correspondance validée, **déplacer la fiche dans `EXCLUS`** (avec la raison) :
simplement supprimée, elle serait republiée la nuit suivante par l'ajout automatique.

Les ajouts et retraits automatiques de la nuit sont listés dans `status.json` (rubrique `pour_completer`).
Le tag masque aussi l'encart en direct quand le titre de la fiche annonce « + plan à langer offert ».

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
