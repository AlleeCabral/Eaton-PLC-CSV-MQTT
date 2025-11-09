02.11.2025
## ⚙️ **System Overview**

**Architecture**
```
PLC (Eaton XSoft / CODESYS)
│
├── CSV Reader FB (state machine with SysFile functions)
├── JSON Builder F (manual JSON string construction)
└── MQTT Publisher FB (dual connection mode with error recovery)
       ├── Connection A: Laptop (shared Internet)
       └── Connection B: Router (LAN)
```

## 🧩 **1. Required Libraries**

Add the following libraries to your CODESYS project:

- `SysFile` (for file operations: SysFileOpen, SysFileRead, SysFileClose)
- `IotMqtt` or `MQTT` (CODESYS MQTT Client library)
- `Standard` (for basic functions: CONCAT, LEN, etc.)
- `SysTypes` (for RTS_IEC_HANDLE and other system types)

## 🧱 **2. Data Structure (DUT)**

### **ST_CSVRow.st**
```
PSEUDOCODE:
- Define structure type ST_CSVRow
- Create 13 string fields (Col1 to Col13)
- Each field capacity: 64 characters
- Purpose: Store one row of CSV data
```

## 🗂️ **3. CSV Reader Function Block**

### **FB_CSVReader.st**
```
PSEUDOCODE:

INPUTS:
- xEnable: Start/stop reading
- sFilePath: Path to CSV file

OUTPUTS:
- RowOut: Parsed CSV row (ST_CSVRow structure)
- xNewRow: Pulse when new row ready
- xBusy, xError, xDone: Status flags
- eError: Error code

STATE MACHINE:
1. IDLE:
   - Wait for xEnable signal
   - Reset all variables
   
2. OPEN_FILE:
   - Call SysFileOpen(path, AM_READ)
   - Validate file handle
   - On success → READ_FILE
   - On error → ERROR state

3. READ_FILE:
   - Call SysFileRead(handle, buffer, size)
   - Store content in string buffer
   - On success → PARSE_LINES
   - On error → CLOSE_FILE with error flag

4. PARSE_LINES:
   - Extract next line from buffer
   - Skip header row (first line)
   - Parse CSV line into structure fields
   - Set xNewRow pulse for each row
   - Continue until no more lines
   - Then → CLOSE_FILE

5. CLOSE_FILE:
   - Call SysFileClose(handle)
   - Set xDone flag
   - Return to IDLE

6. ERROR:
   - Close file if open
   - Set error flags
   - Return to IDLE

EDGE CASES:
- Handle CRLF and LF line endings
- Reset on falling edge of xEnable
- Proper resource cleanup
```

## 🔧 **4. Helper Functions**

### **F_GetNextLine.st**
```
PSEUDOCODE:

INPUT: Buffer string, start position
OUTPUT: Extracted line, end position, success boolean

ALGORITHM:
- Start from given position in buffer
- Iterate character by character
- Detect line break (LF=10 or CR=13)
- Handle both CRLF and LF formats
- Extract substring as one line
- Return new position after line break
- Return FALSE if no more lines
```

### **F_ParseCSVLine.st**
```
PSEUDOCODE:

INPUT: CSV line string
OUTPUT: ST_CSVRow structure

ALGORITHM:
- Initialize field counter = 0
- Initialize empty field string
- Iterate through each character:
  - IF character = comma AND not in quotes:
    - Save current field to structure
    - Increment field counter
    - Clear field string
  - ELSE IF character = quote:
    - Toggle "inside quotes" flag
  - ELSE:
    - Append character to field string
- After loop: save last field
- Call F_AssignField for each field
- Return populated structure
```

### **F_AssignField.st**
```
PSEUDOCODE:

INPUT: Pointer to structure, field number, value
OUTPUT: Success boolean

ALGORITHM:
- Validate field number (1-13)
- Use CASE statement:
  - Field 1 → assign to Col1
  - Field 2 → assign to Col2
  - ... (repeat for all 13 fields)
- Return TRUE if successful
```

### **F_BuildJsonFromRow.st**
```
PSEUDOCODE:

INPUT: ST_CSVRow structure
OUTPUT: JSON string

ALGORITHM:
- Initialize JSON string = "{"
- For each column (Col1 to Col13):
  - Append: "ColN":"value"
  - Add comma separator (except last)
- Append closing "}"
- Use CONCAT function for string building
- Return completed JSON string
```

