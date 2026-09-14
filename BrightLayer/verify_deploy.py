import json, urllib.request
req = urllib.request.Request('http://127.0.0.1:1880/flows', headers={'Node-RED-API-Version': 'v2'})
with urllib.request.urlopen(req) as resp:
    data = json.loads(resp.read())
flows = data['flows']
tabs = [n for n in flows if n.get('type') == 'tab']
print(f'Total nodes: {len(flows)}')
print('Tabs:')
for t in tabs:
    tab_nodes = [n for n in flows if n.get('z') == t['id']]
    print(f'  [{t["id"]}] "{t["label"]}" — {len(tab_nodes)} nodes')
