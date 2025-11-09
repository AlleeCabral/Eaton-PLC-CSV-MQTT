# ARCHITECTURE - CSV-MQTT PLC System

**System design, algorithms, and pseudocode**

---

## 🏗️ System Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     PLC (CODESYS v3.5.x)                    │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────┐                                          │
│  │  PLC_PRG     │  Main state machine coordinator          │
│  │  (Program)   │  - 10s cycle timer                       │
│  └──────┬───────┘  - Row-by-row orchestration             │
│         │                                                   │
│    ┌────┴─────┐                                            │
│    │          │                                            │
│    ▼          ▼                                            │
│  ┌────────┐  ┌─────────┐                                  │
│  │CSV     │  │MQTT     │                                  │
│  │Reader  │  │Publisher│                                  │
│  │(FB)    │  │(FB)     │                                  │
│  └────┬───┘  └────┬────┘                                  │
│       │           │                                        │
│       │           │                                        │
└───────┼───────────┼────────────────────────────────────────┘
        │           │
        ▼           ▼
   CSV File    broker.hivemq.com
   (on PLC)    (Cloud MQTT)
```

---

## 🗂️ Component Architecture

### 1. Data Types (DUTs)

**ST_CSVRow**
```
Purpose: Store one row of CSV data
Structure:
  - 13 STRING fields (Col1 to Col13)
  - Each field: 64 characters capacity
  
Usage: Passed between CSV reader and MQTT publisher
```

---

### 2. Functions

#### F_GetNextLine
```
FUNCTION F_GetNextLine : BOOL

INPUT:
  - sBuffer: STRING    // Full file content
  - iStartPos: INT     // Where to start looking

OUTPUT:
  - sLine: STRING      // Extracted line
  - iEndPos: INT       // Position after line

ALGORITHM:
  1. Start from iStartPos in buffer
  2. Iterate character by character
  3. Detect line break:
     - LF (ASCII 10) = Unix/Mac
     - CRLF (ASCII 13+10) = Windows
  4. Extract substring from start to line break
  5. Return position after line break
  6. Return FALSE if no more lines

HANDLES:
  - Both CRLF and LF line endings
  - Empty lines
  - EOF detection
```

#### F_ParseCSVLine
```
FUNCTION F_ParseCSVLine : ST_CSVRow

INPUT:
  - sLine: STRING      // CSV line to parse

OUTPUT:
  - Populated ST_CSVRow structure

