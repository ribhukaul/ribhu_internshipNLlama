
from extractors.custom_extractors.waminsurance.kid_governance import WamInsuranceKidGovernanceExtractor
from extractors.custom_extractors.waminsurance.gkid_governance import WamInsuranceGKidGovernanceExtractor
from extractors.custom_extractors.waminsurance.kid_credem import WamInsuranceKidCredemExtractor
from extractors.custom_extractors.waminsurance.kid_module import WamInsuranceKidModuleExtractor
from AWSInteraction.EnvVarSetter import EnvVarSetter
from extractors.custom_extractors.wamasset.fullkid import WamAssetKidExtractor
from extractors.custom_extractors.wamasset.kidtable import WamassetKidTableextractor
from extractors.custom_extractors.waminsurance.ribhu_credim import WamInsuranceRibhuExtractor # a copy of kid_credim, eliminate before commiting
import json   # can be removed from the original code
import os
import pandas as pd
# from fpdf import FPDF, XPos, YPos
from extractors.general_extractors.extractor import Extractor
from concurrent.futures import ThreadPoolExecutor, as_completed
from extractors.configs.extraction_config.tags.kid_tags import TabellaCostiIngressoEUscita
import logging
from extractors.models import Models
from extractors.general_extractors.config.prompt_config import table_schemas


from glob import glob

env_setter = EnvVarSetter()
env_setter.configure_local_env_vars()

import asyncio
from llama_parse import LlamaParse
import os
from pydantic import BaseModel, Field

NF = "not found"
NA = "N/A"



# Define extraction functions
def extract_info1(text, general_schema, file_id):
    pydantic_class = table_schemas["it"][general_schema]
    extraction = Models.tag(text, pydantic_class, file_id)
    return extraction

def extract_info2(text, general_schema, file_id):
    pydantic_class = llama3_schema["it"][general_schema]
    extraction = Models.tag(text, pydantic_class, file_id)
    return extraction


schema1 = "general_info"
schema2 = "llama"
file_id = "unique_identifier_for_file_process"

# Initialize the LlamaParse parser
# LlamaParser is being used to check if we can avoid Azure Document Intelligence
parser = LlamaParse(
    api_key="llx-CL0JMQdc01kXPHUkb9cX2xbGtTck8dqvzbKFInYXQMY6sVB0",  # Replace with your actual API key
    result_type="text",
    num_workers=1,
    verbose=True,
    language="it"
)

async def parse_entire_document_async(pdf_path):
    """Asynchronously parse the entire PDF."""
    try:
        print(f"Starting asynchronous parsing of {pdf_path}")
        documents = await parser.aload_data(pdf_path)
        print(f"Finished asynchronous parsing, found {len(documents)} documents")
        return documents
    except Exception as e:
        print(f"Error parsing PDF asynchronously: {e}")
        return []

def parse_entire_document_sync(pdf_path):
    """Synchronously parse the entire PDF."""
    try:
        print(f"Starting synchronous parsing of {pdf_path}")
        documents = parser.load_data(pdf_path)
        print(f"Finished synchronous parsing, found {len(documents)} documents")
        return documents
    except Exception as e:
        print(f"Error parsing PDF synchronously: {e}")
        return []

def save_text_with_page_numbers(extracted_documents, filename, output_dir):
    """Saves text with page numbers to a file."""
    try:
        with open(os.path.join(output_dir, filename), "w", encoding="utf-8") as f:
            for i, document in enumerate(extracted_documents):
                f.write(f"Page {i+1}:\n")
                f.write(document.text)
                f.write("\n\n")
        print(f"Extracted text saved to {filename}")
    except Exception as e:
        print(f"Error saving extracted text: {e}")

async def main_async(pdf_path):
    """Main function for asynchronous parsing."""
    return await parse_entire_document_async(pdf_path)

if __name__ == "__main__":
    pdf_path = r"C:\Users\ribhu.kaul\RibhuLLM\Extraction_Program\Latest_Extraction\LlamaParsing_N_OpenAI_Extraction\ProblemCreator\201801_Aggressive_Unit Melody Advanced Bonus Edition.pdf"
    output_dir = r"C:\Users\ribhu.kaul\RibhuLLM\Extraction_Program\Latest_Extraction\GeminiBased_PerformanceScenario_Extraction"
    # Extract the filename from the path
    filename = os.path.basename(pdf_path)
    # Run synchronous parsing and extraction
    print("Running synchronous extraction...")
    extracted_documents_sync = parse_entire_document_sync(pdf_path)
    save_text_with_page_numbers(extracted_documents_sync, "extracted_text_sync_with_pages.txt", output_dir)

    # Run asynchronous parsing and extraction
    print("Running asynchronous extraction...")
    extracted_documents_async = asyncio.run(main_async(pdf_path))
    save_text_with_page_numbers(extracted_documents_async, "extracted_text_async_with_pages.txt", output_dir)

    

var1 = extract_info1(extracted_documents_async, schema1, file_id)

data1 = {
    "indicatore_sintetico_rischio": var1.indicatore_sintetico_rischio,
    "periodo_detenzione_raccomandato": var1.periodo_detenzione_raccomandato,
    "date": var1.date
}
rhp = data1["periodo_detenzione_raccomandato"]
print(rhp)


