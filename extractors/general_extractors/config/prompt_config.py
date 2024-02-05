
from extractors.general_extractors.custom_extractors.certificates.certificates_config.cert_tags import (
    TabellaCedola,
    TabellaSottostanti,
    TabellaMainInfo,
    CedolaStr,
    InformazioniBaseCertificati,
    SottostantiHeader,
)

from extractors.general_extractors.custom_extractors.kid.kid_config.kid_tags import (
    InformazioniBase,
    ScenariPerformance,
    TabellaRiy,
    TabellaCostiIngresso,
    TabellaCostiGestione,
    InformazioniBaseGkid,
    ScenariPerformanceGkid,
    TabellaRiyPercGkid,
    TabellaRiyEurGkid,
    TabellaCostiIngressoGkid,
    TabellaCostiGestioneGkid,
    PerformanceScenarios,
    TableRiy,
)



prompts = {
    "it": {
        "general_info": """Dal documento seguente, estrai 
            - ISIN
            - Periodo di detenzione raccomandato o per quanto tempo si presuppone di detenere il prodotto(anni), converti in anni se necessario
            - indicatore sintetico di rischio
            - Data di realizzazione del documento
            DOCUMENTO:
            {context}""",
        "performance1y": """Considerando la seguente tabella,estrai qual'è il rendimento percentuale dei seguenti scenari:
            - STRESS
            - SFAVOREVOLE
            - MODERATO
            - FAVOREVOLE 
            a 1 anno?
            --ritorna solo 4 valori, non di più non di meno
            TABELLA:
                {context}?""",
        "performancerhp": """Considerando la seguente tabella,estrai il rendimento percentuale dei seguenti scenari:
            - STRESS
            - SFAVOREVOLE
            - MODERATO
            - FAVOREVOLE 
            a {rhp} anni?
            --ritorna solo i valori dopo {rhp} anni

            TABELLA:
                {context}?""",
        "performancemorte": """Considerando la seguente tabella fornita,
        -dopo o nella la sezione scenario di morte o decesso di evento assicurato
        estrai i possibili rimborsi ai beneficiari al netto dei costi
        -se trovi 3 valori, ritorna solo il primo e l'ultimo
        -ritorna sempre 2 valori, non di più non di meno
 
            TABELLA:
                {context}?""",
        "market": """"Dal documento seguente cita ciò che si dice sugli investitori al dettaglio cui si intende commercializzare il prodotto
        ---ritorna solamente la citazione niente introduzione
        ---dovrebbero essere multiple lunghe frasi
        ---ritorna solamente ciò che è riportato nel documento non rifrasare, non puoi aggiungere niente,non voglio introduzione, fornisci la risposta esatta
        ---se non trovi la citazione, la frase da cercare potrebbe essere leggermente diversa
        

            DOCUMENTO:
            {context}""",
        "general_info_gkid": """Dal documento seguente, estrai 
            - ISIN
            - Periodo di detenzione raccomandato 
            - indicatore sintetico di rischio minimo o peggiore(da:)(il primo)
            - indicatore sintetico di rischio massimo o migliore(a:)(il secondo)
            - Data di realizzazione del documento
            DOCUMENTO:
            {context}""",
        "performance1y-gkid": """Considerando la seguente tabella,estrai qual'è il rendimento percentuale dei seguenti scenari:
            - STRESS
            - SFAVOREVOLE
            - MODERATO
            - FAVOREVOLE 
            a 1 anno?
            --ritorna solo 4 valori, non di più non di meno
            TABELLA:
                {context}?""",
        "performancerhp-gkid": """Considerando la seguente tabella,estrai il rendimento percentuale dei seguenti scenari:
            - STRESS
            - SFAVOREVOLE
            - MODERATO
            - FAVOREVOLE 
            a {rhp} anni?
            --ritorna solo i valori dopo {rhp} anni

            TABELLA:
                {context}?""",
        "performancemorte-gkid": """Considerando la seguente tabella fornita,
        -dopo o nella la sezione scenario di morte o decesso di evento assicurato
        estrai i possibili rimborsi ai beneficiari al netto dei costi
        -se trovi 3 valori, ritorna solo il primo e l'ultimo
        -ritorna sempre 2 valori, non di più non di meno
 
            TABELLA:
                {context}?""",
        "market_gkid": """"Dal documento seguente cita ciò che si dice sugli investitori al dettaglio cui si intende commercializzare il prodotto
        ---ritorna solamente la citazione niente introduzione
        ---dovrebbero essere multiple lunghe frasi
        ---ritorna solamente ciò che è riportato nel documento non rifrasare, non puoi aggiungere niente,non voglio introduzione, fornisci la risposta esatta
        ---se non trovi la citazione, la frase da cercare potrebbe essere leggermente diversa
        

            DOCUMENTO:
            {context}""",
            "general_info_certificati":"""Dal documento seguente, estrai 
            - ISIN
            - descrizione completa del certificato, appare scritta come certificato ... in VALUTA ... su .... , con valuta che può essere EUR o USD
            - emittente o ideatore del certificato, compare dopo: Ideatore:
            DOCUMENTO:
            {context}""",
            "cedola_str":"""
            Dal documento seguente, estrai esattamente come riportato il pezzo di testo
            mi interessa tutto il denso testo numerato che comprende date e costi e che usa il carattere '▪' come spaziatore.
            potrebbe non esistere, in quel caso ritorna N/A
            DOCUMENTO:
            {context}""",
            
    },
    "en": {
        "general_info": """From the following document, extract:
            - ISIN
            - Recommended holding period
            - Synthetic risk indicator

            DOCUMENT:
            {context}""",
        "performance": """Considering the following table, extract both the percentage return and the monetary amount in the following scenarios:
            - STRESS
            - UNFAVORABLE
            - MODERATE
            - FAVORABLE
            both 1 year and {rhp} years?

            TABLE:
                {context}?""",
        "riy": "",
        "market": """From the following document extract only the quote following (but do not add the phrase to the response)this phrase: 
        -the retail investors to whom we intend to market the product
        ---skip your introduction just say the quote
        ---return only what is specified on the document, do not rephrase, do not add anything, be precise
        ---if you cant find it, the phrase could be slightly different

            DOCUMENTO:
            {context}""",
    },
}


