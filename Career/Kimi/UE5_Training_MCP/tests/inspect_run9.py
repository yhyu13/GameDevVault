import json
r = json.load(open('tests/reports/smoke_20260703_142820.json', encoding='utf-8'))
print('=== Summary ===')
print('PASS:', r['summary']['pass'], 'GATED:', r['summary']['gated'], 'FAIL:', r['summary']['fail'])
print('Live tool count:', r['live_tool_count'])
print()
for rec in r['records']:
    if rec['name'] in ('set_property', 'set_visibility', 'set_mobility', 'set_collision', 'snapshot_world', 'summarize_scene'):
        print(f'=== {rec["name"]} ({rec["status"]}) {rec["latency_ms"]}ms ===')
        print('args:', json.dumps(rec['args']))
        print('result:', json.dumps(rec['result'], ensure_ascii=False, indent=2)[:800])
        print()