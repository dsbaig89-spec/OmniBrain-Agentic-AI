from fastapi import APIRouter, UploadFile, File, HTTPException
import shutil
import os

from backend.app.services.pdf_service import extract_text
from backend.app.services.image_service import extract_text_from_image
from backend.app.services.chunk_service import chunk_text
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

    # Extract text
    text = extract_text(file_path)

    if not text.strip():
        raise HTTPException(
            status_code=400,
            detail="No text found inside PDF."
        )

    # Chunk
    chunks = chunk_text(text)

    # Embeddings
    embeddings = generate_embeddings(chunks)

    # Store in Qdrant
    create_collection()
    store_embeddings(chunks, embeddings)

    return {
        "status": "success",
        "type": "pdf",
        "filename": file.filename,
        "characters": len(text),
        "total_chunks": len(chunks),
        "embedding_dimension": len(embeddings[0]),
        "vectors_stored": len(embeddings),
        "message": "PDF processed successfully."
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

    # OCR
    text = extract_text_from_image(file_path)

    if not text.strip():
        raise HTTPException(
            status_code=400,
            detail="No readable text found in image."
        )

    # Chunk
    chunks = chunk_text(text)

    # Embeddings
    embeddings = generate_embeddings(chunks)

    # Store in Qdrant
    create_collection()
    store_embeddings(chunks, embeddings)

    return {
        "status": "success",
        "type": "image",
        "filename": file.filename,
        "characters": len(text),
        "total_chunks": len(chunks),
        "embedding_dimension": len(embeddings[0]),
        "vectors_stored": len(embeddings),
        "extracted_text": text,
        "message": "Image processed successfully."
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