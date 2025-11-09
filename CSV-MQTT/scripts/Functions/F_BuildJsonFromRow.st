// Helper function to build JSON string from CSV row structure
// Formats data as: {"Col1":"value1","Col2":"value2",...}
FUNCTION F_BuildJsonFromRow : BOOL
VAR_INPUT
    row : ST_CSVRow;           // Input CSV row data
END_VAR
VAR_IN_OUT
    sJson : STRING(2048);      // Output JSON string
END_VAR
VAR
    i : INT;
END_VAR

// Build JSON manually since library functions may vary
sJson := '{';

// Add each column as a JSON key-value pair
sJson := CONCAT(sJson, '"Col1":"');  sJson := CONCAT(sJson, row.Col1);  sJson := CONCAT(sJson, '",');
sJson := CONCAT(sJson, '"Col2":"');  sJson := CONCAT(sJson, row.Col2);  sJson := CONCAT(sJson, '",');
sJson := CONCAT(sJson, '"Col3":"');  sJson := CONCAT(sJson, row.Col3);  sJson := CONCAT(sJson, '",');
sJson := CONCAT(sJson, '"Col4":"');  sJson := CONCAT(sJson, row.Col4);  sJson := CONCAT(sJson, '",');
sJson := CONCAT(sJson, '"Col5":"');  sJson := CONCAT(sJson, row.Col5);  sJson := CONCAT(sJson, '",');
sJson := CONCAT(sJson, '"Col6":"');  sJson := CONCAT(sJson, row.Col6);  sJson := CONCAT(sJson, '",');
sJson := CONCAT(sJson, '"Col7":"');  sJson := CONCAT(sJson, row.Col7);  sJson := CONCAT(sJson, '",');
sJson := CONCAT(sJson, '"Col8":"');  sJson := CONCAT(sJson, row.Col8);  sJson := CONCAT(sJson, '",');
sJson := CONCAT(sJson, '"Col9":"');  sJson := CONCAT(sJson, row.Col9);  sJson := CONCAT(sJson, '",');
sJson := CONCAT(sJson, '"Col10":"'); sJson := CONCAT(sJson, row.Col10); sJson := CONCAT(sJson, '",');
sJson := CONCAT(sJson, '"Col11":"'); sJson := CONCAT(sJson, row.Col11); sJson := CONCAT(sJson, '",');
sJson := CONCAT(sJson, '"Col12":"'); sJson := CONCAT(sJson, row.Col12); sJson := CONCAT(sJson, '",');
sJson := CONCAT(sJson, '"Col13":"'); sJson := CONCAT(sJson, row.Col13); sJson := CONCAT(sJson, '"');

sJson := CONCAT(sJson, '}');

F_BuildJsonFromRow := TRUE;

END_FUNCTION
