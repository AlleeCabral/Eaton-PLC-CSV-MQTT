// Data structure for a single CSV row with 13 columns
// Each column stores string data up to 64 characters
TYPE ST_CSVRow :
STRUCT
    Col1  : STRING(64);  // First column
    Col2  : STRING(64);  // Second column
    Col3  : STRING(64);  // Third column
    Col4  : STRING(64);  // Fourth column
    Col5  : STRING(64);  // Fifth column
    Col6  : STRING(64);  // Sixth column
    Col7  : STRING(64);  // Seventh column
    Col8  : STRING(64);  // Eighth column
    Col9  : STRING(64);  // Ninth column
    Col10 : STRING(64);  // Tenth column
    Col11 : STRING(64);  // Eleventh column
    Col12 : STRING(64);  // Twelfth column
    Col13 : STRING(64);  // Thirteenth column
END_STRUCT
END_TYPE
