"""Données compactes pour le tag « Variantes » : produits (URL + image), groupes de variantes, compositions."""
import json, re, collections
exec(open('regroupement.py').read().split("if __name__")[0])

EAN_PREFIX = '3500760'


def size_key(v):
    if v in SIZE_ORDER:
        return (0, SIZE_ORDER.index(v), 0)
    m = re.match(r'(\d+)x(\d+)', v or '')
    if m:
        return (1, int(m.group(1)), int(m.group(2)))
    m = re.match(r'(\d+)', v or '')
    return (2, int(m.group(1)) if m else 999, 0)


def size_display(v):
    return v + ' cm' if re.fullmatch(r'\d+x\d+', v or '') else (v.replace(' et ', ' et ') + ' cm' if re.fullmatch(r'\d+x\d+ et \d+x\d+', v or '') else v)


BED = {'lit', 'duo', 'trio', 'duo_armoire'}
values, vindex = [], {}


def vid(v):
    if v not in vindex:
        vindex[v] = len(values)
        values.append(v)
    return vindex[v]


out_groups = []
review_groups = []
for gi, g in enumerate(groups):
    dims, mem = g['dims'], g['members']
    vk = lambda d, v: size_key(v) if d == 's' else (0, norm(v), 0)
    mem = sorted(mem, key=lambda m: tuple(vk(d, m[d]) for d in dims))
    labels = []
    for d in dims:
        if d == 'c':
            labels.append(g['attr'])
        elif d == 's':
            labels.append('Taille du lit' if any(m['comp'] in BED for m in mem) else 'Taille')
        else:
            labels.append(DIM_LABELS[d])
    enc = [[m['id']] + [vid(size_display(m[d]) if d == 's' else m[d]) for d in dims] for m in mem]
    orders = []
    for k, d in enumerate(dims):
        vals = sorted({(vk(d, m[d]), e[k + 1]) for m, e in zip(mem, enc)})
        orders.append([v for _, v in vals])
    out_groups.append([[vid(l) for l in labels], orders, enc])
    review_groups.append((gi + 1, labels, dims, mem))

LABELS, lindex = [], {}
comp_lists, comp_index, x = [], {}, {}
for pid, opts in sorted(comp_options.items()):
    enc = []
    for lab, tid in opts:
        if lab not in lindex:
            lindex[lab] = len(LABELS); LABELS.append(lab)
        enc.append([lindex[lab], tid])
    key = json.dumps(enc)
    if key not in comp_index:
        comp_index[key] = len(comp_lists); comp_lists.append(enc)
    x[pid] = comp_index[key]

used = set()
for _, _o, mem in out_groups:
    used |= {m[0] for m in mem}
for pid, opts in comp_options.items():
    used |= {t for _, t in opts} | {pid}

cats, cindex, products = [], {}, {}
for pid in sorted(used):
    it = items[pid]
    cat, slug = it['path'].split('/', 1)
    assert slug.startswith(f'{pid}-'), (pid, slug)
    rest = slug[len(str(pid)) + 1:]
    m = re.fullmatch(rf'product-{EAN_PREFIX}(\d{{6}})', rest)
    if cat not in cindex:
        cindex[cat] = len(cats); cats.append(cat)
    products[pid] = [cindex[cat], int(m.group(1)) if m else rest, it['imgid'] or 0]
    # vérif : reconstruction identique
    rebuilt = f"{cat}/{pid}-" + (f"product-{EAN_PREFIX}{products[pid][1]:06d}" if m else rest)
    assert rebuilt == it['path'], (rebuilt, it['path'])

data = {'c': cats, 'v': values, 'l': LABELS, 'p': products, 'g': out_groups, 'x': x, 'xl': comp_lists}
raw = json.dumps(data, ensure_ascii=False, separators=(',', ':'))
open('variants_data.json', 'w').write(raw)
json.dump({'review_groups': [(n, l, d, [m['id'] for m in mem]) for n, l, d, mem in review_groups]},
          open('variants_review.json', 'w'), ensure_ascii=False)
if __name__ == '__main__':
    print('produits', len(products), '| groupes', len(out_groups), '| compositions', len(x), '| listes', len(comp_lists))
    print('JSON compact :', len(raw.encode()), 'octets')
    for k in data:
        print('  ', k, len(json.dumps(data[k], ensure_ascii=False, separators=(',', ':')).encode()))
