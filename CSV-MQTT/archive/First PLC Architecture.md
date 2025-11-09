02.11.2025
## ⚙️ **System Overview**

**Architecture**
PLC (Eaton XSoft) 
│
├── CSV Reader FB (reads each row → STRUCT[13])
├── JSON Builder FB (maps columns → JSON)
└── MQTT Publisher FB (sends JSON via broker)
       ├── Connection A: through Laptop (shared Internet)
       └── Connection B: through Router (LAN)
## 🧩 **1. Required Libraries**

Add the following libraries to your project:

- `SysFile`
- `CAA.JSON` (or `IOT_JSON`)
- `MQTT` (CODESYS MQTT Client)
- `Standard`
- `Util` (for string manipulation)
## 🧱 **2. Data Structure for 13 Columns**

``` pascal
TYPE ST_CSVRow :
STRUCT
    Col1  : STRING(64);
    Col2  : STRING(64);
    Col3  : STRING(64);
    Col4  : STRING(64);
    Col5  : STRING(64);
    Col6  : STRING(64);
    Col7  : STRING(64);
    Col8  : STRING(64);
    Col9  : STRING(64);
    Col10 : STRING(64);
    Col11 : STRING(64);
    Col12 : STRING(64);
    Col13 : STRING(64);
END_STRUCT
END_TYPE
```
## 🗂️ **3. CSV Reader Function Block**

Reads one row per cycle and outputs `ST_CSVRow`
``` pascal
FUNCTION_BLOCK FB_CSVReader
VAR_INPUT
    sFilePath : STRING; // access csv in plc for row. path given in Main function
    xEnable   : BOOL;
END_VAR
VAR_OUTPUT
    RowOut    : ST_CSVRow; // STRUCT with 13 values
    xNewRow   : BOOL;
END_VAR
VAR
    fbFileOpen : SysFile.FB_FileOpen;
    fbRead     : SysFile.FB_FileRead;
    fbClose    : SysFile.FB_FileClose;
    buffer     : ARRAY [0..1023] OF BYTE;
    fileHandle : SysFile.RTS_IEC_HANDLE;
    sLine      : STRING(1024);
    lines      : ARRAY[1..100] OF STRING(256);
    iIndex     : INT;
    bHeaderSkipped : BOOL;
END_VAR

IF xEnable THEN
    fbFileOpen(sFileName := sFilePath, eFileMode := SysFile.FILE_MODE.READ);
    fbFileOpen();
    IF fbFileOpen.xReady THEN
        fileHandle := fbFileOpen.hFile;
        fbRead(hFile := fileHandle, pBuffer := ADR(buffer), udiBufferSize := SIZEOF(buffer));
        fbRead();
        sLine := TO_STRING(buffer);

        // Split into lines
        lines := STRING_SPLIT(sLine, '\n');
        IF NOT bHeaderSkipped THEN
            bHeaderSkipped := TRUE; // skip header row
        ELSE
            IF iIndex < UPPER_BOUND(lines,1) THEN
                iIndex := iIndex + 1;
                RowOut := ParseCSVLine(lines[iIndex]);
                xNewRow := TRUE;
            END_IF
        END_IF
        fbClose(hFile := fileHandle);
        fbClose();
    END_IF
END_IF


// Helper function
FUNCTION ParseCSVLine : ST_CSVRow
VAR_INPUT sLine : STRING; END_VAR
VAR result : ST_CSVRow; arr : ARRAY[1..13] OF STRING(64); i : INT;
arr := STRING_SPLIT(sLine, ',');
FOR i:=1 TO 13 DO
    CASE i OF
        1: result.Col1 := arr[i];
        2: result.Col2 := arr[i];
        3: result.Col3 := arr[i];
        4: result.Col4 := arr[i];
        5: result.Col5 := arr[i];
        6: result.Col6 := arr[i];
        7: result.Col7 := arr[i];
        8: result.Col8 := arr[i];
        9: result.Col9 := arr[i];
        10: result.Col10 := arr[i];
        11: result.Col11 := arr[i];
        12: result.Col12 := arr[i];
        13: result.Col13 := arr[i];
    END_CASE
END_FOR
ParseCSVLine := result;
END_FUNCTION

``` 

## 🌐 **4. MQTT Publisher (two connection modes)**

