from fastapi import APIRouter, UploadFile, File, HTTPException
import shutil
import os
from backend.app.services.vlm_service import analyze_image
from backend.app.services.pdf_service import extract_text, extract_pages
from backend.app.services.image_service import extract_text_from_image
from backend.app.services.chunk_service import chunk_text, chunk_pages
from backend.app.services.embedding_service import generate_embeddings
from backend.app.services.csv_service import extract_text_from_csv
from backend.app.services.vector_service import (
    create_collection,
    store_embeddings,
)

router = APIRouter()

UPLOAD_FOLDER = "backend/uploads"
IMAGE_FOLDER = "backend/uploads/images"
CSV_FOLDER = "backend/uploads/csv"

os.makedirs(CSV_FOLDER, exist_ok=True)
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(IMAGE_FOLDER, exist_ok=True)


# ==========================================
# PDF Upload
# ==========================================
@router.post("/upload", tags=["Upload"])
async def upload_pdf(file: UploadFile = File(...)):

    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are allowed."
        )

    file_path = os.path.join(UPLOAD_FOLDER, file.filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # ==========================================
    # Extract PDF page-by-page
    # ==========================================

    pages = extract_pages(file_path)

    if not pages:
        raise HTTPException(
            status_code=400,
            detail="No text found inside PDF."
        )

    # ==========================================
    # Chunk while preserving page number
    # ==========================================

    page_chunks = chunk_pages(pages)

    chunks = [item["text"] for item in page_chunks]

    metadata = [
        {
            "page": item["page"],
            "filename": file.filename,
            "type": "pdf"
        }
        for item in page_chunks
    ]

    # ==========================================
    # Generate embeddings
    # ==========================================

    embeddings = generate_embeddings(chunks)

    # ==========================================
    # Store in Qdrant
    # ==========================================

    create_collection()

    store_embeddings(
        chunks,
        embeddings,
        metadata
    )

    # ==========================================
    # Response
    # ==========================================

    return {
        "status": "success",
        "type": "pdf",
        "filename": file.filename,
        "pages": len(pages),
        "total_chunks": len(chunks),
        "embedding_dimension": len(embeddings[0]),
        "vectors_stored": len(embeddings),
        "message": "PDF processed successfully with page metadata."
    }
# ==========================================
# Image Upload
# ==========================================
@router.post("/upload-image", tags=["Upload"])
async def upload_image(file: UploadFile = File(...)):

    if file.content_type is None or not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=400,
            detail="Please upload an image."
        )

    file_path = os.path.join(IMAGE_FOLDER, file.filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # ==========================================
    # OCR
    # ==========================================

    try:
        ocr_text = extract_text_from_image(file_path)
    except Exception as e:
        ocr_text = f"OCR failed: {str(e)}"

    # ==========================================
    # VLM ANALYSIS
    # ==========================================

    try:
        vlm_text = analyze_image(file_path)
    except Exception as e:
        vlm_text = f"VLM analysis failed: {str(e)}"

    # ==========================================
    # Combine OCR + VLM
    # ==========================================

    combined_text = f"""
IMAGE FILE: {file.filename}

OCR TEXT:
{ocr_text}

VISUAL ANALYSIS:
{vlm_text}
"""

    if not ocr_text.strip() and not vlm_text.strip():
        raise HTTPException(
            status_code=400,
            detail="No information could be extracted from image."
        )

    # ==========================================
    # Chunk
    # ==========================================

    chunks = chunk_text(combined_text)

    # ==========================================
    # Embeddings
    # ==========================================

    embeddings = generate_embeddings(chunks)

    # ==========================================
    # Store in Qdrant
    # ==========================================

    create_collection()

    metadata = [
        {
            "filename": file.filename,
            "type": "image",
            "source": "OCR + VLM"
        }
        for _ in chunks
    ]

    store_embeddings(
        chunks,
        embeddings,
        metadata
    )

    # ==========================================
    # Response
    # ==========================================

    return {
        "status": "success",
        "type": "image",
        "filename": file.filename,
        "ocr_text": ocr_text,
        "vlm_analysis": vlm_text,
        "total_chunks": len(chunks),
        "vectors_stored": len(embeddings),
        "message": "Image processed using OCR + VLM successfully."
    }
    
    
@router.post("/upload-csv", tags=["Upload"])
async def upload_csv(file: UploadFile = File(...)):

    if not file.filename.lower().endswith(".csv"):
        raise HTTPException(
            status_code=400,
            detail="Only CSV files are allowed."
        )

    file_path = os.path.join(CSV_FOLDER, file.filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Read CSV
    text = extract_text_from_csv(file_path)

    # Split into chunks
    chunks = chunk_text(text)

    # Generate embeddings
    embeddings = generate_embeddings(chunks)

    # Store in Qdrant
    create_collection()
    store_embeddings(chunks, embeddings)

    return {
        "status": "success",
        "filename": file.filename,
        "rows": len(chunks),
        "message": "CSV uploaded successfully."
    }