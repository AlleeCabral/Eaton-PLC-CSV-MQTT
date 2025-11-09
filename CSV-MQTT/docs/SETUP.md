# SETUP Guide - CSV-MQTT PLC Project

**Complete installation and configuration instructions**

---

## 📋 Prerequisites

- CODESYS v3.5.x installed
- Eaton PLC connected
- CSV file prepared (13 columns, semicolon-delimited)
- Internet connection (for cloud MQTT broker)

---

## 🔢 Step 1: Import Files to CODESYS

**⚠️ IMPORTANT: Import in this exact order to avoid dependency errors**

1. **ST_CSVRow.st** (DUT)
2. **F_AssignField.st** (Function)
3. **F_GetNextLine.st** (Function)
4. **F_ParseCSVLine.st** (Function)
5. **F_BuildJsonFromRow.st** (Function)
6. **FB_CSVReader.st** (Function Block)
7. **FB_MQTTPublisher.st** (Function Block)
8. **PLC_PRG.st** (Program)

**How to import:**
```
Project → Add Object → Existing Object → Browse to .st file → Open
```

---

## 📚 Step 2: Add Required Libraries

**Library Manager → Add Library:**

| Library Name | Version | Notes |
|-------------|---------|-------|
| SysFile | v3.5.17.0 or later | For file operations |
| IotMqtt or MQTT | Latest available | MQTT client (name varies by installation) |
| Standard | Latest | Basic functions |
| SysTypes | Latest | System types |

**How to add:**
```
Project → Library Manager → Add Library → 
Search for library → Select version → OK
```

---

## ⚙️ Step 3: Configure PLC_PRG Variables

Open `PLC_PRG.st` and set these values:

### File Configuration
```st
sCSVFilePath := '/usr/data.csv';  // ← Change to your CSV file path
```

### Connection Mode
```st
xUseLaptopMode := TRUE;  // ← TRUE for laptop gateway, FALSE for router
```

### MQTT Broker (both modes use cloud broker)
```st
// Already configured in FB_MQTTPublisher:
// sBrokerLaptop := 'broker.hivemq.com';
// sBrokerLAN := 'broker.hivemq.com';
// uiPort := 1883;
```

### Topic Configuration
```st
// In FB_MQTTPublisher default:
// sTopic := 'UE/139ukr';  // ← Change if needed
```

---

## 📄 Step 4: Prepare CSV File

### Required Format
```csv
Header1;Header2;Header3;Header4;Header5;Header6;Header7;Header8;Header9;Header10;Header11;Header12;Header13
value1;value2;value3;value4;value5;value6;value7;value8;value9;value10;value11;value12;value13
value1;value2;value3;value4;value5;value6;value7;value8;value9;value10;value11;value12;value13
```

### Rules
- ✅ **Delimiter**: Semicolon (`;`)
- ✅ **Columns**: Exactly 13
- ✅ **First row**: Header (automatically skipped)
- ✅ **Quotes**: Use for fields containing semicolons: `"field;with;semicolons"`
- ✅ **Line endings**: CRLF or LF (both supported)
- ✅ **Max file size**: ~4KB (can be increased by adjusting buffer)

### Upload to PLC
```
1. CODESYS: Tools → Device → File Browser
2. Navigate to /usr/ (or your configured path)
3. Right-click → Upload File
4. Select your CSV file
5. Verify upload complete
```

---

## 🌐 Step 5: Network Configuration

**Choose your connection mode and follow the corresponding guide in [NETWORK.md](NETWORK.md):**

- **Option A**: Laptop Gateway (for development/testing)
- **Option B**: Industrial Router + Home Router (for production)

### Quick Summary

**Laptop Mode:**
- PLC IP: `192.168.137.2`
- Gateway: `192.168.137.1`
- DNS: `8.8.8.8`
- Code: `xUseLaptopMode := TRUE`

**Router Mode:**
- PLC IP: `192.168.10.204`
- Gateway: `192.168.10.1`
- DNS: `8.8.8.8`
- Code: `xUseLaptopMode := FALSE`

---

## 🏗️ Step 6: Build Project

```
Build → Build (or F11)
```

**Check for errors:**
- ✅ All libraries found
- ✅ No syntax errors
- ✅ All dependencies resolved

**Common build errors:**
- ❌ "Library not found" → Add library in Library Manager
- ❌ "Type mismatch" → Check if IotMqtt vs MQTT library name
- ❌ "Unknown identifier" → Check import order

---

## 📥 Step 7: Download to PLC

