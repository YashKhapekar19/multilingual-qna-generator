from pathlib import Path
from docx import Document
from pypdf import PdfReader

SUPPORTED = {'.pdf', '.docx', '.txt'}

def _clean_text(text):
    return '\n'.join(line.strip() for line in text.splitlines() if line.strip())

def load_pdf(path):
    reader = PdfReader(str(path))
    return _clean_text('\n'.join(page.extract_text() or '' for page in reader.pages))

def load_docx(path):
    doc = Document(str(path))
    return _clean_text('\n'.join(p.text for p in doc.paragraphs))

def load_txt(path):
    return _clean_text(Path(path).read_text(encoding='utf-8'))

def load_document(path):
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(path)
    if path.suffix.lower() not in SUPPORTED:
        raise ValueError('Supported formats: PDF, DOCX, TXT')
    loaders = {'.pdf': load_pdf, '.docx': load_docx, '.txt': load_txt}
    text = loaders[path.suffix.lower()](path)
    if not text.strip():
        raise ValueError('No readable text found.')
    return text
