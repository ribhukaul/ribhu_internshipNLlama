
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
    "autocallable":"autocallable|rimbors.{1,5}anticipat",
    "softcallable":"softcallable|diritt.{1,4}non.{0,3}obblig",
    "effetto_memoria":"effett.{1,5}memori",
    "putable":"putable",
}