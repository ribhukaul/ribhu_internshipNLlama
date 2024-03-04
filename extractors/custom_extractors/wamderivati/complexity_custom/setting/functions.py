import pyodbc
import PyPDF2
from datetime import datetime
from dateutil import parser


def extract_text_from_pdf(pdf_path):
    text = ""

    with open(pdf_path, 'rb') as pdf_file:
        pdf_reader = PyPDF2.PdfReader(pdf_file)

        for page_number in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_number]
            text += page.extract_text()
    return text


def insert_dataframe_into_table(database, table, input_df):
    server = 'WAM-HAL9000'
    conn_str = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};trusted_connection=yes"
    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()
    try:
        columns = input_df.columns.tolist()
        placeholders = input_df.loc[0, :].values.flatten().tolist()
        placeholders = ['NULL' if val is None else val for val in placeholders]
        query = f"INSERT INTO {database}.{table} ({', '.join(columns)}) VALUES ({str(placeholders)[1:-1]})"
        query = query.replace("'NULL'", "NULL")
        cursor.execute(query)
        conn.commit()
        print("Inserimento completato con successo!")
    except Exception as e:
        conn.rollback()
        print("Errore durante l'inserimento:", e)
    finally:
        cursor.close()
        conn.close()


def get_new_column_name(column_dict, column):
    for new_column, possible_columns in column_dict.items():
        if column in possible_columns:
            return new_column
    return column


def truncate(x):
    if isinstance(x, str):
        return x[:100]
    else:
        return x


def pulisci_emittenti(valore):
    valore_pulito = valore.replace(".", "").replace(",", "").lower()
    return valore_pulito


def clean_value(x):
    if isinstance(x, str):
        x = x.replace(',', '')  # Rimuovi le virgole
        x = x.replace('EUR', '')  # Rimuovi 'EUR'
        x = x.replace('%', '')  # Rimuovi '%'
        x = x.replace('per Certificate', '')  # Rimuovi '%'
        x = x.replace('per certificate', '')  # Rimuovi '%'
        return x
    else:
        return x


def convert_date(date_str):
    try:
        date_obj = datetime.strptime(date_str, '%d/%m/%Y')
        return date_obj.strftime('%Y-%m-%d')
    except ValueError:
        return date_str

