// Main PLC Program - Orchestrates CSV reading and MQTT publishing
// Reads CSV file row by row and publishes each row via MQTT
PROGRAM PLC_PRG
VAR
    // Function block instances
    fbCSVReader    : FB_CSVReader;      // CSV file reader
    fbMQTT         : FB_MQTTPublisher;  // MQTT publisher
    
    // Configuration parameters
    sCSVFilePath   : STRING(255) := '/usr/139DATA/139_last6M_241025.csv'; // OR '/139DATA/139_last6M_241025.csv' Path to CSV file on PLC
    xUseLaptopMode : BOOL := TRUE;  // TRUE = laptop connection, FALSE = router/LAN
    
    // Control flags
    xSystemEnable  : BOOL := FALSE; // Master enable for entire system
    
    // Timing control
    tonReadCycle   : TON;           // Timer for periodic reading
    tReadInterval  : TIME := T#10S; // Read every 10 seconds
    
    // State machine for main control
    eMainState     : (IDLE, INIT_MQTT, WAIT_CONNECT, READING_CSV, WAIT_PUBLISH, ERROR) := IDLE;
    
    // Status monitoring
    iRowsProcessed : INT := 0;      // Counter for processed rows
    sSystemStatus  : STRING(128);   // Overall system status
    xSystemError   : BOOL;          // System error flag
END_VAR

// Main state machine
CASE eMainState OF
    
    IDLE:
        // Wait for system enable
        sSystemStatus := 'System Idle - waiting for enable';
        IF xSystemEnable THEN
            eMainState := INIT_MQTT;
        END_IF;
    
    INIT_MQTT:
        // Initialize MQTT connection
        sSystemStatus := 'Initializing MQTT connection...';
        fbMQTT.xEnable := TRUE;
        fbMQTT.xUseLaptop := xUseLaptopMode;
        fbMQTT();
        
        eMainState := WAIT_CONNECT;
    
    WAIT_CONNECT:
        // Wait for MQTT to connect
        fbMQTT();
        
        IF fbMQTT.xConnected THEN
            sSystemStatus := 'MQTT Connected - ready to process CSV';
            tonReadCycle(IN := TRUE, PT := tReadInterval);
            eMainState := READING_CSV;
        ELSIF fbMQTT.xError THEN
            sSystemStatus := 'MQTT connection error';
            xSystemError := TRUE;
            eMainState := ERROR;
        END_IF;
    
    READING_CSV:
        // Periodic CSV reading and publishing
        fbMQTT();
        
        // Start CSV reading on timer
        tonReadCycle(IN := TRUE, PT := tReadInterval);
        
        IF tonReadCycle.Q THEN
            tonReadCycle(IN := FALSE); // Reset timer
            
            // Start reading CSV file
            fbCSVReader.xEnable := TRUE;
            fbCSVReader.sFilePath := sCSVFilePath;
        END_IF;
        
        // Call CSV reader
        fbCSVReader();
        
        // Check for new row available
        IF fbCSVReader.xNewRow THEN
            iRowsProcessed := iRowsProcessed + 1;
            sSystemStatus := CONCAT('Processing row: ', INT_TO_STRING(iRowsProcessed));
            
            // Trigger MQTT publish
            fbMQTT.RowIn := fbCSVReader.RowOut;
            fbMQTT.xTrigger := TRUE;
            eMainState := WAIT_PUBLISH;
        END_IF;
        
        // Check for CSV reading complete
        IF fbCSVReader.xDone THEN
            fbCSVReader.xEnable := FALSE; // Stop reader
            sSystemStatus := CONCAT('CSV complete. Total rows: ', INT_TO_STRING(iRowsProcessed));
            tonReadCycle(IN := FALSE); // Restart cycle timer
        END_IF;
        
        // Check for CSV error
        IF fbCSVReader.xError THEN
            sSystemStatus := 'CSV reading error';
            xSystemError := TRUE;
            eMainState := ERROR;
        END_IF;
        
        // Check if system disabled
        IF NOT xSystemEnable THEN
            fbCSVReader.xEnable := FALSE;
            fbMQTT.xEnable := FALSE;
            eMainState := IDLE;
        END_IF;
    
    WAIT_PUBLISH:
        // Wait for MQTT publish to complete
        fbMQTT.xTrigger := FALSE; // Clear trigger
        fbMQTT();
        fbCSVReader();
        
        IF fbMQTT.xPublished THEN
            sSystemStatus := CONCAT('Row ', INT_TO_STRING(iRowsProcessed));
            sSystemStatus := CONCAT(sSystemStatus, ' published');
            eMainState := READING_CSV; // Continue reading next row
        ELSIF fbMQTT.xError THEN
            sSystemStatus := 'MQTT publish error';
            xSystemError := TRUE;
            eMainState := ERROR;
        END_IF;
    
    ERROR:
        // Error state - attempt recovery
        sSystemStatus := CONCAT('ERROR: ', fbMQTT.sStatus);
        
        // Stop all operations
        fbCSVReader.xEnable := FALSE;
        
        // Reset on system disable/enable cycle
        IF NOT xSystemEnable THEN
            xSystemError := FALSE;
            fbMQTT.xEnable := FALSE;
            eMainState := IDLE;
        END_IF;
        
END_CASE;

END_PROGRAM
