// Helper function to assign a string value to a specific field in ST_CSVRow
// Uses pointer manipulation to access structure fields dynamically
FUNCTION F_AssignField : BOOL
VAR_INPUT
    pStruct    : POINTER TO ST_CSVRow;  // Pointer to the CSV row structure
    iFieldNum  : INT;                   // Field number (1-13)
    sValue     : STRING(64);            // Value to assign
END_VAR

// Validate inputs
IF pStruct = 0 OR iFieldNum < 1 OR iFieldNum > 13 THEN
    F_AssignField := FALSE;
    RETURN;
END_IF;

// Assign value to appropriate field based on field number
CASE iFieldNum OF
    1:  pStruct^.Col1  := sValue;
    2:  pStruct^.Col2  := sValue;
    3:  pStruct^.Col3  := sValue;
    4:  pStruct^.Col4  := sValue;
    5:  pStruct^.Col5  := sValue;
    6:  pStruct^.Col6  := sValue;
    7:  pStruct^.Col7  := sValue;
    8:  pStruct^.Col8  := sValue;
    9:  pStruct^.Col9  := sValue;
    10: pStruct^.Col10 := sValue;
    11: pStruct^.Col11 := sValue;
    12: pStruct^.Col12 := sValue;
    13: pStruct^.Col13 := sValue;
END_CASE;

F_AssignField := TRUE;

END_FUNCTION