```
Online → Login
Online → Download
```

**Download options:**
- ✅ Download all
- ✅ Start after download: Optional (you can start manually)

---

## ▶️ Step 8: Start System

### In CODESYS Online Mode

1. **Go to PLC_PRG in online view**
2. **Set enable flag**:
   ```st
   xSystemEnable := TRUE
   ```
3. **Monitor status variables**:
   - `eMainState` should progress: IDLE → INIT_MQTT → WAIT_CONNECT → READING_CSV
   - `fbMQTT.xConnected` should become TRUE
   - `iRowsProcessed` should increment as rows are published

---

## ✅ Step 9: Verify Operation

### Check CSV Reading
- `fbCSVReader.xBusy` → TRUE while reading
- `fbCSVReader.xNewRow` → Pulses for each row
- `fbCSVReader.RowOut` → Shows current row data

### Check MQTT Publishing
- `fbMQTT.xConnected` → TRUE when connected
- `fbMQTT.xPublished` → Pulses when message sent
- `fbMQTT.sStatus` → Shows connection status

### Check Overall System
- `eMainState` → READING_CSV (normal operation)
- `iRowsProcessed` → Increases with each row
- `sSystemStatus` → Shows current activity

---

## 📱 Step 10: Monitor MQTT Messages

### Using Mosquitto Command Line (Windows)

**Install Mosquitto clients:**
```powershell
# Download from: https://mosquitto.org/download/
# Or with Chocolatey:
choco install mosquitto
```

**Subscribe to your topic:**
```powershell
mosquitto_sub -h broker.hivemq.com -t "UE/139ukr" -v
```

**You should see JSON messages:**
```json
{"Col1":"value1","Col2":"value2",...,"Col13":"value13"}
```

### Using MQTT Explorer (GUI)

**Download and install:**
- Website: http://mqtt-explorer.com/
- Platform: Windows, Mac, Linux

**Configuration:**
```
Protocol:  mqtt://
Host:      broker.hivemq.com
Port:      1883
Username:  (leave empty)
Password:  (leave empty)
```

**Connect** → Browse to `UE/139ukr` → See live messages

---

## 🎛️ Optional: Customize Settings

### Change Read Interval
```st
// In PLC_PRG
tReadInterval := T#10S;  // ← Change to your desired interval
```

### Change Topic
```st
// In FB_MQTTPublisher or PLC_PRG instantiation
fbMQTT.sTopic := 'your/custom/topic';
```

### Change Buffer Size (for larger CSV files)
```st
// In FB_CSVReader
VAR
    sBuffer : STRING(8192);  // ← Double the buffer size
END_VAR
```

### Change QoS Level
```st
// In FB_MQTTPublisher, PUBLISHING state
fbClient.Publish(
    sTopic := sTopic,
    pPayload := ADR(sJsonPayload),
    udiPayloadSize := LEN(sJsonPayload),
    eQoS := IotMqtt.QoS.AtMostOnce  // ← Change QoS
);
// Options: AtMostOnce, AtLeastOnce, ExactlyOnce
```

---

## 🔧 Troubleshooting

### Build Errors

**"SysFile not found"**
```
Solution: Add SysFile library (v3.5.17.0+) in Library Manager
```

**"IotMqtt not found"**
```
Solution: Try adding "MQTT" library instead (name varies)
Check: Device → Library Repository for available MQTT libraries
```

**"Identifier not declared"**
```
Solution: Check import order - DUTs and Functions must be imported first
```

### Runtime Errors

**CSV file not found**
```
Check: File path in sCSVFilePath
Check: File exists on PLC (Tools → File Browser)
Check: File permissions
```

**MQTT won't connect**
```
Check: Network configuration (see NETWORK.md)
Check: fbMQTT.sStatus for error message
Check: DNS settings (8.8.8.8)
Test: Ping broker.hivemq.com from laptop
```

**No rows processed**
```
Check: xSystemEnable := TRUE
Check: CSV file has data (not just header)
Check: CSV has exactly 13 columns
Check: Delimiter is semicolon (;)
```

---

## 📖 Next Steps

- **Network setup**: Read [NETWORK.md](NETWORK.md) for detailed network configuration
- **Architecture**: Read [ARCHITECTURE.md](ARCHITECTURE.md) to understand the system design
- **Reference**: Use [REFERENCE.md](REFERENCE.md) for quick lookups and troubleshooting

---

**Setup Complete!** Your PLC should now be reading CSV files and publishing to MQTT every 10 seconds.
