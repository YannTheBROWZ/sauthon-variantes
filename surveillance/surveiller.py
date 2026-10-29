"""Surveille la copie des données servie par le serveur de Sauthon (docs.sauthon.com/CRO/), que lisent les tags GTM.

La tâche échoue, et GitHub envoie un e-mail d'échec, si l'un des deux fichiers :
- ne répond pas en 200 avec un JSON lisible et complet (date de génération « t » comprise) ;
- n'autorise plus www.sauthon.com à le lire : en-tête CORS absent, faux ou en double (les tags n'affichent plus rien) ;
- dépasse la taille acceptée par les tags ;
- est trop vieux, selon le mode réglé par SURV_SYNCHRO_AUTO dans surveiller.yml :
  · « 0 » (le serveur de Sauthon n'est pas encore synchronisé automatiquement) : échec seulement quand la copie
    approche la coupure des tags (5 jours pour les variantes, 12 pour l'encart ; les tags masquent tout à 7 et 14 jours) ;
  · « 1 » (synchronisation horaire en place) : échec si une génération GitHub n'est pas copiée 3 h après, ou si la
    copie a plus de 36 h ;
ou si le certificat HTTPS de docs.sauthon.com expire dans moins de 15 jours.
Signale aussi, sans échouer : retard de copie, lenteur, compression absente, cache désactivé, type de contenu inattendu.
Les fichiers sont lus exactement comme les tags les lisent (même adresse, en-tête Origin).
"""
import datetime, hashlib, json, math, os, socket, ssl, sys, time, urllib.error, urllib.parse, urllib.request

SERVEUR = os.environ.get('SURV_SERVEUR', 'https://docs.sauthon.com/CRO/')
SOURCE = os.environ.get('SURV_SOURCE', 'https://yannthebrowz.github.io/sauthon-variantes/')
SYNCHRO_AUTO = os.environ.get('SURV_SYNCHRO_AUTO', '0') == '1'
RETARD_MAX_H = float(os.environ.get('SURV_RETARD_MAX_H', '3'))
ORIGINE = 'https://www.sauthon.com'
# fichier : (clés attendues, taille maximale acceptée par les tags, coupure des tags en jours)
FICHIERS = {'variantes.json': ({'c', 'v', 'l', 'p', 'g', 'x', 'xl'}, 300000, 7),
            'pour-completer.json': ({'map', 'plans'}, 50000, 14)}
AGE_MAX_H_AUTO, MARGE_COUPURE_J, CERT_MIN_JOURS, LENT_S = 36, 2, 15, 2.5

echecs, alertes, infos = [], [], []
maintenant = time.time()


def heure(t):
    return datetime.datetime.fromtimestamp(t, datetime.timezone.utc).strftime('%d/%m %H:%M UTC')


def lire(url, entetes=None, essais=3):
    """(statut, en-têtes {nom en minuscules: [valeurs]}, corps, durée du dernier essai en s)."""
    for n in range(essais):
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (surveillance Sauthon)', **(entetes or {})})
        debut = time.time()
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                h = {}
                for k, v in r.headers.items():                    # garde les en-têtes en double
                    h.setdefault(k.lower(), []).append(v)
                return r.status, h, r.read(), time.time() - debut
        except urllib.error.HTTPError as e:
            if n == essais - 1:
                return e.code, {k.lower(): [v] for k, v in e.headers.items()}, b'', time.time() - debut
        except Exception as e:                                   # réseau : on réessaie avant de conclure
            if n == essais - 1:
                return 0, {}, str(e).encode(), time.time() - debut
        time.sleep(20)


def refuser_constante(c):
    raise ValueError(f'valeur {c} interdite en JSON')


def contenu(nom, corps):
    """(données, erreur) en lisant le JSON comme un navigateur (BOM toléré, NaN/Infinity refusés)."""
    cles, taille_max, _ = FICHIERS[nom]
    if len(corps) > taille_max:
        return None, f'{len(corps)} octets (les tags refusent au-delà de {taille_max})'
    try:
        d = json.loads(corps.decode('utf-8-sig'), parse_constant=refuser_constante)
    except Exception as e:
        return None, f'JSON illisible ({e})'
    if not isinstance(d, dict) or not cles <= set(d):
        return None, f'clés manquantes : {sorted(cles - set(d)) if isinstance(d, dict) else "pas un objet"}'
    t = d.get('t')
    if isinstance(t, bool) or not isinstance(t, (int, float)) or not math.isfinite(t):
        return None, 'date de génération « t » absente ou invalide (les tags ne limiteraient plus son âge)'
    return d, None


