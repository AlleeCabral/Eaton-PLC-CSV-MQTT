// MQTT Publisher with dual connection mode (Laptop/Router)
// Builds JSON from CSV row data and publishes to MQTT broker
FUNCTION_BLOCK FB_MQTTPublisher
VAR_INPUT
    xEnable       : BOOL;        // Enable MQTT connection
    xUseLaptop    : BOOL;        // TRUE = laptop connection, FALSE = router/LAN
    RowIn         : ST_CSVRow;   // CSV row data to publish
    xTrigger      : BOOL;        // Trigger to publish current row
    sBrokerLaptop : STRING(255) := 'broker.hivemq.com'; // Cloud broker for laptop mode
    sBrokerLAN    : STRING(255) := 'broker.hivemq.com'; // Cloud broker for LAN mode
    uiPort        : UINT := 1883; // MQTT port (1883 = no TLS)
    sTopic        : STRING(255) := 'UE/139ukr';      // MQTT topic
END_VAR
VAR_OUTPUT
    xConnected    : BOOL;        // TRUE when connected to broker
    xPublished    : BOOL;        // Pulse TRUE when message published
    xError        : BOOL;        // TRUE if error occurred
    sStatus       : STRING(128); // Status/error message
END_VAR
VAR
    // MQTT client instance
    fbClient      : IotMqtt.MqttClient;
    
    // State machine
    eState        : (INIT, CONNECTING, CONNECTED, PUBLISHING, DISCONNECTING, ERROR) := INIT;
    
    // JSON building
    sJsonPayload  : STRING(2048);
    
    // Timing and control
    tonReconnect  : TON;         // Reconnection timer
    xTriggerOld   : BOOL;        // Edge detection
    xEnableOld    : BOOL;        // Edge detection
    
    // Internal flags
    xPublishBusy  : BOOL;
    xPublishDone  : BOOL;
END_VAR

// Edge detection for enable
IF xEnable AND NOT xEnableOld THEN
    eState := CONNECTING;
ELSIF NOT xEnable AND xEnableOld THEN
    eState := DISCONNECTING;
END_IF;
xEnableOld := xEnable;

// Edge detection for trigger
xPublished := FALSE; // Clear pulse

// State machine
CASE eState OF
    
    INIT:
        xConnected := FALSE;
        xError := FALSE;
        sStatus := 'Idle';
        IF xEnable THEN
            eState := CONNECTING;
        END_IF;
    
    CONNECTING:
        sStatus := 'Connecting...';
        
        // Configure client based on connection mode
        IF xUseLaptop THEN
            fbClient.sHostName := sBrokerLaptop;
            fbClient.sClientId := 'EatonPLC_Laptop';
        ELSE
            fbClient.sHostName := sBrokerLAN;
            fbClient.sClientId := 'EatonPLC_LAN';
        END_IF;
        
        fbClient.uiPort := uiPort;
        fbClient.xEnable := TRUE;
        fbClient();
        
        // Check connection status
        IF fbClient.xConnected THEN
            xConnected := TRUE;
            sStatus := 'Connected';
            eState := CONNECTED;
        ELSIF fbClient.xError THEN
            xError := TRUE;
            sStatus := 'Connection failed';
            eState := ERROR;
        END_IF;
    
    CONNECTED:
        fbClient();
        
        // Detect rising edge of trigger
        IF xTrigger AND NOT xTriggerOld THEN
            eState := PUBLISHING;
        END_IF;
        
        // Check if connection lost
        IF NOT fbClient.xConnected THEN
            xConnected := FALSE;
            sStatus := 'Connection lost';
            tonReconnect(IN := TRUE, PT := T#5S);
            IF tonReconnect.Q THEN
                tonReconnect(IN := FALSE);
                eState := CONNECTING;
            END_IF;
        END_IF;
    
    PUBLISHING:
        // Build JSON payload from CSV row
        F_BuildJsonFromRow(RowIn, sJsonPayload);
        
        // Publish message
        fbClient.Publish(
            sTopic := sTopic,
            pPayload := ADR(sJsonPayload),
            udiPayloadSize := LEN(sJsonPayload),
            eQoS := IotMqtt.QoS.ExactlyOnce
        );
        fbClient();
        
        IF fbClient.xPublishComplete THEN
            xPublished := TRUE;
            sStatus := 'Published';
            eState := CONNECTED;
        ELSIF fbClient.xError THEN
            xError := TRUE;
            sStatus := 'Publish failed';
            eState := ERROR;
        END_IF;
    
    DISCONNECTING:
        fbClient.xEnable := FALSE;
        fbClient();
        xConnected := FALSE;
        sStatus := 'Disconnected';
        eState := INIT;
    
    ERROR:
        sStatus := 'Error - retrying...';
        tonReconnect(IN := TRUE, PT := T#10S);
        IF tonReconnect.Q THEN
            tonReconnect(IN := FALSE);
            xError := FALSE;
            eState := INIT;
        END_IF;
        
END_CASE;

xTriggerOld := xTrigger;

END_FUNCTION_BLOCK
