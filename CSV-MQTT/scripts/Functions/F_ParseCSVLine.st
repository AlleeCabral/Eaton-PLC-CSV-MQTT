// Parses a CSV line into a structured data type with 13 columns
// Splits string by semicolon delimiter and handles quoted fields
FUNCTION F_ParseCSVLine : ST_CSVRow
VAR_INPUT 
    sLine : STRING(512);  // Input: CSV line (e.g., "val1;val2;val3;...")
END_VAR
VAR 
    result      : ST_CSVRow;
    sField      : STRING(64);
    iPos        : INT := 1;
    iFieldNum   : INT := 0;
    iLen        : INT;
    bInQuotes   : BOOL := FALSE;
    cChar       : BYTE;
    i           : INT;
    iFieldLen   : INT := 0;
END_VAR

iLen := LEN(sLine);

// Parse through the line character by character
FOR i := 1 TO iLen DO
    cChar := sLine[i];
    
    // Handle quote character
    IF cChar = 34 THEN  // ASCII 34 = double quote
        bInQuotes := NOT bInQuotes;
        // Don't add quotes to field content
    
    // Handle semicolon delimiter (only if not inside quotes)
    ELSIF cChar = 59 AND NOT bInQuotes THEN  // ASCII 59 = semicolon
        iFieldNum := iFieldNum + 1;
        F_AssignField(ADR(result), iFieldNum, sField);
        sField := '';
        iFieldLen := 0;
    
    // Regular character - add to current field
    ELSE
        IF iFieldLen < 63 THEN
            iFieldLen := iFieldLen + 1;
            sField[iFieldLen] := cChar;
        END_IF;
    END_IF;
END_FOR;

// Assign last field
IF iFieldNum < 13 THEN
    iFieldNum := iFieldNum + 1;
    F_AssignField(ADR(result), iFieldNum, sField);
END_IF;

F_ParseCSVLine := result;

END_FUNCTION
