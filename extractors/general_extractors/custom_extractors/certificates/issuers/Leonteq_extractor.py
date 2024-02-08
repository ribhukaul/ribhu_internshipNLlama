
from numpy import extract
from extractors.general_extractors.custom_extractors.certificates.derivati_extractor import DerivatiKidExtractor
import asyncio
import os
import re
import pandas as pd
from extractors.azure.document_intelligence import get_tables_from_doc
from extractors.general_extractors.llm_functions import (
    llm_extraction_and_tag,
)
from extractors.general_extractors.llm_functions import complex_table_inspection, general_table_inspection, llm_extraction, tag_only
    

    
from extractors.models import Models
from extractors.general_extractors.utils import (
    select_desired_page,
    select_desired_table_only_header,
    select_desired_table,
)
from extractors.general_extractors.custom_extractors.kid.kid_utils import (
    clean_response_regex,
    clean_response_strips,
)
from extractors.utils import is_in_text, upload_df_as_excel
from ..certificates_config.cert_cleaning import header_mappings, regex_callable
from extractors.general_extractors.config.prompt_config import word_representation
    


class LeonteqDerivatiKidExtractor(DerivatiKidExtractor):
    
    def __init__(self, doc_path) -> None:
        self.doc_path = doc_path
        super().__init__(doc_path, "it")
        
    
    
    
    async def extract_general_data(self):
        """
        Extract general data from the document (ISIN, RHP, SRI).

        Returns: dict(): data extracted
        """
        try:
            # extract and clean
            extraction = llm_extraction_and_tag(
                [self.text[0]], self.language, "general_info_certificati", self.file_id
            )
            extraction = dict(extraction)
            isin=self.extract_isin()
            extraction.update({"isin": isin})

            """extraction = clean_response_regex(
                "general_info_certificati", self.language, extraction
            )"""

        except Exception as error:
            print("extract general data error" + repr(error))
            error_list =["isin","descrizione","emittente"]
            extraction= {key: (extraction[key] if extraction.get(key) is not None else "ERROR") for key in error_list}  

        return extraction

    def extract_isin(self):
        """extract isin with regex

        Returns:
            str: isin or -
        """
        to_search = self.text[0].page_content[:1600]
        isin = re.search(r"[A-Z]{2}[A-Z0-9]{9}\d", to_search)
        return isin.group(0) if isin else "-"

    async def extract_cedola(self, table):
        """extracts the cedola from the table

        Args:
            table (pd.DataFrame): table containing the cedola

        Returns:
            dict(): dictionary containing the cedola
        """
        try:
            extraction = dict()
            if isinstance(table, str):
                extraction = self.regex_cedola(table)
            else:
                # kind of complex table extraction without tagging
                table = upload_df_as_excel(table)
                extraction = await general_table_inspection(
                    table,
                    "cedola",
                    self.file_id,
                    language=self.language,
                )
        except Exception as error:
            print("extract_cedola error" + repr(error))
            extraction = {"cedola": "ERROR"}

        return extraction

    def regex_cedola(self, og_string):
        """splits dense text into a list of dictionaries

        Args:
            og_string (str): the entire page as a string

        Returns:
            dict: cedole
        """
        # brace yourself, regex is coming
        # why it is so complicated? because it is a dense text
        # idea is to cut before and after, extract headers, split by indexes and create dictionary
        # if changing, go look at what passes around
        names = []
        first_divide = re.split(r"▪", og_string)  # first split
        if len(first_divide) == 1:
            return [{"cedola": "not found"}]

        last_data = re.search(
            r"\d{1,2}[/\-.]\d{1,2}[/\-.]\d{1,4}", first_divide[-1]
        )  # last date
        first_divide = first_divide[0:-1]  # for sure dont need other text

        found_name = re.search(r"data.*$", first_divide[0], re.IGNORECASE)
        if found_name:
            names.append(
                "Data " + found_name.group(0)
            )  # get first header, the worst one
        first_divide = first_divide[1:]

        while not re.search(
            "1[/\-.]\d+[/\-.]\d+[/\-.]\d+", first_divide[0]
        ):  # remove and append other headers
            names.append(first_divide[0])
            first_divide = first_divide[1:]

        string = "▪".join(first_divide)  # remerge clean
        ret = []

        first_date = re.findall(
            "(\d{1,2}[/\-.](?:\n)?\d{1,2}[/\-.]\d{1,2}[/\-.]\d{1,4})", string
        )  # resplit
        names.append(
            first_divide[0].replace(first_date[0], "")
        )  # get last header(is attached to date)
        # Print the result

        names = self.clean_names(names)  # clean them up

        for idx, _ in enumerate(first_date):
            first_date[idx] = first_date[idx][
                first_date[idx].find(".") + 1 :
            ]  # clean first date
        divided = re.split(
            "\d{1,2}[/\-.](?:\n)?\d{1,2}[/\-.]\d{1,2}[/\-.]\d{1,4}", string
        )

        for i, single in enumerate(
            divided[1:], start=1
        ):  # split again and create dictionary
            more_divided = re.split("▪", single)
            extracted = dict()
            for idx, value in enumerate(more_divided):
                if idx == 0:  # first value is date(the one we extracted separatly)
                    value = first_date[i - 1] if 0 <= i - 1 < len(first_date) else "ERR"
                key = names[idx] if 0 <= idx < len(names) else "name not found"
                extracted.update({key: value})
            ret.append(extracted)
        if last_data:
            ret[-1].update({names[-1]: last_data.group(0)})  # add last date
        return ret

    def clean_names(self, names):
        """cleans the names of the headers

        Args:
            names ([str]): the uncleaned names

        Returns:
            [str]: the cleaned names
        """
        for idx, name in enumerate(names):
            for search, value in header_mappings.items():
                if re.search(search, name, re.IGNORECASE):
                    names[idx] = value
                    break
        return names

    async def extract_sottostanti(self, table):
        """extracts the sottostanti from the table

        Args:
            table (pd.DataFrame): table containing the sottostanti

        Returns:
            dict(): dictionary containing the sottostanti
            careful, first extractions are arrays, second are single data
        """
        extraction = dict()
        try:
            tasks=[]
            tasks.append(asyncio.create_task(general_table_inspection(
                table,
                "sottostanti",
                self.file_id,
                language=self.language,
            )))
            tasks.append(asyncio.create_task(general_table_inspection(  # extracts data in the headers
                        table.iloc[0],
                        "sottostanti_header",
                        self.file_id,
                        language=self.language,
                    )))
            await asyncio.wait(tasks, return_when=asyncio.ALL_COMPLETED)
            
            extraction = tasks[0].result()            
            extraction = dict(extraction)
            extraction.update(
                dict(tasks[1].result())  # extracts data in the headers
            )
        
        except Exception as error:
            print("extract_sottostanti first phase error" + repr(error))
        try:
            extraction = dict(extraction)  # ik its ugly, cant do better
            found_liv = "N/A"
            match = None

            # Iterate backwards through the first row

            for cell in table.iloc[0][::-1]:
                if cell and re.search(r"coupon.{0,4}trigge", cell, re.IGNORECASE):
                    match = re.search(r"\d+\.?\d* ?%", cell)
                    if match:
                        found_liv = match.group(0)
                        break
            extraction.update({"liv_att_cedola_perc": found_liv})
            
        except Exception as error:
            print("extract_sottostanti second phase error" + repr(error))

        return extraction

    async def extract_main_info(self, table):
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
                "main_info",
                self.file_id,
                language=self.language,
            )
            # extraction = clean_response_regex( "main_info", self.language, extraction)
        except Exception as error:
            print("extract_main_info error" + repr(error))
            error_list = [
            "valuta", "data_emissione", "periodo", "data_rimborso", "prezzo",
            "liv_fix_fin", "quotazione", "perf_peg", "inv_min", "garanzia_min_perc",
            "data_fix_ini", "data_negoziazione", "data_fix_fin", "liv_fix_ini",
            "mod_pagamento", "tasso_cedola_cond", "cedola_garantita_perc", "rischio_cambio",
            "importo_rimborso", "importo_protezione_capitale", "partecipazione"
            ]
            extraction= {key: (extraction[key] if extraction.get(key) is not None else "ERROR") for key in error_list}

        return extraction

    async def fill_tables(self, page):
        """experimental for faster runs, fills the tables in the document asynchronously all in one

        Args:
            page (_type_): _description_
        """
        fill = get_tables_from_doc(
            self.doc_path, specific_pages=page, language=self.language
        )

        self.di_tables_pages[page-1] = fill

    async def get_tables(self):
        """calc table extractor, it extracts the three tables from the document asynchronously

        Returns:
            dict([pandas.dataframe]): tables as dataframe
        """
        try:
            tasks = []
            tasks.append(asyncio.create_task(self.fill_tables(1)))
            tasks.append(asyncio.create_task(self.fill_tables(2)))

            await asyncio.wait(tasks, return_when=asyncio.ALL_COMPLETED)

            sottostanti_table = self._extract_table_sottostanti(
                "sottostanti", api_version="2023-10-31-preview"
            )
            main_info_table = self._extract_table("main_info")

            cedola_table = self._extract_table("cedola", black_list_pages=[1])
            cedola_table_2 = self._extract_table("cedola", black_list_pages=[0])

            # Check the validity of each table
            cedola_valid = not (
                cedola_table.equals(main_info_table)
                or cedola_table.equals(sottostanti_table)
            ) and (
                "cedola_table" in locals() and isinstance(cedola_table, pd.DataFrame)
            )
            cedola2_valid = not (
                cedola_table_2.equals(main_info_table)
                or cedola_table_2.equals(sottostanti_table)
            ) and (
                "cedola_table_2" in locals()
                and isinstance(cedola_table_2, pd.DataFrame)
                and not re.search(
                    r"detenzion", cedola_table_2.iloc[0, 0], re.IGNORECASE
                )
            )
            if not cedola_valid and not cedola2_valid:
                # No valid table found, concatenate page contents
                cedola_table = (
                    str(getattr(self.text[0], "page_content", ""))
                    + " "
                    + str(getattr(self.text[1], "page_content", ""))
                )
            elif cedola_valid and cedola2_valid:
                # Both tables are valid, concatenate them
                try:
                    while re.search(r"[A-Za-z].*[A-Za-z]", cedola_table_2.iloc[0, 0]):
                        cedola_table_2 = cedola_table_2.iloc[1:, :]
                    cedola_table = pd.concat(
                        [cedola_table, cedola_table_2], ignore_index=True
                    )
                except Exception as error:
                    print("more lines ignored:" + self.file_id)

            elif not cedola_valid and cedola2_valid:
                # Only the second table is valid
                cedola_table = cedola_table_2

        except Exception as error:
            print("get_tables error" + repr(error))
            tables = [sottostanti_table, main_info_table, cedola_table]
            for i, table in enumerate(tables):
                if not table:
                    tables[i] = None

        return dict(
            [
                ("cedola", cedola_table),
                ("sottostanti", sottostanti_table),
                ("main_info", main_info_table),
            ]
        )

    def _extract_table_sottostanti(
        self, type, pages_to_check=[0, 1], api_version="2023-10-31-preview"
    ):  # change from normal is select_desired_table_only_header
        """General table extractor, given a table type it first finds the page within
        the document where the table is located, it then extracts all the tables from
        that page and returns the one with the most occurrences of the words of the table
        type.

        Args:
           type (str): type of table to extract, used to get configuration.
           black_list_pages (int[], optional): Pages to ignore. Defaults to [].

        Returns:
            pandas.DataFrame: dataframe containing the table.
        """
        try:
            # Select page with table
            keywords = word_representation[self.language][type]
            tables = []
            # Get all the tables from the page
            if self.di_tables_pages is not None and not all(
                page in self.di_tables_pages for page in pages_to_check
            ):
                for page in [
                    page
                    for page in pages_to_check
                    if str(page) not in self.di_tables_pages.keys()
                ]:
                    page_num = int(page) + 1
                    new_tables = get_tables_from_doc(
                        self.doc_path,
                        specific_pages=page_num,
                        language=self.language,
                        api_version=api_version,
                    )
                    self.di_tables_pages[page] = new_tables
                    tables.extend(table for table in new_tables)
            else:
                for page in pages_to_check:
                    tables.extend(table for table in self.di_tables_pages[page])

            # Select the right table
            table_nr = select_desired_table_only_header(tables, keywords)
            return tables[int(table_nr)]
        except Exception as error:
            print("extract table error" + repr(error))
            return None
            # @ELIA?
            # exreturn = dict()
            # for table in tables:
            #     exreturn.update(table)

    async def extract_callable(self):
        """extracts the callable from the document
        looks if the word is in the document thats it

        Returns:
            dict(): dictionary containing the callable
        """
        is_callable = {
            "autocallable": 0,
            "softcallable": 0,
            "putable": 0,
            "effetto_memoria": 0,
        }
        is_callable = self.extract_regex_text("leonteq",0, is_callable)
                
        return is_callable

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
            tasks.append(asyncio.create_task(self.extract_callable()))

            await asyncio.wait(tasks, return_when=asyncio.ALL_COMPLETED)

            tables = tasks[0].result()
            basic_information = tasks[1].result()
            is_callable = tasks[2].result()
        except Exception as error:
            print("first stage error" + repr(error))

        # SECOND STAGE: extract RIY, costs, commissions and performances
        try:
            tasks = []
            tasks.append(asyncio.create_task(self.extract_cedola(tables["cedola"])))
            tasks.append(
                asyncio.create_task(self.extract_sottostanti(tables["sottostanti"]))
            )
            tasks.append(
                asyncio.create_task(self.extract_main_info(tables["main_info"]))
            )

            await asyncio.wait(tasks, return_when=asyncio.ALL_COMPLETED)

            cedola = tasks[0].result()
            sottostanti = tasks[1].result()
            main_info = tasks[2].result()

        except Exception as error:
            print("second stage error" + repr(error))

        try:
            # Merge and orders all the results
            basic_information = dict(basic_information)
            is_callable = dict(is_callable)
            exploded_cedola = dict()
            if isinstance(tables["cedola"], str):
                for ced in cedola:
                    for key, value in ced.items():
                        exploded_cedola.setdefault(key, []).append(value)
            else:
                for ced in cedola:
                    exploded_cedola.update({ced[0]: ced[1]})

            max_length = max(
                (len(value) for value in exploded_cedola.values() if isinstance(value, list)), default=0
            )
            # Iterate through the dictionary and fill the arrays with 'N/A'
            for key, value in exploded_cedola.items():
                if isinstance(value, list):
                    # If the array is shorter than max_length, fill with 'N/A'
                    exploded_cedola[key] = value + ["N/A"] * (max_length - len(value))

            max_length = max((len(value) for value in sottostanti.values() if isinstance(value, list)), default=0)

            # Iterate through the dictionary and fill the arrays with 'N/A'
            for key, value in sottostanti.items():
                if isinstance(value, list):
                    # If the array is shorter than max_length, fill with 'N/A'
                    sottostanti[key] = value + ["N/A"] * (max_length - len(value))

            main_info = dict(main_info)

            filename = os.path.splitext(os.path.basename(self.doc_path))[0]

            api_costs = self._process_costs()

            # raccordo
            complete = self.raccorda(
                {
                    **is_callable,
                    **basic_information,
                    **main_info,
                },
                "leonteq",
                keep=True,
            )

            with pd.ExcelWriter(
                "results\\30gennaio\\resultsmarco_{}.xlsx".format(os.path.basename(self.file_id)),
                engine="xlsxwriter",
            ) as excel_writer:
                # Write the first DataFrame to Sheet1
                results1 = pd.DataFrame(complete, index=[filename]).T
                results1.to_excel(
                    excel_writer, sheet_name="info_anagrafiche", header=True
                )

                results2 = pd.DataFrame(self.raccorda(exploded_cedola,"derivati", keep=True))
                results2.to_excel(
                    excel_writer, sheet_name="date cedole autocall", header=True
                )

                # Write the second DataFrame to Sheet2
                results3 = pd.DataFrame(self.raccorda(dict(sottostanti),"derivati", keep=True)).T
                results3.to_excel(excel_writer, sheet_name="sottostanti", header=True)

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
