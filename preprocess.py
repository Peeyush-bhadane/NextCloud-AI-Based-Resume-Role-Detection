import re
import string
import pdfplumber

def clean_resume_text(text):
    """
    Cleans resume text by:
    - Lowercasing
    - Removing special characters and punctuation
    - Removing numbers
    - Handling extra whitespace
    """
    if not text:
        return ""
    text = text.lower()
    # Remove URLs and emails
    text = re.sub(r'http\S+\s*|[\w\.-]+@[\w\.-]+', ' ', text)
    # Remove special characters
    text = re.sub(r'[%s]' % re.escape(string.punctuation), ' ', text)
    # Remove non-ascii
    text = re.sub(r'[^\x00-\x7f]', r' ', text)
    # Remove numbers
    text = re.sub(r'\d+', ' ', text)
    # Extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def extract_text_from_pdf(pdf_file):
    """Extracts text from a PDF file."""
    try:
        with pdfplumber.open(pdf_file) as pdf:
            text = ""
            for page in pdf.pages:
                text += page.extract_text() or ""
            return text
    except Exception as e:
        print(f"Error extracting PDF: {e}")
        return ""
