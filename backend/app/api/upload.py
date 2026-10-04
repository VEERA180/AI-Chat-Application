# ============================================================
# upload.py
# ------------------------------------------------------------
# Responsibility:
#   1. Receive a PDF file from the user
#   2. Validate the file type
#   3. Validate the file size
#   4. Save the PDF locally
#   5. Extract text from the PDF
#   6. Clean the extracted text
#   7. Create text chunks
#   8. Generate an embedding vector for every chunk
#   9. Return processing information
#
# Architecture:
#
#   React Frontend
#        ↓
#   FastAPI /upload
#        ↓
#   Validate PDF
#        ↓
#   Save PDF
#        ↓
#   Extract Text
#        ↓
#   Clean Text
#        ↓
#   Chunk Text
#        ↓
#   Azure OpenAI Embeddings
#        ↓
#   Embedding Vectors
#
# Note:
#   Currently embeddings are only generated in memory.
#   We will store them in a vector database in a later step.
# ============================================================


# ------------------------------------------------------------
# Imports
# ------------------------------------------------------------

from pathlib import Path

from fastapi import APIRouter, UploadFile, File
from pypdf import PdfReader

# Chunking service
from app.services.chunking import create_chunks

# Embedding service
from app.services.embedding import create_embedding


# ------------------------------------------------------------
# Create API Router
# ------------------------------------------------------------

router = APIRouter()


# ------------------------------------------------------------
# Upload directory
# ------------------------------------------------------------
# Uploaded PDF files will be stored inside the "uploads"
# directory.
#
# exist_ok=True means:
#   - Create the directory if it doesn't exist.
#   - Do nothing if it already exists.
# ------------------------------------------------------------

UPLOAD_DIR = Path("uploads")

UPLOAD_DIR.mkdir(exist_ok=True)


# ------------------------------------------------------------
# File validation configuration
# ------------------------------------------------------------

# Only PDF files are currently supported.
ALLOWED_EXTENSIONS = {".pdf"}


# Maximum allowed file size:
# 10 MB
#
# Calculation:
# 10 × 1024 × 1024 bytes
# ------------------------------------------------------------

MAX_FILE_SIZE = 10 * 1024 * 1024


# ============================================================
# Upload Document API
# ============================================================

@router.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    """
    Upload and process a PDF document.

    Processing flow:

        Upload PDF
            ↓
        Validate extension
            ↓
        Validate file size
            ↓
        Save PDF
            ↓
        Extract text
            ↓
        Clean text
            ↓
        Create chunks
            ↓
        Generate embeddings
            ↓
        Return processing information
    """

    # --------------------------------------------------------
    # Step 1: Validate file extension
    # --------------------------------------------------------
    # Example:
    #
    # "sample.pdf" → ".pdf"
    #
    # lower() ensures that:
    #
    # ".PDF"
    # ".Pdf"
    # ".pdf"
    #
    # are treated the same way.
    # --------------------------------------------------------

    extension = Path(file.filename).suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        return {
            "message": "Only PDF files are allowed"
        }


    # --------------------------------------------------------
    # Step 2: Validate file size
    # --------------------------------------------------------
    #
    # We read the uploaded file in 1 MB pieces instead of
    # loading the entire file into memory at once.
    #
    # This is better for memory usage.
    # --------------------------------------------------------

    file_size = 0

    while True:

        # Read up to 1 MB at a time
        chunk = await file.read(1024 * 1024)

        # No more data
        if not chunk:
            break

        # Add the number of bytes read
        file_size += len(chunk)

        # Stop if file exceeds 10 MB
        if file_size > MAX_FILE_SIZE:
            return {
                "message": "File size must be less than 10 MB"
            }


    # --------------------------------------------------------
    # Step 3: Reset file position
    # --------------------------------------------------------
    #
    # We already read the file while checking its size.
    #
    # seek(0) moves the file pointer back to the beginning
    # so we can read the file again when saving it.
    # --------------------------------------------------------

    await file.seek(0)


    # --------------------------------------------------------
    # Step 4: Create file path
    # --------------------------------------------------------
    #
    # Example:
    #
    # uploads/Veera_RPA_Senior_Lead.pdf
    # --------------------------------------------------------

    file_path = UPLOAD_DIR / file.filename


    # --------------------------------------------------------
    # Step 5: Save uploaded PDF
    # --------------------------------------------------------

    with open(file_path, "wb") as buffer:

        # Read the uploaded file and write it to disk
        buffer.write(await file.read())


    # --------------------------------------------------------
    # Step 6: Read PDF
    # --------------------------------------------------------
    #
    # PdfReader reads the saved PDF file so that we can
    # extract text from its pages.
    # --------------------------------------------------------

    reader = PdfReader(file_path)


    # --------------------------------------------------------
    # Step 7: Extract text
    # --------------------------------------------------------
    #
    # Start with an empty string.
    # We will append text from every PDF page.
    # --------------------------------------------------------

    text = ""


    # Loop through every page in the PDF
    for page in reader.pages:

        # extract_text() can sometimes return None.
        #
        # "or ''" ensures that we always append a string.
        text += page.extract_text() or ""


    # --------------------------------------------------------
    # Step 8: Clean extracted text
    # --------------------------------------------------------
    #
    # strip():
    #   Removes leading and trailing whitespace.
    #
    # split():
    #   Splits text based on whitespace.
    #
    # " ".join():
    #   Combines the words using a single space.
    #
    # This removes unnecessary newlines and repeated spaces.
    # --------------------------------------------------------

    text = text.strip()

    text = " ".join(text.split())


    # --------------------------------------------------------
    # Step 9: Create text chunks
    # --------------------------------------------------------
    #
    # The chunking service divides the large document text
    # into smaller pieces.
    #
    # Example:
    #
    # Document
    #    ↓
    # Chunk 1
    # Chunk 2
    # Chunk 3
    # ...
    # --------------------------------------------------------

    chunks = create_chunks(text)


    # --------------------------------------------------------
    # Step 10: Generate embeddings
    # --------------------------------------------------------
    #
    # Every chunk is sent to Azure OpenAI.
    #
    # Example:
    #
    # Chunk 1 → Embedding Vector 1
    # Chunk 2 → Embedding Vector 2
    # Chunk 3 → Embedding Vector 3
    #
    # Each vector currently contains 1536 numbers because
    # we are using text-embedding-3-small with the current
    # configuration.
    # --------------------------------------------------------

    embeddings = []

    for chunk in chunks:

        # Generate embedding for the current chunk
        embedding = create_embedding(chunk)

        # Store the embedding vector in our list
        embeddings.append(embedding)


    # --------------------------------------------------------
    # Step 11: Return processing information
    # --------------------------------------------------------
    #
    # IMPORTANT:
    # We are returning the embeddings temporarily for testing.
    #
    # In the final architecture, we should NOT return all
    # embedding vectors to the frontend.
    #
    # Instead:
    #
    # Chunk + Embedding
    #        ↓
    # Vector Database
    #
    # We will implement that later.
    # --------------------------------------------------------

    return {
        "message": "Document uploaded and embeddings generated successfully",
        "filename": file.filename,
        "text_length": len(text),
        "chunk_count": len(chunks),
        "embedding_count": len(embeddings),
        "embedding_dimensions": len(embeddings[0]) if embeddings else 0,
        "chunks": chunks,
        "embeddings": embeddings
    }