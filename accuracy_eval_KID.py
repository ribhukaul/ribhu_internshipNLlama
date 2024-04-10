from extractors.custom_extractors.wamasset.kidtable import WamassetKidTableextractor
from AWSInteraction.EnvVarSetter import EnvVarSetter
import pandas as pd
import os

env_setter = EnvVarSetter()
env_setter.configure_local_env_vars()

# Load the Excel file for file names and types
excel_path = 'data_test/Fees_Fondi_GenAi_new.xlsm'
df = pd.read_excel(excel_path, usecols='A:B')

# Filter to get filenames where the type is 'KID'
kid_files = df[df['KID/KIID'] == 'KID']['Nome documento'].tolist()

kid_files = kid_files[:3]

pdf_directory = 'data_test/priipkid'

# Function to process each PDF and return the result as a DataFrame
def process_pdf(file_name):
    file_path = os.path.join(pdf_directory, file_name)
    extractor = WamassetKidTableextractor(file_path)
    cost, gestione = extractor.process()  # Unpacking the tuple of dictionaries
    
    # Create DataFrames from the dictionaries
    cost_df = pd.DataFrame([cost])        # Assuming 'cost' is a dictionary suitable for DataFrame
    gestione_df = pd.DataFrame([gestione])  # Assuming 'gestione' is also a dictionary suitable for DataFrame
    
    # Concatenate the 'cost' and 'gestione' DataFrames horizontally (axis=1)
    result_df = pd.concat([cost_df, gestione_df], axis=1)
    return result_df

# Initialize an empty DataFrame for results
final_results_df = pd.DataFrame()

# Loop through each filtered filename and process it
for file in kid_files:
    try:
        file_result_df = process_pdf(file)
        file_result_df['Filename'] = file  # Add a column for the file name
        final_results_df = pd.concat([final_results_df, file_result_df], axis=0, ignore_index=True)
    except Exception as e:
        print(f"Failed to process {file}: {e}")

# Save the concatenated results to an Excel file
final_results_df.to_excel('evaluation_output.xlsx', index=False)






