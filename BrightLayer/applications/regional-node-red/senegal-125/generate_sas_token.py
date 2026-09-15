"""
Azure IoT Hub SAS Token Generator for BrightLayer (125_Senegal)
================================================================

REQUIREMENTS: Python 3.6+  — uses only standard library (no pip install needed)

HOW TO RUN:
  1. Fill in HOSTNAME below (the IoT Hub hostname — same value you typed into
     the azureiothub node config in Node-RED, e.g. "xxx.azure-devices.net")
  2. Open a terminal in VS Code (Ctrl+`) and run:
         python 125_Senegal/generate_sas_token.py
  3. Copy the printed token (the full "SharedAccessSignature sr=..." line)
  4. In Node-RED, open the mqtt out node → edit its broker config and set:
       Server   : <same HOSTNAME>
       Port     : 8883
       TLS      : ✓ (enabled)
       Client ID: 701821c9-d48d-447f-af3c-f8af38dff8de
       Username : <HOSTNAME>/701821c9-d48d-447f-af3c-f8af38dff8de/?api-version=2021-04-12
       Password : <paste the full SharedAccessSignature token here>
  5. Deploy the flow.

TOKEN VALIDITY:
  Change DAYS_VALID below.  Azure has no enforced maximum — 365 (1 year) is
  a safe default; set to 3650 for ~10 years if you prefer set-and-forget.
"""

import hmac
import hashlib
import base64
import urllib.parse
import time

# ─────────────────────────────────────────────────────────────────────────────
# FILL IN YOUR IoT HUB HOSTNAME (same value as in the azureiothub node config)
HOSTNAME  = "iot-etnblc-rm-ext-prd-weu-p01.azure-devices.net"

# Device credentials — already in your Device Tree V2 node, do not change
DEVICE_ID = "80bab332-eefc-4867-86fa-2b70611329e1"
KEY       = "9iELYZuBPPKap/UoMyEaGCuNiZbVZLy3A+CijmSDckY="

# How long the token should be valid (days).  Max practical: ~3650 (10 years)
DAYS_VALID = 400
# ─────────────────────────────────────────────────────────────────────────────

if HOSTNAME == "YOUR-HUB.azure-devices.net":
    print("ERROR: Please edit this script and set HOSTNAME to your IoT Hub address.")
    print("       Example: HOSTNAME = 'myiothub.azure-devices.net'")
    raise SystemExit(1)

expiry  = int(time.time()) + DAYS_VALID * 24 * 3600
resource = urllib.parse.quote(f"{HOSTNAME}/devices/{DEVICE_ID}", safe="")
string_to_sign = f"{resource}\n{expiry}"

sig = base64.b64encode(
    hmac.new(
        base64.b64decode(KEY),
        string_to_sign.encode("utf-8"),
        hashlib.sha256
    ).digest()
).decode()

token = (
    f"SharedAccessSignature "
    f"sr={resource}"
    f"&sig={urllib.parse.quote(sig, safe='')}"
    f"&se={expiry}"
)

expiry_date = time.strftime("%Y-%m-%d", time.localtime(expiry))
print()
print("=" * 72)
print("MQTT Username (paste into Node-RED broker config):")
print(f"  {HOSTNAME}/{DEVICE_ID}/?api-version=2021-04-12")
print()
print("MQTT Password / SAS Token (paste into Node-RED broker config):")
print(f"  {token}")
print()
print(f"Token valid until: {expiry_date}  ({DAYS_VALID} days from now)")
print("=" * 72)
print()
print("Node-RED mqtt-broker settings:")
print(f"  Server   : {HOSTNAME}")
print(f"  Port     : 8883")
print(f"  TLS      : enabled (verify server cert: ON)")
print(f"  Client ID: {DEVICE_ID}")
print()
