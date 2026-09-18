#!/usr/bin/env python3
"""Cross-check the repo's downstream process map against APQC Downstream PCF 7.2.2.

Part A: verify every 5-digit PCF ID cited in the repo against the 7.2.2 workbook.
Part B: coverage analysis - token-overlap matching of repo nodes vs PCF elements,
         reported per APQC L1 category and L2 group, for human review.
"""
import json, re, sys
from collections import defaultdict
import openpyxl

REPO = '/home/hatch/workspace/enterprise-performance-model'
PCF_XLSX = '/home/hatch/workspace/apqc-downstream-pcf-7.2.2.xlsx'
MAP_JSON = REPO + '/business_architecture/business_process/downstream_process_map.json'

CITED_IDS = [11434, 25244, 10690, 10075, 24096, 19025, 12897, 12895, 12894,
             12893, 12050, 12000, 10153, 10132, 10047, 10042, 10006]

# ---------- load PCF ----------
wb = openpyxl.load_workbook(PCF_XLSX, read_only=True, data_only=True)
pcf = {}  # pcf_id -> dict
for ws in wb:
    if ws.title in ('Introduction', 'About', 'Copyright and Attribution'):
        continue
    for row in ws.iter_rows(values_only=True):
        if not row or row[0] == 'PCF ID' or not isinstance(row[0], int):
            continue
        pid, hier, name = row[0], str(row[1] or ''), str(row[2] or '')
        desc = str(row[6] or '') if len(row) > 6 else ''
        # keep the shallowest occurrence (Combined sheet repeats category sheets)
        if pid not in pcf or len(hier) < len(pcf[pid]['hier']):
            pcf[pid] = {'hier': hier, 'name': name, 'desc': desc}
print(f'PCF elements loaded: {len(pcf)}', file=sys.stderr)

# ---------- Part A: ID verification ----------
print('\n=== PART A: cited PCF ID verification vs 7.2.2 ===')
for pid in CITED_IDS:
    e = pcf.get(pid)
    if e:
        print(f'{pid}: FOUND  [{e["hier"]}] {e["name"]}')
    else:
        print(f'{pid}: NOT FOUND in 7.2.2')

# ---------- load repo process map ----------
with open(MAP_JSON) as f:
    roots = json.load(f)

nodes = []  # (name, level, cm_id, breadcrumb)
def walk(node, depth, crumb):
    name = node.get('name', '')
    bc = crumb + [name] if name else crumb
    nodes.append({'name': name, 'level': depth,
                  'id': node.get('id'), 'breadcrumb': ' > '.join(bc)})
    for ch in node.get('children', []) or []:
        walk(ch, depth + 1, bc)
for r in roots:
    walk(r, 0, [])
print(f'\nRepo nodes: {len(nodes)}', file=sys.stderr)

# ---------- Part B: coverage ----------
STOP = set('''a an the and or of to in for on with by as at from is are be
was were will would can could should shall may might must do does did have has
had having its it this that these those then than such via per each other own
into out over under between within without within'''.split())
ABBR = {'mgmt': 'management', 'mgt': 'management', 'ops': 'operations',
        'info': 'information', 'tech': 'technology', 'corp': 'corporate',
        'comm': 'communications', 'ehs': 'environment health safety',
        'gov': 'government', 'fin': 'financial', 'hr': 'human resources',
        'it': 'information technology', 'r&d': 'research development'}

def tokens(text):
    toks = re.findall(r'[a-z0-9]+', text.lower())
    out = []
    for t in toks:
        if t in STOP or len(t) < 3:
            continue
        out.append(ABBR.get(t, t))
    return set(out)

repo_toks = [(n, tokens(n['name'] + ' ' + n['breadcrumb'])) for n in nodes]

def best_match(pcf_name, pcf_desc):
    pt = tokens(pcf_name)
    if not pt:
        return 0.0, None
    best, bestn = 0.0, None
    for n, rt in repo_toks:
        if not rt:
            continue
        inter = pt & rt
        # weighted: recall on PCF terms matters most
        score = len(inter) / len(pt)
        if score > best:
            best, bestn = score, n['name']
    return best, bestn

# group PCF elements by L1 category and L2 group
cats = defaultdict(list)
for pid, e in pcf.items():
    l1 = e['hier'].split('.')[0]
    l2 = '.'.join(e['hier'].split('.')[:2])
    cats[(l1, l2)].append((pid, e))

print('\n=== PART B: coverage by APQC L2 group (score = term overlap vs best repo node) ===')
print('score<0.34 flagged as GAP candidate; 0.34-0.6 as THIN; >0.6 COVERED\n')
results = []
for (l1, l2) in sorted(cats):
    elems = cats[(l1, l2)]
    if len(l2.split('.')) < 2 or l2.endswith('.0'):
        label = f'CAT {l1}'
    else:
        # use the L2 element's own name as the group label
        l2e = next((e for pid, e in elems if e['hier'] == l2), None)
        label = f'{l2} {l2e["name"] if l2e else ""}'
    scores = []
    for pid, e in elems:
        if e['hier'] == l2:
            continue  # the group header itself
        s, m = best_match(e['name'], e['desc'])
        scores.append((s, e['hier'], e['name'], m))
    if not scores:
        continue
    avg = sum(s for s, _, _, _ in scores) / len(scores)
    gaps = [(h, nm, m) for s, h, nm, m in scores if s < 0.34]
    status = 'GAP' if avg < 0.34 else ('THIN' if avg < 0.6 else 'COVERED')
    results.append((status, avg, label, len(scores), gaps))
    print(f'[{status:7s}] avg={avg:.2f} n={len(scores):3d}  {label}')
    for h, nm, m in gaps[:6]:
        print(f'           gap: [{h}] {nm}   (best repo hit: {m})')
    if len(gaps) > 6:
        print(f'           ... +{len(gaps)-6} more gap elements')

with open('/home/hatch/workspace/ontology-build/apqc_crosscheck_results.json', 'w') as f:
    json.dump([{'status': s, 'avg': a, 'label': l, 'n': n,
                'gaps': [{'hier': h, 'name': nm, 'repo_hit': m} for h, nm, m in g]}
               for s, a, l, n, g in results], f, indent=1)
print('\nResults saved.', file=sys.stderr)
