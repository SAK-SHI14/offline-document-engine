import time
import uuid
import numpy as np
from fastapi import UploadFile
from app.models.schema import DocumentResponse, ProcessingMetadata, LayoutBlock
from app.core.logging import logger
from app.services.ingestion import IngestionService
from app.services.preprocessing import PreprocessingService
from app.services.ocr_service import OCRService
from app.services.layout_engine import LayoutEngine
from app.services.postprocessing import PostProcessingService

class DocumentPipeline:
    @staticmethod
    async def process_document(file: UploadFile) -> DocumentResponse:
        start_time = time.time()
        
        # 1. Ingestion
        try:
            image, metadata = await IngestionService.process_upload(file)
        except Exception as e:
            raise e

        # 2. Preprocessing
        # Deskew
        image_deskewed = PreprocessingService.correct_skew(image)
        # Enhance for OCR
        image_for_ocr = PreprocessingService.enhance_image(image_deskewed)

        # 3. OCR Core
        # Pass the preprocessed image to Tesseract
        text_content = OCRService.run_ocr(image_for_ocr)

        # 4. Layout Analysis
        # Use deskewed (but not binary/thresholded) image for table detection usually, 
        # but here we use the original image's shape mostly.
        tables = LayoutEngine.detect_tables(image_deskewed)
        
        # Classify Blocks from OCR lines
        # Group lines into blocks if needed. Using simplified line-based block approach for now.
        layout_blocks = LayoutEngine.classify_blocks(text_content.lines)

        # 5. Post Processing
        entities = PostProcessingService.extract_entities(text_content.full_text)
        normalized_text = PostProcessingService.normalize_text(text_content.full_text)
        text_content.full_text = normalized_text

        # 6. Serialization Construction
        process_time_ms = (time.time() - start_time) * 1000
        
        proc_metadata = ProcessingMetadata(
            runtime_ms=round(process_time_ms, 2),
            ocr_engine="tesseract",
            model_type="lstm"
        )
        
        response = DocumentResponse(
            document_id=uuid.uuid4().hex,
            document_type="unknown", # Could add ML classifier here
            image_metadata=metadata,
            layout={"blocks": layout_blocks},
            text_content=text_content,
            tables=tables,
            entities=entities,
            processing_metadata=proc_metadata
        )
        
        logger.info(f"Pipeline finished in {process_time_ms:.2f}ms")
        return response
