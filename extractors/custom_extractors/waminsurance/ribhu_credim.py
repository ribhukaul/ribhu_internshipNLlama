import os # Added to aid in assigning the correct file number to the extracted data 
from extractors.general_extractors.config.prompt_config import prompts, table_schemas, word_representation
from extractors.general_extractors.utils import select_desired_page
from extractors.models import Models
from extractors.general_extractors.custom_extractors.kid.kid_extractor import KidExtractor
from extractors.general_extractors.llm_functions import complex_table_inspection
from extractors.general_extractors.custom_extractors.kid.kid_utils import clean_response_regex
import pandas as pd
import os

class WamInsuranceRibhuExtractor(KidExtractor):

    def __init__(self, doc_path) -> None:
        self.doc_path = doc_path
        super().__init__(doc_path, "it")
    

#  # method to get Composizione dei costi
    def get_tables1(self):
        """Table extractor, it extracts the table for 'Composizione dei costi' from the document asynchronously

        Returns:
        dict([pandas.dataframe]): tables as dataframe
        """
        try:
            cost_composition_table, _ = self._extract_table("costi_ingresso")
        except Exception as error:
            print("table extraction error" + repr(error))
            cost_composition_table = None  # Assign None if an error occurs

        # Check if the table was successfully extracted
        if cost_composition_table is None:
            return {"costi_ingresso": dict([("ERROR", "ERROR")])}
        else:
            return {"costi_ingresso": cost_composition_table}
        


        
