import json
r = json.load(open('tests/reports/smoke_20260702_235345.json', encoding='utf-8'))
print('=== Summary ===')
print('PASS:', r['summary']['pass'], 'GATED:', r['summary']['gated'], 'FAIL:', r['summary']['fail'])
print()
# Focus on the 3 newly-fixed tools
for name in ('snapshot_world', 'restore_world', 'list_blueprints', 'spawn_actor', 'summarize_scene'):
    for rec in r['records']:
        if rec['name'] == name:
            print(f'=== {name} ({rec["status"]}) {rec["latency_ms"]}ms ===')
            print('args:', json.dumps(rec['args']))
            print('result:', json.dumps(rec['result'], ensure_ascii=False, indent=2)[:800])
            print()
            break
# Side-by-side: snapshot_world was called first, then restore_world with same label
# If both work, the level was saved and restored
# Also check summarize_scene's actor_count to confirm clean state
print('=== Actor count by run ===')
for name in ('summarize_scene', 'class_inventory'):
    for rec in r['records']:
        if rec['name'] == name:
            if name == 'summarize_scene':
                count = rec['result'].get('actor_count')
                bp_template_c = next((c['count'] for c in rec['result'].get('top_classes', []) if c['class'] == 'BP_TemplateCube_C'), None)
                print(f'  summarize_scene: actor_count={count}, BP_TemplateCube_C={bp_template_c}')
            if name == 'class_inventory':
                classes = rec['result'].get('classes', [])
                bp_count = sum(1 for c in classes if c['name'].startswith('BP_'))
                print(f'  class_inventory: {len(classes)} classes total, {bp_count} BP_ classes')
            break