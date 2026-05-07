from pypdf import PdfReader
import os

def extract_text_from_pdf(pdf_path: str) -> str:
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f'Could not find PDF at {pdf_path}')
    reader = PdfReader(pdf_path)
    extracted_content = []
    for (i, page) in enumerate(reader.pages):
        text = page.extract_text()
        if text:
            cleaned_text = ' '.join(text.split())
            extracted_content.append(f'--- Slide {i + 1} ---\n{cleaned_text}\n')
    if not extracted_content:
        return 'No extractable text found in this PDF. It might be an image-only file.'
    return '\n'.join(extracted_content)