def controler(nom):
    cles, taille_max, coupure_j = FICHIERS[nom]
    statut, h, corps, duree = lire(SERVEUR + nom, {'Origin': ORIGINE})
    if statut != 200:
        echecs.append(f'{nom} : le serveur répond {statut or "rien"}'
                      + (f' ({corps[:120].decode("utf-8", "replace")})' if not statut else '') + '.')
        return
    if duree > LENT_S:
        alertes.append(f'{nom} : réponse lente ({duree:.1f} s ; les tags renoncent au-delà de 5 s).')
    acao = [v.strip() for v in h.get('access-control-allow-origin', [])]
    if len(acao) != 1 or acao[0] not in (ORIGINE, '*'):
        echecs.append(f'{nom} : en-tête CORS « Access-Control-Allow-Origin » '
                      + ('absent' if not acao else f'en double ({", ".join(acao)})' if len(acao) > 1 else f'= {acao[0]}')
                      + f' : les navigateurs bloquent la lecture depuis {ORIGINE}, les tags n\'affichent plus rien.')
    if 'json' not in ' '.join(h.get('content-type', [])):
        alertes.append(f'{nom} : type de contenu inattendu ({h.get("content-type")}).')
    d, erreur = contenu(nom, corps)
    if erreur:                                                   # relecture : copie peut-être en cours d'écriture
        time.sleep(15)
        statut, h, corps, _ = lire(SERVEUR + nom, {'Origin': ORIGINE})
        d, erreur = contenu(nom, corps) if statut == 200 else (None, f'le serveur répond {statut}')
    if erreur:
        echecs.append(f'{nom} sur le serveur : {erreur}.')
        return
    t = d['t']
    age_h = (maintenant - t) / 3600
    if SYNCHRO_AUTO and age_h > AGE_MAX_H_AUTO:
        echecs.append(f'{nom} sur le serveur date du {heure(t)} ({age_h:.0f} h) : la synchronisation horaire ne tourne plus.')
    elif age_h > (coupure_j - MARGE_COUPURE_J) * 24:
        echecs.append(f'{nom} sur le serveur date du {heure(t)} ({age_h / 24:.1f} jours) : les tags masqueront tout à '
                      f'{coupure_j} jours. Lancer la synchronisation du serveur.')
    # comparaison avec la version publiée par GitHub (cache GitHub Pages : jusqu'à 10 min de retard, sans conséquence)
    s_statut, _, s_corps, _ = lire(SOURCE + nom)
    s, s_erreur = contenu(nom, s_corps) if s_statut == 200 else (None, f'GitHub répond {s_statut}')
    if s_erreur:
        alertes.append(f'{nom} : version GitHub illisible ({s_erreur}), comparaison impossible.')
    else:
        if (maintenant - s['t']) / 3600 > AGE_MAX_H_AUTO:
            echecs.append(f'{nom} : la dernière génération GitHub date du {heure(s["t"])} : la tâche de génération est en panne.')
        retard_h = (maintenant - s['t']) / 3600
        if s['t'] > t:
            message = (f'{nom} : le serveur a la version du {heure(t)}, GitHub celle du {heure(s["t"])} '
                       f'(publiée il y a {retard_h:.1f} h).')
            if SYNCHRO_AUTO and retard_h > RETARD_MAX_H:
                echecs.append(message + ' La synchronisation horaire ne tourne plus.')
            elif retard_h > RETARD_MAX_H or age_h > 6:
                alertes.append(message + ('' if SYNCHRO_AUTO else ' Pas encore de synchronisation automatique : copie manuelle à faire.'))
            else:
                infos.append(message + ' Copie attendue sous peu.')
        elif s['t'] == t and hashlib.sha256(corps).digest() != hashlib.sha256(s_corps).digest():
            alertes.append(f'{nom} : même date que GitHub mais contenu différent (copie altérée ?).')
        else:
            infos.append(f'{nom} : à jour (génération du {heure(t)}), CORS {acao[0] if acao else "absent"}, {duree:.2f} s.')
    # bonnes pratiques (sans échec)
    _, hz, _, _ = lire(SERVEUR + nom, {'Origin': ORIGINE, 'Accept-Encoding': 'gzip, br'})
    if not hz.get('content-encoding'):
        alertes.append(f'{nom} : pas de compression ({len(corps) // 1024} Ko retéléchargés à chaque fiche vue).')
    cache = ', '.join(h.get('cache-control', []))
    if 'no-store' in cache or not cache:
        alertes.append(f'{nom} : cache désactivé (Cache-Control : {cache or "absent"}).')


def controler_certificat():
    hote = urllib.parse.urlparse(SERVEUR).hostname
    with socket.create_connection((hote, 443), timeout=20) as sock:
        with ssl.create_default_context().wrap_socket(sock, server_hostname=hote) as tls:
            fin = ssl.cert_time_to_seconds(tls.getpeercert()['notAfter'])
    jours = (fin - maintenant) / 86400
    (echecs if jours < CERT_MIN_JOURS else alertes if jours < 30 else infos).append(
        f'Certificat HTTPS de {hote} : expire le {heure(fin)} (dans {jours:.0f} jours).')


for nom_ in FICHIERS:
    try:
        controler(nom_)
    except Exception as e:                                       # toute erreur imprévue devient un échec lisible
        echecs.append(f'{nom_} : contrôle impossible ({type(e).__name__} : {e}).')
try:
    controler_certificat()
except Exception as e:
    echecs.append(f'Certificat HTTPS illisible : {e}')

mode = 'synchronisation horaire en place' if SYNCHRO_AUTO else 'synchronisation manuelle (pas encore automatique)'
rapport = ['# Surveillance de docs.sauthon.com', '', f'Mode : {mode}.', '']
rapport += [f'- ❌ {x}' for x in echecs] + [f'- ⚠️ {x}' for x in alertes] + [f'- ✅ {x}' for x in infos]
rapport += ['', 'Résultat : ' + ('ÉCHEC — les tags risquent de ne plus rien afficher.' if echecs else 'OK.')]
print('\n'.join(rapport))
for x in echecs:                                                 # motif visible directement sur la page de l'exécution
    print(f'::error::{x}')
for x in alertes:
    print(f'::warning::{x}')
if os.environ.get('GITHUB_STEP_SUMMARY'):
    with open(os.environ['GITHUB_STEP_SUMMARY'], 'a', encoding='utf-8') as f:
        f.write('\n'.join(rapport) + '\n')
sys.exit(1 if echecs else 0)
