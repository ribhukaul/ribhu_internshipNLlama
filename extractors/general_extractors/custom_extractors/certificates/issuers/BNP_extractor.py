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
from extractors.general_extractors.utils import select_desired_page
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
        fill = get_tables_from_doc(self.doc_path, specific_pages=page, language=self.language)

        self.di_tables_pages[str(page - 1)] = fill
        

    async def get_tables(self):
        """calc table extractor, it extracts the three tables from the document asynchronously

        Returns:
            dict([pandas.dataframe]): tables as dataframe
        """
        try:
            tasks = []
            for i in range(1, min([len(self.text) + 1, 6])):
                tasks.append(asyncio.create_task(self.fill_tables(i)))

            await asyncio.wait(tasks, return_when=asyncio.ALL_COMPLETED)
            
            

            performance_table = self._extract_table("performance", black_list_pages=[0])

        except Exception as error:
            print("get_tables error" + repr(error))
            tables = [ performance_table]
            for i, table in enumerate(tables):
                if not table:
                    tables[i] = None

        return dict(
            [
                ("performance", performance_table),
            ]
        )

    async def extract_general_data(self):
        """
        Extract general data from the document (ISIN, RHP, SRI).

        Returns: dict(): data extracted
        """
        try:
            extraction = {"description": extract_between(self.text[0].page_content[:800], "Prodotto", "codice")}
            extraction.update(
                dict(llm_extraction_and_tag([self.text[1]], self.language, "general_info_bnp", self.file_id))
            )
            extraction = dict(extraction)
            if extraction.get("description") and is_in_text("airbag", (extraction.get("description"))):
                extraction["airbag"] = 1
            else:
                extraction["airbag"] = 0

            if "periodo_detenzione_raccomandato" in extraction:
                self.rhp = extraction["periodo_detenzione_raccomandato"]
            else:
                self.rhp = "multiple"

        except Exception as error:
            print("extract general data error" + repr(error))
            error_list = ["description", "airbag", "indicatore_sintetico_rishio"]
            extraction = {key: (extraction[key] if extraction.get(key) is not None else "ERROR") for key in error_list}
            self.rhp = extraction["periodo_detenzione_raccomandato"] = "multiple"

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
                "autocallable": 0,
                "unconditional_protection": 0,
                "memory": 0,
                "barrier_type": 0,
            }
            str_to_check = {
                "importo_minimo": NA,
                "leva_cedolare": NA,
                "cap": NA,
                "leva_airbag": NA,
            }
            ret = self.extract_regex_text("bnp", 0, booleans_to_check, str_to_check)

            if ret.get("barrier_type") == 1:
                ret["barrier_type"] = "Europea"
            else:
                ret["barrier_type"] = None

        except Exception as error:
            ret = {**booleans_to_check, **str_to_check}
            print("extract_deductable error" + repr(error))

        return ret

    async def extract_main_info(self):
        """extracts the main info from the table

        Args:
            table (pd.DataFrame): table containing the main info

        Returns:
            dict(): dictionary containing the main info

        """

        pages_for_main = [0, 1]

        extraction = await self.extract_from_multiple_tables(pages_for_main, ["main_info_bnp"])
        # extraction = clean_response_regex( "main_info", self.language, extraction)

        error_list = [
    "currency","strike_date","issue_date","expiry_date","final_valuation_date","nominal",
    "market","barrier","conditional_coupon_barrier","issue_price_perc","observation_coupon_date",
    "payment_coupon_date","unconditional_coupon","conditional_coupon","payment_callable_date",
    "observation_autocall_date","barrier_autocall","payment_autocall_date","value_autocall"]

        extraction = {key: (extraction[key] if extraction.get(key) is not None else "ERROR") for key in error_list}

        return extraction

    async def extract_allegato(self):
        """Extracts the main info from the table

        Args:
            table (pd.DataFrame): table containing the main info

        Returns:
            dict: Dictionary containing the main info

        """                
        error_list = [
            "observation_coupon_date", "payment_coupon_date", "barrier_coupon", "unconditional_coupon",
            "conditional_coupon", "payment_callable_date", "observation_autocall_date", "barrier_autocall",
            "payment_autocall_date", "value_autocall"
        ]
        
        extraction = {}

        try:
            if len(self.di_tables_pages) > 3:
                # Extract tables with specified black list pages
                allegato_scadenza = self._extract_table("allegato_bnp_scadenza", black_list_pages=[0,1])
                allegato_premio = self._extract_table("allegato_bnp_premio", black_list_pages=[0,1])

                # Inspect general tables and update extraction dictionary
                extraction.update(
                    await general_table_inspection(allegato_scadenza, "allegato_bnp_scadenza", self.file_id, language=self.language)
                )
                extraction.update(
                    await general_table_inspection(allegato_premio, "allegato_bnp_premio", self.file_id, language=self.language)
                )

                # Define error list


                # Update extraction with '-' if value is ['not found']
            extraction = {
                key: (extraction[key] if extraction.get(key) != ["not found"] and extraction.get(key) is not None else ["-"]) for key in error_list
            }

        except Exception as error:
            print(f"extract_allegato error: {error}")
            
            # Handle error by setting extraction values to "ERROR" if key is not found
            extraction = {key: (extraction[key] if extraction.get(key) is not None else "ERROR") for key in error_list}

        return extraction

    async def extract_sottostanti(self):
        """extracts the main info from the table

        Args:
            table (pd.DataFrame): table containing the main info

        Returns:
            dict(): dictionary containing the main info
        """
        #TODO: make better
        sottostante = None
        
        sottostante = self._extract_table_only_header("sottostante_bnp", pages_to_check=[0,1])

        extraction = await general_table_inspection(sottostante, "sottostante_bnp", self.file_id, language=self.language)
        
        extraction= dict(extraction)
        if len(self.di_tables_pages) > 3 and (extraction.get("instrument_bloombergcode") == ['not found'] or re.search("allegat",extraction.get("instrument_isin")[0], re.IGNORECASE) ):
            sottostante = self._extract_table_only_header("sottostante_bnp", list(range(3, len(self.di_tables_pages))))

            extraction = await general_table_inspection(sottostante, "sottostante_bnp", self.file_id, language=self.language)
        # extraction = clean_response_regex( "main_info", self.language, extraction)

        error_list = ["instrument_description", "instrument_bloombergcode", "instrument_isin"]
        extraction=dict(extraction)
        extraction = {key: (extraction[key] if extraction.get(key) is not None else "ERROR") for key in error_list}

        return extraction

    async def extract_entryexit_management_costs(self):

        extraction = await self.extract_from_multiple_tables([1, 2], ["costi_gestione", "costi_ingresso"])
        # extraction = clean_response_regex( "main_info", self.language, extraction)

        error_list = [
            "commissione_gestione",
            "commissione_transazione",
            "commissione_performance",
            "costi_ingresso",
            "costi_uscita",
        ]
        extraction = {key: (extraction[key] if extraction.get(key) is not None else "ERROR") for key in error_list}

        return extraction

    async def extract_first_info(self):
        """extracts the main info from the table

        Args:
            table (pd.DataFrame): table containing the main info

        Returns:
            dict(): dictionary containing the main info
        """
        extraction = dict()
        try:
            extraction=llm_extraction_and_tag([self.text[0]], self.language, "first_info_bnp", self.file_id)

            # extraction = clean_response_regex( "first_info_bnp", self.language, extraction)
        except Exception as error:
            print("extract_first_info error" + repr(error))
            error_list = ["isin", "issuer_desc"]
            extraction = {key: (extraction[key] if extraction.get(key) is not None else "ERROR") for key in error_list}

        return extraction
    
    
    def fill_array(self, dictionary):

        max_length = max((len(value) for value in dictionary.values() if isinstance(value, list)), default=0)
        # Iterate through the dictionary and fill the arrays with '-'
        for key, value in dictionary.items():
            if isinstance(value, list):
                # If the array is shorter than max_length, fill with '-'
                dictionary[key] = value + ["-"] * (max_length - len(value))

        return dictionary

    def _write_to_excel(self, complete, complete2, allegato, sottostanti, api_costs, filename):
        
        with pd.ExcelWriter(
            "results\\13febbraio\\resultsmarco_{}.xlsx".format(
                os.path.basename(self.file_id)
            ),
            engine="xlsxwriter",
        ) as excel_writer:
            # Write the first DataFrame to Sheet1
            results1 = pd.DataFrame(complete, index=[filename]).T
            results1.to_excel(excel_writer, sheet_name="info_anagrafiche", header=True)

            results2 = pd.DataFrame(complete2, index=[filename]).T
            results2.to_excel(excel_writer, sheet_name="performance", header=True)

            results3 = pd.DataFrame(self.raccorda(dict(sottostanti), "bnp", keep=True)).T
            results3.to_excel(excel_writer, sheet_name="sottostanti", header=True)

            if allegato:
                results5 = pd.DataFrame(self.raccorda(dict(allegato), "bnp", keep=True)).T
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
            results4.to_excel(excel_writer, sheet_name="api costs", header=True, index=False)

        


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
            
            tables, basic_information, deductables = [task.result() for task in tasks]
            
        except Exception as error:
            print("first stage error" + repr(error))

        # SECOND STAGE: extract RIY, costs, commissions and performances
        try:
            tasks = []
            tasks.append(asyncio.create_task(self.extract_allegato()))
            tasks.append(asyncio.create_task(self.extract_sottostanti()))
            tasks.append(asyncio.create_task(self.extract_main_info()))
            tasks.append(asyncio.create_task(self.extract_first_info()))

            tasks.append(asyncio.create_task(self.extract_riy(2)))
            tasks.append(asyncio.create_task(self.extract_entryexit_management_costs()))
            tasks.append(asyncio.create_task(self.extract_performances(tables["performance"])))

            await asyncio.wait(tasks, return_when=asyncio.ALL_COMPLETED)

            allegato, sottostanti, main_info, first_info, riy, exit_entry_management_costs, performance = [task.result() for task in tasks]

        except Exception as error:
            print("second stage error" + repr(error))

        try:
            # Merge and orders all the results
            
            allegato=self.fill_array(dict(allegato))

            sottostanti=self.fill_array(dict(sottostanti))

            filename = os.path.splitext(os.path.basename(self.doc_path))[0]

            api_costs = self._process_costs()

            # raccordo
            complete = self.raccorda(
                {
                    **dict(deductables),
                    **dict(basic_information),
                    **dict(main_info),
                    **dict(first_info),
                },
                "bnp",
                keep=True,
            )
            
            complete2 = self.raccorda(
                {
                    "file_name": filename,
                    **dict(performance),
                    **dict(riy),
                    **dict(exit_entry_management_costs),
                },
                "kid",
                keep=True,
            )
            
            self._write_to_excel(complete, complete2, allegato, sottostanti, api_costs, filename)


        except Exception as error:
            print("dictionary error: " + repr(error))
            filename = os.path.splitext(os.path.basename(self.doc_path))[0]
            complete = None

        Models.clear_resources_file(filename)
        return complete
