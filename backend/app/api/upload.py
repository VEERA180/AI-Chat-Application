# ============================================================
# upload.py
# ------------------------------------------------------------
# Responsibility:
#   - Handle document upload API request
#   - Validate uploaded file
#   - Validate file size
#   - Save the uploaded PDF
#   - Extract text from the PDF
#   - Clean the extracted text
#   - Send the cleaned text to the chunking service
#
# Note:
#   Chunking logic is kept separately inside:
#       app/services/chunking.py
#
# This follows the Separation of Concerns principle.
# ============================================================


# ------------------------------------------------------------
# FastAPI imports
# ------------------------------------------------------------
# APIRouter:
#   Used to create a separate group of API endpoints.
#
# UploadFile:
#   Represents the uploaded file received from the client.
#
# File:
#   Tells FastAPI that the parameter should be received
#   as a multipart/form-data file.
# ------------------------------------------------------------
from fastapi import APIRouter, UploadFile, File


# ------------------------------------------------------------
# Path import
# ------------------------------------------------------------
# Path provides a clean and platform-independent way to
# work with file and directory paths.
# ------------------------------------------------------------
from pathlib import Path


# ------------------------------------------------------------
# PDF reader
# ------------------------------------------------------------
# PdfReader is used to extract text from PDF documents.
# ------------------------------------------------------------
from pypdf import PdfReader


# ------------------------------------------------------------
# Chunking service
# ------------------------------------------------------------
# Import the chunking function from our service layer.
#
# This keeps chunking logic outside the API layer.
# ------------------------------------------------------------
from app.services.chunking import create_chunks


# ------------------------------------------------------------
# Create API router
# ------------------------------------------------------------
# This router will be registered in main.py.
# ------------------------------------------------------------
router = APIRouter()


# ============================================================
# Upload Configuration
# ============================================================


# ------------------------------------------------------------
# Directory where uploaded documents will be stored.
#
# Path("uploads") creates the uploads directory relative
# to the application's current working directory.
# ------------------------------------------------------------
UPLOAD_DIR = Path("uploads")


# ------------------------------------------------------------
# Create the uploads directory if it does not already exist.
#
# exist_ok=True prevents an error if the directory already
# exists.
# ------------------------------------------------------------
UPLOAD_DIR.mkdir(exist_ok=True)


# ------------------------------------------------------------
# Allowed document extensions.
#
# Currently our RAG application supports PDF files only.
# ------------------------------------------------------------
ALLOWED_EXTENSIONS = {".pdf"}


# ------------------------------------------------------------
# Maximum allowed file size.
#
# 10 * 1024 * 1024 bytes = 10 MB
# ------------------------------------------------------------
MAX_FILE_SIZE = 10 * 1024 * 1024


# ============================================================
# Upload API
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
        Return processing information
    """

    # --------------------------------------------------------
    # Step 1: Validate file extension
    # --------------------------------------------------------
    # Extract the extension from the uploaded filename.
    #
    # Example:
    #   "document.pdf" → ".pdf"
    #
    # lower() ensures that:
    #   .PDF
    #   .Pdf
    #   .pdf
    #
    # are treated the same way.
    # --------------------------------------------------------
    extension = Path(file.filename).suffix.lower()

    # --------------------------------------------------------
    # Check whether the uploaded file is a supported type.
    # --------------------------------------------------------
    if extension not in ALLOWED_EXTENSIONS:
        return {
            "message": "Only PDF files are allowed"
        }


    # --------------------------------------------------------
    # Step 2: Validate file size
    # --------------------------------------------------------
    # We read the uploaded file in 1 MB chunks instead of
    # loading the complete file into memory at once.
    #
    # This is better for memory usage, especially when
    # processing larger files.
    # --------------------------------------------------------
    file_size = 0

    while True:

        # Read up to 1 MB from the uploaded file.
        chunk = await file.read(1024 * 1024)

        # If no data is returned, we reached the end of file.
        if not chunk:
            break

        # Add the number of bytes read to the total size.
        file_size += len(chunk)

        # Stop processing if the file exceeds the limit.
        if file_size > MAX_FILE_SIZE:
            return {
                "message": "File size must be less than 10 MB"
            }


    # --------------------------------------------------------
    # Step 3: Reset file position
    # --------------------------------------------------------
    # The previous step read the complete file.
    #
    # seek(0) moves the file pointer back to the beginning
    # so that we can read the file again while saving it.
    # --------------------------------------------------------
    await file.seek(0)


    # --------------------------------------------------------
    # Step 4: Create the destination file path
    # --------------------------------------------------------
    #
    # Example:
    #
    #   uploads/
    #       Veera_RPA_Senior_Lead.pdf
    #
    # --------------------------------------------------------
    file_path = UPLOAD_DIR / file.filename


    # --------------------------------------------------------
    # Step 5: Save the uploaded PDF
    # --------------------------------------------------------
    # "wb" means:
    #
    #   w → write mode
    #   b → binary mode
    #
    # PDF files must be handled as binary data.
    # --------------------------------------------------------
    with open(file_path, "wb") as buffer:

        # Read the uploaded file and write it to disk.
        buffer.write(await file.read())


    # ========================================================
    # Step 6: Extract text from PDF
    # ========================================================

    # --------------------------------------------------------
    # Create a PdfReader instance for the saved PDF.
    # --------------------------------------------------------
    reader = PdfReader(file_path)


    # --------------------------------------------------------
    # Variable used to store all extracted text.
    # --------------------------------------------------------
    text = ""


    # --------------------------------------------------------
    # Extract text from every page.
    # --------------------------------------------------------
    for page in reader.pages:

        # ----------------------------------------------------
        # extract_text() may return None for pages that do not
        # contain extractable text.
        #
        # "or ''" ensures that we always append a string.
        # ----------------------------------------------------
        text += page.extract_text() or ""


    # ========================================================
    # Step 7: Clean extracted text
    # ========================================================

    # --------------------------------------------------------
    # Remove leading and trailing whitespace.
    # --------------------------------------------------------
    text = text.strip()


    # --------------------------------------------------------
    # Normalize whitespace.
    #
    # Multiple spaces, tabs and newlines are converted into
    # a single space.
    #
    # Example:
    #
    #   "Hello     World\n\nRAG"
    #
    # becomes:
    #
    #   "Hello World RAG"
    # --------------------------------------------------------
    text = " ".join(text.split())


    # ========================================================
    # Step 8: Create document chunks
    # ========================================================

    # --------------------------------------------------------
    # Send the cleaned text to the chunking service.
    #
    # The actual chunking logic is NOT inside upload.py.
    #
    # It is maintained inside:
    #
    #   app/services/chunking.py
    #
    # This makes the application easier to maintain and test.
    # --------------------------------------------------------
    chunks = create_chunks(text)


    # ========================================================
    # Step 9: Return processing result
    # ========================================================

    return {
        "message": "Document uploaded successfully",
        "filename": file.filename,
        "text_length": len(text),
        "chunk_count": len(chunks),
        "chunks": chunks
    }