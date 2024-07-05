# import pandas as pd
# from fuzzywuzzy import fuzz

# # Define file paths
# file1_path = r"C:\Users\ribhu.kaul\RibhuLLM\Extraction_Program\Latest_Extraction\LlamaParsing_N_OpenAI_Extraction\llamaParse_new1.xlsx"
# file2_path = r"C:\Users\ribhu.kaul\RibhuLLM\Extraction_Program\Latest_Extraction\LlamaParsing_N_OpenAI_Extraction\UNIT LINKED (2).xlsx"
# output_path = r"C:\Users\ribhu.kaul\RibhuLLM\Extraction_Program\Latest_Extraction\LlamaParsing_N_OpenAI_Extraction\llamaParse_new1.xlsx"

# # Load the Excel files
# file1_df = pd.read_excel(file1_path)
# file2_df = pd.read_excel(file2_path, sheet_name=0)

# # Normalize the columns for matching
# file1_df['filename'] = file1_df.iloc[:, 0].astype(str).str.strip().str.lower()  # Assuming 'filename' is in the first column
# file2_df['NOME_FILE'] = file2_df.iloc[:, 1].astype(str).str.strip().str.lower()  # Assuming 'NOME_FILE' is in the second column

# # Create a new DataFrame to store the results
# results = []

# # Perform the fuzzy matching and store similarity scores
# for filename in file1_df['filename']:
#     max_similarity = 0
#     best_match_row = None
#     for index, row in file2_df.iterrows():
#         nome_file = row['NOME_FILE']
#         similarity = fuzz.ratio(filename, nome_file)
#         if similarity > max_similarity:
#             max_similarity = similarity
#             best_match_row = row

#     if best_match_row is not None:
#         combined_row = list(file1_df[file1_df['filename'] == filename].iloc[0]) + list(best_match_row) + [max_similarity]
#         results.append(combined_row)

# # Create a DataFrame for the results
# columns = list(file1_df.columns) + list(file2_df.columns) + ['Similarity Score']
# results_df = pd.DataFrame(results, columns=columns)

# # Save the results to a new sheet in the original Excel file
# with pd.ExcelWriter(output_path, mode='a', if_sheet_exists='replace') as writer:
#     results_df.to_excel(writer, sheet_name='Sheet2', index=False)

# print(f"Updated file saved to: {output_path}")

########################################################

import pandas as pd
from fuzzywuzzy import fuzz

# Load the Excel file
file_path = r"C:\Users\ribhu.kaul\RibhuLLM\Extraction_Program\Latest_Extraction\LlamaParsing_N_OpenAI_Extraction\llamaParse_new1.xlsx"
sheet2_df = pd.read_excel(file_path, sheet_name='Sheet2')

# Define the columns to compare and the corresponding columns for similarity scores
comparison_columns = [
    ('indicatore_sintetico_rischio', 'SRI', 'Similarity Score (1)'),
    ('periodo_detenzione_raccomandato', 'RHP (anni)', 'Similarity Score (2)'),
    ('date', 'DATA DEL DOCUMENTO', 'Similarity Score (3)'),
    ('moderato_return', 'RSMOD 1Y %', 'Similarity Score (4)'),
    ('moderato_return_rhp', 'RSMOD RHP %', 'Similarity Score (5)'),
    ('incidenza_annua', 'RIY 1Y %', 'Similarity Score (6)'),
    ('incidenza_annua_rhp', 'RIY RHP %', 'Similarity Score (7)')
]

# Function to clean values and calculate similarity
def clean_and_calculate_similarity(val1, val2):
    val1 = str(val1).replace('%', '').replace(',', '').replace('.', '').strip()
    val2 = str(val2).replace('%', '').replace(',', '').replace('.', '').strip()
    return fuzz.ratio(val1, val2)

# Perform the comparisons and calculate similarity scores for each row
for col1, col2, score_col in comparison_columns:
    sheet2_df[score_col] = sheet2_df.apply(lambda row: clean_and_calculate_similarity(row[col1], row[col2]), axis=1)

# Save the updated DataFrame to a new sheet in the original Excel file
output_path = r"C:\Users\ribhu.kaul\RibhuLLM\Extraction_Program\Latest_Extraction\LlamaParsing_N_OpenAI_Extraction\llamaParse_new1.xlsx"
with pd.ExcelWriter(output_path, mode='a', if_sheet_exists='replace') as writer:
    sheet2_df.to_excel(writer, sheet_name='Sheet2', index=False)

# Display the first few rows of the updated DataFrame
sheet2_df.head()

########################################
# import pandas as pd

# # Load the Excel file
# file_path = r"C:\Users\ribhu.kaul\RibhuLLM\Extraction_Program\Latest_Extraction\LlamaParsing_N_OpenAI_Extraction\llamaParse_new1.xlsx"
# sheet2_df = pd.read_excel(file_path, sheet_name='Sheet2')

# # Function to convert percentage strings to float values
# def convert_percentage_to_float(percentage_str):
#     # Replace ',' with '.' and remove '%', then convert to float and divide by 100
#     try:
#         return float(percentage_str.replace(',', '.').replace('%', '').strip()) / 100
#     except ValueError:
#         return None

# # Apply the conversion to the relevant columns
# columns_to_convert = ['moderato_return', 'moderato_return_rhp', 'incidenza_annua', 'incidenza_annua_rhp']

# for col in columns_to_convert:
#     sheet2_df[col] = sheet2_df[col].apply(convert_percentage_to_float)

# # Save the updated DataFrame to a new sheet in the original Excel file
# output_path = r"C:\Users\ribhu.kaul\RibhuLLM\Extraction_Program\Latest_Extraction\LlamaParsing_N_OpenAI_Extraction\llamaParse_new1.xlsx"
# with pd.ExcelWriter(output_path, mode='a', if_sheet_exists='replace') as writer:
#     sheet2_df.to_excel(writer, sheet_name='Sheet2', index=False)

# # Display the first few rows of the updated DataFrame
# sheet2_df.head()
