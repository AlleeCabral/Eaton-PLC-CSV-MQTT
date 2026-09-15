const now = Math.floor(Date.now() / 1000) - (1000);

var globalKeyLookup = null;

function buildGlobalKeyLookup() {
  var lookup = {};

  if (typeof global.keys !== "function") {
    return lookup;
  }

  var keys = global.keys();

  for (var i = 0; i < keys.length; i++) {
    var key = keys[i];
    var normalizedKey = key.toLowerCase();

    if (lookup[normalizedKey] === undefined) {
      lookup[normalizedKey] = key;
    }
  }

  return lookup;
}

function getGlobalValue(key) {
  var value = global.get(key);

  if (value !== undefined && value !== null) {
    return value;
  }

  if (typeof key !== "string") {
    return null;
  }

  if (globalKeyLookup === null) {
    globalKeyLookup = buildGlobalKeyLookup();
  }

  var matchingKey = globalKeyLookup[key.toLowerCase()];

  if (matchingKey === undefined) {
    return null;
  }

  value = global.get(matchingKey);
  return value !== undefined && value !== null ? value : null;
}

function getFirst() {
  for (var i = 0; i < arguments.length; i++) {
    var v = getGlobalValue(arguments[i]);
    if (v !== undefined && v !== null) return v;
  }
  return null;
}

