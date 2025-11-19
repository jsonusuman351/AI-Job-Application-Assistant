import docx
from pypdf import PdfReader
import os

def read_resume_file(file_path: str) -> str:
    """
    Reads the content of a resume file (PDF or DOCX).
    """
    if not os.path.exists(file_path):
        return "Error: Resume file not found."

    try:
        if file_path.endswith('.pdf'):
            reader = PdfReader(file_path)
            text = ""
            for page in reader.pages:
                text += page.extract_text() or ""
            return text
        elif file_path.endswith('.docx'):
            doc = docx.Document(file_path)
            text = ""
            for para in doc.paragraphs:
                text += para.text + "\n"
            return text
        else:
            return "Error: Unsupported file format. Please upload a PDF or DOCX file."
    except Exception as e:
        return f"Error reading file: {e}"
