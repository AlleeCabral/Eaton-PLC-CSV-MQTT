#!/usr/bin/env python3
"""deploy_to_nodered.py — POST full_program_nodered + Simulation_RO to Node-RED."""
import json
import urllib.request
import urllib.error

FULL_PROG = r'peru_148/full_program_nodered'
SIM_FILE  = r'Simulation/Simulation_RO.json'
NR_URL    = 'http://127.0.0.1:1880'

with open(FULL_PROG, 'r', encoding='utf-8') as f:
    full = json.load(f)
with open(SIM_FILE, 'r', encoding='utf-8') as f:
    sim = json.load(f)

combined = full + sim
print(f"Full program nodes : {len(full)}")
print(f"Simulation nodes   : {len(sim)}")
print(f"Total to deploy    : {len(combined)}")

# Get current rev
req = urllib.request.Request(f'{NR_URL}/flows', headers={'Node-RED-API-Version': 'v2'})
with urllib.request.urlopen(req) as resp:
    current = json.loads(resp.read())
rev = current.get('rev', '')
print(f"Current NR rev     : {rev}")

# POST /flows
body = json.dumps({'flows': combined, 'rev': rev}).encode('utf-8')
post = urllib.request.Request(
    f'{NR_URL}/flows',
    data=body,
    method='POST',
    headers={'Content-Type': 'application/json', 'Node-RED-API-Version': 'v2'}
)
try:
    with urllib.request.urlopen(post) as resp:
        result = json.loads(resp.read())
        new_rev = result.get('rev', str(result))
        print(f"DEPLOY OK — new rev: {new_rev}")
except urllib.error.HTTPError as e:
    body_err = e.read().decode()
    print(f"HTTP ERROR {e.code}: {body_err}")
