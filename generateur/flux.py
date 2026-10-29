"""Télécharge le flux produits et le convertit en rows.json.

Le flux répond parfois « 503 » quelques minutes (trois nuits de suite du 21 au 23/10/2026) : 4 essais en tout, les
nouveaux essais après 2, 5 puis 10 min (jusqu'à ~25 min avec les délais réseau). Un flux presque vide (moins de
MIN_PRODUITS produits, page de maintenance…) compte comme un échec. Si les 4 essais échouent, rien n'est publié
(la version précédente reste en ligne) et GitHub envoie un e-mail d'échec.
"""
import http.client, json, sys, time, urllib.error, urllib.request, xml.etree.ElementTree as ET
URL = 'https://www.sauthon.com/fr/module/xmlfeeds/api?id=8'
NS = {'g': 'http://base.google.com/ns/1.0'}
ATTENTES = (0, 120, 300, 600)       # secondes avant chaque essai
MIN_PRODUITS = 800                   # même seuil que MIN_FLUX dans verifier.py (~1 600 produits aujourd'hui)
ARRET = 'rien n\'est publié, la version précédente reste en ligne.'


def telecharger():
    for n, attente in enumerate(ATTENTES, start=1):
        if attente:
            print(f'Nouvel essai dans {attente // 60} min…', flush=True)
            time.sleep(attente)
        try:
            raw = urllib.request.urlopen(urllib.request.Request(URL, headers={'User-Agent': 'Mozilla/5.0'}), timeout=120).read()
            root = ET.fromstring(raw)
            nb = len(root.findall('.//item'))
            if nb >= MIN_PRODUITS:
                return root
            print(f'Essai {n}/{len(ATTENTES)} : flux trop court ({nb} produits)', flush=True)
        except urllib.error.HTTPError as e:
            if e.code < 500 and e.code not in (408, 429):       # 403, 404… : inutile de réessayer
                sys.exit(f'Flux en erreur HTTP {e.code} : {ARRET}')
            print(f'Essai {n}/{len(ATTENTES)} : flux en erreur HTTP {e.code}', flush=True)
        except (OSError, http.client.HTTPException, ET.ParseError) as e:   # réseau, délai, réponse coupée, XML tronqué
            print(f'Essai {n}/{len(ATTENTES)} : flux illisible ({e})', flush=True)
    sys.exit(f'Flux indisponible après {len(ATTENTES)} essais : {ARRET}')


root = telecharger()
def g(it, t):
    e = it.find('g:' + t, NS)
    return (e.text or '').strip() if e is not None else ''
rows = [dict(id=g(i, 'id'), t=g(i, 'title'), col=g(i, 'custom_label_3'), c0=g(i, 'custom_label_0'), c1=g(i, 'custom_label_1'),
             c2=g(i, 'custom_label_2'), p=g(i, 'price'), sp=g(i, 'sale_price'), av=g(i, 'availability'), link=g(i, 'link'),
             img=g(i, 'image_link'), ref=g(i, 'mpn')) for i in root.findall('.//item')]   # ref = référence produit PrestaShop
json.dump(rows, open('rows.json', 'w'), ensure_ascii=False)
print(len(rows), 'produits')