## 🌐 **5. MQTT Publisher Function Block**

### **FB_MQTTPublisher.st**
```
PSEUDOCODE:

INPUTS:
- xEnable: Enable MQTT connection
- xUseLaptop: Connection mode selector
- RowIn: CSV row data to publish
- xTrigger: Publish trigger
- sBrokerLaptop: Public broker hostname
- sBrokerLAN: Local broker IP
- uiPort: MQTT port (default 1883)
- sTopic: MQTT topic name

OUTPUTS:
- xConnected: Connection status
- xPublished: Publish success pulse
- xError: Error flag
- sStatus: Status message

STATE MACHINE:
1. INIT:
   - Reset all flags
   - Wait for xEnable

2. CONNECTING:
   - Configure MQTT client based on mode:
     - IF xUseLaptop: use public broker
     - ELSE: use LAN broker IP
   - Set client ID with mode suffix
   - Enable MQTT client
   - Wait for connection
   - On success → CONNECTED
   - On error → ERROR

3. CONNECTED:
   - Monitor connection status
   - Wait for xTrigger (rising edge)
   - On trigger → PUBLISHING
   - If connection lost → reconnect with 5s delay

4. PUBLISHING:
   - Build JSON from RowIn using F_BuildJsonFromRow
   - Call MQTT Publish method
   - Set topic, payload, QoS level
   - Wait for completion
   - On success: pulse xPublished → CONNECTED
   - On error → ERROR

5. DISCONNECTING:
   - Disable MQTT client
   - Clean disconnect
   - → INIT

6. ERROR:
   - Set error flags
   - Wait 10 seconds
   - Auto-retry connection
   - → INIT

ERROR RECOVERY:
- Automatic reconnection on connection loss
- Configurable retry delays
- Status messages for diagnostics
```

## 🔁 **6. Main Program**

### **PLC_PRG.st**
```
PSEUDOCODE:

VARIABLES:
- fbCSVReader: Instance of FB_CSVReader
- fbMQTT: Instance of FB_MQTTPublisher
- sCSVFilePath: Path to CSV file
- xUseLaptopMode: Connection mode selector
- xSystemEnable: Master enable
- tonReadCycle: Timer for periodic operations
- tReadInterval: Time between file reads (10s)
- iRowsProcessed: Counter
- eMainState: Main state machine

STATE MACHINE:
1. IDLE:
   - Wait for xSystemEnable
   - Reset counters
   - → INIT_MQTT when enabled

2. INIT_MQTT:
   - Enable MQTT publisher
   - Set connection mode
   - → WAIT_CONNECT

3. WAIT_CONNECT:
   - Wait for MQTT connection
   - Monitor connection status
   - On success → READING_CSV
   - On error → ERROR

4. READING_CSV:
   - Run periodic timer (10s interval)
   - On timer trigger:
     - Enable CSV reader
     - Set file path
   - Monitor CSV reader outputs
   - On xNewRow:
     - Increment row counter
     - Copy row to MQTT publisher
     - Trigger MQTT publish
     - → WAIT_PUBLISH
   - On xDone:
     - Reset CSV reader
     - Restart cycle timer
   - On xError → ERROR

5. WAIT_PUBLISH:
   - Wait for MQTT publish complete
   - Continue CSV reading (next row)
   - On success → READING_CSV
   - On error → ERROR

6. ERROR:
   - Display error status
   - Stop all operations
   - Wait for system disable/enable cycle
   - → IDLE on reset

TIMING:
- CSV file read every 10 seconds
- Each row published immediately after parsing
- Automatic retry on errors
```

## 🌍 **7. Network Configuration Options**

