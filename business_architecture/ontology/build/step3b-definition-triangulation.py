#!/usr/bin/env python3
"""Step 3b — Definition triangulation, part 1: APQC candidates.

For every process-map node that has no repo description (503 of 680),
find the best-matching APQC Downstream PCF v7.2.2 element by name-token
F1, with APQC hierarchy depth recorded so level-equivalence can be
judged ("the equivalent process and level").

Outputs step3b-definition-review.csv: one row per definition-less node
with the LSC process, its APQC candidate (id, hier, name, description,
match score, level delta), and empty columns for the public-source
triangulation (EIA glossary term/definition/URL, agreement) which is
filled in part 2.

Nothing is written to the ontology here: per the agreed rule,
definitions are adopted only where APQC and a public source AGREE,
and agreement cannot be evaluated until part 2 runs.
"""
import csv
import json
import re
import sys
from pathlib import Path

import openpyxl

HOME = Path.home()
BUILD = HOME / "workspace" / "ontology-build"
IDENTITY_MAP = BUILD / "step2-identity-map.json"
SRC = (HOME / "workspace" / "enterprise-performance-model" / "business_architecture"
       / "business_process" / "downstream_process_map.json")
PCF_XLSX = HOME / "workspace" / "apqc-downstream-pcf-7.2.2.xlsx"

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
    out = set()
    for t in re.findall(r'[a-z0-9]+', text.lower()):
        if t in STOP or len(t) < 3:
            continue
        out.add(ABBR.get(t, t))
    return out


def apqc_depth(hier):
    segs = hier.split('.')
    d = len(segs)
    if segs and segs[-1] == '0':
        d -= 1
    return max(d, 1)


def load_pcf():
    wb = openpyxl.load_workbook(PCF_XLSX, read_only=True, data_only=True)
    pcf = {}
    for ws in wb:
        if ws.title in ('Introduction', 'About', 'Copyright and Attribution'):
            continue
        for row in ws.iter_rows(values_only=True):
            if not row or row[0] == 'PCF ID' or not isinstance(row[0], int):
                continue
            pid, hier = row[0], str(row[1] or '')
            name = str(row[2] or '')
            desc = str(row[6] or '') if len(row) > 6 else ''
            if pid not in pcf or len(hier) < len(pcf[pid]['hier']):
                pcf[pid] = {'hier': hier, 'name': name, 'desc': desc,
                            'depth': apqc_depth(hier),
                            'toks': tokens(name)}
    return pcf


def main():
    rows = json.loads(IDENTITY_MAP.read_text(encoding='utf-8'))
    data = json.loads(SRC.read_text(encoding='utf-8'))

    described = set()

    def walk(n):
        if (n.get('description') or '').strip():
            key = n.get('id') or ('L%d %s' % (n['level'], n['name']))
            described.add(key)
        for c in n.get('children', []):
            walk(c)

    for top in data:
        walk(top)

    needy = [r for r in rows
             if (r['skos_notation'] or ('L%d %s' % (r['level'], r['name'])))
             not in described]
    assert len(needy) == 503, f'expected 503, got {len(needy)}'

    # breadcrumbs for context
    kids = {}
    for r in rows:
        if r['parent_slug']:
            kids.setdefault(r['parent_slug'], []).append(r['slug'])
    by_slug = {r['slug']: r for r in rows}

    def crumb(slug):
        parts, s = [], slug
        while s:
            parts.append(by_slug[s]['name'])
            s = by_slug[s]['parent_slug']
        return ' > '.join(reversed(parts))

    pcf = load_pcf()
    print(f'PCF elements: {len(pcf)}', file=sys.stderr)
    elems = list(pcf.items())

    def f1(a, b):
        if not a or not b:
            return 0.0
        inter = len(a & b)
        if not inter:
            return 0.0
        return 2 * inter / (len(a) + len(b))

    out_rows = []
    hist = {'strong': 0, 'weak': 0, 'none': 0}
    for r in rows_needy_order(needy):
        name_toks = tokens(r['name'])
        full_toks = tokens(r['name'] + ' ' + crumb(r['slug']))
        best, best_pid, best_name_only = 0.0, None, 0.0
        for pid, e in elems:
            s_full = f1(full_toks, e['toks'])
            s_name = f1(name_toks, e['toks'])
            s = max(s_full, s_name)
            if s > best:
                best, best_pid, best_name_only = s, pid, s_name
        e = pcf[best_pid] if best_pid else None
        triage = 'STRONG' if best >= 0.6 else ('WEAK' if best >= 0.35 else 'NONE')
        hist[triage.lower()] += 1
        out_rows.append({
            'slug': r['slug'],
            'level': r['level'],
            'is_stub': 'yes' if r['skos_notation'] == '' else 'no',
            'lsc_name': r['name'],
            'breadcrumb': crumb(r['slug']),
            'triage': triage,
            'apqc_id': best_pid or '',
            'apqc_hier': e['hier'] if e else '',
            'apqc_depth': e['depth'] if e else '',
            'level_delta': (r['level'] - e['depth']) if e and r['level'] >= 1 else '',
            'apqc_name': e['name'] if e else '',
            'apqc_match_score': round(best, 3),
            'apqc_name_only_score': round(best_name_only, 3),
            'apqc_description': (e['desc'] or '').strip() if e else '',
            'eia_term': '',
            'eia_definition': '',
            'eia_url': '',
            'agreement': 'pending',
            'decision': 'NEEDS REVIEW',
            'adopted_definition': '',
            'provenance': '',
        })

    with open(BUILD / 'step3b-definition-review.csv', 'w', newline='',
              encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=list(out_rows[0].keys()))
        w.writeheader()
        w.writerows(out_rows)

    print(f'wrote step3b-definition-review.csv: {len(out_rows)} rows', file=sys.stderr)
    print(f'triage histogram: {hist}', file=sys.stderr)
    # show a few strong candidates for the report
    for o in out_rows:
        if o['triage'] == 'STRONG':
            print(f"  STRONG {o['slug']} [{o['level']}] '{o['lsc_name']}' "
                  f"-> APQC {o['apqc_id']} '{o['apqc_name']}' ({o['apqc_match_score']})",
                  file=sys.stderr)


def rows_needy_order(needy):
    return needy


if __name__ == '__main__':
    main()
