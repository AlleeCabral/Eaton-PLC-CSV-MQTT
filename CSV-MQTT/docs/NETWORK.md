# NETWORK Configuration Guide

**Cloud MQTT broker setup for laptop or router connections**

---

## 📋 Table of Contents
1. [Understanding Network Basics](#understanding-network-basics)
2. [Case A: PLC → Laptop → Internet → Cloud MQTT Broker](#case-a-plc--laptop--internet--cloud-mqtt-broker)
3. [Case B: PLC → Industrial Router → Home Router → Internet → Cloud MQTT Broker](#case-b-plc--industrial-router--home-router--internet--cloud-mqtt-broker)
4. [CODESYS Communication Setup](#codesys-communication-setup)
5. [Testing MQTT Connection](#testing-mqtt-connection)

---

## Understanding Network Basics

### **IP Address** (Like a street address)
- Unique identifier for each device on network
- Your PLC: `192.168.1.204` (current, needs change for Case B)
- Format: `XXX.XXX.XXX.XXX`

### **Subnet Mask** (Defines neighborhood)
- Usually: `255.255.255.0`
- Means devices `192.168.1.X` are on same network

### **Gateway** (Like a post office)
- Device that routes traffic to other networks/internet
- Usually the router's IP address
- Example: `192.168.1.1`

### **DNS** (Phone book for internet)
- Converts names (`broker.hivemq.com`) to IP addresses
- Google DNS: `8.8.8.8` (reliable, free)
- Cloudflare DNS: `1.1.1.1`

### **DHCP** (Automatic address assignment)
- Server that automatically gives IP addresses to devices
- Your PLC uses **static IP**, so doesn't need DHCP

### **NAT** (Address translator)
- Converts private IPs (192.168.X.X) to public internet IP
- Happens automatically in routers
- Allows multiple devices to share one internet connection

---

## Case A: PLC → Laptop → Internet → Cloud MQTT Broker

### **Network Diagram**
```
┌──────────────────────────────────────────────────────┐
│                                                      │
│  ┌──────────────┐         ┌──────────────────────┐  │
│  │  Eaton PLC   │ Ethernet│      Your Laptop     │  │
│  │              │────────→│                      │  │
│  │ 192.168.137.2│         │  Ethernet: 192.168.137.1│
│  └──────────────┘         │  WiFi: Connected     │  │
│                           │  (Internet Sharing)  │  │
│                           └──────────┬───────────┘  │
│                                      │              │
└──────────────────────────────────────┼──────────────┘
                                       │ WiFi
                                       ▼
                                  Internet
                                       │
                                       ▼
                            ┌────────────────────┐
                            │ Cloud MQTT Broker  │
                            │ broker.hivemq.com  │
                            │ Port: 1883         │
                            │ (No credentials)   │
                            └────────────────────┘
```

### **Step 1: Enable Internet Sharing on Laptop**

**Windows 10/11:**
```
1. Open "Network Connections" (ncpa.cpl)
2. Right-click your WiFi adapter → Properties
3. Go to "Sharing" tab
4. ✅ Check "Allow other network users to connect"
5. Select: Ethernet adapter (the one connected to PLC)
6. Click OK
```

**Result:**
- Laptop Ethernet becomes: `192.168.137.1`
- Laptop acts as DHCP server for range: `192.168.137.x`

### **Step 2: Configure PLC Network Settings**

**In CODESYS or PLC Web Interface:**
```
IP Address:    192.168.137.2
Subnet Mask:   255.255.255.0
Gateway:       192.168.137.1  (laptop)
DNS Server:    8.8.8.8        (Google DNS)
```

**Why these values?**
- `192.168.137.X` = Windows Internet Sharing always uses this range
- `192.168.137.1` = Laptop automatically gets this IP when sharing
- `192.168.137.2` = Available IP for PLC (you can use .2 to .254)
- `8.8.8.8` = Google DNS to resolve broker.hivemq.com

### **Step 3: Configure FB_MQTTPublisher in PLC Code**

**Connection to cloud broker (broker.hivemq.com):**
```st
VAR
    fbMQTT : FB_MQTTPublisher;
END_VAR

// Configuration
fbMQTT.xEnable := TRUE;
fbMQTT.xUseLaptop := TRUE;                    // Laptop gateway mode
fbMQTT.sBrokerLaptop := 'broker.hivemq.com';  // Public cloud broker
fbMQTT.uiPort := 1883;                        // Standard MQTT port (no TLS)
fbMQTT.sTopic := 'UE/139ukr';                 // Your topic
```

**Alternative public brokers:**
```st
// HiveMQ Cloud (free tier, no credentials on port 1883)
fbMQTT.sBrokerLaptop := 'broker.hivemq.com';

// Eclipse Mosquitto test server
fbMQTT.sBrokerLaptop := 'test.mosquitto.org';

// EMQX public broker
fbMQTT.sBrokerLaptop := 'broker.emqx.io';
```

### **Step 4: Test Connection**

**From laptop (verify internet and broker access):**
```powershell
# Test if cloud broker is reachable
ping broker.hivemq.com

# Install Mosquitto clients for testing (optional)
# Download from: https://mosquitto.org/download/

# Subscribe to your topic to see PLC messages
mosquitto_sub -h broker.hivemq.com -t "UE/139ukr" -v

# Publish a test message
mosquitto_pub -h broker.hivemq.com -t "UE/139ukr" -m "test from laptop"
```

---

## Case B: PLC → Industrial Router → Home Router → Internet → Cloud MQTT Broker

### **Network Diagram**
```
┌───────────────────────────────────────────────────────────────┐
│  Industrial Network (Subnet: 192.168.10.0/24)                 │
│                                                                │
│  ┌──────────────┐         ┌────────────────────────────┐      │
│  │  Eaton PLC   │ Ethernet│  Industrial Router         │      │
│  │              │────────→│  (Weidmüller IE-SR-2GT)    │      │
│  │192.168.10.204│   LAN   │                            │      │
│  └──────────────┘         │  LAN: 192.168.10.1         │      │
│                           │  WAN: 192.168.1.200        │      │
│                           └──────────────┬─────────────┘      │
└────────────────────────────────────────┼────────────────────┘
                                         │ WAN (Ethernet)
                                         ▼
┌───────────────────────────────────────────────────────────────┐
│  Home Network (Subnet: 192.168.1.0/24)                        │
│                                                                │
│                           ┌────────────────────────────┐       │
│                           │  VODAFONE FF44 Router      │       │
│                           │                            │       │
│                           │  LAN: 192.168.1.1          │       │
│                           │  WAN: Public IP (from ISP) │       │
│                           └──────────────┬─────────────┘       │
└────────────────────────────────────────┼───────────────────────┘
                                         │ Internet
                                         ▼
                            ┌─────────────────────────┐
                            │  Cloud MQTT Broker      │
                            │  broker.hivemq.com      │
                            │  Port: 1883             │
                            │  (No credentials)       │
                            └─────────────────────────┘
```

### **Network Explanation**

**Two Separate Networks:**
1. **Industrial Network**: `192.168.10.X` (PLC side)
2. **Home Network**: `192.168.1.X` (Internet side)

**Industrial Router Acts As:**
- Gateway between two networks
- NAT device (translates addresses)
- Firewall (security)

### **Step 1: Configure Industrial Router (IE-SR-2GT)**

**Access router web interface:**
```
1. Connect laptop to router LAN port temporarily
2. Open browser: http://192.168.1.1 (or router's default IP)
3. Login with default credentials (check manual)
```

**WAN Interface Configuration (Internet side):**
```
Connection Type: Static IP
IP Address:      192.168.1.200
Subnet Mask:     255.255.255.0
Gateway:         192.168.1.1  (VODAFONE router)
DNS Primary:     8.8.8.8      (Google DNS)
DNS Secondary:   1.1.1.1      (Cloudflare DNS)
```

**Why these values?**
- `192.168.1.200` = Free IP in your home network range
- `192.168.1.1` = Your VODAFONE router's IP
- `8.8.8.8` = Reliable public DNS to resolve broker.hivemq.com

**LAN Interface Configuration (PLC side):**
```
IP Address:      192.168.10.1
Subnet Mask:     255.255.255.0
DHCP Server:     Disabled (PLC has static IP)
```

**NAT Configuration:**
```
Enable NAT:      YES
NAT Mode:        Masquerade/SNAT
Allow outbound:  All
```

**Firewall Configuration:**
```
Outbound Rules:
- Allow TCP port 1883 (MQTT)
- Allow TCP port 8883 (MQTT over TLS, for future use)
- Allow UDP port 53 (DNS)

Inbound Rules:
- Block all (no need for incoming connections)
```

### **Step 2: Configure VODAFONE Router**

**Access router:**
```
Browser: http://192.168.1.1
Login with your router credentials
```

**Reserve IP for Industrial Router (Optional but recommended):**
```
DHCP Settings → Static Lease
MAC Address: [Industrial Router MAC]
IP Address:  192.168.1.200
```

**Port Forwarding:**
```
NOT NEEDED for outbound MQTT publishing
PLC only needs to connect OUT to cloud broker
```

### **Step 3: Configure PLC Network Settings**

**⚠️ IMPORTANT: Your PLC currently has IP 192.168.1.204**
**You need to CHANGE it to fit the industrial network:**

**In CODESYS or PLC Web Interface:**
```
OLD (won't work):
IP Address:    192.168.1.204  ❌

NEW (correct):
IP Address:    192.168.10.204  ✅
Subnet Mask:   255.255.255.0
Gateway:       192.168.10.1    (industrial router)
DNS Server:    8.8.8.8         (Google DNS)
```

**Why change from .1.204 to .10.204?**
- PLC must be in industrial router's LAN network (192.168.10.X)
- Industrial router is at 192.168.10.1 (your gateway)
- Router will translate 192.168.10.204 → 192.168.1.200 → Internet

### **Step 4: Configure FB_MQTTPublisher in PLC Code**

**Connection to cloud broker:**
```st
VAR
    fbMQTT : FB_MQTTPublisher;
END_VAR

// Configuration
fbMQTT.xEnable := TRUE;
fbMQTT.xUseLaptop := FALSE;                // Using LAN/Router mode
fbMQTT.sBrokerLAN := 'broker.hivemq.com';  // Public cloud broker
fbMQTT.uiPort := 1883;                     // Standard MQTT port (no TLS)
fbMQTT.sTopic := 'UE/139ukr';              // Your topic
```

**Alternative public brokers:**
```st
// HiveMQ Cloud (default)
fbMQTT.sBrokerLAN := 'broker.hivemq.com';

// Eclipse Mosquitto test server
fbMQTT.sBrokerLAN := 'test.mosquitto.org';

// EMQX public broker
fbMQTT.sBrokerLAN := 'broker.emqx.io';
```

### **Step 5: Test Connectivity**

**Test from PLC (if you have access to PLC terminal/diagnostics):**
```bash
# Test gateway (industrial router)
ping 192.168.10.1    # Should work

# Test home router
ping 192.168.1.1     # Should work (routed through gateway)

# Test internet
ping 8.8.8.8         # Should work (confirms internet access)

# Test DNS and broker
ping broker.hivemq.com  # Should resolve and respond
```

**Troubleshooting command from PLC:**
```bash
traceroute broker.hivemq.com
# Should show:
# 1. 192.168.10.1 (industrial router)
# 2. 192.168.1.1 (home router)
# 3. [ISP hops]
# 4. broker.hivemq.com
```

---

## CODESYS Communication Setup

### **Do You Need Communication Manager or Network Variable List?**

**Answer: NO** ❌

**Why?**
- `FB_MQTTPublisher` handles all MQTT communication internally
- CODESYS Communication Manager is for other protocols (OPC UA, Modbus, etc.)
- Network Variable List is for PLC-to-PLC communication
- Your MQTT library (IotMqtt) manages the socket connection automatically

### **What You DO Need in CODESYS:**

**1. Add Libraries:**
```
Library Manager → Add Library:
- IotMqtt (or MQTT) - for MQTT client
- SysFile - for file operations
- Standard - basic functions
- SysTypes - system types
```

**2. Create POUs (Already done in your scripts):**
```
- ST_CSVRow (DUT)
- F_GetNextLine (Function)
- F_ParseCSVLine (Function)
- F_AssignField (Function)
- F_BuildJsonFromRow (Function)
- FB_CSVReader (Function Block)
- FB_MQTTPublisher (Function Block)
- PLC_PRG (Program)
```

**3. Instantiate in PLC_PRG (Already in your code):**
```st
PROGRAM PLC_PRG
VAR
    fbCSVReader : FB_CSVReader;
    fbMQTT      : FB_MQTTPublisher;
    // ... other variables
END_VAR

// Your existing state machine code
// No additional communication objects needed!
```

### **Network Settings in CODESYS IDE:**

**For Case A (Laptop):**
```
Tools → Device → Ethernet Adapter Settings
IP Address:     192.168.137.2
Subnet:         255.255.255.0
Gateway:        192.168.137.1
DNS:            8.8.8.8
```

**For Case B (Industrial Router):**
```
Tools → Device → Ethernet Adapter Settings
IP Address:     192.168.10.204  ← Changed from 192.168.1.204
Subnet:         255.255.255.0
Gateway:        192.168.10.1
DNS:            8.8.8.8
```

---

## Testing MQTT Connection

### **Using Mosquitto Command Line Clients**

**Install Mosquitto clients on your laptop:**
```powershell
# Download from: https://mosquitto.org/download/
# Windows installer includes mosquitto_pub and mosquitto_sub utilities
```

### **Subscribe to PLC Topic (Monitor Messages)**

**For broker.hivemq.com:**
```powershell
# Listen to all messages from your PLC
mosquitto_sub -h broker.hivemq.com -t "UE/139ukr" -v

# Listen with debug output
mosquitto_sub -h broker.hivemq.com -t "UE/139ukr" -v -d
```

### **Publish Test Messages**

**Send test message to verify PLC subscription:**
```powershell
# Send a simple test message
mosquitto_pub -h broker.hivemq.com -t "UE/139ukr" -m "Hello from laptop"

# Send JSON format (like PLC will send)
mosquitto_pub -h broker.hivemq.com -t "UE/139ukr" -m "{\"Col1\":\"test\",\"Col2\":\"data\"}"
```

### **Using MQTT Explorer (GUI Tool)**

**Download and install:**
```
Website: http://mqtt-explorer.com/
Platform: Windows, Mac, Linux
```

**Configuration:**
```
Protocol:  mqtt://
Host:      broker.hivemq.com
Port:      1883
Username:  (leave empty)
Password:  (leave empty)
```

**Connect and:**
- Browse topics in tree view
- See live messages from PLC
- Publish test messages
- View message history
- Export data

---

## Quick Reference Tables

### **Case A: PLC → Laptop**

| Device | Interface | IP Address | Gateway | DNS |
|--------|-----------|------------|---------|-----|
| PLC | Ethernet | 192.168.137.2 | 192.168.137.1 | 8.8.8.8 |
| Laptop | Ethernet | 192.168.137.1 | - | - |
| Laptop | WiFi | (varies) | (ISP router) | 8.8.8.8 |
| Broker | - | broker.hivemq.com:1883 | - | - |

**PLC Code:**
```st
fbMQTT.xUseLaptop := TRUE;
fbMQTT.sBrokerLaptop := 'broker.hivemq.com';
```

---

### **Case B: PLC → Industrial Router → Home Router**

| Device | Interface | IP Address | Subnet | Gateway | DNS |
|--------|-----------|------------|--------|---------|-----|
| PLC | Ethernet | 192.168.10.204 | 255.255.255.0 | 192.168.10.1 | 8.8.8.8 |
| Industrial Router | LAN | 192.168.10.1 | 255.255.255.0 | - | - |
| Industrial Router | WAN | 192.168.1.200 | 255.255.255.0 | 192.168.1.1 | 8.8.8.8 |
| Home Router | LAN | 192.168.1.1 | 255.255.255.0 | - | - |
| Home Router | WAN | (ISP assigned) | - | (ISP) | - |
| Broker | - | broker.hivemq.com:1883 | - | - | - |

**PLC Code:**
```st
fbMQTT.xUseLaptop := FALSE;
fbMQTT.sBrokerLAN := 'broker.hivemq.com';
```

---

## Common Issues & Solutions

### **Issue 1: PLC can't reach gateway**
```
Symptom: Can't ping 192.168.137.1 or 192.168.10.1
Solution: 
- Check Ethernet cable
- Verify PLC IP is in correct subnet
- Check gateway IP matches router LAN IP
- Verify subnet mask is 255.255.255.0
```

### **Issue 2: Can reach gateway but not internet**
```
Symptom: Can ping gateway, but not 8.8.8.8
Solution:
- Case A: Check laptop Internet Sharing is enabled
- Case B: Check industrial router NAT is enabled
- Verify DNS settings (8.8.8.8)
- Check router firewall allows outbound traffic
```

### **Issue 3: Can't resolve broker.hivemq.com**
```
Symptom: Can ping 8.8.8.8 but not broker.hivemq.com
Solution:
- Verify DNS server is set to 8.8.8.8
- Check DNS requests are allowed through firewall (UDP port 53)
- Try alternative DNS: 1.1.1.1 (Cloudflare)
- Test with "nslookup broker.hivemq.com"
```

### **Issue 4: MQTT connection fails**
```
Symptom: fbMQTT.xConnected = FALSE
Solution:
- Verify broker hostname is correct: 'broker.hivemq.com'
- Check port is 1883 (not 8883 for TLS)
- Verify firewall allows outbound TCP port 1883
- Test broker from laptop: mosquitto_sub -h broker.hivemq.com -t "test"
- Check fbMQTT.sStatus for error message
```

### **Issue 5: Wrong PLC IP (192.168.1.204 in Case B)**
```
Symptom: Nothing works with industrial router
Solution:
- Change PLC IP to 192.168.10.204
- PLC must be in industrial router's LAN subnet (192.168.10.X)
- Gateway must be 192.168.10.1
- Verify changes with ping test from PLC
```

### **Issue 6: Messages not appearing on broker**
```
Symptom: PLC shows connected but no messages on mosquitto_sub
Solution:
- Verify topic name matches: 'UE/139ukr'
- Check fbMQTT.xPublished pulse is TRUE
- Verify CSV file is being read (check fbCSVReader.xBusy)
- Test broker subscription: mosquitto_sub -h broker.hivemq.com -t "#" -v
- Check fbMQTT.sStatus for publish errors
```

---

## Summary Checklist

### **Case A Setup:**
- [ ] Enable Internet Sharing on laptop
- [ ] Set PLC IP: 192.168.137.2
- [ ] Set PLC gateway: 192.168.137.1
- [ ] Set PLC DNS: 8.8.8.8
- [ ] Configure FB_MQTTPublisher with xUseLaptop = TRUE
- [ ] Set sBrokerLaptop = 'broker.hivemq.com'
- [ ] Test ping from laptop to broker.hivemq.com
- [ ] Subscribe to topic with mosquitto_sub
- [ ] Download and run PLC program
- [ ] Verify messages appear in mosquitto_sub

### **Case B Setup:**
- [ ] Configure industrial router WAN: 192.168.1.200
- [ ] Configure industrial router LAN: 192.168.10.1
- [ ] Enable NAT on industrial router
- [ ] Configure DNS on industrial router: 8.8.8.8
- [ ] Change PLC IP from 192.168.1.204 to 192.168.10.204
- [ ] Set PLC gateway: 192.168.10.1
- [ ] Set PLC DNS: 8.8.8.8
- [ ] Configure FB_MQTTPublisher with xUseLaptop = FALSE
- [ ] Set sBrokerLAN = 'broker.hivemq.com'
- [ ] Test connectivity: PLC → router → internet
- [ ] Test DNS: ping broker.hivemq.com from PLC
- [ ] Subscribe to topic with mosquitto_sub from laptop
- [ ] Download and run PLC program
- [ ] Verify messages appear in mosquitto_sub

---

**Key Differences from Previous Configuration:**
- ✅ **No local Mosquitto installation needed**
- ✅ **Direct connection to cloud broker (broker.hivemq.com)**
- ✅ **Both connection modes use same cloud broker**
- ✅ **Simplified architecture - no local broker management**
- ✅ **Port 1883 (no TLS) - no certificate configuration needed**

---

**Created:** November 9, 2025
**For:** Eaton PLC CSV-MQTT Project (Cloud Broker Only)
**Your PLC IP:** Currently 192.168.1.204 (change to 192.168.10.204 for Case B)
**Cloud Broker:** broker.hivemq.com:1883 (no credentials required)
