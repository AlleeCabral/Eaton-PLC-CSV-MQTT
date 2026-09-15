"""
Rebuild trends_filtration.js directly from trends_reference.csv.
The CSV is the source of truth (DisplayName ; c (tagId) ; ParameterNames).
"""
import csv

OUTPUT_FILE = "trends_filtration.js"
REFERENCE_FILE = "trends_reference.csv"

DEVICE_ID = "17272566-5e53-4f19-80a8-bafabbcb2ed6"

trends = []

with open(REFERENCE_FILE, "r", encoding="utf-8") as f:
    reader = csv.reader(f, delimiter=";")
    header = next(reader)           # skip header row
    for row in reader:
        if len(row) < 3:
            continue
        display_name = row[0].strip()
        tag_id       = row[1].strip()
        names        = [n.strip() for n in row[2].split(",") if n.strip()]
        if not display_name or not tag_id or not names:
            continue
        trends.append({
            "displayName": display_name,
            "tagId": tag_id,
            "names": names,
        })

print(f"Read {len(trends)} entries from {REFERENCE_FILE}")

lines = []
lines.append('const now = Math.floor(Date.now() / 1000) - (1000);')
lines.append('')
lines.append('msg = {')
lines.append("    'topic': 'telemetry',")
lines.append('    \'payload\': { "trends": [')

for t in trends:
    gets = " || ".join(f'global.get("{n}")' for n in t["names"])
    lines.append(f'{{ "c": "{t["tagId"]}", "t": now, "v": {gets} }}, // {t["displayName"]}')

lines.append(']},')
lines.append("    'properties': [")
lines.append("        {")
lines.append("        'key': 'a', 'value': 'Trends'},")
lines.append("        {")
lines.append(f"            'key': 'p', 'value': '{DEVICE_ID}'")
lines.append("        }")
lines.append("    ]")
lines.append("}")
lines.append("return msg;")

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    f.write("\n".join(lines) + "\n")

print(f"Written {len(trends)} trends → {OUTPUT_FILE}")
