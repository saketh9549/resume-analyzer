def validate_file(uploaded_file):

    allowed_extensions = ["pdf", "docx"]

    extension = uploaded_file.name.split(".")[-1]

    return extension in allowed_extensions