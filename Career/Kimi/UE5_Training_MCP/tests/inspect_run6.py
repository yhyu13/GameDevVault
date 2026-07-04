import json
r = json.load(open('tests/reports/smoke_20260702_233944.json', encoding='utf-8'))
print('=== Summary ===')
print('PASS:', r['summary']['pass'], 'GATED:', r['summary']['gated'], 'FAIL:', r['summary']['fail'])
print()
for rec in r['records']:
    name = rec['name']
    status = rec['status']
    lat = rec['latency_ms']
    print(f'=== {name} ({status}) {lat}ms ===')
    print('args:', json.dumps(rec['args']))
    print('result:', json.dumps(rec['result'], ensure_ascii=False, indent=2)[:600])
    print()