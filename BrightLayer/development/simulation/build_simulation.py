#!/usr/bin/env python3
"""
build_simulation.py
Creates Simulation/Simulation_RO.json for Node-RED import.
Template: applications/regional-node-red/peru-148/full_program_nodered  (Trends + UsedTrends functions copied verbatim)
"""
import json, os, sys, uuid

def nid():
    """Generate a Node-RED style 16-hex-char node ID."""
    return uuid.uuid4().hex[:16]

SOURCE   = r'applications\regional-node-red\peru-148\full_program_nodered'
OUT_DIR  = r'development\simulation\Simulation'
OUT_FILE = os.path.join(OUT_DIR, 'Simulation_RO.json')

# ─── Load source flow ────────────────────────────────────────────────────────
with open(SOURCE, 'r', encoding='utf-8') as f:
    source = json.load(f)

by_id = {n['id']: n for n in source if isinstance(n, dict) and 'id' in n}

# Node IDs we copy verbatim from full_program_nodered
TRENDS_ID        = '6fb0ac50391047cf'   # Trends_filtration_060526
USED_DBG_ID      = '6eeef58c.fd0f9c'   # Used Trends Debug
USED_ARR_ID      = '9ce6f4f7.b3b838'   # Used Trends (Array)²

for node_id, label in [(TRENDS_ID,'Trends'),(USED_DBG_ID,'UsedTrendsDebug'),(USED_ARR_ID,'UsedTrendsArray')]:
    if node_id not in by_id:
        print(f"ERROR: node {node_id} ({label}) not found in source file", file=sys.stderr)
        sys.exit(1)

