import fitz  # PyMuPDF


def extract_text(pdf_path: str):
    document = fitz.open(pdf_path)

    text = ""

    for page in document:
        text += page.get_text() + "\n"

    document.close()

    return text


def extract_pages(pdf_path: str):
    """
    Extract text page-by-page so we can preserve
    the original PDF page number.
    """

    document = fitz.open(pdf_path)

    pages = []

    for page_number, page in enumerate(document, start=1):

        text = page.get_text().strip()

        if text:
            pages.append({
                "page": page_number,
                "text": text
            })

    document.close()

    return pages