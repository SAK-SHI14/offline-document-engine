from fastapi import APIRouter, UploadFile, File, HTTPException
from app.services.pipeline import DocumentPipeline
from app.models.schema import DocumentResponse
from app.core.logging import logger

router = APIRouter()

@router.post("/process", response_model=DocumentResponse)
async def process_document_endpoint(file: UploadFile = File(...)):
    """
    Upload an image document to be processed by the offline OCR engine.
    Returns structured JSON with layout, text, tables, and entities.
    """
    logger.info(f"Received request for file: {file.filename}")
    try:
        result = await DocumentPipeline.process_document(file)
        return result
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Unhandled pipeline error: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error during processing.")
