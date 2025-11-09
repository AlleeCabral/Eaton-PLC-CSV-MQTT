// Helper function to extract next line from a string buffer
// Returns TRUE if a line was found, FALSE if end of buffer reached
FUNCTION F_GetNextLine : BOOL
VAR_INPUT
    sBuffer    : STRING(4096);  // Input buffer containing multiple lines
    iStartPos  : INT;           // Starting position to search from
END_VAR
VAR_OUTPUT
    sLine      : STRING(512);   // Extracted line (without line break)
    iEndPos    : INT;           // Position after the line break
END_VAR
VAR
    i          : INT;
    iLen       : INT;
    iLineLen   : INT := 0;
    cChar      : BYTE;
END_VAR

// Initialize
sLine := '';
iLen := LEN(sBuffer);

// Check if we're at or past end of buffer
IF iStartPos > iLen OR iStartPos < 1 THEN
    F_GetNextLine := FALSE;
    RETURN;
END_IF;

// Extract characters until newline or end of buffer
FOR i := iStartPos TO iLen DO
    cChar := sBuffer[i];
    
    // Check for line break characters (LF=10, CR=13)
    IF cChar = 10 OR cChar = 13 THEN
        iEndPos := i;
        
        // Handle CRLF (skip the LF if next char is LF)
        IF cChar = 13 AND i < iLen THEN
            IF sBuffer[i+1] = 10 THEN
                iEndPos := i + 1;
            END_IF;
        END_IF;
        
        F_GetNextLine := TRUE;
        RETURN;
    END_IF;
    
    // Append character to line
    IF iLineLen < 511 THEN
        iLineLen := iLineLen + 1;
        sLine[iLineLen] := cChar;
    END_IF;
END_FOR;

// Reached end of buffer - return last line if any content found
IF iLineLen > 0 THEN
    iEndPos := iLen;
    F_GetNextLine := TRUE;
ELSE
    F_GetNextLine := FALSE;
END_IF;

END_FUNCTION