table_schemas = {
    "it": {
        "general_info": InformazioniBase,
        "performance": ScenariPerformance,
        "riy": TabellaRiy,
        "costi_ingresso": TabellaCostiIngresso,
        "costi_gestione": TabellaCostiGestione,
        "general_info_gkid": InformazioniBaseGkid,
        "performance-gkid": ScenariPerformanceGkid,
        "riy%/-gkid": TabellaRiyPercGkid,
        "riy€-gkid": TabellaRiyEurGkid,
        "costi_ingresso_gkid": TabellaCostiIngressoGkid,
        "costi_gestione_gkid": TabellaCostiGestioneGkid,
        "cedola":TabellaCedola,
        "sottostanti":TabellaSottostanti,
        "main_info":TabellaMainInfo,
        "cedola_str":CedolaStr,
        "general_info_certificati":InformazioniBaseCertificati,
        "sottostanti_header":SottostantiHeader,
    },
    "en": {
        "performance": PerformanceScenarios, 
        "riy": TableRiy
        },
}



word_representation = {
    "it": {
        "performance": [
            "moderato",
            "sfavorevole",
            "favorevole",
            "stress",
            "possibile rimborso al",
        ],
        "riy": ["costi totali", "Costi totali", "riy", "Riy", "RIY"],
        "riy_perc_gkid": ["costi totali", "Costi totali", "riy", "Riy", "RIY"],
        "costi_ingresso": [
            "costi di ingresso",
            "costi di uscita",
            "Costi di ingresso",
            "Costi di uscita",
        ],
        "costi_gestione": [
            "commissioni di gestione",
            "costi di transazione",
            "commissioni di performance",
            "costi amministrativi",
            "Commissioni di gestione",
            "Costi di transazione",
            "Commissioni di performance",
            "Costi amministrativi",
        ],
        "costi_ingresso_gkid": [
            "costi di ingresso",
            "costi di uscita",
            "Costi di ingresso",
            "Costi di uscita",
        ],
        "costi_gestione_gkid": [
            "commissioni di gestione",
            "costi di transazione",
            "commissioni di performance",
            "costi amministrativi",
            "Commissioni di gestione",
            "Costi di transazione",
            "Commissioni di performance",
            "Costi amministrativi",
        ],
        
        "cedola": ["cedola", "Cedola","Data di Osservazione della Cedola", "Data di Pagamento della Cedola Condizionale", "Importo della Cedola Condizionale"],
        "sottostanti": [ "Bloomberg Ticker", "bloomberg Ticker","Ticker", "Sottostante", "ISIN",],
        "main_info": ["Valuta del prodotto", "Performance Peggiore", "Modalità di Pagamento"],
    },
    "en": {
        "performance": [
            "moderate",
            "unfavorable",
            "favorable",
            "stress",
            "might get back",
        ],
        "riy": ["total costs", "annual cost"],
    },
}
