"""Draft-first firing and harm on M H4 (PLAN: preregistered firing/harm metric, stratified by model and H4 variant).
Firing: entity names rows served in H4 cells whose record list holds a DRAFT amendment row; draft-first = a draft row precedes
every executed (non-draft) record row. Harm: wrong-value (said_wrong) and success on H4 cells whose task has a draft-led item
(the account's newest amendment/contract document is a draft), arm vs control on the same cells. Counts only."""
import json, collections, os, re
R = os.path.expanduser('~/.capy/work/devprep/r1-out/r1')
w = json.load(open(os.path.expanduser('~/.capy/work/mworld/world/world.json')))
ent = {e['id']: e for e in w['entities']}
docs = [d for d in w['docs'] if d['type'] in ('amendment', 'contract')]
def account_docs(eid):
    e = ent[eid]; keys = [e['name']] + list(e['refs'].get('codes', []))
    return [d for d in docs if any(re.search(r'(:|\b)\s*' + re.escape(k) + r'\s*$', d['title']) for k in keys)]
draft_led_items = 0; items = 0; task_draft = {}
for t in w['tasks']:
    if t['family'] != 'H4': continue
    n = 0
    for it in t['gold']['items']:
        items += 1; ds = sorted(account_docs(it['account']), key=lambda d: d['date'])
        if ds and 'draft' in ds[-1]['title'].lower(): n += 1
    draft_led_items += n; task_draft[t['id']] = n > 0
print(f'M H4 items with a draft-led newest-first list: {draft_led_items}/{items}; tasks with one: {sum(task_draft.values())}/{len(task_draft)}')
def canon(path):
    out = {}
    for l in open(path):
        r = json.loads(l)
        if r['stop'] != 'harness_error': out[r['key']] = r
    return out
out = {}
arms = ['control', 'all-on', 'f5', 'f1', 'f1-no-names-row', 'f2', 'f4']
cells = {a: canon(f'{R}/{a}/attempts.jsonl') for a in arms}
for a in arms:
    canon_ids = {r['attempt_id'] for r in cells[a].values()}
    meta = {r['attempt_id']: r for r in cells[a].values()}
    fire = collections.defaultdict(lambda: collections.Counter())
    for l in open(f'{R}/{a}/transcripts.jsonl'):
        tr = json.loads(l)
        if tr['attempt_id'] not in canon_ids: continue
        r = meta[tr['attempt_id']]
        if r['family'] != 'H4': continue
        strata = [('all',), ('model', r['model']), ('long', '+long' in r['variant']), ('draft_task', task_draft[r['task']])]
        cell_df = False
        for tool in tr['tools']:
            if tool['name'] != 'entity' or not isinstance(tool['args'].get('names'), list): continue
            try: js = json.loads(tool['result'][:tool['result'].rfind('}') + 1])
            except Exception: continue
            stack = [x for x in js.get('results', []) if isinstance(x, dict)]
            while stack:
                row = stack.pop(); stack += [s for s in row.get('siblings', []) or [] if isinstance(s, dict)]
                flat = [x for g in row.get('records', []) or [] if isinstance(g, dict) for x in g.get('rows', []) or []]
                if not flat: continue
                isd = ['draft' in str(x.get('title', '')).lower() for x in flat]
                for s in strata:
                    fire[s]['rows_with_records'] += 1
                    if any(isd):
                        fire[s]['rows_with_draft'] += 1
                        if isd.index(True) < (isd.index(False) if False in isd else len(isd)): fire[s]['draft_first'] += 1
                if any(isd) and isd[0]: cell_df = True
        for s in strata:
            fire[s]['h4_cells'] += 1; fire[s]['cells_served_draft_first'] += cell_df
    harm = {}
    for label, pred in [('draft_tasks', lambda t: task_draft[t]), ('other_tasks', lambda t: not task_draft[t])]:
        ks = [k for k, r in cells[a].items() if r['family'] == 'H4' and pred(r['task'])]
        ck = {k.replace(f"|{cells[a][k]['arm']}|", '|'): k for k in ks}
        ctl = {k.replace(f"|{r['arm']}|", '|'): r for k, r in cells['control'].items()}
        for m in ['all'] + sorted({cells[a][k]['model'] for k in ks}):
            sel = [x for x in ck if m == 'all' or cells[a][ck[x]]['model'] == m]
            harm[f'{label}:{m}'] = {'n': len(sel), 'wrong': sum(bool(cells[a][ck[x]]['score'].get('said_wrong')) for x in sel), 'success': sum(cells[a][ck[x]]['score']['success'] for x in sel),
                                   'ctl_wrong': sum(bool(ctl[x]['score'].get('said_wrong')) for x in sel), 'ctl_success': sum(ctl[x]['score']['success'] for x in sel)}
    out[a] = {'firing': {'|'.join(map(str, k)): dict(v) for k, v in fire.items()}, 'harm': harm}
