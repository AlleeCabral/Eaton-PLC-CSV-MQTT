# REFERENCE Guide - Quick Lookup & Troubleshooting

**Fast reference for common tasks and issues**

---

## ⚙️ Quick Configuration Reference

### PLC_PRG Settings
```st
sCSVFilePath   := '/usr/139DATA/139_last6M_241025.csv'; // OR '/139DATA/139_last6M_241025.csv' Path to CSV file on PLC
xUseLaptopMode := TRUE;                 // TRUE=laptop, FALSE=router
xSystemEnable  := FALSE;                // Set TRUE to start
tReadInterval  := T#10S;                // Read cycle time
```

### FB_MQTTPublisher Defaults
```st
sBrokerLaptop := 'broker.hivemq.com';  // Laptop mode broker
sBrokerLAN    := 'broker.hivemq.com';  // Router mode broker
uiPort        := 1883;                  // MQTT port (no TLS)
sTopic        := 'UE/139ukr';          // Default topic
```

### Network Settings Quick Ref

| Mode | PLC IP | Gateway | DNS |
|------|--------|---------|-----|
| **Laptop** | 192.168.137.2 | 192.168.137.1 | 8.8.8.8 |
| **Router** | 192.168.10.204 | 192.168.10.1 | 8.8.8.8 |

---

## 📊 Status Monitoring

### Key Variables to Watch

#### System Level (PLC_PRG)
| Variable | Type | Normal Value | Description |
|----------|------|--------------|-------------|
| `eMainState` | ENUM | READING_CSV | Current system state |
| `sSystemStatus` | STRING | "Reading CSV..." | Status message |
| `iRowsProcessed` | INT | Increasing | Total rows published |
| `xSystemError` | BOOL | FALSE | System error flag |

#### CSV Reader (fbCSVReader)
| Variable | Type | Normal Value | Description |
|----------|------|--------------|-------------|
| `xBusy` | BOOL | TRUE/FALSE | Reading in progress |
| `xNewRow` | BOOL | Pulse | New row available |
| `xDone` | BOOL | TRUE | File read complete |
| `xError` | BOOL | FALSE | Error occurred |
| `eError` | DWORD | 0 | SysFile error code |
| `RowOut` | ST_CSVRow | Data | Current row |

#### MQTT Publisher (fbMQTT)
| Variable | Type | Normal Value | Description |
|----------|------|--------------|-------------|
| `xConnected` | BOOL | TRUE | Connected to broker |
| `xPublished` | BOOL | Pulse | Message sent |
| `xError` | BOOL | FALSE | Error occurred |
| `sStatus` | STRING | "Connected" | Connection status |

---

## 🎯 State Machine States

### PLC_PRG States
| State | Description | Next State |
|-------|-------------|------------|
| **IDLE** | Waiting for enable | INIT_MQTT (on enable) |
| **INIT_MQTT** | Starting MQTT | WAIT_CONNECT |
| **WAIT_CONNECT** | Waiting for MQTT | READING_CSV |
| **READING_CSV** | Normal operation | (loop) |
| **WAIT_PUBLISH** | Publishing row | READING_CSV |
| **ERROR** | Error occurred | IDLE (on reset) |

### FB_CSVReader States
| State | Description | Duration |
|-------|-------------|----------|
| **IDLE** | Waiting | Until xEnable |
| **OPEN_FILE** | Opening CSV | <100ms |
| **READ_FILE** | Reading content | <500ms |
| **PARSE_LINES** | Processing rows | ~100ms/row |
| **CLOSE_FILE** | Cleanup | <100ms |
| **ERROR** | Error handling | Until reset |

### FB_MQTTPublisher States
| State | Description | Duration |
|-------|-------------|----------|
| **INIT** | Waiting | Until xEnable |
| **CONNECTING** | Connecting | 1-5s |
| **CONNECTED** | Idle, ready | Until trigger |
| **PUBLISHING** | Sending message | <100ms |
| **DISCONNECTING** | Cleanup | <100ms |
| **ERROR** | Retry delay | 10s |

---

## 🐛 Troubleshooting Guide

### Build/Compile Issues

#### "Library not found: SysFile"
```
Problem: Missing SysFile library
Solution:
  1. Open Library Manager
  2. Add Library → SysFile
  3. Select v3.5.17.0 or later
  4. Rebuild project
```

