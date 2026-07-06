import re

path = r"C:\Git-repo-my\GameDevVault\Routine\05-技术雷达\_tools\gen_p0_cards.py"
with open(path, "r", encoding="utf-8") as f:
    src = f.read()

marker_start = 'HTML_TEMPLATE = """<!DOCTYPE html>'
marker_end_search = '</html>\n"""'
start = src.find(marker_start)
end = src.find(marker_end_search, start)
if start == -1 or end == -1:
    print("Markers not found!")
    raise SystemExit(1)
end += len(marker_end_search)
print(f"Template block: {start} to {end} ({end-start} chars)")

template = src[start:end]
new_template = template

# 1. JSON dumps -> __XXX_JSON__
new_template = new_template.replace(
    "{json.dumps(entry['drag'], ensure_ascii=False, indent=2)}", "__DRAG_JSON__"
)
new_template = new_template.replace(
    "{json.dumps(entry['single'], ensure_ascii=False, indent=2)}", "__SINGLE_JSON__"
)
new_template = new_template.replace(
    "{json.dumps(entry['multi'], ensure_ascii=False, indent=2)}", "__MULTI_JSON__"
)
new_template = new_template.replace(
    "{json.dumps(entry['tf'], ensure_ascii=False, indent=2)}", "__TF_JSON__"
)

# 2. entry fields -> __TITLE__ etc.
new_template = new_template.replace("{entry['title']}", "__TITLE__")
new_template = new_template.replace("{entry['subtitle']}", "__SUBTITLE__")
new_template = new_template.replace("{entry['source_md']}", "__SOURCE_MD__")

# 3. {{ -> { (f-string escape for literal {)
new_template = new_template.replace("{{", "{")

# 4. }} -> }
new_template = new_template.replace("}}", "}")

new_src = src[:start] + new_template + src[end:]
with open(path, "w", encoding="utf-8") as f:
    f.write(new_src)
print("Done.")
# Verify
print("\n--- First 400 chars of new template ---")
print(new_template[:400])
print("\n--- Last 300 chars of new template ---")
print(new_template[-300:])