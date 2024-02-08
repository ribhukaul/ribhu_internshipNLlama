
header_mappings={
    "Data.+realizzazion": "data_realizzazione_cedola",
    "Data.+osservazion.+cedol.+": "data_osservazione_cedola",
    "Data.+osservazion.+autocal.+": "data_osservazione_autocall",
    "Autocal.+Trigge": "autocall_trigger_lvl",
    "Data.+Pagament": "data_pagamento_cedola",
    "Import.+": "importo_cedola",
    "Giorno.+ monitor": "giorno_monitoraggio_rimborso",
    "data.+rimbors.+": "data_rimborso_cedola",
}



regex_callable ={
    "leonteq":{
    "autocallable":"autocallable|rimbors.{1,5}anticipat",
    "softcallable":"softcallable|diritt.{1,4}non.{0,3}obblig",
    "effetto_memoria":"effett.{1,5}memori",
    "putable":"putable",
    },
    "bnp": {
        "callable": r"Scadenza\s*Anticipata\s*Opzionale",
        "putable": r"Scadenza\s*Anticipata\s*Automatica",
        "unconditional_protection": r"questo\s*prodotto\s*offre\s*una\s*protezione\s*totale\s*dell'Importo\s*Nozionale\s*a\s*scadenza",
        "memory": r"Tutti\s*i\s*Premi\s*Condizionati\s*non\s*versati\s*si\s*accumuleranno\s*e\s*saranno\s*versati\s*solo\s*se\s*la\s*Condizione\s*del\s*Premio\s*Condizionato\s*verrà\s*soddisfatta\s*successivamente",
        "barrier_type": r"se\s*,\s*in\s*corrspondenza\s*della\s*data\s*di\s*Valutazione\s*dell'importo\s*di\s*Liqidazione,\s*il\s*prezzo\s*di\s*Riferimento\s*Finale\s*è\s*inferiroe\s*alla\s*barriera",
        "importo_minimo": r"tuttavia\s*l'importo\s*minimo\s*sarà\s*pari\s*al\s*\d{0,3}[,\.]?\d{1,2}\s?%\s*dell'Importo\s*Nozionale",
        "leva_cedolare": r"(aumentato\s*del\\s*\d{0,3}[,\.]?\d{1,2}\s?%\sdella\s*performance\s*del\s*Sottostante\s*)|(\s*più\s*un\s*importo\s*commisurato\s*al\s*\d{0,3}[,\.]?\d{1,2}\s?%\sdella\s*Performance)",
        "cap": r"1\.\s*Se\s*il\s*Prezzo\s*di\s*Riferimento\s*Finale\s*è\s*pari\s*o\s*superiore\s*al\s*\d{0,3}[,\.]?\d{1,2}\s?%\s*Prezzo\s*di\s*Riferimento\s*Iniziale",
        "leva_airbag": r"meno\s*un\s*importo\s*commisurato\s*al166,67%\s*della\s*Performance\s*del\s*Sottostante",
    },
}


 
REGEX_PERC = r"\d{0,3}[,\.]?\d{1,2}\s?%"
check_for={
    "leonteq":{},
    "bnp":{
        "importo_minimo": REGEX_PERC,
        "leva_cedolare":  REGEX_PERC,
        "cap":  REGEX_PERC,
        "leva_airbag":  REGEX_PERC,
        },
}