ALGORITHM:
  1. Initialize field counter = 0
  2. Initialize field accumulator = ''
  3. Initialize quote flag = FALSE
  
  4. FOR each character in line:
     IF character = semicolon (;) AND NOT in_quotes:
       - Save field to structure (call F_AssignField)
       - Increment field counter
       - Clear field accumulator
     
     ELSE IF character = double quote ("):
       - Toggle in_quotes flag
       - (Handles fields with semicolons: "value;with;semicolons")
     
     ELSE:
       - Append character to field accumulator
  
  5. Save last field (no trailing semicolon)
  6. Return populated structure

HANDLES:
  - Quoted fields with semicolons
  - Empty fields
  - Exactly 13 columns (European CSV standard)
```

#### F_AssignField
```
FUNCTION F_AssignField : BOOL

INPUT:
  - pRow: POINTER TO ST_CSVRow  // Structure to populate
  - iFieldNum: INT               // Field number (1-13)
  - sValue: STRING               // Value to assign

ALGORITHM:
  CASE iFieldNum OF
    1: pRow^.Col1 := sValue;
    2: pRow^.Col2 := sValue;
    ...
    13: pRow^.Col13 := sValue;
    ELSE: RETURN FALSE;
  END_CASE
  RETURN TRUE;

PURPOSE:
  - Dynamic field assignment using pointer
  - Enables F_ParseCSVLine to assign fields programmatically
```

#### F_BuildJsonFromRow
```
FUNCTION F_BuildJsonFromRow : BOOL

INPUT:
  - stRow: ST_CSVRow    // CSV row data
  - sJson: STRING       // Output JSON string (passed by reference)

ALGORITHM:
  1. sJson := '{'
  2. FOR i := 1 TO 13:
     - Append: '"ColN":"value"'
     - IF i < 13: Append ','
  3. Append: '}'
  4. RETURN TRUE

OUTPUT FORMAT:
  {"Col1":"v1","Col2":"v2",...,"Col13":"v13"}

USES:
  - CONCAT function for string building
  - No external JSON library needed
```

---

### 3. Function Blocks

#### FB_CSVReader

**Purpose**: Read CSV file row-by-row with state machine control

**State Machine**:
```
        xEnable
   ┌─────────────────┐
   │                 │
   ▼                 │
┌──────┐             │
│ IDLE │◄────────────┤
└───┬──┘             │
    │ xEnable        │
    ▼                │
┌───────────┐        │
│ OPEN_FILE │        │
└─────┬─────┘        │
      │ Success      │
      ▼              │
┌───────────┐        │
│ READ_FILE │        │
└─────┬─────┘        │
      │ Success      │
      ▼              │
┌─────────────┐      │
│ PARSE_LINES │◄─────┤ More rows
└──────┬──────┘      │
       │ Done        │
       ▼             │
┌────────────┐       │
│ CLOSE_FILE │───────┘
└────────────┘

   Errors
      ↓
┌─────────┐
│  ERROR  │──→ IDLE
└─────────┘
```

**States Explained**:

1. **IDLE**
   - Wait for xEnable = TRUE
   - Reset all outputs
   - Clear error flags

2. **OPEN_FILE**
   - Call: `hFile := SysFileOpen(sFilePath, AM_READ, ADR(eError))`
   - Validate: `hFile <> RTS_INVALID_HANDLE`
   - Success → READ_FILE
   - Failure → ERROR

3. **READ_FILE**
   - Call: `iBytesRead := SysFileRead(hFile, ADR(sBuffer), SIZEOF(sBuffer), ADR(eError))`
   - Store entire file in sBuffer
   - Success → PARSE_LINES
   - Failure → CLOSE_FILE with error flag

4. **PARSE_LINES**
   - Call: `bLineFound := F_GetNextLine(sBuffer, iCurrentPos, sCurrentLine, iNextPos)`
   - Skip first line (header)
   - For each subsequent line:
     * Call: `RowOut := F_ParseCSVLine(sCurrentLine)`
     * Pulse: `xNewRow := TRUE`
     * Update: `iCurrentPos := iNextPos`
   - When no more lines → CLOSE_FILE

5. **CLOSE_FILE**
   - Call: `SysFileClose(hFile)`
   - Set: `xDone := TRUE`
   - Return to: IDLE

6. **ERROR**
   - Set: `xError := TRUE`
   - Close file if open
   - Return to: IDLE

**Key Features**:
- ✅ Reads entire file once (efficient)
- ✅ Proper resource cleanup
- ✅ Edge detection (rising edge of xEnable)
- ✅ Status outputs for monitoring

---

#### FB_MQTTPublisher

**Purpose**: MQTT client with dual connection mode and auto-recovery

**State Machine**:
```
        xEnable
   ┌─────────────────┐
   │                 │
   ▼                 │
┌──────┐             │
│ INIT │             │
└───┬──┘             │
    │ xEnable        │
    ▼                │
┌────────────┐       │
│ CONNECTING │       │
└──────┬─────┘       │
       │ Success     │
       ▼             │
┌───────────┐        │
│ CONNECTED │◄───────┤
└─────┬─────┘        │
      │ xTrigger     │
      ▼              │
┌────────────┐       │
│ PUBLISHING │───────┘ Success
└──────┬─────┘
       │ Error or xEnable=FALSE
       ▼
┌──────────────┐
│ DISCONNECTING│──→ INIT
└──────────────┘

   Errors
      ↓
┌─────────┐
│  ERROR  │──→ Wait 10s → INIT
└─────────┘
```

**States Explained**:

1. **INIT**
   - Reset flags
   - Wait for xEnable = TRUE

2. **CONNECTING**
   - Configure based on mode:
     * IF xUseLaptop: `fbClient.sHostName := sBrokerLaptop`
     * ELSE: `fbClient.sHostName := sBrokerLAN`
   - Set: `fbClient.xEnable := TRUE`
   - Call: `fbClient()`
   - On `fbClient.xConnected` → CONNECTED
   - On `fbClient.xError` → ERROR

3. **CONNECTED**
   - Monitor connection
   - Wait for rising edge of xTrigger
   - On trigger → PUBLISHING
   - If connection lost → ERROR (with 5s retry)

4. **PUBLISHING**
   - Call: `F_BuildJsonFromRow(RowIn, sJsonPayload)`
   - Call: `fbClient.Publish(...)`
   - On `fbClient.xPublishComplete`:
     * Pulse: `xPublished := TRUE`
     * Return to: CONNECTED
   - On error → ERROR

5. **DISCONNECTING**
   - Set: `fbClient.xEnable := FALSE`
   - Clean disconnect
   - Return to: INIT

6. **ERROR**
   - Set: `xError := TRUE`
   - Update: `sStatus` with error message
   - Wait 10 seconds (auto-retry timer)
   - Return to: INIT

**Key Features**:
- ✅ Dual mode (laptop/router) - both use cloud broker
- ✅ Automatic reconnection on connection loss
- ✅ QoS support (ExactlyOnce by default)
- ✅ Edge detection for triggers
- ✅ Detailed status messages

---

### 4. Main Program (PLC_PRG)

**Purpose**: Orchestrate CSV reading and MQTT publishing

**State Machine**:
```
xSystemEnable
   │
   ▼
┌──────┐
│ IDLE │
└───┬──┘
    │
    ▼
┌───────────┐
│ INIT_MQTT │ Enable MQTT publisher
└─────┬─────┘
      │
      ▼
┌──────────────┐
│ WAIT_CONNECT │ Wait for MQTT connection
└───────┬──────┘
        │ Connected
        ▼
┌──────────────┐
│ READING_CSV  │◄─────┐
└───────┬──────┘      │
        │             │
        ├─ Timer (10s)─┘
        │
        ├─ xNewRow → Publish row
        │
        └─ xDone → Reset reader

   Errors
      ↓
┌─────────┐
│  ERROR  │──→ IDLE
└─────────┘
```

**Operation Flow**:

1. **Initialization**
   - Wait for `xSystemEnable := TRUE`
   - Enable MQTT publisher
   - Wait for connection

2. **Periodic Reading**
   - Every 10 seconds (configurable):
     * Enable CSV reader
     * Set file path
   
3. **Row Processing**
   - On `fbCSVReader.xNewRow`:
     * Increment `iRowsProcessed`
     * Copy row to `fbMQTT.RowIn`
     * Trigger `fbMQTT.xTrigger := TRUE`
     * Wait for publish complete
   
4. **Cycle Complete**
   - On `fbCSVReader.xDone`:
     * Reset CSV reader
     * Restart 10s timer

**Key Variables**:
- `eMainState` - Current state
- `iRowsProcessed` - Total rows published
- `sSystemStatus` - Human-readable status
- `tonReadCycle` - 10-second timer
- `xSystemEnable` - Master enable switch

---

## 🔄 Complete Data Flow

```
1. Timer triggers (every 10s)
   ↓
2. CSV Reader opens /usr/data.csv
   ↓
3. Reads entire file into buffer
   ↓
4. Parses line by line:
   - Extract line (F_GetNextLine)
   - Parse CSV (F_ParseCSVLine)
   - Output structure (ST_CSVRow)
   ↓
5. For each row:
   - Build JSON (F_BuildJsonFromRow)
   - Publish to MQTT (FB_MQTTPublisher)
   - Wait for confirmation
   ↓
6. Close file, wait for next cycle
```

---

## 📊 Key Design Decisions

### Why State Machines?
- ✅ Non-blocking operation
- ✅ Predictable behavior
- ✅ Easy error recovery
- ✅ Clear status monitoring

### Why Semicolon Delimiter?
- ✅ European CSV standard
- ✅ Handles comma-containing values
- ✅ Configured in F_ParseCSVLine

### Why Cloud Broker?
- ✅ No local installation needed
- ✅ Always accessible
- ✅ Free tier available
- ✅ Simplifies architecture

### Why Manual JSON Building?
- ✅ No external library needed
- ✅ Lightweight and fast
- ✅ Full control over format
- ✅ Predictable output

### Why Pointer in F_AssignField?
- ✅ Enables dynamic field assignment
- ✅ Reduces code duplication
- ✅ More maintainable

---

## 🎯 Performance Characteristics

| Metric | Value | Notes |
|--------|-------|-------|
| **CSV Read Cycle** | 10 seconds | Configurable via tReadInterval |
| **File Size Limit** | ~4KB | Configurable via buffer size |
| **Max Row Length** | 512 chars | Configurable in F_GetNextLine |
| **Publish Latency** | <100ms | Per row, depends on network |
| **Reconnect Time** | 5-10s | Automatic retry delays |
| **Memory Usage** | ~10KB | Approximate, varies by row count |

---

## 🔍 Functions vs Function Blocks

**Functions** (have return types):
- `F_GetNextLine : BOOL`
- `F_ParseCSVLine : ST_CSVRow`
- `F_AssignField : BOOL`
- `F_BuildJsonFromRow : BOOL`

**Function Blocks** (have outputs, retain state):
- `FB_CSVReader` → VAR_OUTPUT
- `FB_MQTTPublisher` → VAR_OUTPUT

**Programs** (top-level execution):
- `PLC_PRG` → Called every scan cycle

---

## 📝 Error Handling Strategy

### CSV Reader Errors
- File not found → eError code, xError flag
- Read failure → Close file, set error, return to IDLE
- Parse errors → Skip malformed rows, continue

### MQTT Errors
- Connection failure → Auto-retry after 10s
- Publish failure → Return to CONNECTED, retry on next trigger
- Connection loss → Auto-reconnect after 5s

### System Errors
- Any component error → Set xSystemError flag
- Status displayed in sSystemStatus
- Requires xSystemEnable reset to recover

---

**Architecture Complete** - See [REFERENCE.md](REFERENCE.md) for troubleshooting and [SETUP.md](SETUP.md) for deployment
