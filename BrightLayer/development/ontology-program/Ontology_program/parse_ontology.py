import json
from pathlib import Path

ONTOLOGY_FILE = "Water_filtration_final.json"
FLOWS_FILE = "flows-16.json"
OUTPUT_FILE = "Ontology_new_flow.json"

def load_json(path: str):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def save_json(path: str, data):
    if not isinstance(data, list):
        data = [data]
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def build_trends_func_from_ontology(ontology: dict) -> str:
    """
    Build the JS function body for the 'Trends - Filteration' node
    using all parameters that have a tagId in firmware[0].parameters.
    """
    firmware = ontology.get("firmware", [])
    if not firmware:
        raise ValueError("No firmware array found in ontology")

    params = firmware[0].get("parameters", [])
    tag_entries = []

    for p in params:
        tag_id = p.get("tagId")
        if isinstance(tag_id, int):
            key_value = p.get("keyValue") or p.get("name") or ""
            tag_entries.append((tag_id, key_value))

    # sort by tagId for deterministic order
    tag_entries.sort(key=lambda x: x[0])

    lines = []
    lines.append("const now = Math.floor(Date.now() / 1000);")
    lines.append("")
    lines.append("// Auto-generated from ontology firmware[0].parameters[*].tagId")
    lines.append("const trends = [")

    for tag_id, key_value in tag_entries:
        comment = f" // {key_value}" if key_value else ""
        lines.append(
            f"  {{c: '{tag_id}', t: now, v: global.get('{tag_id}') || 0}},{comment}"
        )

    lines.append("];")
    lines.append("")
    lines.append("msg.topic = 'telemetry';")
    lines.append("msg.payload = { trends };")
    lines.append("")
    lines.append("return msg;")

    return "\n".join(lines)

def update_flows_with_trends(flows, new_func_body: str):
    """
    Find the function node named 'Trends - Filteration' and replace its func.
    """
    found = False
    for node in flows:
        if (
            isinstance(node, dict)
            and node.get("type") == "function"
            and node.get("name") == "Trends - Filteration"
        ):
            node["func"] = new_func_body
            found = True

    if not found:
        raise RuntimeError("Function node 'Trends - Filteration' not found in flows")

    return flows

def main():
    ontology = load_json(ONTOLOGY_FILE)
    flows = load_json(FLOWS_FILE)

    new_func = build_trends_func_from_ontology(ontology)
    updated_flows = update_flows_with_trends(flows, new_func)

    save_json(OUTPUT_FILE, updated_flows)

    print(
        f"Updated 'Trends - Filteration' with {new_func.count('{c:')} tagIds "
        f"and wrote {OUTPUT_FILE}"
    )

if __name__ == "__main__":
    main()
