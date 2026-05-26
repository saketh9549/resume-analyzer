import pdfplumber

def extract_text_from_pdf(file_path: str) -> str:
    """
    Extracts clean readable text from a PDF file. Handles multi-page documents.
    """
    text = ""
    try:
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
    except Exception as e:
        print(f"Error reading PDF {file_path}: {e}")
    return text