#### "Library not found: IotMqtt"
```
Problem: MQTT library name varies
Solution:
  1. Try adding "MQTT" instead of "IotMqtt"
  2. Check Device → Library Repository for available MQTT libraries
  3. Adjust code: Replace "IotMqtt.MqttClient" with your library's class
```

#### "Identifier 'ST_CSVRow' not declared"
```
Problem: Import order incorrect
Solution:
  1. Delete all imported objects
  2. Re-import in correct order (DUTs first)
  3. See SETUP.md Step 1 for order
```

---

### Runtime Issues

#### CSV File Not Found (eError = 16#00000002)
```
Problem: File doesn't exist or wrong path
Checks:
  ✓ File path correct in sCSVFilePath
  ✓ File exists on PLC (Tools → File Browser)
  ✓ File uploaded to correct directory
  ✓ Path format: '/usr/data.csv' (Unix-style)
```

#### CSV Parsing Errors
```
Problem: Wrong delimiter or column count
Checks:
  ✓ Delimiter is semicolon (;) not comma
  ✓ Exactly 13 columns per row
  ✓ No trailing semicolons
  ✓ Quoted fields for values with semicolons
  
Example correct row:
value1;value2;value3;value4;value5;value6;value7;value8;value9;value10;value11;value12;value13

Example wrong row:
value1,value2,value3  ← Using commas
value1;value2;value3  ← Only 3 columns
```

#### MQTT Won't Connect
```
Problem: Network or broker issue
Checks:
  ✓ PLC has network connectivity
  ✓ Gateway configured correctly (see Network Settings table)
  ✓ DNS set to 8.8.8.8
  ✓ Firewall allows outbound port 1883
  ✓ broker.hivemq.com is accessible
  
Test from laptop:
  mosquitto_sub -h broker.hivemq.com -t "test" -v
  
If this fails → network issue
If this works → check PLC network settings
```

#### No Messages Published
```
Problem: System not enabled or CSV empty
Checks:
  ✓ xSystemEnable := TRUE
  ✓ CSV file has data (not just header)
  ✓ fbMQTT.xConnected = TRUE
  ✓ iRowsProcessed incrementing
  ✓ Topic subscription correct
  
Test subscription:
  mosquitto_sub -h broker.hivemq.com -t "UE/139ukr" -v
```

#### Connection Keeps Dropping
```
Problem: Network instability
Solutions:
  • Increase reconnect delay in FB_MQTTPublisher
  • Check network cable/connection
  • Verify router NAT timeout settings
  • Consider QoS level change (AtMostOnce faster)
```

#### Published Data Looks Wrong
```
Problem: JSON format or parsing issue
Checks:
  ✓ Watch fbMQTT.sJsonPayload in online mode
  ✓ Verify CSV parsing in fbCSVReader.RowOut
  ✓ Check for special characters in CSV
  ✓ Verify quote handling in F_ParseCSVLine
```

---

## 📱 Testing MQTT Connection

### Using Mosquitto Command Line

**Subscribe to topic:**
```powershell
# Listen to PLC messages
mosquitto_sub -h broker.hivemq.com -t "UE/139ukr" -v

# Listen with timestamp
mosquitto_sub -h broker.hivemq.com -t "UE/139ukr" -v --pretty

# Listen to all topics (debug)
mosquitto_sub -h broker.hivemq.com -t "#" -v
```

**Publish test message:**
```powershell
# Send test message to verify PLC subscription
mosquitto_pub -h broker.hivemq.com -t "UE/139ukr" -m "test message"

# Send JSON format
mosquitto_pub -h broker.hivemq.com -t "UE/139ukr" -m "{\"Col1\":\"test\"}"
```

### Using MQTT Explorer (GUI)

**Configuration:**
```
Protocol:  mqtt://
Host:      broker.hivemq.com
Port:      1883
Username:  (empty)
Password:  (empty)
```

**Features:**
- ✅ Topic tree browser
- ✅ Message history
- ✅ Publish test messages
- ✅ Export data to JSON/CSV
- ✅ Real-time updates

---

## 🔧 Common Adjustments

### Change Read Interval
```st
// In PLC_PRG
tReadInterval := T#30S;  // Every 30 seconds
tReadInterval := T#1M;   // Every 1 minute
tReadInterval := T#5S;   // Every 5 seconds (fast)
```

### Change MQTT Topic
```st
// In PLC_PRG, when instantiating fbMQTT
fbMQTT(
    xEnable := TRUE,
    sTopic := 'my/custom/topic',  // ← Custom topic
    ...
);
```

