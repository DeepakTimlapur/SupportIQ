from pathlib import Path
from typing import Dict, List
import pymupdf
from docx import Document


SUPPORTED_EXTENSIONS = {".pdf", ".docx", ".txt", ".md"}


def load_pdf(path: Path) -> str:
    pages = []
    with pymupdf.open(path) as pdf:
        for page_number, page in enumerate(pdf, start=1):
            text = page.get_text("text").strip()
            if text:
                pages.append(f"[Page {page_number}]\n{text}")
    return "\n\n".join(pages)


def load_docx(path: Path) -> str:
    document = Document(path)
    paragraphs = [p.text.strip() for p in document.paragraphs if p.text.strip()]

    for table in document.tables:
        for row in table.rows:
            cells = [cell.text.strip() for cell in row.cells]
            paragraphs.append(" | ".join(cells))

    return "\n".join(paragraphs)


def load_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def load_document(path: Path) -> Dict:
    path = Path(path)
    extension = path.suffix.lower()

    if extension not in SUPPORTED_EXTENSIONS:
        raise ValueError(f"Unsupported document type: {extension}")

    if extension == ".pdf":
        content = load_pdf(path)
    elif extension == ".docx":
        content = load_docx(path)
    else:
        content = load_text(path)

    if not content.strip():
        raise ValueError(f"No extractable text found in: {path.name}")

    return {
        "source": path.name,
        "path": str(path),
        "file_type": extension,
        "content": content.strip(),
    }


def load_documents(directory: str) -> List[Dict]:
    root = Path(directory)
    if not root.exists():
        raise FileNotFoundError(f"Directory not found: {root}")

    documents = []
    for path in sorted(root.rglob("*")):
        if path.is_file() and path.suffix.lower() in SUPPORTED_EXTENSIONS:
            try:
                documents.append(load_document(path))
            except Exception as error:
                print(f"Skipped {path.name}: {error}")

    return documents

