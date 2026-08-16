from langchain_text_splitters import RecursiveCharacterTextSplitter


def chunk_text(text: str):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=100
    )

    return splitter.split_text(text)


def chunk_pages(pages):
    """
    Split each PDF page into chunks while preserving
    the original PDF page number.
    """

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=100
    )

    chunks = []

    for page in pages:

        page_number = page["page"]
        text = page["text"]

        page_chunks = splitter.split_text(text)

        for chunk in page_chunks:
            chunks.append({
                "text": chunk,
                "page": page_number
            })

    return chunks