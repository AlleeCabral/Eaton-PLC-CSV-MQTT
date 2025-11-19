// MQTT Publisher using Stefan Dreyer MQTT library
// Builds JSON from CSV row data and publishes it to the configured broker
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
    // MQTT client structure and handler instances
    mqttInOut     : SD_MQTT.MQTT_IN_OUT;   // Shared MQTT data structure
    fbMQTTClient  : SD_MQTT.MqttClient;    // Main MQTT client FB
    fbMQTTPublish : SD_MQTT.MqttPublish;   // Publish helper FB

    // Connection / publish state machine
    eState        : (IDLE, CONNECTING, READY, PUBLISHING, ERROR) := IDLE;
    ePrevState    : (IDLE, CONNECTING, READY, PUBLISHING, ERROR) := IDLE;

    // Payload buffers
    sJsonPayload  : STRING(2048);
    sActiveTopic  : STRING(255);
    sActiveHost   : STRING(255);
    sUrlBuffer    : STRING(512);
    sPortBuffer   : STRING(16);

    // Helpers
    trigPublish   : Standard.R_TRIG;
    trigSend      : Standard.R_TRIG;
    xSendPulseReq : BOOL;
    xLinkDone     : BOOL;
    xUseTLS       : BOOL;
    xErrorLatched : BOOL;

    // MQTT client error latches
    dwClientError : DWORD;
    byClientError : BYTE;

    // Default QoS (0 = at most once)
    eDefaultQoS   : SD_MQTT.QoS := 0;
END_VAR
VAR CONSTANT
    c_tClientTimeout : TIME := T#5S;
END_VAR

// Clear pulse outputs each call
xPublished := FALSE;
xSendPulseReq := FALSE;

// Link publish FB once to the shared MQTT data
IF NOT xLinkDone THEN
    fbMQTTPublish.SetMqttInOut(MQTT_IN_OUT := mqttInOut);
    xLinkDone := TRUE;
END_IF;

// Select active host and client ID based on connection mode
IF xUseLaptop THEN
    sActiveHost := sBrokerLaptop;
    mqttInOut.ClientID := 'EatonPLC_Laptop';
ELSE
    sActiveHost := sBrokerLAN;
    mqttInOut.ClientID := 'EatonPLC_LAN';
END_IF;

// Align dynamic allocation limits with payload buffer size
mqttInOut.COM_CONFIG.MaxPayloadSize := UDINT#2048;

// Build URL in form host:port for client FB
sPortBuffer := UINT_TO_STRING(uiPort);
sUrlBuffer := Standard.CONCAT(STR1 := sActiveHost, STR2 := ':');
sUrlBuffer := Standard.CONCAT(STR1 := sUrlBuffer, STR2 := sPortBuffer);

// Enable TLS automatically for the standard secure port
xUseTLS := uiPort = 8883;

// Drive Stefan Dreyer MQTT client every cycle
fbMQTTClient(
    MQTT_IN_OUT := mqttInOut,
    ENABLE := xEnable,
    URL := sUrlBuffer,
    TIMEOUT := c_tClientTimeout,
    TLS := xUseTLS,
    ERROR_C => dwClientError,
    ERROR_T => byClientError
);

// Rising edge detection for publish trigger
trigPublish(CLK := xTrigger);

// State machine controlling connection and publish flow
CASE eState OF
    IDLE:
        xConnected := FALSE;
        IF NOT xEnable THEN
            xErrorLatched := FALSE;
            sStatus := 'Idle';
        ELSE
            sStatus := 'Connecting...';
            eState := CONNECTING;
        END_IF;

    CONNECTING:
        xConnected := FALSE;
        sStatus := 'Connecting...';
        IF NOT xEnable THEN
            eState := IDLE;
        ELSIF mqttInOut.BROKER_CONNECTED THEN
            sStatus := 'Connected';
            eState := READY;
        ELSIF (dwClientError <> DWORD#0) OR (byClientError <> BYTE#0) THEN
            xErrorLatched := TRUE;
            sStatus := 'Connection error';
            eState := ERROR;
        END_IF;

    READY:
        xConnected := TRUE;
        sStatus := 'Connected';
        IF NOT xEnable THEN
            eState := IDLE;
        ELSIF NOT mqttInOut.BROKER_CONNECTED THEN
            sStatus := 'Reconnecting...';
            eState := CONNECTING;
        ELSE
            // Keep local copy of topic while idle
            sActiveTopic := sTopic;

            IF trigPublish.Q THEN
                IF fbMQTTPublish.sendActive THEN
                    sStatus := 'Publish busy';
                ELSIF NOT F_BuildJsonFromRow(row := RowIn, sJson := sJsonPayload) THEN
                    xErrorLatched := TRUE;
                    sStatus := 'JSON build failed';
                    eState := ERROR;
                ELSE
                    xSendPulseReq := TRUE;
                    sStatus := 'Publishing...';
                    eState := PUBLISHING;
                END_IF;
            END_IF;
        END_IF;

    PUBLISHING:
        xConnected := mqttInOut.BROKER_CONNECTED;
        sStatus := 'Publishing...';
        IF NOT xEnable THEN
            eState := IDLE;
        ELSIF NOT mqttInOut.BROKER_CONNECTED THEN
            xErrorLatched := TRUE;
            sStatus := 'Connection lost';
            eState := ERROR;
        ELSIF fbMQTTPublish.done THEN
            xPublished := TRUE;
            sStatus := 'Published';
            eState := READY;
        ELSIF fbMQTTPublish.SendTimeout THEN
            xErrorLatched := TRUE;
            sStatus := 'Publish timeout';
            eState := ERROR;
        END_IF;

    ERROR:
        xConnected := FALSE;
        IF NOT xEnable THEN
            xErrorLatched := FALSE;
            sStatus := 'Idle';
            eState := IDLE;
        ELSIF (dwClientError <> DWORD#0) OR (byClientError <> BYTE#0) THEN
            sStatus := 'Client error';
        ELSE
            sStatus := 'Retrying...';
            eState := CONNECTING;
        END_IF;
END_CASE;

// Positive edge on publish send input
trigSend(CLK := xSendPulseReq);

// Execute publish FB (string payload mode)
fbMQTTPublish(
    Topic := ADR(sActiveTopic),
    PayloadString := ADR(sJsonPayload),
    PublishAsString := TRUE,
    Payload := 0,
    PayloadLength := 0,
    QoSIn := eDefaultQoS,
    MRetain := FALSE,
    send := trigSend.Q
);

// Clear latched error once stable connection restored
IF (ePrevState <> eState) AND (eState = READY) THEN
    xErrorLatched := FALSE;
END_IF;
ePrevState := eState;

// Final outputs
xConnected := xEnable AND mqttInOut.BROKER_CONNECTED;
xError := xErrorLatched OR (xEnable AND ((dwClientError <> DWORD#0) OR (byClientError <> BYTE#0)));

IF NOT xEnable THEN
    sStatus := 'Disabled';
END_IF;

END_FUNCTION_BLOCK