# ─── PLC Simulator function body ─────────────────────────────────────────────
PLC_SIM_FUNC = r"""
// ╔══════════════════════════════════════════════════════════════════════════╗
// ║  PLC SIMULATOR - Peru 148 RO Water Filtration System                   ║
// ║  Replaces BOTH UDP NetVar receivers (port 1203 + 1202).                 ║
// ║  Sets global context identically to "Parse NetVar triplets".            ║
// ╠══════════════════════════════════════════════════════════════════════════╣
// ║  HOW TO CONFIGURE UPDATE FREQUENCY                                      ║
// ║                                                                         ║
// ║  ▶ OPTION A – change the main cycle rate (recommended):                ║
// ║      1. Double-click the "▶ 30s cycle (main)" inject node              ║
// ║      2. Change "Repeat every __ seconds" to any value                  ║
// ║      3. Click Done → Deploy                                             ║
// ║      Suggested values: 5s (fast debug) | 30s (default) | 300s (real)   ║
// ║                                                                         ║
// ║  ▶ OPTION B – use a preset inject (enable one, disable main):          ║
// ║      Right-click "⚡ Fast: 5s"  → Enable   (disable ▶ 30s first)      ║
// ║      Right-click "🐢 Slow: 300s" → Enable  (disable ▶ 30s first)      ║
// ║      ⚠  Only ONE inject node should run at a time.                     ║
// ║                                                                         ║
// ║  ▶ OPTION C – one-shot manual tick:                                    ║
// ║      Click the square button on "▶ Manual trigger"                     ║
// ╚══════════════════════════════════════════════════════════════════════════╝

// ── State persistence between ticks (totals accumulate) ──────────────────
const STATE_KEY = "sim_peru148_state";
let s = flow.get(STATE_KEY) || {
    solarTotal:       120.5,  solarToday:      3.2,
    solarThisHour:    0.8,    solarThisMonth:  48.2,
    gridTotal:        15.1,   gridToday:       0.0,
    gridThisHour:     0.0,    gridThisMonth:   0.0,
    outTotal:         135.6,  outToday:        3.2,
    outThisHour:      0.8,    outThisMonth:    48.2,
    rawTotal:         52.4,   rawToday:        1.85,
    rawThisHour:      0.38,   rawThisMonth:    18.2,
    permTotal:        38.1,   permToday:       1.38,
    permThisHour:     0.28,   permThisMonth:   13.5,
    runTotal:         14520,
    uvInHours:        2340,   uvOutHours:      2340,
    uvInSwitch:       12,     uvOutSwitch:     8,
    boreholeTotalRun: 1820,
    boostTotalRun:    2150,
    feedTotalRun:     3200,
    lastTick:         Date.now()
};

const now = Date.now();
// Elapsed seconds since last call (capped at 120s to avoid huge jumps on restart)
const elapsed = Math.min((now - s.lastTick) / 1000, 120);
s.lastTick = now;

// ── Helpers ───────────────────────────────────────────────────────────────
function jitter(base, pct) { return base * (1 + (Math.random() * 2 - 1) * pct / 100); }
function r2(v) { return parseFloat(v.toFixed(2)); }
function r1(v) { return parseFloat(v.toFixed(1)); }

// ── Time context ──────────────────────────────────────────────────────────
const d = new Date();
const H = d.getHours();
const daytime = (H >= 7 && H < 18);   // solar production hours

// ── Solar/Grid power scenario ─────────────────────────────────────────────
const solarW = daytime ? jitter(2500, 5) : 0;
const gridW  = daytime ? 0 : jitter(2200, 3);
const totalW = solarW + gridW;
const feedW  = daytime ? jitter(1100, 4) : 0;
const boostW = daytime ? jitter(820,  4) : 0;
const pumpW  = daytime ? jitter(650,  5) : 0;

// ── Accumulate energy (kWh = W × s ÷ 3600000) ────────────────────────────
const kwhInc = (w, dt) => (w * dt) / 3600000;
s.solarThisHour  += kwhInc(solarW, elapsed);
s.solarToday     += kwhInc(solarW, elapsed);
s.solarThisMonth += kwhInc(solarW, elapsed);
s.solarTotal     += kwhInc(solarW, elapsed);
s.gridThisHour   += kwhInc(gridW,  elapsed);
s.gridToday      += kwhInc(gridW,  elapsed);
s.gridThisMonth  += kwhInc(gridW,  elapsed);
s.gridTotal      += kwhInc(gridW,  elapsed);
s.outThisHour    += kwhInc(totalW, elapsed);
s.outToday       += kwhInc(totalW, elapsed);
s.outThisMonth   += kwhInc(totalW, elapsed);
s.outTotal       += kwhInc(totalW, elapsed);

// ── Accumulate water volume (m³ = m³/h × s ÷ 3600) ───────────────────────
const rawRate  = daytime ? jitter(0.6,  3) : 0;    // m³/h raw water
const permRate = daytime ? jitter(0.45, 3) : 0;    // m³/h permeate (~75% recovery)
const m3Inc = (r, dt) => (r * dt) / 3600;
s.rawThisHour  += m3Inc(rawRate,  elapsed);
s.rawToday     += m3Inc(rawRate,  elapsed);
s.rawThisMonth += m3Inc(rawRate,  elapsed);
s.rawTotal     += m3Inc(rawRate,  elapsed);
s.permThisHour += m3Inc(permRate, elapsed);
s.permToday    += m3Inc(permRate, elapsed);
s.permThisMonth+= m3Inc(permRate, elapsed);
s.permTotal    += m3Inc(permRate, elapsed);

// ── Accumulate runtimes (seconds) ─────────────────────────────────────────
s.runTotal += elapsed;
if (daytime) {
    s.boreholeTotalRun += elapsed;
    s.boostTotalRun    += elapsed;
    s.feedTotalRun     += elapsed;
    s.uvInHours  += elapsed / 3600;
    s.uvOutHours += elapsed / 3600;
}
flow.set(STATE_KEY, s);

// ── Inverter electrical values ────────────────────────────────────────────
const dcFeed    = daytime ? Math.round(jitter(382, 2)) : 0;
const dcBooster = daytime ? Math.round(jitter(378, 2)) : 0;
const dcPump    = daytime ? Math.round(jitter(375, 2)) : 0;
const tFeed     = r1(daytime ? jitter(43.5, 3) : jitter(25, 2));
const tBooster  = r1(daytime ? jitter(42.1, 3) : jitter(24, 2));
const tPump     = r1(daytime ? jitter(41.8, 3) : jitter(24, 2));
const fFeed     = r1(daytime ? jitter(47.5, 2) : 0);
const fBooster  = r1(daytime ? jitter(45.2, 2) : 0);
const fPump     = r1(daytime ? jitter(43.8, 3) : 0);
const iFeed     = r2(daytime ? jitter(4.8, 4) : 0);
const iBooster  = r2(daytime ? jitter(3.6, 4) : 0);
const iPump     = r2(daytime ? jitter(3.0, 5) : 0);
const iTot      = r2(daytime ? jitter(11.4, 3) : jitter(7.2, 3));

// ╔══════════════════════════════════════════════════════════════════════════╗
// ║  PLC variable object — names match EXACTLY what Parse NetVar triplets   ║
// ║  produces (getFirst() in Trends will find them via case-insensitive     ║
// ║  lookup).  All alarms = 0 → healthy machine, normal Pro/Solar mode.     ║
// ╚══════════════════════════════════════════════════════════════════════════╝
const plc = {
    // ── PORT 1203 ── BOOLs (switches / status / alarms) ──────────────────
    _11_Auto_Manual:                               1,
    _12_CIP_Switch:                                0,
    _13_Feed_Switch:                               daytime ? 1 : 0,
    _14_Booster_Switch:                            daytime ? 1 : 0,
    _15_Back_Wash_Switch:                          0,
    _16_Bohrhole_Switch:                           daytime ? 1 : 0,
    _17_Uv_Out_Switch:                             daytime ? 1 : 0,
    _18_Machine_Run:                               daytime ? 1 : 0,
    _19_CIPtank_High:                              0,
    _20_CIPtank_Low:                               1,
    _21_Anti_Scalant_Tank:                         1,
    _22_Raw_Water_Tank_High:                       0,
    _23_Raw_Water_Tank_Low:                        daytime ? 0 : 1,
    _24_Borhole_Float_Switch:                      1,
    _25_Premeate_Tank:                             daytime ? 0 : 1,
    _26_Grid_is_ON:                                daytime ? 0 : 1,
    _27_Alarm_Well_Level_Alarm:                    0,
    _28_Alarm_Feed_Inverter_Status_Alarm:          0,
    _29_Alarm_Booster_Inverter_Status_Alarm:       0,
    _30_Alarm_Bohrhole_Inverter_Status_Alarm:      0,
    _31_Alarm_High_Pressure_Alarm:                 0,
    _32_Alarm_High_TDS_Alarm:                      0,
    _33_Alarm_Feed_Inverter_Temperature_Alarm:     0,
    _34_Alarm_Booster_Inverter_Temperature_Alarm:  0,
    _35_Alarm_Bohrhole_Inverter_Temperature_Alarm: 0,
    _36_Alarm_UV_In_Lamp_Alarm:                    0,
    _37_Alarm_UV_Out_Lamp_Alarm:                   0,
    _38_Alarm_Anti_Scalant_Alarm:                  0,
    _39_Alarm_Flow_Meter_Alarm:                    0,
    _40_Alarm_Unstable_Voltage_Alarm:              0,
    _41_AlarmRaw_Tank_Alarm:                       0,
    _42_Alarm_Valve_1_Alarm:                       0,
    _43_Alarm_Valve_2_Alarm:                       0,
    _44_Alarm_Valve_3_Alarm:                       0,
    _45_Alarm_Valve_4_Alarm:                       0,
    _46_Alarm_Valve_5_Alarm:                       0,

    // ── PORT 1203 ── REALs & INTs (power, measurements) ──────────────────
    _50_Solar_Power:                   r1(solarW),
    _51_Grid_Power:                    r1(gridW),
    _52_Total_Power:                   r1(totalW),
    _53_Feed_Power:                    r1(feedW),
    _54_Booster_Power:                 r1(boostW),
    _55_Pump_Power:                    r1(pumpW),
    _56_Machine_Capacity:              daytime ? Math.round(jitter(85, 5)) : 0,
    _57_Machine_Grid_Percentage:       daytime ? 0 : 100,
    _58_Machine_Solar_Percentage:      daytime ? 100 : 0,
    _59_Alarm:                         0,
    _60_Total_Current:                 iTot,
    _61_DC_Voltage_Feed:               dcFeed,
    _62_DC_Voltage_Booster:            dcBooster,
    _63_DC_Voltage_Pump:               dcPump,
    _64_Temperature_Inverter_Feed:     tFeed,
    _65_Temperature_Inverter_Booster:  tBooster,
    _66_Temperature_Inverter_Pump:     tPump,
    _67_Frequency_Inverter_Feed:       fFeed,
    _68_Frequency_Inverter_Booster:    fBooster,
    _69_Frequency_Inverter_Pump:       fPump,
    _70_Current_Inverter_Feed:         iFeed,
    _71_Current_Inverter_Booster:      iBooster,
    _72_Current_Inverter_Pump:         iPump,
    _73_Solar_Power_KWh_Total:         r2(s.solarTotal),
    _74_Solar_Power_KWh_This_Hour:     r2(s.solarThisHour),
    _75_Solar_Power_KWh_Today:         r2(s.solarToday),
    _76_Solar_Power_KWh_This_Month:    r2(s.solarThisMonth),
    _77_Grid_Power_KWh_Total:          r2(s.gridTotal),
    _78_Grid_Power_KWh_This_Hour:      r2(s.gridThisHour),
    _79_Grid_Power_KWh_Today:          r2(s.gridToday),
    _80_Grid_Power_KWh_This_Month:     r2(s.gridThisMonth),
    _81_Output_Power_KWh_Total:        r2(s.outTotal),
    _82_Output_Power_KWh_This_Hour:    r2(s.outThisHour),
    _83_Output_Power_KWh_Today:        r2(s.outToday),
    _84_Output_Power_KWh_This_Month:   r2(s.outThisMonth),
    _85_Raw_Water_M3_Total:            r2(s.rawTotal),
    _86_Raw_Water_M3_This_Hour:        r2(s.rawThisHour),
    _87_Raw_Water_M3_Today:            r2(s.rawToday),
    _88_Raw_Water_M3_This_Month:       r2(s.rawThisMonth),
    _89_Premeate_Water_M3_Total:       r2(s.permTotal),
    _90_Premeate_Water_M3_This_Hour:   r2(s.permThisHour),
    _91_Premeate_Water_M3_Today:       r2(s.permToday),
    _92_Premeate_Water_M3_This_Month:  r2(s.permThisMonth),
    _93_Current_Hour:                  d.getHours(),
    _94_Current_Day:                   d.getDate(),
    _95_Current_Month:                 d.getMonth() + 1,
    _96_Current_Year:                  d.getFullYear(),
    _97_Machine_Mode_Pro:              daytime ? 1 : 0,
    _98_Machine_Mode_CIP:              0,
    _99_Machine_Mode_Filling:          daytime ? 0 : 1,
    _100_Machine_Mode_Flush:           0,
    _101_Machine_Mode_Backwash:        0,
    _102_Machine_Mode_Bohrhole:        0,
    _103_Datum_Backwash_Done:          0,
    _104_Datum_CIP_Done:               0,
    _105_Dosing_Pump_Alarm:            0,

    // ── PORT 1202 ── Secondary variables ──────────────────────────────────
    _106_EC_Value:           r1(jitter(450, 3)),
    _107_Pressure_Value:     r2(jitter(8.5, 4)),
    _108_UV_In_Work_Hours:   Math.round(s.uvInHours),
    _109_UV_Out_Work_Hours:  Math.round(s.uvOutHours),
    _110_UV_In_Switching:    s.uvInSwitch,
    _111_Antitank_Empty:     0,
    _112_UV_In_Ctrl:         daytime ? 1 : 0,
    _113_UV_Out_Ctrl:        daytime ? 1 : 0,
    _114_Rawtank_Low_Lvl:    0,
    _115_Rawtank_Top_Lvl:    daytime ? 0 : 1,
    _116_Premtank_Top_Lvl:   daytime ? 0 : 1,
    _117_Mains_On:           daytime ? 0 : 1,
    _118_Anti_Pump:          0,
    _119_Borehole_Total_Run: Math.round(s.boreholeTotalRun),
    _120_Boost_Total_Run:    Math.round(s.boostTotalRun),
    _121_Feed_Total_Run:     Math.round(s.feedTotalRun),
    _122_CIP_Full:           0,
    _123_CIP_Empty:          1,
    _124_SCBW_V1_Ctrl:       0,
    _125_Water_Flowing:      daytime ? 1 : 0,
    _126_Pipe_Pressure:      r2(jitter(6.2, 4))
};

// ── Store in global context (identical to Parse NetVar triplets) ──────────
const merged = Object.assign(global.get("plc") || {}, plc);
global.set("plc", merged);
for (const [k, v] of Object.entries(plc)) {
    global.set(k, v);
}
// Required by Trends function (used in telemetry 'p' property)
global.set("second_gwId", "30d5ef4e-835e-43e3-a839-5069d5d06b1d");

msg.payload = plc;
msg.topic = "sim-plc-values";
return msg;
""".strip()

