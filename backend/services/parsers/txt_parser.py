def extract_text_from_txt(file_path: str) -> str:
    """
    Extracts text from a plain text (TXT) file.
    """
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()
    except Exception as e:
        print(f"Error reading TXT {file_path}: {e}")
        return ""
