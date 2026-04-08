"""
Generate trends_filtration.js sorted by displayName,
with all alternative names from ParamsVSDisplayname.csv chained in global.get().
"""
import json
import csv
import re

# ── 1. Load ontology ──────────────────────────────────────────────────────────
with open("Water_filtration_integer_010426.json", "r", encoding="utf-8") as f:
    ontology = json.load(f)

params = ontology["firmware"][0]["parameters"]   # all 183 Trend params

# ── 2. Parse ParamsVSDisplayname.csv ─────────────────────────────────────────
# Format:  Name1, Name2, ...;DisplayName   (semicolon separator)
# Some rows have quoted fields that contain a semicolon — csv handles them.
name_to_row: dict[str, tuple[list[str], str]] = {}

with open("ParamsVSDisplayname_010426.csv", "r", encoding="utf-8") as f:
    reader = csv.reader(f, delimiter=";")
    for row in reader:
        if len(row) < 2:
            continue
        names_str = row[0].strip()
        display_name = row[1].strip()
        if not display_name or names_str.lower() in ("name", ""):
            continue
        names = [n.strip() for n in re.split(r"[,;]", names_str) if n.strip()]
        for n in names:
            name_to_row[n] = (names, display_name)

print(f"CSV lookup entries: {len(name_to_row)}")

# Also build a lowercase → row lookup for case-insensitive fallback
name_to_row_lower = {k.lower(): v for k, v in name_to_row.items()}


def csv_lookup(name: str):
    """Try the name as-is, then normalized variants to find a CSV row."""
    candidates = [
        name,
        name.replace("__", "_"),               # _11__Foo  →  _11_Foo
        name.lstrip("_"),                       # _AlarmFoo →  AlarmFoo
        name.replace("__", "_").lstrip("_"),    # both
        re.sub(r"_position$", "", name, flags=re.IGNORECASE),              # Valves_CIP_position → Valves_CIP
        re.sub(r"_position$", "", name, flags=re.IGNORECASE).lstrip("_"),
        re.sub(r"C$", "", name),                # _BackwashSwitchC → _BackwashSwitch
        re.sub(r"C$", "", name).lstrip("_"),    # strip C then leading _
        re.sub(r"C$", "", name).replace("__", "_").lstrip("_"),
        re.sub(r"(Switch_P\d+)_.+", r"\1", name),  # Switch_P1_Foo → Switch_P1
    ]
    for c in candidates:
        if c in name_to_row:
            return name_to_row[c]
    # Case-insensitive fallback (handles _ctrl_Uvout → ctrl_UVout)
    for c in candidates:
        if c.lower() in name_to_row_lower:
            return name_to_row_lower[c.lower()]
    return None


# ── 3. Build trend list ───────────────────────────────────────────────────────
trends = []
unmatched = []

for p in params:
    name = p.get("name", "")
    tag_id = str(p.get("tagId", ""))
    if not name or not tag_id:
        continue

    result = csv_lookup(name)
    if result:
        csv_names, display_name = result
        # Prepend the actual ontology name if it's not already in the list
        all_names = list(csv_names)
        if name not in all_names:
            all_names = [name] + all_names
    else:
        all_names = [name]
        display_name = p.get("displayName") or name
        unmatched.append(name)

    trends.append({
        "tagId": tag_id,
        "names": all_names,
        "displayName": display_name,
    })

# Sort by displayName (case-insensitive)
trends.sort(key=lambda x: x["displayName"].lower())

if unmatched:
    print(f"WARNING – {len(unmatched)} params not found in CSV (used ontology displayName):")
    for u in unmatched:
        print(f"  {u}")

# ── 4. Render JS ──────────────────────────────────────────────────────────────
HEADER = """\
const now = Math.floor(Date.now() / 1000) - (1000);

msg = {
    'topic': 'telemetry',
    'payload': { "trends": [\
"""

FOOTER = """\
]},
    'properties': [
        {
        'key': 'a', 'value': 'Trends'},
        {
            'key': 'p', 'value': '17272566-5e53-4f19-80a8-bafabbcb2ed6'
        }
    ]
}
return msg;
"""

lines = [HEADER]
for t in trends:
    gets = " || ".join(f'global.get("{n}")' for n in t["names"])
    lines.append(f'{{ "c": "{t["tagId"]}", "t": now, "v": {gets} }}, // {t["displayName"]}')
lines.append(FOOTER)

output = "\n".join(lines)

with open("trends_filtration.js", "w", encoding="utf-8") as f:
    f.write(output)

print(f"Generated {len(trends)} trends → trends_filtration.js")

# ── 5. Export CSV ─────────────────────────────────────────────────────────────
with open("trends_reference.csv", "w", encoding="utf-8", newline="") as f:
    writer = csv.writer(f, delimiter=";")
    writer.writerow(["DisplayName", "c (tagId)", "ParameterNames"])
    for t in trends:
        writer.writerow([t["displayName"], t["tagId"], ", ".join(t["names"])])

print(f"Generated {len(trends)} rows → trends_reference.csv")
