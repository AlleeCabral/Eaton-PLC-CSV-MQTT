# CODESYS Library Catalog - Quick Reference

## � Available Library Categories

This catalog lists the CODESYS libraries available in this project for quick reference when developing PLC applications.

---

## �️ System Libraries

### **SysFile** (v3.5.17.0)
**Path:** `System/SysFile/`
**Purpose:** File system operations

**Key Functions:**
- `SysFileOpen()` - Open/create file (returns RTS_IEC_HANDLE)
- `SysFileRead()` - Read bytes from file
- `SysFileWrite()` - Write bytes to file
- `SysFileClose()` - Close file handle
- `SysFileEOF()` - Check end of file
- `SysFileGetSize()` - Get file size
- `SysFileDelete()` - Delete file
- `SysFileRename()` - Rename file

**Key Types:**
- `RTS_IEC_HANDLE` - File handle type
- `ACCESS_MODE` - File access modes (AM_READ, AM_WRITE, AM_APPEND, etc.)

---

### **SysTypes** (System)
**Path:** `System/SysTypes/`
**Purpose:** Basic system data types

**Key Types:**
- `RTS_IEC_HANDLE` - Generic handle type
- `DWORD`, `UDINT`, `DINT` - Data types
- System constants and enumerations

---

### **Standard**
**Path:** `System/Standard/`
**Purpose:** Standard IEC 61131-3 functions

**Key Functions:**
- `CONCAT()` - String concatenation
- `LEN()` - String length
- `LEFT()`, `RIGHT()`, `MID()` - String extraction
- `FIND()` - Find substring
- Type conversion functions (INT_TO_STRING, etc.)

---

### **StringUtils**
**Path:** `System/StringUtils/` or `System/IECStringUtils/`
**Purpose:** Extended string manipulation

**Functions Available:**
- String trimming and formatting
- Case conversion
- String comparison utilities

---

## 🌐 Communication Libraries

### **IotMqtt / MQTT**
**Purpose:** MQTT protocol client

**Typical Components:**
- `MqttClient` - Main MQTT client FB
- `MqttPublish` - Publish messages
- `MqttSubscribe` - Subscribe to topics
- `QoS` enumeration - Quality of Service levels

**Note:** Exact names may vary by CODESYS version. Check actual library in your project.

---

## 🏭 Industrial Protocol Libraries

### **CANopen Libraries**
- 3S CANopenStack
- 3S CANopenSafety
- CAA CANopen Manager

### **EtherCAT**
- EtherCATStack
- IoDrvEtherCAT

### **Profinet**
- IoDrvProfinet
- ProfinetDevice

### **Modbus**
- IoDrvModbusTCP
- ModbusFB

### **EtherNet/IP**
- IoDrvEtherNetIP
- CIP Object

---

## 🔧 I/O Driver Libraries

Located in `System/` and various vendor folders:
- IoDrvEtherCAT
- IoDrvEtherNetIP
- IoDrvModbusTCP
- IoDrvProfinet
- Various vendor-specific drivers

---

## 📊 Data Management Libraries

### **CAA File** (CAA Technical Workgroup)
**Purpose:** Advanced file operations

**Key FBs:**
- `FILE.Open` - Open file
- `FILE.Read` - Read from file
- `FILE.Write` - Write to file
- `FILE.Close` - Close file

---

### **CAA Storage**
**Purpose:** Persistent data storage

---

## 🛠️ Utility Libraries

### **Collections**
**Path:** `System/Collections/`
**Purpose:** Data structures (lists, arrays, etc.)

### **Util**
**Path:** `System/Util/`
**Purpose:** General utility functions

### **FloatingPointUtils**
**Purpose:** REAL/LREAL handling and conversion

---

## � Library Selection Guidelines

### For File Operations:
✅ **Use:** `SysFile` library
- Provides: `SysFileOpen`, `SysFileRead`, `SysFileClose`
- Best for: Direct file system access

### For String Operations:
✅ **Use:** `Standard` library + custom functions
- Provides: `CONCAT`, `LEN`, `FIND`
- Note: No `STRING_SPLIT` - implement custom parsing

### For MQTT:
✅ **Use:** `IotMqtt` or `MQTT` library
- Check your specific CODESYS version
- Provides: Client, Publish, Subscribe functions

### For Network Communication:
✅ **Use:** 
- TCP/UDP: `SysSocket` libraries
- Industrial protocols: Protocol-specific libraries

---

## ⚠️ Important Notes

### Functions That DON'T Exist:
❌ `SysFile.FB_FileOpen` - Use `SysFileOpen()` function instead
❌ `SysFile.FB_FileRead` - Use `SysFileRead()` function instead
❌ `SysFile.FB_FileClose` - Use `SysFileClose()` function instead
❌ `STRING_SPLIT()` - Not a standard function, implement custom parsing
❌ `SysFile.FILE_MODE.READ` - Use `AM_READ` constant instead
❌ `SysFile.RTS_IEC_HANDLE` - Use `RTS_IEC_HANDLE` (from SysTypes)

### Correct Usage:
✅ `SysFileOpen()` - Function, not function block
✅ `AM_READ`, `AM_WRITE`, `AM_APPEND` - Access mode constants
✅ `RTS_IEC_HANDLE` - From SysTypes library
✅ `RTS_INVALID_HANDLE` - Invalid handle constant

---

## 🔍 How to Find Library Information

1. **In CODESYS IDE:**
   - Library Manager → Double-click library → Browse objects
   - Right-click object → "Help" for documentation

2. **Browse Cache Files:**
   - Each library has a `browsercache` file
   - Contains XML with function/FB definitions

3. **Online Documentation:**
   - CODESYS Help: https://help.codesys.com/
   - Library-specific documentation

---

## 📖 Library Versions

Libraries in this project are from CODESYS v3.5.x family. Always check compatibility with your target PLC.

**Common versions:**
- SysFile: 3.5.17.0
- SysTypes: 3.5.x
- Standard: Built-in
- IotMqtt: Varies by installation

---

**Last Updated:** November 6, 2025
**Location:** `/lib/`
