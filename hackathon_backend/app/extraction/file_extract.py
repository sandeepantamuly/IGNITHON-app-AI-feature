from pathlib import Path


def extract_text_from_pdf(path: str) -> str:
    from pypdf import PdfReader
    reader = PdfReader(path)
    return "\n".join(page.extract_text() or "" for page in reader.pages)


def extract_text_from_docx(path: str) -> str:
    from docx import Document
    doc = Document(path)
    return "\n".join(p.text for p in doc.paragraphs)


def extract_text_from_file(path: str, content_type: str | None = None) -> tuple[str, str]:
    suffix = Path(path).suffix.lower()
    if suffix == ".pdf":
        return extract_text_from_pdf(path), "pdf"
    if suffix == ".docx":
        return extract_text_from_docx(path), "docx"
    if suffix in {".txt", ".csv", ".json"}:
        return Path(path).read_text(encoding="utf-8", errors="replace"), suffix.lstrip(".")
    if suffix in {".png", ".jpg", ".jpeg", ".webp"}:
        try:
            import pytesseract
            from PIL import Image
            return pytesseract.image_to_string(Image.open(path)), "screenshot"
        except Exception:
            return "", "screenshot"
    raise ValueError(f"Unsupported file type: {suffix or content_type or 'unknown'}")