json.dump({'draft_led_items': draft_led_items, 'h4_items': items, 'arms': out}, open(os.path.expanduser('~/.capy/work/devprep/r1-draft-first.json'), 'w'), indent=1)
for a, v in out.items():
    f = v['firing']; g = f.get('all', {})
    print(f"{a:16s} rows_w_records {g.get('rows_with_records',0):4d} w_draft {g.get('rows_with_draft',0):4d} draft_first {g.get('draft_first',0):4d} cells_served_df {g.get('cells_served_draft_first',0)}/{g.get('h4_cells')}",
          ' by model', {k.split('|')[1].split('-')[1] if 'claude' in k else 'sol': v2.get('draft_first', 0) for k, v2 in f.items() if k.startswith('model')},
          ' long', {k: v2.get('draft_first', 0) for k, v2 in f.items() if k.startswith('long')})
    h = v['harm']; print('   harm draft_tasks', {k.split(':')[1]: f"W{x['wrong']}/c{x['ctl_wrong']} S{x['success']}/c{x['ctl_success']} n{x['n']}" for k, x in h.items() if k.startswith('draft')}, ' other', {k.split(':')[1]: f"W{x['wrong']}/c{x['ctl_wrong']} n{x['n']}" for k, x in h.items() if k == 'other_tasks:all'})

print('\nHarm on cells where the arm served a draft-first names row (arm vs control, same model+task):')
ctl = {(r['model'], r['task']): r for r in cells['control'].values()}
served = {}
for a in ['all-on', 'f1', 'f1-no-names-row']:
    ids = {r['attempt_id']: r for r in cells[a].values() if r['family'] == 'H4'}
    hit = set()
    for l in open(f'{R}/{a}/transcripts.jsonl'):
        tr = json.loads(l); r = ids.get(tr['attempt_id'])
        if not r: continue
        for tool in tr['tools']:
            if tool['name'] == 'entity' and isinstance(tool['args'].get('names'), list) and '"DRAFT' in tool['result'].upper().replace('\\"', '"'):
                try: js = json.loads(tool['result'][:tool['result'].rfind('}') + 1])
                except Exception: continue
                stack = [x for x in js.get('results', []) if isinstance(x, dict)]
                while stack:
                    row = stack.pop(); stack += [s for s in row.get('siblings', []) or [] if isinstance(s, dict)]
                    flat = [x for g in row.get('records', []) or [] if isinstance(g, dict) for x in g.get('rows', []) or []]
                    if flat and 'draft' in str(flat[0].get('title', '')).lower(): hit.add((r['model'], r['task']))
    by = collections.defaultdict(lambda: [0, 0, 0, 0, 0])
    for k in hit:
        r = next(x for x in ids.values() if (x['model'], x['task']) == k)
        for m in ('all', k[0]):
            b = by[m]; b[0] += 1; b[1] += bool(r['score'].get('said_wrong')); b[2] += bool(ctl[k]['score'].get('said_wrong')); b[3] += r['score']['success']; b[4] += ctl[k]['score']['success']
    served[a] = {m: dict(zip(['n', 'wrong', 'ctl_wrong', 'success', 'ctl_success'], v)) for m, v in by.items()}
    print(f'{a:16s}', {m.split("-")[1] if "claude" in m else m.replace("gpt-6.1-", ""): f"n{v[0]} W{v[1]}/c{v[2]} S{v[3]}/c{v[4]}" for m, v in sorted(by.items())})
d = json.load(open(os.path.expanduser('~/.capy/work/devprep/r1-draft-first.json'))); d['harm_on_served_draft_first_cells'] = served
json.dump(d, open(os.path.expanduser('~/.capy/work/devprep/r1-draft-first.json'), 'w'), indent=1)
