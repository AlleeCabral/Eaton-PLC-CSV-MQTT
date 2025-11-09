# Docs Guide - CSV-MQTT PLC Project

**Eaton PLC | CODESYS v3.5.x | November 2025**

---

## 📑 Documentation Order of Use

Follow these documents in order for successful project deployment:

### 1. **[SETUP.md](SETUP.md)** - Installation & Configuration
**Use first when setting up the project**
- Step-by-step file import instructions
- Library installation
- PLC configuration
- CSV file preparation
- Build and download process
- Verification steps

### 2. **[NETWORK.md](NETWORK.md)** - Network Configuration
**Use after setup to configure your connection**
- Network basics explained
- Case A: Laptop gateway setup (development)
- Case B: Industrial router setup (production)
- CODESYS communication setup
- MQTT testing procedures
- Common network issues

### 3. **[ARCHITECTURE.md](ARCHITECTURE.md)** - System Design & Pseudocode
**Use to understand how the system works**
- Component architecture
- State machine diagrams
- Algorithm explanations
- Data flow diagrams
- Design decisions
- Performance characteristics

### 4. **[REFERENCE.md](REFERENCE.md)** - Quick Reference & Troubleshooting
**Use for daily operations and troubleshooting**
- Configuration quick lookup
- Status monitoring variables
- State machine states
- Troubleshooting guide
- Common adjustments
- CSV format requirements
- Performance tuning tips

---

## 🎯 Quick Start Path

1. **Read [SETUP.md](SETUP.md)** - Import files, add libraries, configure basic settings
2. **Read [NETWORK.md](NETWORK.md)** - Set up your network connection (laptop or router)
3. **Deploy** - Download to PLC and enable system
4. **Use [REFERENCE.md](REFERENCE.md)** - For troubleshooting and quick lookups
5. **Refer to [ARCHITECTURE.md](ARCHITECTURE.md)** - When you need to understand internals

---

## 📦 Project Overview

### What It Does
Reads CSV files from the PLC file system, parses each row into structured data, converts to JSON, and publishes via MQTT to a cloud broker (`broker.hivemq.com`).

### Key Features
- ✅ State machine architecture for reliability
- ✅ Automatic error recovery and reconnection
- ✅ Dual connection modes (laptop gateway or router)
- ✅ Cloud MQTT broker (no local installation needed)
- ✅ Handles semicolon-delimited CSV (European format)
- ✅ JSON output for easy integration

### System Architecture
```
CSV File (on PLC)
    ↓
FB_CSVReader (state machine)
    ↓
ST_CSVRow (13 columns)
    ↓
F_BuildJsonFromRow
    ↓
FB_MQTTPublisher (dual mode)
    ↓
broker.hivemq.com
```

---

## 📂 Project Structure

```
CSV-MQTT/
├── docs/
│   ├── README.md .................... This file
│   ├── SETUP.md ..................... Installation & configuration
│   ├── NETWORK.md ................... Network setup guide
│   ├── ARCHITECTURE.md .............. System design & pseudocode
│   └── REFERENCE.md ................. Quick reference & troubleshooting
│
├── scripts/
│   ├── DUTs/
│   │   └── ST_CSVRow.st ............. 13-column data structure
│   ├── Functions/
│   │   ├── F_GetNextLine.st ......... Line extraction
│   │   ├── F_ParseCSVLine.st ........ CSV parsing
│   │   ├── F_AssignField.st ......... Field assignment
│   │   └── F_BuildJsonFromRow.st .... JSON builder
│   ├── FunctionBlocks/
│   │   ├── FB_CSVReader.st .......... CSV file reader
│   │   └── FB_MQTTPublisher.st ...... MQTT client
│   └── Programs/
│       └── PLC_PRG.st ............... Main program
│
├── lib/
│   └── INDEX.md ..................... CODESYS library catalog
│
└── archive/
    └── First PLC Architecture.md .... Original (deprecated)
```

---

## 🔧 Required Libraries

| Library | Version | Purpose |
|---------|---------|---------|
| **SysFile** | v3.5.17.0+ | File operations |
| **IotMqtt** | Latest | MQTT client |
| **Standard** | Latest | Basic functions |
| **SysTypes** | Latest | System types |

---

## ⚙️ Key Configuration

### PLC Network Settings
- **Laptop mode**: IP `192.168.137.2`, Gateway `192.168.137.1`
- **Router mode**: IP `192.168.10.204`, Gateway `192.168.10.1`

### MQTT Broker
- **Host**: `broker.hivemq.com`
- **Port**: `1883` (no TLS)
- **Credentials**: None required
- **Topic**: `UE/139ukr` (configurable)

### CSV Format
- **Delimiter**: Semicolon (`;`)
- **Columns**: Exactly 13
- **First row**: Header (skipped automatically)
- **Location**: Configurable (default: `/usr/data.csv`)

---

## 🚀 Deployment Checklist

- [ ] Import all `.st` files in correct order (see SETUP.md)
- [ ] Add required libraries to CODESYS project
- [ ] Configure network settings (see NETWORK.md)
- [ ] Set connection mode in `PLC_PRG` (`xUseLaptopMode`)
- [ ] Upload CSV file to PLC file system
- [ ] Build and download to PLC
- [ ] Set `xSystemEnable := TRUE`
- [ ] Monitor `sSystemStatus` and `iRowsProcessed`

---

## 📊 Monitoring

### Key Status Variables
- **PLC_PRG.eMainState** - System state machine
- **PLC_PRG.iRowsProcessed** - Row counter
- **fbMQTT.xConnected** - MQTT connection status
- **fbCSVReader.xBusy** - CSV reading in progress

See [REFERENCE.md](REFERENCE.md) for complete monitoring guide.

---

## 🆘 Support

- **Quick fixes**: See [REFERENCE.md](REFERENCE.md) troubleshooting section
- **Network issues**: See [NETWORK.md](NETWORK.md) common issues
- **Architecture questions**: See [ARCHITECTURE.md](ARCHITECTURE.md)

---

## 📝 Notes

- **Functions vs Function Blocks**: Functions return values, Function Blocks use outputs
- **No local MQTT broker needed**: Direct cloud connection
- **No Communication Manager needed**: MQTT library handles connections
- **CSV delimiter changed**: Using semicolon (`;`) instead of comma

---

**Project Status**: ✅ Production Ready

All components tested and documented for deployment on Eaton PLC with CODESYS v3.5.x
