
from pathlib import Path
from langchain.schema import Document
from pypdf import PdfReader


def load_cv(pdf_path: str) -> list[Document]:
    
    path = Path(pdf_path)
    if not path.exists():
        raise FileNotFoundError(
            f"❌ مش لاقي الـ CV في: {pdf_path}\n"
            f"   حط الـ PDF في: data/cv.pdf"
        )

    reader = PdfReader(str(path))
    documents = []

    full_text = ""
    for page_num, page in enumerate(reader.pages):
        text = page.extract_text()
        if text.strip():
            full_text += text + "\n"

    
    if full_text.strip():
        documents.append(
            Document(
                page_content=full_text,
                metadata={
                    "source": "CV",
                    "type": "resume",
                    "file": pdf_path,
                    "pages": len(reader.pages),
                },
            )
        )

    print(f"✅ CV: اتقرأ {len(reader.pages)} صفحة من {path.name}")
    return documents
