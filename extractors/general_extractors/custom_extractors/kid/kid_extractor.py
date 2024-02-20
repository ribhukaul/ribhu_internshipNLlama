import asyncio
import re

from ...llm_functions import complex_table_inspection, general_table_inspection, llm_extraction, tag_only
from ...extractor import Extractor

from ...llm_functions import (
    llm_extraction_and_tag,
)
from .kid_utils import clean_response_regex, clean_response_strips


class KidExtractor(Extractor):

    def __init__(self, doc_path, predefined_language=False) -> None:
        super().__init__(doc_path, predefined_language)


    def get_tables(self):
        """calc table extractor, it extracts the three tables from the document asynchronously

        Returns:
            dict([pandas.dataframe]): tables as dataframe
        """
        try:
            performance_table,_ = self._extract_table("performance")
            costi_ingresso_table,_ = self._extract_table("costi_ingresso", black_list_pages=[0])
            costi_gestione_table,_ = self._extract_table("costi_gestione")
        except Exception as error:
            print("calc table error" + repr(error))
            error_list = [performance_table, costi_ingresso_table, costi_gestione_table]
            for i, key in enumerate(error_list):
                if not key:
                    error_list[i] = dict([("ERROR", "ERROR")])

        return dict(
            [
                ("costi_ingresso", costi_ingresso_table),
                ("costi_gestione", costi_gestione_table),
                ("performance", performance_table),
            ]
        )

    def extract_general_data(self):
        """
        Extract general data from the document. Namely RHP and SRI.


        Returns: dict(): data extracted
        """
        try:
            # extract and clean
            extraction = llm_extraction_and_tag(self.text, self.language, "general_info", self.file_id)
            extraction = clean_response_regex("general_info", self.language, extraction)
            extraction = dict(extraction)

            # REVIEW: ISIN EXTRACTION TO BE MOVED OUTSIDE?
            isin = self.extract_isin()
            extraction.update({"isin": isin})
            if (
                "periodo_detenzione_raccomandato" in extraction
                and extraction["periodo_detenzione_raccomandato"] != "-"
                and re.search(r"\d+", extraction["periodo_detenzione_raccomandato"])
            ):

                rhp_temp = extraction["periodo_detenzione_raccomandato"]
                number = re.search(r"\d+", rhp_temp).group(0)
                if re.search(r"(?i)mesi", rhp_temp):
                    extraction["periodo_detenzione_raccomandato"] = "1"
                else:
                    extraction["periodo_detenzione_raccomandato"] = str(int(number))

                self.rhp = extraction["periodo_detenzione_raccomandato"]
            else:
                self.rhp = "multiple"

        except Exception as error:
            print("extract general data error" + repr(error))
            error_list = ["isin", "indicatore_sintetico_rishio"]
            extraction = {key: (extraction[key] if extraction.get(key) is not None else "ERROR") for key in error_list}
            self.rhp = extraction["periodo_detenzione_raccomandato"] = "multiple"

        return extraction

    def extract_isin(self):
        to_search = self.text[0].page_content[20:1600]
        isin = re.search(r"[A-Z]{2}[A-Z0-9]{9}\d", to_search)
        return isin.group(0) if isin else "-"
    
    def extract_market(self, market_type="market"):
        """extracts market from the document

        Args:
            market_type (str, optional): type of market to extract. Defaults to "market".
                Can also be "maket_gkid".

        Returns:
            dict(): market extracted
        """
        market = None
        try:
            market = llm_extraction(self.text[0], market_type, self.file_id, self.language)
            # procedural cleaning
            market = clean_response_strips("market", self.language, market)

        except Exception as error:
            print("market extraction error" + repr(error))
            if not market:
                market = "ERROR"

        market = dict([("target_market", market)])
        return market

    #REVIEW: NEED TO UPLOAD TABLE AS DF
    def extract_riy(self, page=1):
        """extracts riy from the document

        Returns:
            dict(): riy extracted
        """
        try:
            # Select page with RIY
            extraction_riy = tag_only(self.text[page:], "riy", self.language, self.file_id, rhp=self.rhp)
            extraction_riy = clean_response_regex("riy", self.language, extraction_riy)
        except Exception as error:
            print("extract riy error" + repr(error))
            error_list = ["incidenza_costo_1", "incidenza_costo_rhp"]

            extraction_riy = {
                key: (extraction_riy[key] if extraction_riy.get(key) is not None else "ERROR") for key in error_list
            }

        return extraction_riy

    #REVIEW: NEED TO UPLOAD TABLE AS DF
    def extract_entryexit_costs(self, table):

        try:
            extraction = general_table_inspection(
                table,
                "costi_ingresso",
                self.file_id,
                language=self.language,
                add_text="estrai il valore % dopo {} anni".format(self.rhp),
            )
            extraction = clean_response_regex("costi_ingresso", self.language, extraction)
        except Exception as error:
            print("extract entry exit costs error" + repr(error))
            error_list = ["costi_ingresso", "costi_uscita"]
            extraction = {key: (extraction[key] if extraction.get(key) is not None else "ERROR") for key in error_list}

        return extraction

    # REVIEW: NEED TO UPLOAD TABLE AS DF
    def extract_management_costs(self, table):

        try:
            extraction = dict()
            extraction = general_table_inspection(
                table,
                "costi_gestione",
                self.file_id,
                language=self.language,
                add_text="estrai il valore % dopo {} anni".format(self.rhp),
            )
            extraction = clean_response_regex("costi_gestione", self.language, extraction)
        except Exception as error:
            print("extract management costs error" + repr(error))
            error_list = ["commissione_gestione", "commissione_transazione", "commissione_performance"]
            extraction = {key: (extraction[key] if extraction.get(key) is not None else "ERROR") for key in error_list}

        return extraction

    def extract_performances(self, table):
        """extracts performances from scenarios in the document

        Args:
            table (pandas.dataframe): table containing the performances

        Returns:
            dict(): dict containing the performances
        """
        performance = dict()
        try:
            performance = dict(
                complex_table_inspection(
                    table,
                    self.rhp,
                    "performance",
                    self.file_id,
                    direct_tag=True,
                    language=self.language,
                )
            )

            morte = dict(
                [
                    ("scenario_morte_1", performance.get("scenario_morte_1")),
                    ("scenario_morte_rhp", performance.get("scenario_morte_rhp")),
                ]
            )
            performance = clean_response_regex("performance", self.language, performance)
            morte = clean_response_regex("performance_morte", self.language, morte)
            performance["scenario_morte_1"] = morte.get("scenario_morte_1")
            performance["scenario_morte_rhp"] = morte.get("scenario_morte_rhp")
        except Exception as error:
            print("extract performances error" + repr(error))
            error_list = [
                "scenario_morte_1",
                "scenario_morte_rhp",
                "stress_return",
                "sfavorevole_return",
                "moderato_return",
                "favorable_return",
                "stress_return_rhp",
                "sfavorevole_return_rhp",
                "moderato_return_rhp",
                "favorable_return_rhp",
            ]
            performance = {
                key: (performance[key] if performance.get(key) is not None else "ERROR") for key in error_list
            }

        return performance


if __name__ == "__main__":
    # testing
    doc_folder = "data\C\MEDIOLANUM\MYLIFEPIC_FR0011660851.pdf"
    kid_extractor = KidExtractor(doc_folder)
