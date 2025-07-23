from fastapi import UploadFile
import docx
import pypdf
import io

def parse_file(file: UploadFile) -> str:
    content = ""
    file_content = file.file.read()
    if file.filename.endswith('.pdf'):
        pdf_reader = pypdf.PdfReader(io.BytesIO(file_content))
        for page in pdf_reader.pages:
            content += page.extract_text() + "\n"
    elif file.filename.endswith('.docx'):
        doc = docx.Document(io.BytesIO(file_content))
        for para in doc.paragraphs:
            content += para.text + "\n"
    else:
        content = file_content.decode('utf-8') # fallback for .txt
    return content