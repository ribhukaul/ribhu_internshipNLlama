from llama_parse import LlamaParse

# Initialize the parser
parser = LlamaParse(
    api_key="llx-CL0JMQdc01kXPHUkb9cX2xbGtTck8dqvzbKFInYXQMY6sVB0",  # Replace with your actual API key
    result_type="text",  # Use "text" for easier processing
    num_workers=1,  # Number of workers for batch processing
    verbose=True,
    language="it"  # Assuming the document is in Italian
)

def parse_entire_document_sync(pdf_path):
    """Synchronously parse the entire PDF."""
    try:
        documents = parser.load_data(pdf_path)
        return documents if documents else []
    except Exception as e:
        print(f"Error during synchronous parsing: {e}")
        return []

def clean_text(text):
    """Cleans the text extracted from the PDF by normalizing newline sequences and removing unnecessary leading/trailing whitespace."""
    # Normalize newline sequences
    cleaned_text = text.replace('\r\n', '\n').replace('\r', '\n')  # Standardize on Unix newlines
    # Compact multiple newlines to a maximum of two (you can adjust this based on how much spacing you want to preserve)
    while '\n\n\n' in cleaned_text:
        cleaned_text = cleaned_text.replace('\n\n\n', '\n\n')
    # Strip leading and trailing whitespace including excessive newlines at the start or end
    cleaned_text = cleaned_text.strip()
    return cleaned_text

def extract_second_page_text(pages):
    """Extract text from the second page of the document after cleaning it."""
    if len(pages) > 1:
        second_page_text = pages[1]
        # Clean the text from the second page
        cleaned_text = clean_text(second_page_text)
        print(f"Debug: Extracted text from second page:\n{cleaned_text[:1000]}...")  # Debug point
        return cleaned_text
    else:
        return "Second page not found or the document has only one page."

def main_sync(pdf_path):
    """Main function for synchronous parsing and printing the second page."""
    extracted_documents = parse_entire_document_sync(pdf_path)
    if extracted_documents:
        document_text = extracted_documents[0].text
        print(f"Debug: Full document text:\n{document_text[:1000]}...")  # Debug point
        extracted_text = extract_second_page_text(document_text)
        print("Extracted Text from Page 2:", extracted_text)
    else:
        print("No text extracted from the synchronous method.")

if __name__ == "__main__":
    pdf_path = "C:/Users/ribhu.kaul/RibhuLLM/Extraction_Program/Latest_Extraction/GeminiBased_PerformanceScenario_Extraction/input_tester/202302_MULTI-OBIETTIVO CRESCITA_Vera financial Multi - Obiettivo Personal.pdf"
    
    # Run synchronous parsing and extraction
    print("Running synchronous extraction...")
    main_sync(pdf_path)
