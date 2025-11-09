// This function block reads CSV files row by row for PLC processing
// Uses state machine approach for efficient file handling
FUNCTION_BLOCK FB_CSVReader
VAR_INPUT
    xEnable   : BOOL;   // TRUE = start/continue reading, FALSE = stop and reset
    sFilePath : STRING; // File path to the CSV file (e.g., '/usr/data.csv')
END_VAR
VAR_OUTPUT
    RowOut    : ST_CSVRow; // Output: One parsed row with 13 columns of data
    xNewRow   : BOOL;      // Pulse TRUE when a new row is ready
    xBusy     : BOOL;      // TRUE while processing
    xError    : BOOL;      // TRUE if error occurred
    eError    : DWORD;     // Error code from file operations
    xDone     : BOOL;      // TRUE when finished reading entire file
END_VAR
VAR
    // State machine control
    eState : (IDLE, OPEN_FILE, READ_FILE, PARSE_LINES, CLOSE_FILE, ERROR) := IDLE;
    
    // File operation variables
    hFile      : RTS_IEC_HANDLE := RTS_INVALID_HANDLE; // File handle
    sBuffer    : STRING(4096);   // Buffer for file content
    udiReadSize : UDINT;         // Actual bytes read
    diResult   : DINT;           // Function return values
    
    // Parsing variables
    iLineStart : INT := 1;       // Current position in buffer
    iLineEnd   : INT;            // End of current line
    sCurrentLine : STRING(512);  // Current line being processed
    iLineCount : INT := 0;       // Total lines processed
    bHeaderSkipped : BOOL := FALSE; // Track header skip
    
    // Control flags
    xEnableOld : BOOL := FALSE;  // Edge detection
END_VAR

// Reset on falling edge of xEnable
IF NOT xEnable AND xEnableOld THEN
    eState := IDLE;
    xBusy := FALSE;
    xError := FALSE;
    xDone := FALSE;
    xNewRow := FALSE;
    iLineStart := 1;
    iLineCount := 0;
    bHeaderSkipped := FALSE;
    IF hFile <> RTS_INVALID_HANDLE THEN
        diResult := SysFileClose(hFile := hFile);
        hFile := RTS_INVALID_HANDLE;
    END_IF;
END_IF;
xEnableOld := xEnable;

// State machine processing
xNewRow := FALSE; // Clear pulse output

CASE eState OF
    
    IDLE:
        IF xEnable THEN
            eState := OPEN_FILE;
            xBusy := TRUE;
            xError := FALSE;
            xDone := FALSE;
            sBuffer := '';
            iLineStart := 1;
        END_IF;
    
    OPEN_FILE:
        // Open file using SysFile function (not FB)
        hFile := SysFileOpen(szFile := sFilePath, am := AM_READ, pResult := ADR(diResult));
        IF hFile <> RTS_INVALID_HANDLE THEN
            eState := READ_FILE;
        ELSE
            eError := DWORD_TO_DWORD(diResult);
            xError := TRUE;
            eState := ERROR;
        END_IF;
    
    READ_FILE:
        // Read entire file content into buffer
        udiReadSize := SysFileRead(hFile := hFile, pbyBuffer := ADR(sBuffer), 
                                    ulSize := SIZEOF(sBuffer)-1, pResult := ADR(diResult));
        IF diResult = 0 THEN
            eState := PARSE_LINES;
        ELSE
            eError := DWORD_TO_DWORD(diResult);
            xError := TRUE;
            eState := CLOSE_FILE;
        END_IF;
    
    PARSE_LINES:
        // Extract next line from buffer
        IF F_GetNextLine(sBuffer, iLineStart, sCurrentLine, iLineEnd) THEN
            iLineStart := iLineEnd + 1;
            iLineCount := iLineCount + 1;
            
            // Skip header row
            IF NOT bHeaderSkipped THEN
                bHeaderSkipped := TRUE;
            ELSE
                // Parse CSV line into structure
                RowOut := F_ParseCSVLine(sCurrentLine);
                xNewRow := TRUE; // Signal new row available
            END_IF;
        ELSE
            // No more lines - finished
            eState := CLOSE_FILE;
        END_IF;
    
    CLOSE_FILE:
        IF hFile <> RTS_INVALID_HANDLE THEN
            diResult := SysFileClose(hFile := hFile);
            hFile := RTS_INVALID_HANDLE;
        END_IF;
        xDone := TRUE;
        xBusy := FALSE;
        eState := IDLE;
    
    ERROR:
        xBusy := FALSE;
        IF hFile <> RTS_INVALID_HANDLE THEN
            diResult := SysFileClose(hFile := hFile);
            hFile := RTS_INVALID_HANDLE;
        END_IF;
        eState := IDLE;
        
END_CASE;