# Define the new class using the specified name
class Llama3Parse(BaseModel):
    scenario_moderato: str = Field(NF, description= "Rendimento percentuale(%) o '-'  1 anno scenario moderato")
    scenario_moderato_rhp: str = Field(NF, description= f"Rendimento percentuale(%) o '-' {rhp} anni scenario moderato")
    impatto_dei_costi: str = Field(NF, description= "Impatto sui costi annuali in % per uscita dopo 1 anno")
    impatto_dei_costi_rhp : str = Field(NF,description= f"Impatto sui costi annuali in % per uscita dopo {rhp} anno")

# Updated schema dictionary to use the new class name
llama3_schema = {
    "it": {
        "llama": Llama3Parse
    }
}

var2 = extract_info2(extracted_documents_async, schema2, file_id)

data2 = {
    "moderato_return": var2.scenario_moderato,
    "moderato_return_rhp": var2.scenario_moderato_rhp,
    "incidenza_annua": var2.impatto_dei_costi,
    "incidenza_annua_rhp": var2. impatto_dei_costi_rhp    
}

# Convert the dictionary to a pandas DataFrame
df1 = pd.DataFrame([data1])
df2 = pd.DataFrame([data2])

# Add the filename as the first column in both DataFrames
df1.insert(0, 'filename', filename)
df2.insert(0, 'filename', filename)

print(df1)
print(df2)
  # Concatenate DataFrames and save to Excel
final_df = pd.concat([df1, df2], axis=1)
excel_file_path = os.path.join(output_dir, "llama_parse_data.xlsx")
final_df.to_excel(excel_file_path, index=False)
print(f"Data successfully saved to {excel_file_path}")


# file_path1 = r"C:\Users\ribhu.kaul\RibhuLLM\Extraction_Program\Latest_Extraction\GeminiBased_PerformanceScenario_Extraction\input_tester\202302_MULTI-OBIETTIVO CRESCITA_Vera financial Multi - Obiettivo Personal.pdf"

# text_file_path = 'C://Users//ribhu.kaul//RibhuLLM//Codes//tables_output5.txt'
# pdf_file_path = 'C://Users//ribhu.kaul//RibhuLLM//Codes//ribhu_testing_table3.pdf'
# excel_file_path = 'C://Users//ribhu.kaul//RibhuLLM//Codes//extracted_tables4E.xlsx'
# pdf_excel_path = 'C://Users//ribhu.kaul//RibhuLLM//Codes//ribhu_testing_table5.pdf'


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
# logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# class BatchDocumentExtractor:
#     def __init__(self, directory_path, file_extension='.pdf'):
#         self.directory_path = directory_path
#         self.file_extension = file_extension

#     def process_file(self, file_path):
#         try:
#             extractor = WamInsuranceRibhuExtractor(file_path)
#             result = extractor.process1()
#             if result:
#                 # Convert TabellaCostiIngressoEUscita to dict immediately after extraction
#                 if isinstance(result['data'].get('costi_ingresso_e_uscita'), TabellaCostiIngressoEUscita):
#                     result['data']['costi_ingresso_e_uscita'] = result['data']['costi_ingresso_e_uscita'].dict()
#                 result['filename'] = os.path.basename(file_path)
#                 return result
#             else:
#                 return {'filename': os.path.basename(file_path), 'data': 'No data found'}
#         except Exception as e:
#             logging.error(f"Error processing {file_path}: {e}")
#             return {'filename': os.path.basename(file_path), 'error': str(e)}


#     def run_extraction(self, max_workers=5):
#         all_data = []
#         with ThreadPoolExecutor(max_workers=max_workers) as executor:
#             futures = [executor.submit(self.process_file, os.path.join(self.directory_path, filename))
#                        for filename in os.listdir(self.directory_path) if filename.endswith(self.file_extension)]
#             for future in as_completed(futures):
#                 result = future.result()
#                 logging.info(f"Result: {result}")
#                 if result:
#                     all_data.append(result)

#         # Process results to gather them in a list and format for Excel output
#         final_data = self.format_data_for_output(all_data)

#         if final_data:
#             self.save_data_to_excel(final_data)

#     def format_data_for_output(self, all_data):
#         final_data = []
#         for data in all_data:
#             if data and 'data' in data and isinstance(data['data'], dict):
#                 entry = {
#                     'Filename': data['filename'],
#                     'Commissione Gestione': data['data'].get('gestione_commissioni', {}).get('commissione_gestione', 'N/A'),
#                     'Commissione Transazione': data['data'].get('gestione_commissioni', {}).get('commissione_transazione', 'N/A'),
#                     'Commissione Performance': data['data'].get('gestione_commissioni', {}).get('commissione_performance', 'N/A'),
#                     'Costi Ingresso': data['data'].get('costi_ingresso_e_uscita', {}).get('costi_ingresso', 'Not Found'),
#                     'Costi Uscita': data['data'].get('costi_ingresso_e_uscita', {}).get('costi_uscita', 'Not Found'),
#                 }
#                 final_data.append(entry)
#         return final_data

#     def save_data_to_excel(self, final_data):
#         df = pd.DataFrame.from_records(final_data)
#         excel_path = os.path.join(self.directory_path, 'Extraction_ResultsTT.xlsx')
#         df.to_excel(excel_path, index=False)
#         logging.info(f"Data saved to {excel_path}")

# # Example usage
# directory_path = 'C://Users//ribhu.kaul//RibhuLLM//Data//WAMASSET//priipkid'
# batch_extractor = BatchDocumentExtractor(directory_path)
# batch_extractor.run_extraction(max_workers=10)


############################################################################
# Code to compare the extraction with the expected outcomes of the extraction and calculate the efficiency
# Paths to the Excel files