# ─── Generate all node IDs up front (proper hex format) ──────────────────────
TAB          = nid()
ID_CMT_FREQ  = nid()
ID_INJ_30S   = nid()
ID_INJ_MAN   = nid()
ID_INJ_5S    = nid()
ID_INJ_300S  = nid()
ID_FN_SIM    = nid()
ID_DBG_RAW   = nid()
ID_CMT_PIPE  = nid()
ID_FN_TRENDS = nid()
ID_FN_READ   = nid()
ID_FN_ARR    = nid()
ID_DBG_READ  = nid()
ID_DBG_ARR   = nid()
ID_DBG_JSON  = nid()

# Print the IDs so they can be found in the UI
print(f"Tab ID          : {TAB}")
print(f"Inject 30s      : {ID_INJ_30S}")
print(f"Inject Manual   : {ID_INJ_MAN}")
print(f"Inject 5s       : {ID_INJ_5S}  (disabled)")
print(f"Inject 300s     : {ID_INJ_300S} (disabled)")
print(f"PLC Sim fn      : {ID_FN_SIM}")
print(f"Trends fn       : {ID_FN_TRENDS}")

nodes = []

# ── Tab node ──────────────────────────────────────────────────────────────────
nodes.append({
    "id": TAB, "type": "tab",
    "label": "SIM - Peru 148",
    "disabled": False,
    "info": "Simulation tab for Peru 148 RO Water Filtration.\nUse the inject nodes to control update frequency.\nSee PLC Simulator function header for full documentation.",
    "env": []
})

