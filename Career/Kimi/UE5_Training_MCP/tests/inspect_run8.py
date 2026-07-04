import json
r = json.load(open('tests/reports/smoke_20260703_133048.json', encoding='utf-8'))
print('=== Summary ===')
print('PASS:', r['summary']['pass'], 'GATED:', r['summary']['gated'], 'FAIL:', r['summary']['fail'])
print()
# Focus on the previously-soft-failing tools
for name in ('snapshot_world', 'restore_world', 'list_blueprints', 'spawn_actor', 'summarize_scene'):
    for rec in r['records']:
        if rec['name'] == name:
            print(f'=== {name} ({rec["status"]}) {rec["latency_ms"]}ms ===')
            print('args:', json.dumps(rec['args']))
            print('result:', json.dumps(rec['result'], ensure_ascii=False, indent=2)[:800])
            print()
            break