### Change QoS Level
```st
// In FB_MQTTPublisher, PUBLISHING state
fbClient.Publish(
    sTopic := sTopic,
    pPayload := ADR(sJsonPayload),
    udiPayloadSize := LEN(sJsonPayload),
    eQoS := IotMqtt.QoS.AtMostOnce  // Fastest, no confirmation
    // Options:
    // - AtMostOnce (QoS 0): Fastest, fire-and-forget
    // - AtLeastOnce (QoS 1): Confirmed, may duplicate
    // - ExactlyOnce (QoS 2): Guaranteed once, slowest
);
```

### Increase Buffer for Larger Files
```st
// In FB_CSVReader
VAR
    sBuffer : STRING(8192);  // Double to 8KB
    // Or even larger:
    sBuffer : STRING(16384); // 16KB
END_VAR
```

### Handle Longer CSV Rows
```st
// In F_GetNextLine
VAR
    sLine : STRING(1024);  // Double to 1024 chars
END_VAR
```

---

## 📋 CSV Format Requirements

### Correct Format
```csv
H1;H2;H3;H4;H5;H6;H7;H8;H9;H10;H11;H12;H13
v1;v2;v3;v4;v5;v6;v7;v8;v9;v10;v11;v12;v13
"quoted;value";v2;v3;v4;v5;v6;v7;v8;v9;v10;v11;v12;v13
```

### Rules
| Requirement | Example |
|-------------|---------|
| **Delimiter** | Semicolon `;` |
| **Columns** | Exactly 13 |
| **Header** | First row (auto-skipped) |
| **Quotes** | For fields with `;` |
| **Line ending** | CRLF or LF (both work) |
| **Encoding** | ASCII or UTF-8 |
| **Max size** | ~4KB (default buffer) |

### Common Mistakes
❌ Using commas: `value1,value2,value3`
❌ Wrong column count: `v1;v2;v3` (only 3)
❌ Trailing semicolon: `v1;v2;v3;`
❌ Missing quotes: `value;with;semicolons;v2;v3...`

---

## 🎛️ Performance Tuning

### For Faster Processing
```st
// Reduce read interval
tReadInterval := T#5S;

// Use QoS 0
eQoS := IotMqtt.QoS.AtMostOnce

// Smaller CSV files (<1KB)
```

### For Reliability
```st
// Increase read interval (reduce load)
tReadInterval := T#30S;

// Use QoS 2
eQoS := IotMqtt.QoS.ExactlyOnce

// Monitor xPublished confirmation
```

### For Large Files
```st
// Increase buffer
sBuffer : STRING(16384);

// Increase line length
sLine : STRING(2048);

// Consider splitting CSV into multiple files
```

---

## 🔍 Debug Breakpoints

### Recommended Breakpoint Locations

**CSV Reading:**
```
FB_CSVReader
  - Line after OPEN_FILE → PARSE_LINES
  - After F_ParseCSVLine call
  - After xNewRow := TRUE
```

**MQTT Publishing:**
```
FB_MQTTPublisher
  - In CONNECTED state (before PUBLISHING)
  - After F_BuildJsonFromRow
  - After fbClient.Publish call
```

**Main Program:**
```
PLC_PRG
  - After tonReadCycle.Q
  - After fbCSVReader.xNewRow
  - After fbMQTT.xPublished
```

### Watch Variables
```
fbCSVReader.sBuffer         // Raw file content
fbCSVReader.sCurrentLine    // Current CSV line being parsed
fbCSVReader.RowOut          // Parsed row structure
fbMQTT.sJsonPayload         // Generated JSON string
eMainState                  // System state
```

---

## 📞 Quick Help Matrix

| Problem | Check First | Solution File |
|---------|-------------|---------------|
| Won't compile | Libraries added? | SETUP.md Step 2 |
| File not found | File path correct? | SETUP.md Step 4 |
| No MQTT connection | Network configured? | NETWORK.md |
| Wrong data format | CSV delimiter `;`? | This file (CSV Format) |
| How does it work? | - | ARCHITECTURE.md |
| First time setup | - | SETUP.md |

---

## 📖 File Cross-Reference

- **[README.md](README.md)** - Documentation overview
- **[SETUP.md](SETUP.md)** - Installation and configuration
- **[NETWORK.md](NETWORK.md)** - Network setup (laptop/router)
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - System design and algorithms
- **This file** - Quick reference and troubleshooting

---

**Quick Reference Complete** - For detailed explanations, see ARCHITECTURE.md