# ── Comment: frequency configuration ─────────────────────────────────────────
nodes.append({
    "id": ID_CMT_FREQ, "type": "comment", "z": TAB,
    "name": "⚙ FREQUENCY CONFIG  ─  A: edit '▶ 30s cycle' repeat field  ─  B: enable ⚡5s or 🐢300s (disable main first)  ─  C: click ▶ Manual for one-shot",
    "info": (
        "HOW TO CONFIGURE UPDATE FREQUENCY\n"
        "══════════════════════════════════\n\n"
        "OPTION A – change the main cycle rate (recommended)\n"
        "  1. Double-click the '▶ 30s cycle (main)' inject node\n"
        "  2. Change 'Repeat every __ seconds' to any value\n"
        "     (5s = fast debug | 30s = default | 300s = real BL rate)\n"
        "  3. Click Done → Deploy\n\n"
        "OPTION B – use a preset inject\n"
        "  Right-click '⚡ Fast: 5s'   → Enable   (disable ▶ 30s first)\n"
        "  Right-click '🐢 Slow: 300s' → Enable   (disable ▶ 30s first)\n"
        "  ⚠  Only ONE inject should run at a time.\n\n"
        "OPTION C – one-shot manual tick\n"
        "  Click the ■ button on the '▶ Manual trigger' inject node.\n\n"
        "NOTE: All frequency settings survive a Deploy but are reset if\n"
        "Node-RED restarts unless saved."
    ),
    "x": 440, "y": 60, "wires": []
})

