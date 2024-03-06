
# typeof
INT = "Integer"
FLOAT = "Float"
STRING = "String"
DATE= "Date"
BOOL = "Boolean"
#model of
PERCENT = "%"
EURO = "€"
YEARS = "anni"
CAPS = "CAPS"

TRUE = "true"
FALSE = "false"
NA = "N/A"

PERCENT_RANGE = []
ISIN_RANGE = []
DATE_RANGE = []

SRI_RANGE = []
NO_RANGE = []

kidcredem = {
    "fields": {
        "date": {
            "field_name": "cod_date",
            "renaming": "Data",
            "allow_null": FALSE,
            "type_of": DATE,
            "model_of": NA,
            "decimals_of": NA,
            "range_of": DATE_RANGE 
            },
        "isin": {
            "field_name": "cod_isin",
            "renaming": "ISIN",
            "allow_null": FALSE,
            "type_of": STRING,
            "model_of": CAPS,
            "decimals_of": NA,
            "range_of": ISIN_RANGE        
            },
        "periodo_detenzione_raccomandato": {
            "field_name": "cod_rhp",
            "renaming": "RHP (anni)",
            "allow_null": FALSE,
            "type_of": INT,
            "model_of": YEARS,
            "decimals_of": NA,
            "range_of": PERCENT_RANGE        
            },
        "favorable_return_rhp": {
            "field_name": "cod_rsfav_rhp",
            "renaming": "RSFAV RHP %",
            "allow_null": FALSE,
            "type_of": FLOAT,
            "model_of": PERCENT,
            "decimals_of": 2,
            "range_of": PERCENT_RANGE        
            },
        "indicatore_sintetico_rischio": {
            "field_name": "cod_sri",
            "renaming": "SRI",
            "allow_null": FALSE,
            "type_of": INT,
            "model_of": YEARS,
            "decimals_of": NA,
            "range_of": SRI_RANGE        
            },
        "moderato_return_rhp": {
            "field_name": "cod_rsmod_rhp",
            "renaming": "RSMOD RHP %",
            "allow_null": FALSE,
            "type_of": FLOAT,
            "model_of": PERCENT,
            "decimals_of": 2,
            "range_of": PERCENT_RANGE        
            },
        "incidenza_costo_1": {
            "field_name": "cod_riy_1y",
            "renaming": "RIY 1Y %",
            "allow_null": TRUE,
            "type_of": FLOAT,
            "model_of": PERCENT,
            "decimals_of": 2,
            "range_of": PERCENT_RANGE        
            },
        "incidenza_costo_rhp": {
            "field_name": "cod_riy_rhp",
            "renaming": "RIY RHP %",
            "allow_null": FALSE,
            "type_of": FLOAT,
            "model_of": PERCENT,
            "decimals_of": 2,
            "range_of": PERCENT_RANGE        
            }
    },
    "sections": 
    {
        "section0": {
            "name": "Informazioni di base",
            "list": ["cod_date", "cod_isin", "cod_sri", "cod_rhp"]
        },
        "section1": {
            "name": "Performance",
            "list": ["cod_rsfav_rhp", "cod_rsmod_rhp"]
        },
        "section2": {
            "name": "Reduction In Yield",
            "list": ["cod_riy_1y", "cod_riy_rhp"]
        }
    }
}


