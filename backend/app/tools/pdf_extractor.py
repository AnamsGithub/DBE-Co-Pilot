import pdfplumber
import fitz  # PyMuPDF
from pathlib import Path


def extract_text_pdfplumber(pdf_path: str) -> str:
    """Primary extractor — handles most resume PDFs cleanly."""
    text_parts = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text(x_tolerance=2, y_tolerance=2)
            if page_text:
                text_parts.append(page_text)
    return "\n".join(text_parts)


def extract_text_pymupdf(pdf_path: str) -> str:
    """Fallback extractor — better with scanned or image-heavy PDFs."""
    text_parts = []
    doc = fitz.open(pdf_path)
    for page in doc:
        text_parts.append(page.get_text("text"))
    doc.close()
    return "\n".join(text_parts)


def extract_resume_text(pdf_path: str) -> str:
    """
    Extract raw text from a resume PDF.
    Tries pdfplumber first; falls back to PyMuPDF if output is too short
    (which usually means the PDF is image-based or has encoding issues).
    """
    path = Path(pdf_path)
    if not path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")
    if path.suffix.lower() != ".pdf":
        raise ValueError(f"Expected a .pdf file, got: {path.suffix}")

    text = extract_text_pdfplumber(pdf_path)

    # If pdfplumber returns very little text, fall back to PyMuPDF
    if len(text.strip()) < 100:
        text = extract_text_pymupdf(pdf_path)

    if len(text.strip()) < 50:
        raise ValueError(
            "Could not extract readable text from this PDF. "
            "It may be scanned without OCR. Please upload a text-based PDF."
        )

    return text.strip()