# ── Inject: 30s main ─────────────────────────────────────────────────────────
nodes.append({
    "id": ID_INJ_30S, "type": "inject", "z": TAB,
    "name": "▶ 30s cycle (main)",
    "props": [{"p": "payload"}, {"p": "topic", "vt": "str"}],
    "repeat": "30", "crontab": "",
    "once": True, "onceDelay": 0.1,
    "topic": "", "payload": "", "payloadType": "date",
    "x": 170, "y": 180,
    "wires": [[ID_FN_SIM]]
})

# ── Inject: Manual ────────────────────────────────────────────────────────────
nodes.append({
    "id": ID_INJ_MAN, "type": "inject", "z": TAB,
    "name": "▶ Manual trigger",
    "props": [{"p": "payload"}, {"p": "topic", "vt": "str"}],
    "repeat": "", "crontab": "",
    "once": False, "onceDelay": 0.1,
    "topic": "", "payload": "", "payloadType": "date",
    "x": 170, "y": 240,
    "wires": [[ID_FN_SIM]]
})

# ── Inject: Fast 5s (disabled) ────────────────────────────────────────────────
nodes.append({
    "id": ID_INJ_5S, "type": "inject", "z": TAB,
    "name": "⚡ Fast: 5s",
    "props": [{"p": "payload"}, {"p": "topic", "vt": "str"}],
    "repeat": "5", "crontab": "",
    "once": False, "onceDelay": 0.1,
    "topic": "", "payload": "", "payloadType": "date",
    "d": True,
    "x": 170, "y": 300,
    "wires": [[ID_FN_SIM]]
})

