import os
from services.parsers.pdf_parser import extract_text_from_pdf
from services.parsers.docx_parser import extract_text_from_docx
from services.parsers.txt_parser import extract_text_from_txt

def extract_text(file_path: str) -> str:
    """
    Detects the file extension and delegates text extraction to the appropriate parser.
    """
    if not os.path.exists(file_path):
        print(f"Error: Extraction file path does not exist: {file_path}")
        return ""

    _, ext = os.path.splitext(file_path)
    ext = ext.lower()

    if ext == ".pdf":
        return extract_text_from_pdf(file_path)
    elif ext in [".docx", ".doc"]:
        return extract_text_from_docx(file_path)
    else:
        # Fallback to UTF-8 plain text reader
        return extract_text_from_txt(file_path)