``` pascal
FUNCTION_BLOCK FB_MQTTPublisher
VAR_INPUT
    ModeLaptop : BOOL;        // TRUE = use laptop connection, FALSE = use router (LAN)
    RowIn      : ST_CSVRow;
    xTrigger   : BOOL;
END_VAR
VAR
    fbClient : MQTT.MQTTClient;
    fbPub    : MQTT.MQTTPublish;
    json     : CAA.JSON_Builder;
    jsonStr  : STRING(2048);
    topic    : STRING := 'plc/data';
END_VAR

IF NOT fbClient.xConnected THEN
    IF ModeLaptop THEN
        fbClient(sClientId := 'EatonPLC_Laptop',
                 sHostName := 'broker.hivemq.com', // or your broker
                 uiPort := 1883,
                 xEnable := TRUE);
    ELSE
        fbClient(sClientId := 'EatonPLC_LAN',
                 sHostName := '192.168.0.10', // your router/broker IP
                 uiPort := 1883,
                 xEnable := TRUE);
    END_IF
END_IF

IF xTrigger AND fbClient.xConnected THEN
    // Build JSON dynamically
    json.StartObject();
    json.AddString('Col1',  RowIn.Col1);
    json.AddString('Col2',  RowIn.Col2);
    json.AddString('Col3',  RowIn.Col3);
    json.AddString('Col4',  RowIn.Col4);
    json.AddString('Col5',  RowIn.Col5);
    json.AddString('Col6',  RowIn.Col6);
    json.AddString('Col7',  RowIn.Col7);
    json.AddString('Col8',  RowIn.Col8);
    json.AddString('Col9',  RowIn.Col9);
    json.AddString('Col10', RowIn.Col10);
    json.AddString('Col11', RowIn.Col11);
    json.AddString('Col12', RowIn.Col12);
    json.AddString('Col13', RowIn.Col13);
    json.EndObject();
    json.GetJSONString(jsonStr);

    fbPub(xExecute := TRUE,
          sTopic := topic,
          pPayload := ADR(jsonStr),
          udiPayloadSize := LEN(jsonStr),
          eQoS := MQTT.QoS_0);
    fbPub();
END_IF

``` 

## 🔁 **5. Main Program (PLC_PRG)**

``` pascal
PROGRAM PLC_PRG
VAR
    fbReader : FB_CSVReader;
    fbPub    : FB_MQTTPublisher;
    tonCycle : TON;
    useLaptop : BOOL := TRUE;   // set to FALSE for Router mode
END_VAR

// Trigger every 10 s
tonCycle(IN := TRUE, PT := T#10S);
IF tonCycle.Q THEN
    fbReader(sFilePath := '/usr/data.csv', xEnable := TRUE);
    fbReader();
    IF fbReader.xNewRow THEN
        fbPub(ModeLaptop := useLaptop,
               RowIn := fbReader.RowOut,
               xTrigger := TRUE);
        fbPub();
    END_IF
    tonCycle(IN := FALSE); // reset timer
END_IF


``` 

## 🌍 **6. Network Configuration Options**

### **A. Laptop-Ethernet connection (shared Internet)**
- Connect PLC ⇄ Laptop via Ethernet cable.
- On the laptop:
    - Enable **Internet Connection Sharing** for your Wi-Fi to the Ethernet adapter.
    - PLC receives IP via DHCP (e.g., 192.168.137.x).
- Use broker host: `broker.hivemq.com` or your **Cedalo Cloud broker**.
- This allows MQTT over your laptop’s Internet without separate LAN.
### **B. PLC-Router (LAN) connection**
- Connect PLC Ethernet port to router/switch (normal LAN).
- Assign static IP (e.g., 192.168.0.50).
- Broker host = internal IP or DNS of your MQTT broker (e.g., `192.168.0.10`).
- Use `ModeLaptop := FALSE` to switch connection path.

---
## ✅ **Summary**

| Layer                | Function                                      |
| -------------------- | --------------------------------------------- |
| **CSV Reader FB**    | Reads one row at a time (13 columns)          |
| **Publisher FB**     | Builds JSON and sends via MQTT                |
| **Main Program**     | Triggers reading/publishing every 10 s        |
| **Network Option A** | Laptop shared Internet (direct broker access) |
| **Network Option B** | PLC connected to router (LAN broker)          |
