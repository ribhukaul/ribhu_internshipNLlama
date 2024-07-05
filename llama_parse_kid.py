# import asyncio
# from llama_parse import LlamaParse
# import os

# # Initialize the LlamaParse parser
# # Code to parse a single file and print output
# parser = LlamaParse(
#     api_key="llx-CL0JMQdc01kXPHUkb9cX2xbGtTck8dqvzbKFInYXQMY6sVB0",  # Replace with your actual API key
#     result_type="text",
#     num_workers=1,
#     verbose=True,
#     language="it"
# )

# async def parse_entire_document_async(pdf_path):
#     """Asynchronously parse the entire PDF."""
#     try:
#         print(f"Starting asynchronous parsing of {pdf_path}")
#         documents = await parser.aload_data(pdf_path)
#         print(f"Finished asynchronous parsing, found {len(documents)} documents")
#         return documents
#     except Exception as e:
#         print(f"Error parsing PDF asynchronously: {e}")
#         return []

# def parse_entire_document_sync(pdf_path):
#     """Synchronously parse the entire PDF."""
#     try:
#         print(f"Starting synchronous parsing of {pdf_path}")
#         documents = parser.load_data(pdf_path)
#         print(f"Finished synchronous parsing, found {len(documents)} documents")
#         return documents
#     except Exception as e:
#         print(f"Error parsing PDF synchronously: {e}")
#         return []

# def save_text_with_page_numbers(extracted_documents, filename, output_dir):
#     """Saves text with page numbers to a file."""
#     try:
#         with open(os.path.join(output_dir, filename), "w", encoding="utf-8") as f:
#             for i, document in enumerate(extracted_documents):
#                 f.write(f"Page {i+1}:\n")
#                 f.write(document.text)
#                 f.write("\n\n")
#         print(f"Extracted text saved to {filename}")
#     except Exception as e:
#         print(f"Error saving extracted text: {e}")

# async def main_async(pdf_path):
#     """Main function for asynchronous parsing."""
#     return await parse_entire_document_async(pdf_path)

# if __name__ == "__main__":
#     pdf_path = r"C:\Users\ribhu.kaul\RibhuLLM\Extraction_Program\Latest_Extraction\GeminiBased_PerformanceScenario_Extraction\input_tester\202302_MULTI-OBIETTIVO CRESCITA_Vera financial Multi - Obiettivo Personal.pdf"
#     output_dir = r"C:\Users\ribhu.kaul\RibhuLLM\Extraction_Program\Latest_Extraction\GeminiBased_PerformanceScenario_Extraction"
    
#     # Run synchronous parsing and extraction
#     print("Running synchronous extraction...")
#     extracted_documents_sync = parse_entire_document_sync(pdf_path)
#     save_text_with_page_numbers(extracted_documents_sync, "extracted_text_sync_with_pages.txt", output_dir)

#     # Run asynchronous parsing and extraction
#     print("Running asynchronous extraction...")
#     extracted_documents_async = asyncio.run(main_async(pdf_path))
#     save_text_with_page_numbers(extracted_documents_async, "extracted_text_async_with_pages.txt", output_dir)



##########################################
# Parallel processing--> Information extraction from KID documents using llama parse to avoid Azure document intelligence, the parsed document is passed
# through Open AI (Azure) to get relevant information from the doc.
import asyncio
from pydantic import BaseModel, Field
from llama_parse import LlamaParse
import os
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed
from glob import glob
from extractors.models import Models
from extractors.general_extractors.config.prompt_config import table_schemas
from AWSInteraction.EnvVarSetter import EnvVarSetter
from extractors.general_extractors.llm_functions import llm_extraction_and_tag
from langchain_core.prompts.prompt import PromptTemplate

env_setter = EnvVarSetter()
env_setter.configure_local_env_vars()

NF = "not found"
NA = "N/A"

schema1 = "general_info"
schema2 = "llama"
file_id = "unique_identifier_for_file_process"

# Define extraction functions
def extract_info1(text, general_schema, file_id):
    pydantic_class = table_schemas["it"][general_schema]
    extraction = Models.tag(text, pydantic_class, file_id)
    return extraction



# Initialize the LlamaParse parser
parser = LlamaParse(
    api_key="llx-CL0JMQdc01kXPHUkb9cX2xbGtTck8dqvzbKFInYXQMY6sVB0",
    result_type="text",
    num_workers=1,
    verbose=True,
    language="it"
)

async def parse_document(pdf_path):
    try:
        print(f"Starting parsing of {pdf_path}")
        documents = await parser.aload_data(pdf_path)
        print(f"Finished parsing, found {len(documents)} documents in {pdf_path}")
        return documents
    except Exception as e:
        print(f"Error parsing PDF {pdf_path}: {e}")
        return []

def parse_entire_document_sync(pdf_path):
    """Synchronously parse the entire PDF."""
    documents = parser.load_data(pdf_path)
    return documents if documents else []

