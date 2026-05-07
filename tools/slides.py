from pypdf import PdfReader
import os

def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Extracts text from a PDF file.
    Returns the extracted text formatted with page numbers to help the LLM 
    understand the structure of the slides.
    
    Args:
        pdf_path (str): The absolute or relative path to the PDF file.
        
    Returns:
        str: A concatenated string of all text found in the PDF.
    """
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"Could not find PDF at {pdf_path}")
        
    reader = PdfReader(pdf_path)
    extracted_content = []
    
    for i, page in enumerate(reader.pages):
        text = page.extract_text()
        if text:
            # Clean up the text a bit by removing excessive newlines and spaces
            cleaned_text = " ".join(text.split())
            extracted_content.append(f"--- Slide {i + 1} ---\n{cleaned_text}\n")
            
    if not extracted_content:
        return "No extractable text found in this PDF. It might be an image-only file."
        
    return "\n".join(extracted_content)

if __name__ == "__main__":
    # Small test block
    print("Testing slides extraction tool...")
    test_pdf = "../aua_nlp_agentic_telegram_bot_homework_short.pdf"
    if os.path.exists(test_pdf):
        print(extract_text_from_pdf(test_pdf)[:500])
        print("... (truncated)")
    else:
        print(f"Could not find {test_pdf} to test.")
