
from extractors.custom_extractors.waminsurance.kid_governance import WamInsuranceKidGovernanceExtractor
from extractors.custom_extractors.waminsurance.gkid_governance import WamInsuranceGKidGovernanceExtractor
from extractors.custom_extractors.waminsurance.kid_credem import WamInsuranceKidCredemExtractor
from extractors.custom_extractors.waminsurance.kid_module import WamInsuranceKidModuleExtractor
from AWSInteraction.EnvVarSetter import EnvVarSetter
from extractors.custom_extractors.wamasset.fullkid import WamAssetKidExtractor
from extractors.custom_extractors.wamasset.kidtable import WamassetKidTableextractor
from extractors.custom_extractors.waminsurance.kid_credem_credim import WamInsuranceKidCredemExtractor # a copy of kid_credim, eliminate before commiting
import json   # can be removed from the original code
import os
import pandas as pd
from fpdf import FPDF, XPos, YPos
from extractors.general_extractors.extractor import Extractor
from concurrent.futures import ThreadPoolExecutor, as_completed
from extractors.configs.extraction_config.tags.kid_tags import TabellaCostiIngressoEUscita
import logging


from glob import glob

env_setter = EnvVarSetter()
env_setter.configure_local_env_vars()


file_path1 = 'C://Users//ribhu.kaul//RibhuLLM//Data//WAMASSET//priipkid//priipkid_IT0000380649_PAC.pdf'

text_file_path = 'C://Users//ribhu.kaul//RibhuLLM//Codes//tables_output5.txt'
pdf_file_path = 'C://Users//ribhu.kaul//RibhuLLM//Codes//ribhu_testing_table3.pdf'
excel_file_path = 'C://Users//ribhu.kaul//RibhuLLM//Codes//extracted_tables4E.xlsx'
pdf_excel_path = 'C://Users//ribhu.kaul//RibhuLLM//Codes//ribhu_testing_table5.pdf'


# USe the code given below to run the extraction on a single document
# extractor_table = WamInsuranceRibhuExtractor(file_path1)
# extraction_test = extractor_table.process1()
# print(extraction_test)

# table_inspection = extractor_table.get_tables1()
# print(table_inspection)

################################################################
# The code given below parallelly extracts required information from pdf files using process1 method 
# and transforms the data to an excel. works pretty well

# # Setting up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class BatchDocumentExtractor:
    def __init__(self, directory_path, file_extension='.pdf'):
        self.directory_path = directory_path
        self.file_extension = file_extension

    def process_file(self, file_path):
        try:
            extractor = WamInsuranceKidCredemExtractor(file_path)
            result = extractor.process1()
            if result:
                # Convert TabellaCostiIngressoEUscita to dict immediately after extraction
                if isinstance(result['data'].get('costi_ingresso_e_uscita'), TabellaCostiIngressoEUscita):
                    result['data']['costi_ingresso_e_uscita'] = result['data']['costi_ingresso_e_uscita'].dict()
                result['filename'] = os.path.basename(file_path)
                return result
            else:
                return {'filename': os.path.basename(file_path), 'data': 'No data found'}
        except Exception as e:
            logging.error(f"Error processing {file_path}: {e}")
            return {'filename': os.path.basename(file_path), 'error': str(e)}


    def run_extraction(self, max_workers=5):
        all_data = []
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [executor.submit(self.process_file, os.path.join(self.directory_path, filename))
                       for filename in os.listdir(self.directory_path) if filename.endswith(self.file_extension)]
            for future in as_completed(futures):
                result = future.result()
                logging.info(f"Result: {result}")
                if result:
                    all_data.append(result)

        # Process results to gather them in a list and format for Excel output
        final_data = self.format_data_for_output(all_data)

        if final_data:
            self.save_data_to_excel(final_data)

    def format_data_for_output(self, all_data):
        final_data = []
        for data in all_data:
            if data and 'data' in data and isinstance(data['data'], dict):
                entry = {
                    'Filename': data['filename'],
                    'Commissione Gestione': data['data'].get('gestione_commissioni', {}).get('commissione_gestione', 'N/A'),
                    'Commissione Transazione': data['data'].get('gestione_commissioni', {}).get('commissione_transazione', 'N/A'),
                    'Commissione Performance': data['data'].get('gestione_commissioni', {}).get('commissione_performance', 'N/A'),
                    'Costi Ingresso': data['data'].get('costi_ingresso_e_uscita', {}).get('costi_ingresso', 'Not Found'),
                    'Costi Uscita': data['data'].get('costi_ingresso_e_uscita', {}).get('costi_uscita', 'Not Found'),
                }
                final_data.append(entry)
        return final_data

    def save_data_to_excel(self, final_data):
        df = pd.DataFrame.from_records(final_data)
        excel_path = os.path.join(self.directory_path, 'Extraction_ResultsTT.xlsx')
        df.to_excel(excel_path, index=False)
        logging.info(f"Data saved to {excel_path}")

# Example usage
directory_path = 'C://Users//ribhu.kaul//RibhuLLM//Data//WAMASSET//priipkid'
batch_extractor = BatchDocumentExtractor(directory_path)
batch_extractor.run_extraction(max_workers=10)


############################################################################
# Code to compare the extraction with the expected outcomes of the extraction and calculate the efficiency
# Paths to the Excel files