def main_sync(pdf_path):
    """Main function for synchronous parsing and printing the second page."""
    extracted_documents = parse_entire_document_sync(pdf_path)
    print(f"Debug: Extracted Documents: {extracted_documents}")  # Debug point
    if extracted_documents:
       return extracted_documents[0].text

def process_file(pdf_path):
    documents3 = main_sync(pdf_path)
    #asyncio.set_event_loop(asyncio.new_event_loop())
    #documents = asyncio.run(parse_document(pdf_path))
    if documents3:
        var1 = extract_info1(documents3, "general_info", file_id)
        data1 = {
            "indicatore_sintetico_rischio": var1.indicatore_sintetico_rischio,
            "periodo_detenzione_raccomandato": var1.periodo_detenzione_raccomandato,
            "date": var1.date
        }

        # Convert to DataFrame for easier manipulation
        df_data1 = pd.DataFrame([data1])
        df_data1['periodo_detenzione_raccomandato'] = pd.to_numeric(df_data1['periodo_detenzione_raccomandato'],errors='coerce')


        rhp = int(df_data1['periodo_detenzione_raccomandato'][0])
        # Define the new class using the specified name
        prompts = {"it": 
                   {"llama":f""" Dal documento fornito-

                                Estrarre i "Costi totali" per 1 anno. Cerca la sezione in cui i costi nel tempo vengono 
                                discussi in una tabella e identifica specificamente i costi totali dopo 1 anno. Il formato 
                                deve essere un valore numerico seguito dalla percentuale, ad esempio "4%".

                                Estrai i "Costi totali" per un periodo di {rhp} anni. Cerca la sezione in cui i costi nel 
                                tempo vengono discussi in una tabella e identifica specificamente i costi totali dopo {rhp} anni. 
                                Il formato deve essere un valore numerico seguito dalla percentuale, ad esempio "4%".

                                Estrarre il rendimento percentuale dello "Scenario Moderato" dopo 1 anno. Cerca la sezione 
                                che descrive i diversi scenari di performance (stressante, sfavorevole, moderato, favorevole) 
                                e identifica lo scenario moderato per 1 anno. Il formato dovrebbe essere una percentuale, 
                                ad esempio "6,51%".

                                Estrai il rendimento percentuale dello "Scenario moderato" dopo {rhp} anni. Cerca la sezione 
                                che descrive i diversi scenari di performance (stressato, sfavorevole, moderato, favorevole) 
                                e identifica lo scenario moderato per il periodo dell'anno {rhp}. Il formato dovrebbe essere 
                                una percentuale, ad esempio "6,64%".  
        """}
        }

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
        def extract_info2(text, general_schema, file_id):
            template = prompts["it"]["llama"]
            pydantic_class = llama3_schema["it"][general_schema]
            prompt = PromptTemplate(input_variables=["context"], template=template)
            model="gpt-4-turbo"
            # Construct chain and extract relevan info
            extraction1 = Models.extract(file_id, model, prompt, text)
            tagged = Models.tag(extraction1, pydantic_class, file_id)
            return tagged
        
        var2 = extract_info2(documents3, "llama", file_id)
        data2 = {
            "moderato_return": var2.scenario_moderato,
            "moderato_return_rhp": var2.scenario_moderato_rhp,
            "incidenza_annua": var2.impatto_dei_costi,
            "incidenza_annua_rhp": var2.impatto_dei_costi_rhp    
        }

        df1 = pd.DataFrame([data1])
        df2 = pd.DataFrame([data2])
        filename = os.path.basename(pdf_path)
        df1.insert(0, 'filename', filename)
        df2.insert(0, 'filename', filename)
        
        return df1, df2

    return None, None

if __name__ == "__main__":
    input_dir = r"C:\Users\ribhu.kaul\RibhuLLM\Extraction_Program\Latest_Extraction\LlamaParsing_N_OpenAI_Extraction\ProblemCreator"
    output_path = r"C:\Users\ribhu.kaul\RibhuLLM\Extraction_Program\Latest_Extraction\LlamaParsing_N_OpenAI_Extraction\llamaParse_new1_errors.xlsx"
    files = glob(os.path.join(input_dir, '*.pdf'))
    
    all_df1 = []
    all_df2 = []

    with ThreadPoolExecutor(max_workers=5) as executor:
        future_to_file = {executor.submit(process_file, file): file for file in files}
        for future in as_completed(future_to_file):
            df1, df2 = future.result()
            if df1 is not None and df2 is not None:
                all_df1.append(df1)
                all_df2.append(df2)

    final_df1 = pd.concat(all_df1, ignore_index=True)
    final_df2 = pd.concat(all_df2, ignore_index=True)
    final_df = pd.concat([final_df1, final_df2], axis=1)
    
    final_df.to_excel(output_path, index=False)
    print(f"Data successfully saved to {output_path}")
