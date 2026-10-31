# Sauthon – variantes produits

Données des sélecteurs de variantes (couleur, taille, autres) et de composition (commode seule / duo / trio)
affichés sur les fiches produit de [sauthon.com](https://www.sauthon.com) par un tag Google Tag Manager.

## Fonctionnement

1. **Deux fois par jour** (demandée à 03:15 et 13:40 UTC ; GitHub décale souvent les tâches planifiées, passage du
   matin observé entre 07:40 et 10:45 UTC), la tâche *Régénérer les variantes*
   ([.github/workflows/regenerer.yml](.github/workflows/regenerer.yml)) :
   - télécharge le flux produits du site (`generateur/flux.py`, jusqu'à 4 essais en ~25 min si le flux répond « 503 » ou arrive presque vide) ;
   - lit le contenu réel des packs duo / trio sur les fiches (`generateur/packs.py`) ;
   - regroupe les produits en variantes et compositions (`generateur/regroupement.py`, `generateur/donnees.py`) ;
   - contrôle le résultat (`generateur/verifier.py`) puis publie `docs/variantes.json`.
2. Le fichier est servi par GitHub Pages :
   <https://yannthebrowz.github.io/sauthon-variantes/variantes.json>
   (état de la dernière génération : [status.json](https://yannthebrowz.github.io/sauthon-variantes/status.json)).
3. Le serveur de Sauthon en garde une copie, que lisent les tags GTM : <https://docs.sauthon.com/CRO/variantes.json>
   et <https://docs.sauthon.com/CRO/pour-completer.json> (voir « Copie sur le serveur de Sauthon »).
4. Le tag GTM ([tag/tag-gtm-variantes.html](tag/tag-gtm-variantes.html)) charge ce fichier sur chaque fiche produit.
   Il n'y a rien à republier dans GTM quand le catalogue change.

## Encart « Pour compléter »

Le second tag GTM ([tag/tag-gtm-pour-completer.html](tag/tag-gtm-pour-completer.html)) propose sous le bouton panier
jusqu'à 3 produits : le plan à langer assorti, les matelas (`generateur/matelas.py`, à partir des fiches lues par
`generateur/lire_fiches_matelas.py`) et les compléments demandés par Sauthon par référence produit — draps housse,
housses de matelas à langer, panières… (`generateur/complements_regles.py`), assemblés par `generateur/encart.py`
(liste « l » du fichier publié). **Seules les règles validées par Sauthon sont publiées** (`PUBLIER` dans
`generateur/encart.py`, décision du 31/10/2026 : plans à langer, matelas de lit des lits 120x60 / 140x70, des duos et
des trios, compléments demandés, housses des matelas à langer) ; les autres propositions (matelas à langer, sommiers,
matelas des berceaux et lits junior…) restent « à valider » dans le tableau de validation. Pour en publier une, passer sa
règle à `True`. Une fiche illisible pendant la lecture du site garde sa liste de la veille.
Sa table des plans est publiée à chaque génération dans
<https://yannthebrowz.github.io/sauthon-variantes/pour-completer.json> par `generateur/pour_completer.py` :

- elle part des correspondances validées (`TABLE_VALIDEE` dans `generateur/pour_completer_regles.py`) ;
- retire automatiquement les fiches ou plans à langer sortis du flux (ils reviennent quand ils y reviennent) ;
- ajoute automatiquement les nouveautés sans ambiguïté : un seul plan à langer dans les accessoires PrestaShop
  d'une nouvelle fiche, ou nouveau duo / trio dont la commode a déjà son plan ;
- n'ajoute jamais les fiches de `A_VALIDER` (en attente du client) ni d'`EXCLUS`.

Pour refuser une suggestion ou retirer une correspondance validée, **déplacer la fiche dans `EXCLUS`** (avec la raison) :
simplement supprimée, elle serait republiée la nuit suivante par l'ajout automatique.

Les ajouts et retraits automatiques de la nuit sont listés dans `status.json` (rubrique `pour_completer`).
Le tag retire aussi en direct un produit que le titre de la fiche annonce offert ou inclus (« + plan à langer offert »,
« + matelas offert », « + 2 draps offerts »…).

## Garde-fous

Si le flux reste indisponible après 4 essais, s'il est vide ou tronqué, si le site ne répond pas, ou si le nombre
de produits reliés chute de plus de 25 %
d'une nuit à l'autre, **rien n'est publié** : la version de la veille reste en ligne et GitHub envoie un e-mail
d'échec. Une baisse importante mais légitime du catalogue se valide en relançant la tâche après avoir ajusté
`SEUIL_BAISSE` dans `generateur/verifier.py`.

## Copie sur le serveur de Sauthon

Les visiteurs ne contactent jamais GitHub : les tags lisent la copie de `docs.sauthon.com/CRO/`, que le serveur de
Sauthon récupère depuis GitHub Pages (lien manuel `https://docs.sauthon.com/CRO/synchroniser.php`, en attendant une
tâche planifiée toutes les heures). Conditions pour que les tags affichent quelque chose :

- en-tête `Access-Control-Allow-Origin: https://www.sauthon.com` sur les deux fichiers (sinon le navigateur bloque) ;
- copie à jour : les tags masquent tout seuls les blocs quand les données ont plus de 7 jours (variantes) ou 14 jours
  (« Pour compléter ») ;
- la synchronisation ne remplace un fichier que par un JSON valide et plus récent (date `t`), sans réécrire le `.htaccess`.

## Surveillance

La tâche *Surveiller la copie Sauthon* ([.github/workflows/surveiller.yml](.github/workflows/surveiller.yml),
script [surveillance/surveiller.py](surveillance/surveiller.py)) contrôle `docs.sauthon.com` deux fois par jour
(demandé vers 12:40 et 19:40 UTC, horaires indicatifs). Elle échoue, et GitHub envoie un e-mail d'échec, si un fichier
n'est plus lisible depuis www.sauthon.com (CORS absent, faux ou en double), si son contenu est invalide, s'il est trop
vieux, ou si le certificat HTTPS expire dans moins de 15 jours. Le détail apparaît dans le résumé de l'exécution
(onglet **Actions**). « Trop vieux » dépend du réglage `SURV_SYNCHRO_AUTO` de
[surveiller.yml](.github/workflows/surveiller.yml) :

- `'0'` (tant que le serveur de Sauthon n'est pas synchronisé automatiquement) : échec seulement quand la copie
  approche la coupure des tags (plus de 5 jours pour les variantes, 12 pour l'encart) ; le retard de copie est signalé
  sans échec ;
- `'1'` (dès que la synchronisation horaire tourne) : échec si une génération GitHub n'est pas copiée sous 3 h, ou si
  la copie a plus de 36 h.

Les e-mails d'échec partent vers le compte GitHub qui a modifié en dernier les horaires des tâches : vérifier dans
<https://github.com/settings/notifications> (rubrique *Actions*) que l'envoi par e-mail est activé, pour les échecs
seulement.
Contrôle immédiat : **Actions** > *Surveiller la copie Sauthon* > **Run workflow**.

## Forcer une mise à jour

Onglet **Actions** > *Régénérer les variantes* > **Run workflow**. Toute modification de `generateur/`
relance aussi la génération.

## Corriger un regroupement

Les règles manuelles sont en tête de `generateur/regroupement.py` : `MERGES` (produits à regrouper),
`OVERRIDES` (libellé de couleur / taille forcé), `EXCLUDE` (produits à ignorer), `LINE` (gammes Paloma).