msg = {
    'topic': 'telemetry',
    'payload': { "trends": [
{ "c": "10472631", "t": now, "v": getFirst("_Anti_pump", "Anti_pump") }, // Alarm_Anti_Pump
{ "c": "10472617", "t": now, "v": getFirst("_AlarmAntiScalant", "AlarmAntiScalant", "Anti_Tank", "Anti_Tankk", "Anti_Tankkk", "AntiScalantTank", "AntiTank", "AntiTank_empty", "AntiTankkk") }, // Alarm_AntiScalant_Tank
{ "c": "10472616", "t": now, "v": getFirst("_Alarm_Well_Level", "Alarm_Well_Level", "Alarm_Well_Water", "AlarmWellLevel", "_40_Alarm_Well_Level") }, // Alarm_Borehole_empty
{ "c": "10472604", "t": now, "v": getFirst("_23__Comp_Alarm", "_23_Comp_Alarm", "_35_Alarm_Comp", "Alarm_Comp", "Comp_Alarm") }, // Alarm_Comp
{ "c": "10473768", "t": now, "v": global.get("Dosing_Pump_Alarm") }, // Alarm_Dosing_Pump
{ "c": "10472609", "t": now, "v": getFirst("_31__Alarm_DPS", "_31_Alarm_DPS", "Alarm_DPSe") }, // Alarm_DPS
{ "c": "10472608", "t": now, "v": getFirst("_30__Alarm_Drain_Valve", "_30_Alarm_Drain_Valve", "Alarm_Drain_Valve") }, // Alarm_Drain_Valve
{ "c": "10472603", "t": now, "v": getFirst("_22__Evap_Motor_Alarm", "_22_Evap_Motor_Alarm", "_34_Alarm_Evap", "_41_Alarm_Evap_Rotation", "Alarm_Evap", "Alarm_Evap_Rotation", "Evap_Motor_Alarm") }, // Alarm_Evap_Motor
{ "c": "10472601", "t": now, "v": getFirst("_20__Fan_1_Alarm", "_20_Fan_1_Alarm", "_32_Alarm_Fan_1", "Alarm_Fan_1", "Fan_1_Alarm", "_21_Fan_2_Alarm", "Alarm_Fan_2", "Fan_2_Alarm", "_33_Alarm_Fan_2") }, // Alarm_Fan_1
{ "c": "10472620", "t": now, "v": getFirst("_AlarmFlowMeter", "AlarmFlowMeter") }, // Alarm_Flowmeter
{ "c": "10472607", "t": now, "v": getFirst("_29__Alarm_Inlet_Valve_Water", "_29_Alarm_Inlet_Valve_Water", "Alarm_Inlet_Valve_Water") }, // Alarm_Inlet_Valve
{ "c": "10472613", "t": now, "v": getFirst("_Alarm_Inverter_A", "Alarm_Inverter_A", "AlarmFeedInverterStatus") }, // Alarm_Inverter1
{ "c": "10472614", "t": now, "v": getFirst("_Alarm_Inverter_B", "Alarm_Inverter_B", "AlarmBoosterInverterStatus") }, // Alarm_Inverter2
{ "c": "10472615", "t": now, "v": getFirst("_Alarm_Inverter_C", "Alarm_Inverter_C", "AlarmBohrholeInverterStatus") }, // Alarm_Inverter3
{ "c": "10472606", "t": now, "v": getFirst("_28__Alarm_Lid", "_28_Alarm_Lid", "Alarm_Lid", "_12_Lid_Alarm") }, // Alarm_Lid
{ "c": "10473782", "t": now, "v": global.get("Ph_Alarm") }, // Alarm_Ph
{ "c": "10472612", "t": now, "v": getFirst("_Alarm_High_Pressure", "Alarm_High_Pressure", "Pressurre_Alarm", "_15_Pressurre_Alarm", "_17_Alarm_High_Pressure", "AlarmHighPressure") }, // Alarm_Pressure
{ "c": "10472622", "t": now, "v": getFirst("_AlarmRaw_Tank_Alarm", "AlarmRaw_Tank_Alarm") }, // Alarm_Raw_Tank
{ "c": "10472611", "t": now, "v": getFirst("_39__Alarm_Tank", "_39_Alarm_Tank") }, // Alarm_Tank
{ "c": "10472621", "t": now, "v": getFirst("_AlarmHighTDS", "AlarmHighTDS") }, // Alarm_TDS
{ "c": "10472598", "t": now, "v": getFirst("_18__Alarm_Inverter", "_18_Alarm_Inverter", "_19_Alarm_Temperature_Inverter", "Alarm_Inverter", "Alarm_Temperature_Inverter") }, // Alarm_Temp_Inverter
{ "c": "10472610", "t": now, "v": getFirst("_36__Alarm_Inverter_A", "_36_Alarm_Inverter_A", "_42_Alarm_Inverter_1_Over_Temperature", "Alarm_Inverter_1_Over_Temperature", "AlarmBohrholeInverterTemperature") }, // Alarm_Temp_Inverter1
{ "c": "10472619", "t": now, "v": getFirst("_AlarmFeedInverterTemperature", "AlarmFeedInverterTemperature", "_37_Alarm_Inverter_B", "_43_Alarm_Inverter_2_Over_Temperature", "Alarm_Inverter_2_Over_Temperature") }, // Alarm_Temp_Inverter2
{ "c": "10472618", "t": now, "v": getFirst("_AlarmBoosterInverterTemperature", "AlarmBoosterInverterTemperature", "_38_Alarm_Inverter_C", "_44_Alarm_Inverter_3_Over_Temperature") }, // Alarm_Temp_Inverter3
{ "c": "10472623", "t": now, "v": getFirst("_AlarmUnstableVoltage", "AlarmUnstableVoltage") }, // Alarm_Unstable_Volt
{ "c": "10472600", "t": now, "v": getFirst("_20__Alarm_UV_Lamp", "_20_Alarm_UV_Lamp", "Alarm_UV_Lamp") }, // Alarm_UV_Lamp
{ "c": "10472624", "t": now, "v": getFirst("_AlarmUVInLamp", "AlarmUVInLamp") }, // Alarm_UVIn_Lamp
{ "c": "10472625", "t": now, "v": getFirst("_AlarmUVOutLamp", "AlarmUVOutLamp") }, // Alarm_UVOut_Lamp
{ "c": "10472626", "t": now, "v": getFirst("_AlarmValve1", "AlarmValve1") }, // Alarm_Valve1
{ "c": "10472627", "t": now, "v": getFirst("_AlarmValve2", "AlarmValve2") }, // Alarm_Valve2
{ "c": "10472628", "t": now, "v": getFirst("_AlarmValve3", "AlarmValve3") }, // Alarm_Valve3
{ "c": "10472629", "t": now, "v": getFirst("_AlarmValve4", "AlarmValve4") }, // Alarm_Valve4
{ "c": "10472630", "t": now, "v": getFirst("_AlarmValve5", "AlarmValve5") }, // Alarm_Valve5
{ "c": "10472602", "t": now, "v": getFirst("_21__Alarm_6_Water_Meter", "_21_Alarm_6_Water_Meter", "Alarm_6_Water_Meter") }, // Alarm_Watermeter
{ "c": "10472589", "t": now, "v": getFirst("_11__Auto_Manual", "_11_Auto_Manual", "_12_Auto_Manual", "Auto_Manual", "Switch_Auto") }, // Auto_Manual_Switch
{ "c": "10472632", "t": now, "v": getFirst("_BackwashSwitch", "BackwashSwitch") }, // Backwash_Switch
{ "c": "10472633", "t": now, "v": getFirst("_BackwashSwitchC", "BackwashSwitch") }, // Backwash_Switch
{ "c": "10473793", "t": now, "v": getFirst("Switch_P3_BoosterSwitch", "Switch_P3", "BoosterSwitch") }, // Booster_Pump_Switch
{ "c": "10466958", "t": now, "v": global.get("Feed_TotalRUN") }, // Booster_Pump_Total_Run
{ "c": "10472595", "t": now, "v": getFirst("_16__Alarm_Well_Water", "_16_Alarm_Well_Water") }, // Borehole_empty
{ "c": "10472593", "t": now, "v": getFirst("_14__Borhole_Float_Switch", "_14_Borhole_Float_Switch", "_24_Borhole_Float_Switch", "Borhole_Float_Switch", "BorholeFloatSwitch", "Borehole_lvl") }, // Borehole_Float_Switch
{ "c": "10466803", "t": now, "v": getFirst("_61_Pump_Current", "Current_Inverter_Pump", "_72_Current_Inverter_Pump") }, // Borehole_Pump_Current
{ "c": "10466793", "t": now, "v": global.get("_55_Pump_Power") }, // Borehole_Pump_Power
{ "c": "10473791", "t": now, "v": getFirst("Switch_P1_BohrholeSwitch", "Switch_P1", "BohrholeSwitch") }, // Borehole_Pump_Switch
{ "c": "10472636", "t": now, "v": getFirst("_CIPSwitch", "CIPSwitch", "Switch_CIP") }, // CIP_Switch
{ "c": "10472637", "t": now, "v": getFirst("_CIPSwitchC", "CIPSwitch", "Switch_CIP") }, // CIP_Switch
{ "c": "10472634", "t": now, "v": getFirst("_CIP_tankempty", "CIP_tankempty", "CIPtank_empty") }, // CIP_Tank_Empty
{ "c": "10472635", "t": now, "v": getFirst("_CIP_tankfull", "CIP_tankfull", "CIPtankHigh", "CIPtank_full", "CIPtankLow") }, // CIP_Tank_Full
{ "c": "10466790", "t": now, "v": getFirst("_54_Comp_Power", "Comp_Power") }, // Comp_Power
{ "c": "10472596", "t": now, "v": getFirst("_16__Comp_Run", "_16_Comp_Run", "Comp_Run") }, // Comp_Run
{ "c": "10466934", "t": now, "v": global.get("CurrentInverterBooster") }, // Current_Booster_Pump
{ "c": "10466822", "t": now, "v": getFirst("_71_Current_Inverter_Comp", "Current_Inverter_Comp", "Frequency_Inverter_Comp") }, // Current_Comp
{ "c": "10466820", "t": now, "v": getFirst("_70_Current_Inverter_Evap", "Current_Inverter_Evap", "Frequency_Inverter_Evap") }, // Current_Evap
{ "c": "10466935", "t": now, "v": global.get("CurrentInverterFeed") }, // Current_Feed_Pump
{ "c": "10472640", "t": now, "v": getFirst("_Datum_Backwash_Done", "Datum_Backwash_Done", "Last_Backwash") }, // Date_Backwash_Done
{ "c": "10472641", "t": now, "v": getFirst("_Datum_CIP_Done", "Datum_CIP_Done") }, // Date_CIP_Done
{ "c": "10466799", "t": now, "v": getFirst("_59_DC_Voltage", "DC_Voltage") }, // DC_Voltage
{ "c": "10466943", "t": now, "v": global.get("DCVoltageBooster") }, // DC_Voltage_Booster
{ "c": "10466945", "t": now, "v": global.get("DCVoltagePump") }, // DC_Voltage_Borehole
{ "c": "10466806", "t": now, "v": getFirst("_63_DC_Voltage_Pump", "DC_Voltage_Pump") }, // DC_Voltage_Borehole_Pump
{ "c": "10466804", "t": now, "v": getFirst("_62_DC_Voltage_Comp", "DC_Voltage_Comp") }, // DC_Voltage_Comp
{ "c": "10466802", "t": now, "v": getFirst("_61_DC_Voltage_Evap", "DC_Voltage_Evap") }, // DC_Voltage_Evap
{ "c": "10466944", "t": now, "v": global.get("DCVoltageFeed") }, // DC_Voltage_Feed
{ "c": "10473769", "t": now, "v": global.get("DriveError_Drv1") }, // DriveError_Drv1
{ "c": "10473770", "t": now, "v": global.get("DriveError_Drv2") }, // DriveError_Drv2
{ "c": "10473771", "t": now, "v": global.get("DriveError_Drv3") }, // DriveError_Drv3
{ "c": "10466950", "t": now, "v": getFirst("ec_value", "_14_Conductivity_Switch", "Conductivity_Switch", "EC_Value", "Leitfaehigkeit") }, // EC_Value
{ "c": "10472590", "t": now, "v": getFirst("_12__Eco", "_12_Eco", "_13_Eco", "Eco") }, // Eco
{ "c": "10472591", "t": now, "v": global.get("_12C_Eco") }, // Eco_control
{ "c": "10473794", "t": now, "v": global.get("Switch_P4") }, // Elevating_Pump_Switch
{ "c": "10466788", "t": now, "v": getFirst("_53_Evap_Power", "Evap_Power") }, // Evap_Power
{ "c": "10472597", "t": now, "v": getFirst("_17__Evap_Run", "_17_Evap_Run", "Evap_Run") }, // Evap_Run
{ "c": "10466957", "t": now, "v": global.get("Feed_Kwh") }, // Feed_Kwh
{ "c": "10473792", "t": now, "v": getFirst("Switch_P2_FeedSwitch", "Switch_P2", "FeedSwitch") }, // Feed_Pump_Switch
{ "c": "10472592", "t": now, "v": getFirst("_13__Float_Switch", "_13_Float_Switch", "Float_Switch") }, // Float_Switch
{ "c": "10466816", "t": now, "v": global.get("_68_Frequency_Inverter_Comp") }, // Frequency_Comp
{ "c": "10462379", "t": now, "v": getFirst("_69_Frequency_Inverter_Pump", "freq_drv1", "Frequency_Drv", "Frequency_Inverter_Pump", "FrequencyInverterPump", "Frequenz_Inv1") }, // Frequency_Drv1
{ "c": "10462380", "t": now, "v": getFirst("freq_drv2", "Frequency_Drv2", "FrequencyInverterFeed", "Frequenz_Inv2") }, // Frequency_Drv2
{ "c": "10462381", "t": now, "v": getFirst("freq_drv3", "Frequency_Drv3", "FrequencyInverterBooster", "Frequenz_Inv3") }, // Frequency_Drv3
{ "c": "10466974", "t": now, "v": global.get("Frequenz_Inv4") }, // Frequency_Drv4
{ "c": "10466814", "t": now, "v": global.get("_67_Frequency_Inverter_Evap") }, // Frequency_Evap
{ "c": "10466786", "t": now, "v": getFirst("_51_Grid_Power", "Grid_Power") }, // Grid_Power
{ "c": "10466815", "t": now, "v": getFirst("_67_Grid_Power_KWh_This_Hour", "_78_Grid_Power_KWh_This_Hour", "Grid_Power_KWh_This_Hour") }, // Grid_Power_KWh_This_Hour
{ "c": "10466819", "t": now, "v": getFirst("_69_Grid_Power_KWh_This_Month", "_80_Grid_Power_KWh_This_Month", "Grid_Power_KWh_This_Month") }, // Grid_Power_KWh_This_Month
{ "c": "10466817", "t": now, "v": getFirst("_68_Grid_Power_KWh_Today", "_79_Grid_Power_KWh_Today", "Grid_Power_KWh_Today") }, // Grid_Power_KWh_This_Today
{ "c": "10466812", "t": now, "v": getFirst("_66_Grid_Power_KWh_Total", "_77_Grid_Power_KWh_Total", "Grid_Power_KWh_Total") }, // Grid_Power_Total
{ "c": "10472594", "t": now, "v": getFirst("_15__Grid_is_On", "_15_Grid_is_On", "_27_Grid_is_ON", "Grid_is_ON", "Grid_is_On", "GridisON") }, // Grid_Switch
{ "c": "10473772", "t": now, "v": getFirst("IceMachine_Run", "_19_IceMachine_Run") }, // IceMachine_On
{ "c": "10466791", "t": now, "v": getFirst("_54_Machine_Capacity", "_56_Machine_Capacity", "Machine_Capacity", "MachineCapacity") }, // Machine_Capacity
{ "c": "10466792", "t": now, "v": getFirst("_55_Machine_Grid_Percentage", "_57_Machine_Grid_Percentage", "Machine_Grid_Percentage", "MachineGridPercentage") }, // Machine_Grid_Percentage
{ "c": "10473773", "t": now, "v": global.get("Machine_Mode_Backwash") }, // Machine_Mode_Backwash
{ "c": "10473774", "t": now, "v": global.get("Machine_Mode_Bohrhole") }, // Machine_Mode_Borehole
{ "c": "10473775", "t": now, "v": global.get("Machine_Mode_CIP") }, // Machine_Mode_CIP
{ "c": "10473776", "t": now, "v": global.get("Machine_Mode_Filling") }, // Machine_Mode_Filling
{ "c": "10473777", "t": now, "v": global.get("Machine_Mode_Flush") }, // Machine_Mode_Flush
{ "c": "10473778", "t": now, "v": global.get("Machine_Mode_Pro") }, // Machine_Mode_Pro
{ "c": "10473779", "t": now, "v": global.get("MachineRun") }, // Machine_Run
{ "c": "10466795", "t": now, "v": getFirst("_56_Machine_Solar_Percentage", "_58_Machine_Solar_Percentage", "Machine_Solar_Percentage", "MachineSolarPercentage") }, // Machine_Solar_Percentage
{ "c": "10473780", "t": now, "v": getFirst("mains_on", "_11_Start", "Mains_ON", "Mains_OON") }, // Main_ON
{ "c": "10473783", "t": now, "v": global.get("PremeateTank") }, // Permeate_Tank_has_water
{ "c": "10467008", "t": now, "v": global.get("Ph_Tank1") }, // Ph_Tank1
{ "c": "10467009", "t": now, "v": global.get("Ph_Tank2") }, // Ph_Tank2
{ "c": "10467015", "t": now, "v": getFirst("pressure", "_57_Actual_Pressure", "Actual_Pressure", "Pressure", "Systemdruck") }, // Pressure
{ "c": "10474987", "t": now, "v": global.get("Pressure2") }, // Pressure2
{ "c": "10467017", "t": now, "v": global.get("Pump_Current") }, // Pump_Current
{ "c": "10466789", "t": now, "v": getFirst("_53_Pump_Power", "Pump_Power") }, // Pump_Power
{ "c": "10472599", "t": now, "v": getFirst("_18__Pump_Run", "_18_Pump_Run", "Pump_Run") }, // Pump_Run
{ "c": "10473786", "t": now, "v": global.get("SC_ctrl1") }, // SCBW_1st_Ctrl
{ "c": "10473789", "t": now, "v": global.get("SCBW1_ok") }, // SCBW_1st_Done
{ "c": "10473787", "t": now, "v": global.get("SC_ctrl2") }, // SCBW_2nd_Ctrl
{ "c": "10473790", "t": now, "v": global.get("SCBW2_ok") }, // SCBW_2nd_Done
{ "c": "10473788", "t": now, "v": global.get("SC_Sw") }, // SCBW_Switch
{ "c": "10466785", "t": now, "v": getFirst("_50_Solar_Power", "_62_Solar_Power_KWh_Total", "_73_Solar_Power_KWh_Total", "Solar_Power") }, // Solar_Power
{ "c": "10466807", "t": now, "v": getFirst("_63_Solar_Power_KWh_This_Hour", "_74_Solar_Power_KWh_This_Hour", "Solar_Power_KWh_This_Hour") }, // Solar_Power_KWh_This_Hour
{ "c": "10466810", "t": now, "v": getFirst("_65_Solar_Power_KWh_This_Month", "_76_Solar_Power_KWh_This_Month", "Solar_Power_KWh_This_Month") }, // Solar_Power_KWh_This_Month
{ "c": "10466808", "t": now, "v": getFirst("_64_Solar_Power_KWh_Today", "_75_Solar_Power_KWh_Today", "Solar_Power_KWh_Today") }, // Solar_Power_KWh_Today
{ "c": "10467037", "t": now, "v": global.get("Solar_Power_KWh_Total") }, // Solar_Power_KWh_Total
{ "c": "10472605", "t": now, "v": getFirst("_25__Tank_High_Level", "_25_Tank_High_Level", "Tank_High_Level", "_26_Tank_Low_Level", "Tank_Low_Level") }, // Tank_High_Level
{ "c": "10473785", "t": now, "v": getFirst("Rawtank_toplvl", "RawWaterTankHigh") }, // Tank_Raw_High_Level
{ "c": "10473784", "t": now, "v": getFirst("Rawtank_lowlvl", "RawWaterTankLow") }, // Tank_Raw_Low_Level
{ "c": "10473781", "t": now, "v": global.get("Permtank_toplvl") }, // Tank_Water_Clean_High_Level
{ "c": "10466811", "t": now, "v": global.get("_65_Temperature_Inverte_Comp") }, // Temp_Comp
{ "c": "10467049", "t": now, "v": getFirst("temp_drv1", "_60_Inverter_Temperature", "_66_Temperature_Inverter_Pump", "Inverter_Temperature", "Temp_Drv1") }, // Temp_Drv1
{ "c": "10467050", "t": now, "v": getFirst("temp_drv2", "Temp_Drv2") }, // Temp_Drv2
{ "c": "10467051", "t": now, "v": getFirst("temp_drv3", "Temp_Drv3") }, // Temp_Drv3
{ "c": "10466809", "t": now, "v": global.get("_64_Temperature_Inverter_Evap") }, // Temp_Evap
{ "c": "10467055", "t": now, "v": global.get("TemperatureInverterBooster") }, // Temp_Inverter_Booster
{ "c": "10467052", "t": now, "v": global.get("Temperature_Inverter_Comp") }, // Temp_Inverter_Comp
{ "c": "10467053", "t": now, "v": global.get("Temperature_Inverter_Evap") }, // Temp_Inverter_Evap
{ "c": "10467056", "t": now, "v": global.get("TemperatureInverterFeed") }, // Temp_Inverter_Feed
{ "c": "10467054", "t": now, "v": getFirst("Temperature_Inverter_Pump", "TemperatureInverterPump") }, // Temp_Inverter_Pump
{ "c": "10466801", "t": now, "v": getFirst("_60_Total_Current", "system_current", "Total_Current") }, // Total_Current
{ "c": "10466787", "t": now, "v": getFirst("_52_Total_Power", "_70_Output_Power_KWh_Total", "_81_Output_Power_KWh_Total", "Output_Power_KWh_Total", "Total_Power") }, // Total_Power
{ "c": "10466907", "t": now, "v": global.get("BoosterPower") }, // Total_Power_Booster
{ "c": "10466959", "t": now, "v": global.get("FeedPower") }, // Total_Power_Feed
{ "c": "10466823", "t": now, "v": getFirst("_71_Output_Power_KWh_This_Hour", "_82_Output_Power_KWh_This_Hour", "Output_Power_KWh_This_Hour") }, // Total_Power_KWh_This_Hour
{ "c": "10466826", "t": now, "v": getFirst("_73_Output_Power_KWh_This_Month", "_84_Output_Power_KWh_This_Month", "Output_Power_KWh_This_Month") }, // Total_Power_KWh_This_Month
{ "c": "10466825", "t": now, "v": getFirst("_72_Output_Power_KWh_Today", "_83_Output_Power_KWh_Today", "Output_Power_KWh_Today") }, // Total_Power_KWh_This_Today
{ "c": "10466837", "t": now, "v": getFirst("_78_Total_Run_Time", "Total_Run_Time") }, // Total_Run_Time
{ "c": "10462372", "t": now, "v": global.get("totalwater_pro") }, // Totalwater_Clean
{ "c": "10462371", "t": now, "v": global.get("totalwater_in") }, // TotalWater_Raw
{ "c": "10472638", "t": now, "v": getFirst("_Ctrl_Uvin", "Ctrl_Uvin", "UVin2_ctrl", "UVin_ctrl", "UVin_ctrll") }, // UV_In_Ctrl
{ "c": "10467065", "t": now, "v": getFirst("UV_inside_lifetime", "UVin_lifetime") }, // UV_In_Lifetime
{ "c": "10467066", "t": now, "v": getFirst("UV_inside_switching_operations", "UVin_switching", "uvi_switching") }, // UV_In_Switch
{ "c": "10467071", "t": now, "v": getFirst("UVin_Betriebsstunden", "UVin_workhours", "uvin_workhours") }, // UV_In_Workhours
{ "c": "10467067", "t": now, "v": global.get("UV_Lamp_Run_Time") }, // UV_Lamp_Run_Time
{ "c": "10472639", "t": now, "v": getFirst("_ctrl_Uvout", "ctrl_UVout", "UV_outside_switching_operations", "UVout2_ctrl", "UVout_ctrl", "UVout_ctrll") }, // UV_Out_Ctrl
{ "c": "10467068", "t": now, "v": getFirst("UV_outside_lifetime", "UVout_lifetime") }, // UV_Out_Lifetime
{ "c": "10467077", "t": now, "v": getFirst("UVo_switching", "uvo_switching", "UvOutSwitch") }, // UV_Out_Switch
{ "c": "10473795", "t": now, "v": global.get("UVo_Watersensor") }, // UV_Out_Water_Sensor
{ "c": "10467079", "t": now, "v": getFirst("UVo_workhours", "uvo_workhours") }, // UV_Out_Workhours
{ "c": "10466839", "t": now, "v": global.get("_79_UV_Lamp_Run_Time") }, // UV_workhours
{ "c": "10473797", "t": now, "v": global.get("valves_cip") }, // Valves_CIP
{ "c": "10473799", "t": now, "v": global.get("valves_filling") }, // Valves_Filling
{ "c": "10473801", "t": now, "v": global.get("valves_flush") }, // Valves_Flush
{ "c": "10473796", "t": now, "v": global.get("Valves_bw") }, // Valves_Position_BW
{ "c": "10473798", "t": now, "v": getFirst("Valves_CIP_position", "Valves_CIP", "Valves_Position_cip") }, // Valves_Position_CIP
{ "c": "10473800", "t": now, "v": getFirst("Valves_Filling_position", "Valves_Filling", "Valves_Position_fillingcip") }, // Valves_Position_Filling
{ "c": "10473802", "t": now, "v": getFirst("Valves_Flush_position", "Valves_Flush", "Valves_Position_flush") }, // Valves_Position_Flush
{ "c": "10473803", "t": now, "v": getFirst("Valves_Position_pro", "Valves_Pro", "valves_pro") }, // Valves_Position_Pro
{ "c": "10467095", "t": now, "v": getFirst("voltage_drv1", "Voltage_Drv1") }, // Voltage_Drv1
{ "c": "10467096", "t": now, "v": getFirst("voltage_drv2", "Voltage_Drv2") }, // Voltage_Drv2
{ "c": "10467097", "t": now, "v": getFirst("voltage_drv3", "Voltage_Drv3") }, // Voltage_Drv3
{ "c": "10467098", "t": now, "v": global.get("Voltage_Drv4") }, // Voltage_Drv4
{ "c": "10473804", "t": now, "v": global.get("Waterflowing") }, // Water_flowing
{ "c": "10466843", "t": now, "v": global.get("_81_Water_M3_This_Hour") }, // Water_This_Hour
{ "c": "10467011", "t": now, "v": global.get("PremeateWaterM3ThisHour") }, // Water_This_Hour_Clean
{ "c": "10467105", "t": now, "v": global.get("Water_M3_This_Hour") }, // Water_This_Hour_Pro
{ "c": "10467022", "t": now, "v": global.get("RawWaterM3ThisHour") }, // Water_This_Hour_Raw
{ "c": "10466847", "t": now, "v": global.get("_83_Water_M3_Per_This_Month") }, // Water_This_Month
{ "c": "10467012", "t": now, "v": global.get("PremeateWaterM3ThisMonth") }, // Water_This_Month_Clean
{ "c": "10467104", "t": now, "v": getFirst("Water_M3_Per_This_Month", "Water_M3_This_Month") }, // Water_This_Month_Pro
{ "c": "10467023", "t": now, "v": global.get("RawWaterM3ThisMonth") }, // Water_This_Month_Raw
{ "c": "10466845", "t": now, "v": global.get("_82_Water_M3_Today") }, // Water_Today
{ "c": "10467013", "t": now, "v": getFirst("PremeateWaterM3Today", "Water_Today_prod", "WaterToday_Clean", "WaterToday_pro", "WaterToday_prod", "Water_M3_Today") }, // Water_Today_Clean
{ "c": "10467024", "t": now, "v": getFirst("RawWaterM3Today", "Water_Today_in", "WaterToday_in", "WaterToday_Raw") }, // Water_Today_Raw
{ "c": "10467120", "t": now, "v": getFirst("WaterToday_recov", "WaterToday_Recovery") }, // Water_Today_Recovery
{ "c": "10467113", "t": now, "v": getFirst("Water_Today_sold", "WaterToday_sold") }, // Water_Today_Sold
{ "c": "10466841", "t": now, "v": global.get("_80_Water_M3_Total") }, // Water_Total
{ "c": "10467005", "t": now, "v": getFirst("Permeat", "PremeateWaterM3Total", "Totalwater_Clean", "Water_produced", "WaterTotal_pro") }, // Water_Total_Clean
{ "c": "10467100", "t": now, "v": getFirst("Wasser_permeat", "Water_M3_Total") }, // Water_Total_Pro
{ "c": "10467025", "t": now, "v": getFirst("RawWaterM3Total", "TotalWater_Raw", "Wasser_eingang", "Wassereingang", "Water_in", "WaterTotal_in") }, // Water_Total_Raw
{ "c": "10467063", "t": now, "v": getFirst("TotalWater_Recovery", "WaterTotal_recovery") }, // Water_Total_Recovery
{ "c": "10467064", "t": now, "v": getFirst("TotalWater_Sold", "Verkauftes_Wasser", "Wasser_verkauft", "Water_sold", "WaterTotal_sold") }, // Water_Total_Sold
]},
    'properties': [
        {
        'key': 'a', 'value': 'Trends'},
        {
            'key': 'p', 'value': '17272566-5e53-4f19-80a8-bafabbcb2ed6'
        }
    ]
}
return msg;
