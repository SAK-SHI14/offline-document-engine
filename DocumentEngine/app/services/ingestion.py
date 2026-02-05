import cv2
import numpy as np
from PIL import Image, UnidentifiedImageError
import io
from fastapi import UploadFile, HTTPException
from typing import Tuple, Dict, Any
from app.core.logging import logger
from app.models.schema import ImageMetadata

class IngestionService:
    @staticmethod
    def _extract_metadata(image: np.ndarray, file_format: str = "unknown") -> ImageMetadata:
        """Extracts metadata from the loaded OpenCV image."""
        h, w = image.shape[:2]
        # Estimating DPI is hard without EXIF, defaulting to 72 or 300 if unknown
        # In a real scenario, we might read EXIF from the original bytes before CV2 conversion
        return ImageMetadata(
            width=w,
            height=h,
            dpi=0, # Placeholder, will need EXIF parsing if crucial
            format=file_format,
            color_space="BGR" if len(image.shape) == 3 else "GRAY"
        )

    @staticmethod
    async def process_upload(file: UploadFile) -> Tuple[np.ndarray, ImageMetadata]:
        """
        Reads a generic UploadFile, validates it, and converts strictly to an OpenCV array.
        """
        logger.info(f"Ingesting file: {file.filename}, Content-Type: {file.content_type}")
        
        if file.content_type not in ["image/jpeg", "image/png", "image/bmp", "image/tiff", "application/pdf"]:
            # Note: PDF support requires pdf2image, handling images only for now as per MVP constraints
            if file.content_type == "application/pdf":
                 raise HTTPException(status_code=400, detail="PDF input requires 'pdf2image' and poppler installed. Please upload an image for this version.")
            raise HTTPException(status_code=400, detail=f"Unsupported content type: {file.content_type}")

        try:
            contents = await file.read()
            # 1. basic PIL check (more robust for formats)
            try:
                pil_img = Image.open(io.BytesIO(contents))
                pil_img.verify() # Verify integrity
                pil_img = Image.open(io.BytesIO(contents)) # Re-open after verify
            except UnidentifiedImageError:
                raise HTTPException(status_code=400, detail="Invalid image file or corrupted data.")

            # 2. Convert to OpenCV format (numpy)
            # PIL -> Numpy -> BGR
            np_img = np.array(pil_img)
            
            # 3. Color space handling
            if len(np_img.shape) == 2:
                # Grayscale to BGR for consistency in standard pipeline
                cv_img = cv2.cvtColor(np_img, cv2.COLOR_GRAY2BGR)
            elif np_img.shape[2] == 3:
                # RGB (PIL) to BGR (OpenCV)
                cv_img = cv2.cvtColor(np_img, cv2.COLOR_RGB2BGR)
            elif np_img.shape[2] == 4:
                # RGBA to BGR
                cv_img = cv2.cvtColor(np_img, cv2.COLOR_RGBA2BGR)
            else:
                cv_img = np_img

            metadata = IngestionService._extract_metadata(cv_img, file_format=pil_img.format or "unknown")
            logger.info(f"Image loaded successfully: {metadata}")
            
            return cv_img, metadata

        except Exception as e:
            logger.error(f"Error processing upload: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Image ingestion failed: {str(e)}")