# ── Inject: Slow 300s (disabled) ──────────────────────────────────────────────
nodes.append({
    "id": ID_INJ_300S, "type": "inject", "z": TAB,
    "name": "🐢 Slow: 300s",
    "props": [{"p": "payload"}, {"p": "topic", "vt": "str"}],
    "repeat": "300", "crontab": "",
    "once": False, "onceDelay": 0.1,
    "topic": "", "payload": "", "payloadType": "date",
    "d": True,
    "x": 170, "y": 360,
    "wires": [[ID_FN_SIM]]
})

# ── Function: PLC Simulator ───────────────────────────────────────────────────
nodes.append({
    "id": ID_FN_SIM, "type": "function", "z": TAB,
    "name": "PLC Simulator (Peru 148)",
    "func": PLC_SIM_FUNC,
    "outputs": 1, "timeout": 0, "noerr": 0,
    "initialize": "", "finalize": "", "libs": [],
    "x": 450, "y": 270,
    "wires": [[ID_DBG_RAW, ID_FN_TRENDS]]
})

# ── Debug: Raw PLC values ─────────────────────────────────────────────────────
nodes.append({
    "id": ID_DBG_RAW, "type": "debug", "z": TAB,
    "name": "SIM: Raw PLC Values",
    "active": True, "tosidebar": True, "console": False, "tostatus": False,
    "complete": "payload", "targetType": "msg",
    "statusVal": "", "statusType": "auto",
    "x": 720, "y": 200, "wires": []
})