### **A. Laptop-Ethernet Connection (Internet via Laptop)**
```
SETUP:
1. Connect PLC ↔ Laptop via Ethernet cable
2. Laptop configuration:
   - Enable "Internet Connection Sharing" (ICS)
   - Share Wi-Fi connection to Ethernet adapter
   - Laptop becomes DHCP server (192.168.137.1)
3. PLC network settings:
   - Set to DHCP client mode
   - Receives IP: 192.168.137.x
4. PLC program settings:
   - xUseLaptopMode = TRUE
   - sBrokerLaptop = "broker.hivemq.com" (or your cloud broker)
   
ADVANTAGES:
- No separate network infrastructure needed
- Access to cloud MQTT brokers
- Easy development/testing setup

DISADVANTAGES:
- Laptop must remain powered and connected
- Dependent on laptop's Internet connection
```

### **B. PLC-Router Connection (LAN)**
```
SETUP:
1. Connect PLC Ethernet port to network router/switch
2. PLC network settings:
   - Static IP: 192.168.0.50 (example)
   - Subnet: 255.255.255.0
   - Gateway: 192.168.0.1 (router)
3. MQTT Broker:
   - Install on local server or use router
   - Assign static IP: 192.168.0.10 (example)
4. PLC program settings:
   - xUseLaptopMode = FALSE
   - sBrokerLAN = "192.168.0.10"

ADVANTAGES:
- Independent operation
- Reliable LAN connection
- Better for production environments

DISADVANTAGES:
- Requires local MQTT broker
- More network configuration
```

## 📂 **8. Project File Structure**

```
CSV-MQTT/
├── scripts/
│   ├── DUTs/
│   │   └── ST_CSVRow.st                 (Data structure)
│   ├── Functions/
│   │   ├── F_GetNextLine.st             (Line extraction)
│   │   ├── F_ParseCSVLine.st            (CSV parsing)
│   │   ├── F_AssignField.st             (Field assignment)
│   │   └── F_BuildJsonFromRow.st        (JSON builder)
│   ├── FunctionBlocks/
│   │   └── FB_MQTTPublisher.st          (MQTT handler)
│   ├── Programs/
│   │   └── PLC_PRG.st                   (Main program)
│   └── FB_CSVReader.st                  (CSV reader - corrected)
```

## ✅ **Summary Table**

| Component            | Type | Purpose                                      | Key Features                              |
| -------------------- | ---- | -------------------------------------------- | ----------------------------------------- |
| **ST_CSVRow**        | DUT  | Data structure for one CSV row               | 13 string fields (64 chars each)          |
| **FB_CSVReader**     | FB   | Read CSV file row by row                     | State machine, error handling, SysFile    |
| **F_GetNextLine**    | F    | Extract lines from buffer                    | Handles CRLF/LF, boundary checks          |
| **F_ParseCSVLine**   | F    | Parse CSV line into structure                | Quote handling, comma separation          |
| **F_AssignField**    | F    | Assign value to structure field              | Pointer-based, dynamic assignment         |
| **F_BuildJsonFromRow** | F  | Convert structure to JSON                    | Manual string building, proper formatting |
| **FB_MQTTPublisher** | FB   | MQTT client with dual connection             | Auto-reconnect, QoS support, error retry  |
| **PLC_PRG**          | PRG  | Main orchestration program                   | 10s cycle, state machine, error recovery  |

## 🔍 **Key Improvements Over Original**

1. **Correct CODESYS Functions**: Uses actual SysFile functions (not non-existent FBs)
2. **State Machine Architecture**: Proper sequential control with error handling
3. **No External Dependencies**: Implements string parsing without non-existent STRING_SPLIT
4. **Resource Management**: Proper file handle management and cleanup
5. **Error Recovery**: Automatic reconnection and retry logic
6. **Status Monitoring**: Comprehensive status outputs for debugging
7. **Edge Detection**: Proper trigger handling with edge detection
8. **Modular Design**: Separated concerns into functions, FBs, and program
9. **Production Ready**: Includes all necessary error handling and validation

## 🚀 **Deployment Steps**

1. Create CODESYS project with Eaton target
2. Add required libraries (SysFile, IotMqtt, Standard)
3. Import all .st files in correct order:
   - DUTs first
   - Functions next
   - Function Blocks
   - Programs last
4. Configure network settings on PLC
5. Set CSV file path in PLC_PRG
6. Set connection mode (Laptop/LAN)
7. Configure MQTT broker addresses
8. Build and download to PLC
9. Set xSystemEnable = TRUE to start operation
10. Monitor status variables for diagnostics

---

**End of Architecture Document**