# Method to get performance

    def get_tables(self):
        """calc table extractor, it extracts the three tables from the document asynchronously

        Returns:
            dict([pandas.dataframe]): tables as dataframe
        """
        try:
            performance_table,_ = self._extract_table("performance")

        except Exception as error:
            print("calc table error" + repr(error))
            error_list = [performance_table]
            for i, key in enumerate(error_list):
                if not key:
                    error_list[i] = dict([("ERROR", "ERROR")])

        return dict(
            [
                ("performance", performance_table),
            ]
        )


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
                    "performance_credem",
                    self.file_id,
                    direct_tag=True,
                    language=self.language,
                )
            )

            performance = clean_response_regex("performance", self.language, performance)
        except Exception as error:
            print("extract performances error" + repr(error))
            error_list = [
                "moderato_return_rhp",
                "favorable_return_rhp",
            ]
            performance = {
                key: (performance[key] if performance.get(key) is not None else "ERROR") for key in error_list
            }

        return performance
    



    def process1(self):
        """
        Main processor to extract commission management and entry cost data from the document.
        Returns:
        dict: A dictionary containing the filename and extracted data.
        """
        
        try:
            # First, extract tables
            tables_result = self.get_tables1()
            # Attempt to retrieve 'costi_ingresso' as a DataFrame
            cost_table_df = tables_result.get('costi_ingresso')

            # Define function parameters for threading, now with direct access to the DataFrame
            functions_parameters = {
                "gestione_commissioni": {"function": self.extract_commissioni_gestione1},
                "costi_ingresso_e_uscita": {"function": self.extract_costi_ingresso_e_uscita, "args": {"cost_table": cost_table_df}}
            }

            # Execute the threaded function calls, gestione_commissioni does not need the table
            result1 = self.threader(functions_parameters)

            filename = os.path.basename(self.doc_path)

            # Check for error in 'costi_ingresso_e_uscita' and run alternative method if needed
            if 'ERROR' in result1.get('costi_ingresso_e_uscita', {}):
                result1['costi_ingresso_e_uscita'] = self.extract_costi_ingresso_e_uscita1()

            # Compile the results into a structured dictionary
            return {
                "filename": filename,
                "data": result1  # Including the result under a 'data' key for clarity
            }

        except Exception as error:
            print(f"Error during commission management data extraction: {repr(error)}")
            return {
                "filename": os.path.basename(self.doc_path),
                "data": {}
            }

    

    def process2(self): # A variation of process1 method to rather work on a pandas df instead of a pdf
        """
        Main processor to extract commission management and entry cost data from the document.
        Returns:
        dict: A dictionary containing the filename and extracted data.
        """
            
        try:
            # First, extract tables
            tables_result = self.get_tables1()
            # Attempt to retrieve 'costi_ingresso' as a DataFrame
            cost_table_df = tables_result.get('costi_ingresso')

            # Define function parameters for threading, now with direct access to the DataFrame
            functions_parameters = {
                "gestione_commissioni": {"function": self.extract_commissioni_gestione1},
                "costi_ingresso_e_uscita": {"function": self.extract_costi_ingresso_e_uscita, "args": {"cost_table": cost_table_df}}
            }

            # Execute the threaded function calls, gestione_commissioni does not need the table
            result1 = self.threader(functions_parameters)

            filename = os.path.basename(self.doc_path)

            # Compile the results into a structured dictionary
            return {
                "filename": filename,
                "data": result1  # Including the result under a 'data' key for clarity
            }

        except Exception as error:
            print(f"Error during commission management data extraction: {repr(error)}")
            return {
                "filename": os.path.basename(self.doc_path),
                "data": {}
            }

    
    def process3(self): # Defined by Ribhu
        """
        Main processor to extract commission management and entry cost data from the document.

        Returns:
            dict: A dictionary containing the filename and extracted data.
        """
        
        try:
            # Define function parameters for threading
            functions_parameters = {
                #"tables": {"function":self.get_tables1},
                "gestione_commissioni": {"function": self.extract_commissioni_gestione1},
                "costo_entrata_e_uscita": {"function": self.extract_costi_ingresso_e_uscita1},
            }

            # Execute the threaded function calls
            result1 = self.threader(functions_parameters)
            

            
            filename =  os.path.basename(self.doc_path) 

            # Compile the results into a structured dictionary
            return {
                "filename": filename,
                "data": result1  # Including the result under a 'data' key for clarity
            }

        except Exception as error:
            print(f"Error during commission management data extraction: {repr(error)}")
            return {
                "filename": os.path.basename(self.doc_path),
                "data": {}
            }

        
        

    def process(self):
        """main processor in different phases, first phases extracts the tables and general information,
        and target market, second phase extracts the rest of the fields.

        Returns:
            dict(filename,dict()): dictionary containing the results for the file
        """
        # FIRST STAGE: get tables and general information
        try:
      
            functions_parameters = {
                "tables": {"function":self.get_tables}, 
                "basic_information": {"function":self.extract_general_data}, # method from class KidExtractor 
                }
            results = self.threader(functions_parameters)

            tables = results["tables"]
            basic_information = results["basic_information"]

        except Exception as error:
            print("first stage error" + repr(error))

        # SECOND STAGE: extract RIY, costs, commissions and performances
        try:
            functions_parameters = {
                "riy": {"function":self.extract_riy_small}, 
                "performance": {"function":self.extract_performances, "args":{"table":tables["performance"]}}
                }
            results = self.threader(functions_parameters)
            riy = results["riy"]
            performance = results["performance"]       

        except Exception as error:
            print("second stage error" + repr(error))

        try:
            
            # REVIEW: what name do they need?
            filename = os.path.splitext(os.path.basename(self.doc_path))[0]

            api_costs = self._process_costs()

            complete = self.create_output(
                "waminsurance",
                "kidcredem",
                {
                    "file_name": filename,
                    **dict(basic_information),
                    **dict(performance),
                    **dict(riy),
                    "api_costs": api_costs,
                }
   
            )

        except Exception as error:
            print("dictionary error" + repr(error))
            filename = os.path.splitext(os.path.basename(self.doc_path))[0]
            complete = dict([(filename), dict()])

        print(complete)
        Models.clear_resources_file(filename)

        return complete

