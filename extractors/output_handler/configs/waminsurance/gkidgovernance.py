
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

gkid = {
    "fields": {
        "date": {
            "field_name": "cod_date",
            "renaming": "Data",
            "allow_null": FALSE,
            "type_of": DATE,
            "model_of": NA,
            "decimals_of": None,
            "range_of": DATE_RANGE        
            },
        "periodo_detenzione_raccomandato": {
            "field_name": "cod_rhp",
            "renaming": "RHP (anni)",
            "allow_null": FALSE,
            "type_of": INT,
            "model_of": YEARS,
            "decimals_of": None,
            "range_of": PERCENT_RANGE        
            },
        "indicatore_sintetico_rischio_min": {
            "field_name": "cod_sri_min",
            "renaming": "SRI MIN",
            "allow_null": FALSE,
            "type_of": INT,
            "model_of": YEARS,
            "decimals_of": None,
            "range_of": SRI_RANGE        
            },
        "indicatore_sintetico_rischio_max": {
            "field_name": "cod_sri_max",
            "renaming": "SRI MAX",
            "allow_null": FALSE,
            "type_of": INT,
            "model_of": YEARS,
            "decimals_of": None,
            "range_of": SRI_RANGE        
            },
        "incidenza_costo_eur_1_min": {
            "field_name": "cod_riy_eur_1_min",
            "renaming": "RIY 1Y EUR MIN",
            "allow_null": TRUE,
            "type_of": FLOAT,
            "model_of": EURO,
            "decimals_of": 2,
            "range_of": PERCENT_RANGE        
            },
        "incidenza_costo_eur_1_max": {
            "field_name": "cod_riy_eur_1_max",
            "renaming": "RIY 1Y EUR MAX",
            "allow_null": FALSE,
            "type_of": FLOAT,
            "model_of": EURO,
            "decimals_of": 2,
            "range_of": PERCENT_RANGE        
            },
        "incidenza_costo_eur_2_min": {
            "field_name": "cod_riy_eur_2_min",
            "renaming": "RIY RHP/2 EUR MIN",
            "allow_null": FALSE,
            "type_of": FLOAT,
            "model_of": EURO,
            "decimals_of": 2,
            "range_of": PERCENT_RANGE        
            },
        "incidenza_costo_eur_2_max": {
            "field_name": "cod_riy_eur_2_max",
            "renaming": "RIY RHP/2 EUR MAX",
            "allow_null": FALSE,
            "type_of": FLOAT,
            "model_of": EURO,
            "decimals_of": 2,
            "range_of": PERCENT_RANGE        
            },
        "incidenza_costo_eur_rhp_min": {
            "field_name": "cod_riy_eur_rhp_min",
            "renaming": "RIY RHP EUR MIN",
            "allow_null": FALSE,
            "type_of": FLOAT,
            "model_of": EURO,
            "decimals_of": 2,
            "range_of": PERCENT_RANGE        
            },
        "incidenza_costo_eur_rhp_max": {
            "field_name": "cod_riy_eur_rhp_max",
            "renaming": "RIY RHP EUR MAX",
            "allow_null": FALSE,
            "type_of": FLOAT,
            "model_of": EURO,
            "decimals_of": 2,
            "range_of": PERCENT_RANGE        
            },
        "incidenza_costo_perc_1_min": {
            "field_name": "cod_riy_perc_1_min",
            "renaming": "RIY 1Y % MIN",
            "allow_null": TRUE,
            "type_of": FLOAT,
            "model_of": PERCENT,
            "decimals_of": 2,
            "range_of": PERCENT_RANGE        
            },
        "incidenza_costo_perc_1_max": {
            "field_name": "cod_riy_perc_1_max",
            "renaming": "RIY 1Y % MAX",
            "allow_null": FALSE,
            "type_of": FLOAT,
            "model_of": PERCENT,
            "decimals_of": 2,
            "range_of": PERCENT_RANGE        
            },
        "incidenza_costo_perc_2_min": {
            "field_name": "cod_riy_perc_2_min",
            "renaming": "RIY RHP/2 % MIN",
            "allow_null": FALSE,
            "type_of": FLOAT,
            "model_of": PERCENT,
            "decimals_of": 2,
            "range_of": PERCENT_RANGE        
            },
        "incidenza_costo_perc_2_max": {
            "field_name": "cod_riy_perc_2_max",
            "renaming": "RIY RHP/2 % MAX",
            "allow_null": FALSE,
            "type_of": FLOAT,
            "model_of": PERCENT,
            "decimals_of": 2,
            "range_of": PERCENT_RANGE        
            },
        "incidenza_costo_perc_rhp_min": {
            "field_name": "cod_riy_perc_rhp_min",
            "renaming": "RIY RHP % MIN",
            "allow_null": FALSE,
            "type_of": FLOAT,
            "model_of": PERCENT,
            "decimals_of": 2,
            "range_of": PERCENT_RANGE        
            },
        "incidenza_costo_perc_rhp_max": {
            "field_name": "cod_riy_perc_rhp_max",
            "renaming": "RIY RHP % MAX",
            "allow_null": FALSE,
            "type_of": FLOAT,
            "model_of": PERCENT,
            "decimals_of": 2,
            "range_of": PERCENT_RANGE        
            },
        "costi_ingresso_gkid_min": {
            "field_name": "cod_costi_ingresso_min",
            "renaming": "Costi ingresso MIN",
            "allow_null": TRUE,
            "type_of": FLOAT,
            "model_of": EURO,
            "decimals_of": 2,
            "range_of": PERCENT_RANGE        
            },
        "costi_ingresso_gkid_max": {
            "field_name": "cod_costi_ingresso_max",
            "renaming": "Costi ingresso MAX",
            "allow_null": FALSE,
            "type_of": FLOAT,
            "model_of": EURO,
            "decimals_of": 2,
            "range_of": PERCENT_RANGE        
            },
        "costi_uscita_gkid_min": {
            "field_name": "cod_costi_uscita_min",
            "renaming": "Costi uscita MIN",
            "allow_null": TRUE,
            "type_of": FLOAT,
            "model_of": EURO,
            "decimals_of": 2,
            "range_of": PERCENT_RANGE        
            },
        "costi_uscita_gkid_max": {
            "field_name": "cod_costi_uscita_max",
            "renaming": "Costi uscita MAX",
            "allow_null": FALSE,
            "type_of": FLOAT,
            "model_of": EURO,
            "decimals_of": 2,
            "range_of": PERCENT_RANGE        
            },
        "commissione_gestione_gkid_min": {
            "field_name": "cod_commissioni_di_gestione_min",
            "renaming": "Commissioni di gestione MIN",
            "allow_null": FALSE,
            "type_of": FLOAT,
            "model_of": PERCENT,
            "decimals_of": 2,
            "range_of": PERCENT_RANGE        
            },
        "commissione_gestione_gkid_max": {
            "field_name": "cod_commissioni_di_gestione_max",
            "renaming": "Commissioni di gestione MAX",
            "allow_null": FALSE,
            "type_of": FLOAT,
            "model_of": PERCENT,
            "decimals_of": 2,
            "range_of": PERCENT_RANGE        
            },
        "commissione_transazione_gkid_min": {
            "field_name": "cod_costi_di_transazione_min",
            "renaming": "Costi di transazione MIN",
            "allow_null": FALSE,
            "type_of": FLOAT,
            "model_of": PERCENT,
            "decimals_of": 2,
            "range_of": PERCENT_RANGE        
            },
        "commissione_transazione_gkid_max": {
            "field_name": "cod_costi_di_transazione_max",
            "renaming": "Costi di transazione MAX",
            "allow_null": FALSE,
            "type_of": FLOAT,
            "model_of": PERCENT,
            "decimals_of": 2,
            "range_of": PERCENT_RANGE        
            },
        "commissione_performance_gkid_min": {
            "field_name": "cod_commissioni_di_performance_min",
            "renaming": "Commissioni di performance MIN",
            "allow_null": TRUE,
            "type_of": FLOAT,
            "model_of": PERCENT,
            "decimals_of": 2,
            "range_of": PERCENT_RANGE        
            },
        "commissione_performance_gkid_max": {
            "field_name": "cod_commissioni_di_performance_max",
            "renaming": "Commissioni di performance MAX",
            "allow_null": FALSE,
            "type_of": FLOAT,
            "model_of": PERCENT,
            "decimals_of": 2,
            "range_of": PERCENT_RANGE        
            },
        "target_market": {
            "field_name": "cod_target_market",
            "renaming": "Target Market",
            "allow_null": FALSE,
            "type_of": STRING,
            "model_of": NA,
            "decimals_of": None,
            "range_of": NO_RANGE        
            },
        "api_costs": {
            "renaming": "Costi API",
            }
        },
    "sections":{
        "section0": {
            "name": "Informazioni di base",
            "list": ["cod_date", "cod_rhp", "cod_sri_min", "cod_sri_max"]
        },
        "section1": {
            "name": "Reduction In Yield",
            "list": ["cod_riy_eur_1_min", "cod_riy_eur_1_max", "cod_riy_eur_2_min",  "cod_riy_eur_2_max", "cod_riy_eur_rhp_min", "cod_riy_eur_rhp_max",
            "cod_riy_perc_1_min", "cod_riy_perc_1_max", "cod_riy_perc_2_min", "cod_riy_perc_2_max", "cod_riy_perc_rhp_min", "cod_riy_perc_rhp_max"
            ]
        },
        "section2": {
            "name": "Costi e Commissioni",
            "list": [
                "cod_costi_ingresso_min",
                "cod_costi_ingresso_max",
                "cod_costi_uscita_min",
                "cod_costi_uscita_max",
                "cod_commissioni_di_gestione_min",
                "cod_commissioni_di_gestione_max",
                "cod_costi_di_transazione_min",
                "cod_costi_di_transazione_max",
                "cod_commissioni_di_performance_min",
                "cod_commissioni_di_performance_max"
            ]
        },
        "section3": {
            "name": "Target Market",
            "list": ["cod_target_market"]
        }
    }

}