# ── Comment: Pipeline separator ───────────────────────────────────────────────
nodes.append({
    "id": ID_CMT_PIPE, "type": "comment", "z": TAB,
    "name": "─── BrightLayer Pipeline  (Trends + UsedTrends copied verbatim from full_program_nodered — NO Azure IoT node) ───",
    "info": (
        "The three function nodes below are EXACT copies of the production functions\n"
        "in full_program_nodered:\n\n"
        "  • Trends_filtration_060526  → reads global context set by PLC Simulator\n"
        "    and builds the { trends: [{c,t,v},...] } BrightLayer payload.\n\n"
        "  • Used Trends Debug         → maps tag IDs to human-readable names\n"
        "    (key=name, value=reading).\n\n"
        "  • Used Trends (Array)²      → same but returns [ [name, id, value], ...]\n\n"
        "⚠  No azureiotdevice node is connected here. Output goes to debug nodes only.\n"
        "   To test the real upload path, use the existing 'Flow 2' tab."
    ),
    "x": 550, "y": 440, "wires": []
})

# ── Function: Trends (verbatim copy from source) ──────────────────────────────
trends_node = by_id[TRENDS_ID]
nodes.append({
    "id": ID_FN_TRENDS, "type": "function", "z": TAB,
    "name": "Trends_filtration_060526  [SIM – read-only copy]",
    "func": trends_node['func'],
    "outputs": 1, "timeout": 0, "noerr": 0,
    "initialize": "", "finalize": "", "libs": [],
    "x": 490, "y": 520,
    "wires": [[ID_FN_READ, ID_FN_ARR, ID_DBG_JSON]]
})

# ── Function: Used Trends Debug (verbatim copy) ───────────────────────────────
dbg_node = by_id[USED_DBG_ID]
nodes.append({
    "id": ID_FN_READ, "type": "function", "z": TAB,
    "name": "Used Trends Debug  [SIM]",
    "func": dbg_node['func'],
    "outputs": 1, "noerr": 0,
    "initialize": "", "finalize": "", "libs": [],
    "x": 760, "y": 480,
    "wires": [[ID_DBG_READ]]
})

# ── Function: Used Trends Array (verbatim copy) ───────────────────────────────
arr_node = by_id[USED_ARR_ID]
nodes.append({
    "id": ID_FN_ARR, "type": "function", "z": TAB,
    "name": "Used Trends (Array)²  [SIM]",
    "func": arr_node['func'],
    "outputs": 1, "noerr": 0,
    "initialize": "", "finalize": "", "libs": [],
    "x": 760, "y": 560,
    "wires": [[ID_DBG_ARR]]
})

# ── Debug: Readable output ────────────────────────────────────────────────────
nodes.append({
    "id": ID_DBG_READ, "type": "debug", "z": TAB,
    "name": "→ BrightLayer  READABLE",
    "active": True, "tosidebar": True, "console": False, "tostatus": False,
    "complete": "payload", "targetType": "msg",
    "statusVal": "", "statusType": "auto",
    "x": 1020, "y": 480, "wires": []
})

# ── Debug: Arrays output ──────────────────────────────────────────────────────
nodes.append({
    "id": ID_DBG_ARR, "type": "debug", "z": TAB,
    "name": "→ BrightLayer  ARRAYS",
    "active": True, "tosidebar": True, "console": False, "tostatus": False,
    "complete": "payload", "targetType": "msg",
    "statusVal": "", "statusType": "auto",
    "x": 1020, "y": 560, "wires": []
})

# ── Debug: Raw JSON output ────────────────────────────────────────────────────
nodes.append({
    "id": ID_DBG_JSON, "type": "debug", "z": TAB,
    "name": "→ BrightLayer  RAW JSON",
    "active": True, "tosidebar": True, "console": False, "tostatus": False,
    "complete": "payload", "targetType": "msg",
    "statusVal": "", "statusType": "auto",
    "x": 760, "y": 640, "wires": []
})

# ─── Write output ─────────────────────────────────────────────────────────────
os.makedirs(OUT_DIR, exist_ok=True)
with open(OUT_FILE, 'w', encoding='utf-8') as f:
    json.dump(nodes, f, indent=2, ensure_ascii=False)

print(f"SUCCESS: {OUT_FILE}  ({len(nodes)} nodes)")
print(f"  Tab ID : {TAB}")
print(f"  Nodes  : {', '.join(n.get('name', n['type']) for n in nodes if n.get('type') != 'tab')}")
