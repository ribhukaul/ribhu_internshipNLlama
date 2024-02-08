
import asyncio
import os
import re
from numpy import extract
import pandas as pd
from extractors.azure.document_intelligence import get_tables_from_doc
from extractors.general_extractors.config.json_config import NA
from extractors.general_extractors.custom_extractors.certificates.derivati_extractor import DerivatiKidExtractor
from extractors.general_extractors.custom_extractors.kid.kid_config.kid_tags import NF
from extractors.general_extractors.llm_functions import general_table_inspection, llm_extraction_and_tag
from extractors.models import Models
from extractors.utils import extract_between, is_in_text, search_in_pattern_in_text


class BNPDerivatiKidExtractor(DerivatiKidExtractor):
    
    def __init__(self, doc_path) -> None:
        self.doc_path = doc_path
        super().__init__(doc_path)
        
        
    async def fill_tables(self, page):
        """experimental for faster runs, fills the tables in the document asynchronously all in one

        Args:
            page (_type_): _description_
        """
        fill = get_tables_from_doc(
            self.doc_path, specific_pages=page, language=self.language
        )

        self.di_tables_pages[str(page-1)] = fill

    async def get_tables(self):
        """calc table extractor, it extracts the three tables from the document asynchronously

        Returns:
            dict([pandas.dataframe]): tables as dataframe
        """
        try:
            tasks = []
            for i in range(1, min([len(self.text) + 1,6])):
                tasks.append(asyncio.create_task(self.fill_tables(i)))
            

            await asyncio.wait(tasks, return_when=asyncio.ALL_COMPLETED)

            

            first_info_table = self._extract_table("first_info_bnp")
            allegato_table_scadenza= self._extract_table("allegato_bnp_scadenza", black_list_pages=[0,1])
            performance_table = self._extract_table("performance", black_list_pages=[0])
            
        except Exception as error:
            print("get_tables error" + repr(error))
            tables = [allegato_table_scadenza, first_info_table, performance_table]
            for i, table in enumerate(tables):
                if not table:
                    tables[i] = None

        return dict(
            [
                ("allegato_scadenza", allegato_table_scadenza),
                ("first_info", first_info_table),
                ("performance", performance_table),
            ]
        )

    async def extract_general_data(self):
        """
        Extract general data from the document (ISIN, RHP, SRI).

        Returns: dict(): data extracted
        """
        try:
            extraction= {"description":extract_between(self.text[0].page_content[:800], "Prodotto", "codice")}
            extraction.update(dict( llm_extraction_and_tag(
                [self.text[1]], self.language, "general_info_bnp", self.file_id
            )))
            extraction=dict(extraction)
            if extraction.get("description") and is_in_text("airbag",(extraction.get("description"))):
                extraction["airbag"]=1
            else:
                extraction["airbag"]=0
                
                
            
            
            if ("periodo_detenzione_raccomandato" in extraction):
                self.rhp = extraction["periodo_detenzione_raccomandato"]
            else:
                self.rhp = "multiple"
            
        except Exception as error:
            print("extract general data error" + repr(error))
            error_list =["description", "airbag","indicatore_sintetico_rishio"]
            extraction= {key: (extraction[key] if extraction.get(key) is not None else "ERROR") for key in error_list}  
            self.rhp = extraction["periodo_detenzione_raccomandato"]= "multiple"

        return extraction
 
    
 
    async def extract_deductables(self):
        """extracts the callable from the document
        looks if the word is in the document thats it

        Returns:
            dict(): dictionary containing the callable
        """
        try:
            booleans_to_check = {
                "callable": 0,
                "putable": 0,
                "unconditional_protection": 0,
                "memory": 0,
                "barrier_type": 0,
            }
            str_to_check={
                "importo_minimo": NA,
                "leva_cedolare":  NA,
                "cap":  NA,
                "leva_airbag": NA,
            }
            ret=self.extract_regex_text("bnp",0, booleans_to_check, str_to_check)
            
            if ret.get("barrier_type") == 1:
                ret["barrier_type"] = "Europea"
            else:
                ret["barrier_type"] = None
                
        except Exception as error:
            ret= {**booleans_to_check, **str_to_check}
            print("extract_deductable error" + repr(error))
            
        return ret
    
    async def extract_main_info(self):
        """extracts the main info from the table

        Args:
            table (pd.DataFrame): table containing the main info

        Returns:
            dict(): dictionary containing the main info
            
        """
        
        pages_for_main = [0]
        if len(self.di_tables_pages) > 3:
            pages_for_main.extend([-1, -2])
            
        extraction = await self.extract_from_multiple_tables(pages_for_main, ["main_info_bnp"])
        # extraction = clean_response_regex( "main_info", self.language, extraction)
        
        error_list = [
        "currency", "strike_date", "issue_date", "expiry_date", "final_valuation_date", "nominal",
        "market", "barrier", "unconditional_coupon_min", "conditional_coupon_min", "autocall",
        "autocall_barrier", "conditional_coupon_barrier", "issue_price_perc"
        ]
        extraction= {key: (extraction[key] if extraction.get(key) is not None else "ERROR") for key in error_list}

        return extraction
    
    async def extract_allegato(self,table_scadenza):
        """extracts the main info from the table

        Args:
            table (pd.DataFrame): table containing the main info

        Returns:
            dict(): dictionary containing the main info
            
        """
        
        try:
            extraction = dict()
            
            extraction.update(dict( await general_table_inspection(
                table_scadenza,
                "allegato_bnp_scadenza",
                self.file_id,
                language=self.language,
            )))
            
            # extraction = clean_response_regex( "allegato_bnp", self.language, extraction)
        except Exception as error:
            print("extract_allegato error" + repr(error))
            error_list = [
                "observation_coupon_date", "payment_coupon_date", "barrier_coupon", "unconditional_coupon",
                "conditional_coupon", "payment_callable_date", "observation_autocall_date", "barrier_autocall",
                "payment_autocall_date", "value_autocall"
            ]
            extraction= {key: (extraction[key] if extraction.get(key) is not None else "ERROR") for key in error_list}

        return extraction
    
    async def extract_sottostanti(self):
        """extracts the main info from the table

        Args:
            table (pd.DataFrame): table containing the main info

        Returns:
            dict(): dictionary containing the main info
        """
        
        pages_for_sottostanti = [0,1]
        if len(self.di_tables_pages) > 3:
            pages_for_sottostanti.extend([-1, -2])
            
            
        extraction = await self.extract_from_multiple_tables(pages_for_sottostanti, ["sottostante_bnp"])
        # extraction = clean_response_regex( "main_info", self.language, extraction)
        
        error_list = ["instrument_description", "instrument_bloombergcode", "instrument_isin"]
        extraction= {key: (extraction[key] if extraction.get(key) is not None else "ERROR") for key in error_list}

        return extraction
    
    async def extract_entryexit_management_costs(self):
        
        extraction = await self.extract_from_multiple_tables([1,2], ["costi_gestione", "costi_ingresso"])
        # extraction = clean_response_regex( "main_info", self.language, extraction)
        
        error_list = [
        "commissione_gestione", "commissione_transazione", "commissione_performance","costi_ingresso", "costi_uscita"
        ]
        extraction= {key: (extraction[key] if extraction.get(key) is not None else "ERROR") for key in error_list}

        return extraction
        
    
    async def extract_first_info(self, table):
        """extracts the main info from the table

        Args:
            table (pd.DataFrame): table containing the main info

        Returns:
            dict(): dictionary containing the main info
        """
        try:
            extraction = dict()
            extraction = await general_table_inspection(
                table,
                "first_info_bnp",
                self.file_id,
                language=self.language,
            )
            # extraction = clean_response_regex( "first_info_bnp", self.language, extraction)
        except Exception as error:
            print("extract_first_info error" + repr(error))
            error_list = [
                "isin", "issuer_desc"
            ]
            extraction= {key: (extraction[key] if extraction.get(key) is not None else "ERROR") for key in error_list}

        return extraction





    
    async def process(self):
        """main processor in different phases, first phases extracts the tables and general information,
        and target market, second phase extracts the rest of the fields.

        Returns:
            dict(filename,dict()): dictionary containing the results for the file
        """
        # FIRST STAGE: get tables and general information
        try:
            print("REAL START")
            tasks = []
            tasks.append(asyncio.create_task(self.get_tables()))
            tasks.append(asyncio.create_task(self.extract_general_data()))
            tasks.append(asyncio.create_task(self.extract_deductables()))

            await asyncio.wait(tasks, return_when=asyncio.ALL_COMPLETED)

            tables = tasks[0].result()
            basic_information = tasks[1].result()
            deductables = tasks[2].result()
        except Exception as error:
            print("first stage error" + repr(error))

        # SECOND STAGE: extract RIY, costs, commissions and performances
        try:
            tasks = []
            tasks.append(asyncio.create_task(self.extract_allegato(tables["allegato_scadenza"])))
            tasks.append(
                asyncio.create_task(self.extract_sottostanti())
            )
            tasks.append(
                asyncio.create_task(self.extract_main_info())
            )
            tasks.append(
                asyncio.create_task(self.extract_first_info(tables["first_info"]))
            )
            
            tasks.append(asyncio.create_task(self.extract_riy(2)))
            tasks.append(asyncio.create_task(self.extract_entryexit_management_costs()))
            tasks.append(asyncio.create_task(self.extract_performances(tables["performance"])))

            await asyncio.wait(tasks, return_when=asyncio.ALL_COMPLETED)

            allegato = tasks[0].result()
            sottostanti = tasks[1].result()
            main_info = tasks[2].result()
            first_info = tasks[3].result()
            riy = tasks[4].result()
            exit_entry_management_costs = tasks[5].result()
            performance = tasks[6].result()

        except Exception as error:
            print("second stage error" + repr(error))

        try:
            # Merge and orders all the results
            basic_information = dict(basic_information)
            
            allegato = dict(allegato)
            
            
            max_length = max((len(value) for value in allegato.values() if isinstance(value, list)), default=0)

            # Iterate through the dictionary and fill the arrays with 'N/A'
            for key, value in allegato.items():
                if isinstance(value, list):
                    # If the array is shorter than max_length, fill with 'N/A'
                    allegato[key] = value + ["N/A"] * (max_length - len(value))

            main_info = dict(main_info)
            
            deductables= dict(deductables)
            
            sottostanti = dict(sottostanti)
              
            performance= dict(performance)
            riy = dict(riy)
            exit_entry_management_costs = dict(exit_entry_management_costs)
            

            max_length = max((len(value) for value in sottostanti.values() if isinstance(value, list)), default=0)

            # Iterate through the dictionary and fill the arrays with 'N/A'
            for key, value in sottostanti.items():
                if isinstance(value, list):
                    # If the array is shorter than max_length, fill with 'N/A'
                    sottostanti[key] = value + ["N/A"] * (max_length - len(value))
            
            first_info = dict(first_info)

            filename = os.path.splitext(os.path.basename(self.doc_path))[0]

            api_costs = self._process_costs()

            # raccordo
            complete = self.raccorda(
                {
                    **deductables,
                    **basic_information,
                    **main_info,
                    **first_info,
                    
                },
                "bnp",
                keep=True,
            )
            complete2 = self.raccorda(
                {
                    "file_name": filename,
                    **performance,
                    **riy,
                    **exit_entry_management_costs,
                },
                "kid",
                keep=True,
            )

            with pd.ExcelWriter(
                "results\\6febbraio\\resultsmarco_{}.xlsx".format(os.path.basename(self.file_id)),
                engine="xlsxwriter",
            ) as excel_writer:
                # Write the first DataFrame to Sheet1
                results1 = pd.DataFrame(complete, index=[filename])
                results1.to_excel(
                    excel_writer, sheet_name="info_anagrafiche", header=True
                )
                
                
                results2 = pd.DataFrame(complete2, index=[filename])
                results2.to_excel(
                    excel_writer, sheet_name="performance", header=True
                )
                
                results3 = pd.DataFrame(self.raccorda(dict(sottostanti),"bnp", keep=True)).T
                results3.to_excel(excel_writer, sheet_name="sottostanti", header=True)

                if(allegato):
                    results5 = pd.DataFrame(self.raccorda(dict(allegato),"bnp", keep=True)).T
                    results5.to_excel(excel_writer, sheet_name="allegati", header=True)



                # Write the second DataFrame to Sheet2
                results4 = pd.DataFrame.from_dict(api_costs, orient="index")
                results4 = pd.concat(
                    [
                        pd.DataFrame([results4.columns], columns=results4.columns),
                        results4,
                    ]
                )
                results4.reset_index(inplace=True)
                results4.columns = ["API"] + list(results4.columns)[1:]
                results4.to_excel(
                    excel_writer, sheet_name="api costs", header=True, index=False
                )

        except Exception as error:
            print("dictionary error: " + repr(error))
            filename = os.path.splitext(os.path.basename(self.doc_path))[0]
            complete = None

        Models.clear_resources_file(filename)
        return complete
