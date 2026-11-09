"""Télécharge les flux produits espagnol et italien -> rows-es.json et rows-it.json (mêmes champs que rows.json de flux.py),
lus par variantes_langues.py. La génération française ne lit que rows.json : ce script ne peut rien lui changer.

C'est l'identifiant du flux qui choisit la langue (id=11 : espagnol, id=10 : italien ; /es/… et /it/… donnent le même
fichier, vérifié le 05/11/2026). Un flux indisponible, presque vide, tronqué ou dans une autre langue (liens qui ne
commencent pas par https://www.sauthon.com/<langue>/) n'arrête rien : son rows-<langue>.json n'est pas écrit (celui
d'un essai précédent est supprimé), variantes_langues.py garde alors la version publiée de la veille pour cette langue,
et la tâche envoie un e-mail. 2 essais seulement (le flux français en a 4 : le site vient de répondre pour lui), pour ne
pas allonger la tâche. Option --fichier es=<flux.xml> it=<flux.xml> : lecture de flux déjà téléchargés (essais hors ligne).
"""
import http.client, json, os, sys, time, urllib.error, urllib.request, xml.etree.ElementTree as ET

URLS = {'es': 'https://www.sauthon.com/fr/module/xmlfeeds/api?id=11',
        'it': 'https://www.sauthon.com/fr/module/xmlfeeds/api?id=10'}
SITE = 'https://www.sauthon.com/'
NS = {'g': 'http://base.google.com/ns/1.0'}
ATTENTES = (0, 60)                   # secondes avant chaque essai
MIN_PRODUITS = 800                   # même seuil que flux.py et verifier.py (~1 600 produits aujourd'hui)


def g(it, t):
    e = it.find('g:' + t, NS)
    return (e.text or '').strip() if e is not None else ''


def lignes(root):
    # mêmes clés que flux.py
    return [dict(id=g(i, 'id'), t=g(i, 'title'), col=g(i, 'custom_label_3'), c0=g(i, 'custom_label_0'),
                 c1=g(i, 'custom_label_1'), c2=g(i, 'custom_label_2'), p=g(i, 'price'), sp=g(i, 'sale_price'),
                 av=g(i, 'availability'), link=g(i, 'link'), img=g(i, 'image_link'), ref=g(i, 'mpn'))
            for i in root.findall('.//item')]


def probleme(langue, rows):
    """Raison de refuser un flux lu en entier, ou None."""
    dans_la_langue = sum(1 for r in rows if r['link'].startswith(f'{SITE}{langue}/'))
    if dans_la_langue < MIN_PRODUITS:
        return f'{len(rows)} produits, dont {dans_la_langue} avec un lien {SITE}{langue}/ (minimum {MIN_PRODUITS})'
    return None


def sans_prefixe(raw, nom):
    """Texte avant le XML (avertissements PHP « Deprecated: … » du module de flux, vus le 09/11/2026) : ignoré et signalé
    dans le journal ; un XML abîmé plus loin reste refusé par le lecteur."""
    i = raw.find(b'<?xml')
    if i < 0:
        i = raw.find(b'<rss')
    if i > 0:
        print(f'{nom} : {i} octets de texte avant le XML ignorés ({raw[:i].strip()[:80]!r})', flush=True)
        return raw[i:]
    return raw


def lire(langue, fichier=None):
    """Lignes du flux de la langue, ou None après le dernier essai (raison affichée dans le journal)."""
    for n, attente in enumerate((0,) if fichier else ATTENTES, start=1):
        if attente:
            print(f'{langue} : nouvel essai dans {attente} s…', flush=True)
            time.sleep(attente)
        try:
            if fichier:
                raw = open(fichier, 'rb').read()
            else:
                req = urllib.request.Request(URLS[langue], headers={'User-Agent': 'Mozilla/5.0'})
                raw = urllib.request.urlopen(req, timeout=120).read()
            rows = lignes(ET.fromstring(sans_prefixe(raw, langue)))
            raison = probleme(langue, rows)
            if raison is None:
                return rows
            print(f'{langue} essai {n} : flux refusé ({raison})', flush=True)
        except urllib.error.HTTPError as e:
            print(f'{langue} essai {n} : flux en erreur HTTP {e.code}', flush=True)
        except (OSError, http.client.HTTPException, ET.ParseError) as e:   # réseau, délai, réponse coupée, XML tronqué
            print(f'{langue} essai {n} : flux illisible ({e})', flush=True)
    return None


if __name__ == '__main__':
    fichiers = dict(a.split('=', 1) for a in sys.argv[sys.argv.index('--fichier') + 1:]) if '--fichier' in sys.argv else {}
    echecs = []
    for langue in URLS:
        rows = lire(langue, fichiers.get(langue))
        if rows is None:
            if os.path.exists(f'rows-{langue}.json'):
                os.remove(f'rows-{langue}.json')
            echecs.append(langue)
            continue
        json.dump(rows, open(f'rows-{langue}.json', 'w'), ensure_ascii=False)
        print(langue, len(rows), 'produits')
    if echecs:
        sys.exit(f'Flux indisponible : {", ".join(echecs)} (version de la veille gardée pour cette langue, '
                 f'français non concerné).')
