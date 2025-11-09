# CSV-MQTT PLC Project

**Eaton PLC | CODESYS v3.5.x | November 2025**

---

## 📖 Project Documentation

All documentation has been consolidated into focused, non-redundant files:

### **[📂 DOCS_GUIDE.md](CSV-MQTT/docs/DOCS_GUIDE.md)**
**Documentation guide with order of use**
- 1. SETUP.md - Installation & configuration
- 2. NETWORK.md - Network configuration
- 3. ARCHITECTURE.md - System design & pseudocode
- 4. REFERENCE.md - Quick reference & troubleshooting

### **[🔧 SETUP.md](CSV-MQTT/docs/SETUP.md)**
**Complete installation and configuration guide**
- Step-by-step file import instructions
- Library installation
- PLC configuration
- CSV file preparation
- Build and download process
- Verification steps

### **[🌐 NETWORK.md](CSV-MQTT/docs/NETWORK.md)**
**Network configuration for both connection modes**
- Network basics explained
- Case A: Laptop gateway setup (development)
- Case B: Industrial router setup (production)
- CODESYS communication setup
- MQTT testing procedures
- Common network issues

### **[🏗️ ARCHITECTURE.md](CSV-MQTT/docs/ARCHITECTURE.md)**
**System design, algorithms, and pseudocode**
- Component architecture
- State machine diagrams
- Algorithm explanations
- Data flow diagrams
- Design decisions
- Performance characteristics

### **[📋 REFERENCE.md](CSV-MQTT/docs/REFERENCE.md)**
**Quick reference and troubleshooting**
- Configuration quick lookup
- Status monitoring variables
- State machine states
- Troubleshooting guide
- Common adjustments
- CSV format requirements
- Performance tuning tips

---

## 🚀 Quick Start

1. **[Read SETUP.md](CSV-MQTT/docs/SETUP.md)** → Import files and configure
2. **[Read NETWORK.md](CSV-MQTT/docs/NETWORK.md)** → Set up your connection
3. **Deploy** → Build, download, and enable
4. **[Use REFERENCE.md](CSV-MQTT/docs/REFERENCE.md)** → For troubleshooting

---

## 📂 Project Structure

```
Eaton_PLC/
│
├── README.md ........................ This file (documentation index)
│
└── CSV-MQTT/
    │
    ├── docs/ ....................... Documentation folder
    │   ├── DOCS_GUIDE.md ........... Documentation guide (start here)
    │   ├── SETUP.md ................ Installation guide
    │   ├── NETWORK.md .............. Network configuration
    │   ├── ARCHITECTURE.md ......... System design
    │   └── REFERENCE.md ............ Quick reference
    │
    ├── scripts/ .................... Source code
    │   ├── DUTs/
    │   │   └── ST_CSVRow.st
    │   ├── Functions/
    │   │   ├── F_GetNextLine.st
    │   │   ├── F_ParseCSVLine.st
    │   │   ├── F_AssignField.st
    │   │   └── F_BuildJsonFromRow.st
    │   ├── FunctionBlocks/
    │   │   ├── FB_CSVReader.st
    │   │   └── FB_MQTTPublisher.st
    │   └── Programs/
    │       └── PLC_PRG.st
    │
    ├── lib/
    │   └── INDEX.md ................ CODESYS library catalog
    │
    ├── archive/ .................... Deprecated documents
    │   ├── First PLC Architecture.md
    │   └── 2nd PLC Architecture.md
    │
    └── hivemq/
        ├── credentials ............. MQTT credentials (if needed)
        └── no credentials connection .. Test connection info
```

---

## ✅ What This Project Does

Reads CSV files from the PLC file system, parses each row into structured data (13 columns), converts to JSON, and publishes to cloud MQTT broker (`broker.hivemq.com`).

### Key Features
- ✅ State machine architecture
- ✅ Automatic error recovery
- ✅ Dual connection modes (laptop/router)
- ✅ Cloud MQTT (no local broker needed)
- ✅ Semicolon-delimited CSV
- ✅ JSON output

---

## 🎯 Configuration Summary

| Setting | Value |
|---------|-------|
| **CSV Delimiter** | Semicolon (`;`) |
| **CSV Columns** | Exactly 13 |
| **MQTT Broker** | broker.hivemq.com |
| **MQTT Port** | 1883 (no TLS) |
| **Default Topic** | UE/139ukr |
| **Read Interval** | 10 seconds |
| **Laptop IP** | 192.168.137.2 |
| **Router IP** | 192.168.10.204 |

---

## 📚 Required Libraries

- SysFile (v3.5.17.0+)
- IotMqtt or MQTT
- Standard
- SysTypes

---

## 🆘 Need Help?

1. **Setup issues** → [SETUP.md](CSV-MQTT/docs/SETUP.md)
2. **Network issues** → [NETWORK.md](CSV-MQTT/docs/NETWORK.md)
3. **How it works** → [ARCHITECTURE.md](CSV-MQTT/docs/ARCHITECTURE.md)
4. **Quick lookup** → [REFERENCE.md](CSV-MQTT/docs/REFERENCE.md)

---

**Documentation Version**: 2.0 (Consolidated, Non-Redundant)  
**Last Updated**: November 9, 2025  
**Status**: ✅ Production Ready
