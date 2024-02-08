import re
from langchain_community.document_loaders import PyPDFLoader
import tiktoken
#import PyPDF2
import os
from langchain_community.document_loaders import UnstructuredExcelLoader
import uuid


def upload_df_as_excel(df):
    """Upload DF as excel file for LargeLanguageModel analysis.

    Args:
        df (pd.DataFrame): dataframe to upload

    Returns:
        str: path of the uploaded file
    """
    if os.environ.get("ENV") == "local":
        tmp_path = "tmp"
    else:
        tmp_path = "/tmp"
    # Modify empty cells with " " to avoid upload errors
    df = df.replace(to_replace="", value=" ")

    # Save table to excel and upload it back
    random_file_name = str(uuid.uuid4()) + ".xlsx"
    save_name = os.path.join(tmp_path, random_file_name)
    df.to_excel(save_name, index=False, header=False)
    loader = UnstructuredExcelLoader(save_name)
    loaded_table = loader.load()
    os.remove(save_name)

    return loaded_table

def num_tokens_from_string(string: str, encoding_name: str = "cl100k_base") -> int:
    """
    Returns the number of tokens in a given string using the specified encoding.

    Args:
        string (str): The input string to count tokens from.
        encoding_name (str, optional): The name of the encoding to use. Defaults to 'cl100k_base'.

    Returns:
        int: The number of tokens in the input string.
    """
    encoding = tiktoken.get_encoding(encoding_name)
    num_tokens = len(encoding.encode(string))
    return num_tokens

def is_more_number(text):
    """Check if a text in the page is composed  more than 30% of numbers

    Args:
        text (str): text to check

    Returns:
        Bool: if the text is composed more than 30% of numbers
    """

    letter_count = sum(1 for char in text if char.isalpha())
    number_count = sum(1 for char in text if char.isnumeric())
    ratio = number_count / (number_count + letter_count)
    if ratio > 0.3:
        return True
    else:
        return False

def _decode_first_condtition(text):
    """Decode the first condition

    Args:
        text (str): text to decode

    Returns:
        str: decoded text
    """
    return "".join(
        char
        for char in text
        if char.isalnum()
        or char.isspace()
        or char in [",", ".", "€", "%", ":", ";", "(", ")", "-", "/"]
    )

def _decode_second_condition(text):
    """Decode the second condition

    Args:
        text (str): text to decode

    Returns:
        str: decoded text
    """
    content = text.split("/")
    return "".join(
        [
            chr(int(code))
            for code in content
            if code and 32 <= int(code) <= 110000000
        ]
    )

def get_document_text(file_path):
    """Uploads a file to the server and returns the pages.

    Args:
        file_name (path): _description_

    Returns:
        _type_: _description_
    """
    try:
        loader = PyPDFLoader(file_path)
        pages = loader.load()
        del loader

        # Decoding conditions
        first_page = pages[0].page_content
        first_encoded_condition = first_page.count("\x00") > 100
        second_encoded_condition = is_more_number(first_page)
        # Decode
        for page in pages:
            content = page.page_content
            if first_encoded_condition:
                page.page_content = _decode_first_condtition(content)
            elif second_encoded_condition:
                page.page_content = _decode_second_condition(content)
        return pages
    
    except Exception as error:
        print("get document text error" + repr(error))
        raise error

def is_in_text(pattern, text)->bool:
    
    pattern = re.compile(pattern, re.IGNORECASE)
    ret = bool(
        pattern.search(text)
    )
    return ret
    
def search_in_pattern_in_text(pattern, text, pattern_inside):
    match= re.search(pattern, text, re.IGNORECASE)
    if not match:
        return
    match= re.search(pattern_inside, match.group(0), re.IGNORECASE)
    if not match:
        return 
    return match.group(0)

def extract_between(text, start, end):
    pattern = f"(\\n)?\s*{re.escape(start)}\s*(\\n)?\s*(\S.*?)\s*(?={re.escape(end)})"
    matches = re.findall(pattern, text, re.IGNORECASE)
    return matches[0][-1] if matches and matches[0] else None 
        
def format_pages_num(arr):
    if not arr:
        return None
    if isinstance(arr, str):
        return arr
    if isinstance(arr, int):
        return str(arr)
    
    
    arr = sorted(set(arr))  # Sort the array and remove duplicates
    ranges = []
    start = arr[0]
    end = arr[0]

    for i in range(1, len(arr)):
        if arr[i] - arr[i-1] == 1:
            end = arr[i]
        else:
            if start == end:
                ranges.append(str(start))
            else:
                ranges.append(f"{start}-{end}")
            start = arr[i]
            end = arr[i]

    # Add the last range or number
    if start == end:
        ranges.append(str(start))
    else:
        ranges.append(f"{start}-{end}")

    return ",".join(ranges)
###############
# LEGACY CODE #
###############
# def extract_text_from_pdf(pdf_path):
#     text = ""

#     with open(pdf_path, "rb") as pdf_file:
#         pdf_reader = PyPDF2.PdfReader(pdf_file)

#         for page_number in range(len(pdf_reader.pages)):
#             page = pdf_reader.pages[page_number]
#             text += page.extract_text()
#     return text

