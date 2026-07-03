import json
r = json.load(open('tests/reports/smoke_20260702_161807.json', encoding='utf-8'))
print('=== Summary ===')
print('PASS:', r['summary']['pass'], 'GATED:', r['summary']['gated'], 'FAIL:', r['summary']['fail'])
print()
print('=== spawn_actor result (the only FAIL) ===')
for rec in r['records']:
    if rec['name'] == 'spawn_actor':
        print('args:', json.dumps(rec['args']))
        print('result:', json.dumps(rec['result'], ensure_ascii=False, indent=2))
        print('status:', rec['status'])
        break
print()
print('=== set_actor_transform (now against Brush_1, movable) ===')
for rec in r['records']:
    if rec['name'] == 'set_actor_transform':
        print('args:', json.dumps(rec['args']))
        print('result:', json.dumps(rec['result'], ensure_ascii=False, indent=2))
        break
print()
print('=== verify_position (confirms transform actually applied) ===')
for rec in r['records']:
    if rec['name'] == 'verify_position':
        print('args:', json.dumps(rec['args']))
        print('result:', json.dumps(rec['result'], ensure_ascii=False, indent=2))
        break
print()
print('=== GATED payloads ===')
for rec in r['records']:
    if rec['status'] == 'GATED':
        print(f"{rec['name']}: {rec['result']}")