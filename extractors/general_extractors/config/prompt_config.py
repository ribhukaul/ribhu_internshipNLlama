from extractors.general_extractors.custom_extractors.certificates.certificates_config.cert_tags import (
    InformazioniBaseBNP,
    TabellaAllegatoScadenzaBNP,
    TabellaCedola,
    TabellaSottostanti,
    TabellaMainInfo,
    CedolaStr,
    InformazioniBaseCertificati,
    TabellaSottostantiHeader,
    TabellaAllegatoPremioBNP,
    TabellaFirstInfoBNP,
    TabellaSottostanteBNP,
    TabellaMainInfoBNP,
)

from extractors.general_extractors.custom_extractors.kid.kid_config.kid_tags import (
    InformazioniBase,
    TabellaScenariPerformance,
    TabellaRiy,
    TabellaCostiIngresso,
    TabellaCostiGestione,
    InformazioniBaseGkid,
    TabellaScenariPerformanceGkid,
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
        "general_info_certificati": """Dal documento seguente, estrai 
            - ISIN
            - descrizione completa del certificato, appare scritta come certificato ... in VALUTA ... su .... , con valuta che può essere EUR o USD
            - emittente o ideatore del certificato, compare dopo: Ideatore:
            DOCUMENTO:
            {context}""",
        "cedola_str": """
            Dal documento seguente, estrai esattamente come riportato il pezzo di testo
            mi interessa tutto il denso testo numerato che comprende date e costi e che usa il carattere '▪' come spaziatore.
            potrebbe non esistere, in quel caso ritorna N/A
            DOCUMENTO:
            {context}""",
        "general_info_bnp": """Dal documento seguente, estrai 
             -il periodo di detenzione raccomandato
             -l'indicatore di rischio su 7 come dato
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
        "performance": TabellaScenariPerformance,
        "riy": TabellaRiy,
        "costi_ingresso": TabellaCostiIngresso,
        "costi_gestione": TabellaCostiGestione,
        "general_info_gkid": InformazioniBaseGkid,
        "performance-gkid": TabellaScenariPerformanceGkid,
        "riy%/-gkid": TabellaRiyPercGkid,
        "riy€-gkid": TabellaRiyEurGkid,
        "costi_ingresso_gkid": TabellaCostiIngressoGkid,
        "costi_gestione_gkid": TabellaCostiGestioneGkid,
        "cedola": TabellaCedola,
        "sottostanti": TabellaSottostanti,
        "main_info": TabellaMainInfo,
        "cedola_str": CedolaStr,
        "general_info_certificati": InformazioniBaseCertificati,
        "sottostanti_header": TabellaSottostantiHeader,
        "general_info_bnp": InformazioniBaseBNP,
        "main_info_bnp": TabellaMainInfoBNP,
        "allegato_bnp_premio": TabellaAllegatoPremioBNP,
        "allegato_bnp_scadenza": TabellaAllegatoScadenzaBNP,
        "first_info_bnp": TabellaFirstInfoBNP,
        "sottostante_bnp": TabellaSottostanteBNP,
    },
    "en": {"performance": PerformanceScenarios, "riy": TableRiy},
}


word_representation = {
    "it": {
        "performance": ["moderato", "sfavorevole", "favorevole", "stress", "possibile rimborso al"],
        "riy": ["costi totali", "riy"],
        "riy_perc_gkid": ["costi totali", "riy"],
        "costi_ingresso": ["costi di ingresso", "costi di uscita"],
        "costi_gestione": [
            "commissioni di gestione",
            "costi di transazione",
            "commissioni di performance",
            "costi amministrativi",
        ],
        "costi_ingresso_gkid": ["costi di ingresso", "costi di uscita"],
        "costi_gestione_gkid": [
            "commissioni di gestione",
            "costi di transazione",
            "commissioni di performance",
            "costi amministrativi",
        ],
        "cedola": [
            "cedola",
            "cedola",
            "data di osservazione della cedola",
            "data di pagamento della cedola condizionale",
            "importo della cedola condizionale",
        ],
        "sottostanti": ["bloomberg ticker", "ticker", "sottostante", "isin"],
        "main_info": ["valuta del prodotto", "performance peggiore", "modalità di pagamento"],
        "sottostanti_table": ["bloomberg ticker", "ticker", "sottostante", "isin"],
        "first_info_bnp": ["codice isin", "isin", "autorità competente", "redazione", "produttore"],
        "main_info_bnp": ["data di strike", "strike", "prezzo di emissione", "emissione", "(rimborso)"],
        "main_info_bnp2": ["valuta", "valuta del prodotto", "importo nozionale", "nozionale"],
        "sottostante_bnp": ["bloomberg", "codice bloomberg", "sottostante", "isin"],
        "allegato_bnp_premio": ["premio/i", "premio", "barriera/e", "condizionato"],
        "allegato_bnp_scadenza": ["liquidazione", "anticipata", "facoltativa", "scadenza"],
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
