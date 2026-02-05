import cv2
import numpy as np
from app.core.logging import logger

class PreprocessingService:
    @staticmethod
    def correct_skew(image: np.ndarray) -> np.ndarray:
        """
        Detects text orientation and corrects skew.
        """
        try:
            # 1. Convert to grayscale if needed
            gray = image if len(image.shape) == 2 else cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # 2. Inverse thresholding (text becomes white on black background)
            # This helps in finding contours of the text blocks
            _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
            
            # 3. Find coords of all non-zero pixels
            coords = np.column_stack(np.where(thresh > 0))
            
            # 4. Compute the minimum area rectangle that covers the text
            if len(coords) == 0:
                logger.warning("No text detected for skew correction.")
                return image

            angle = cv2.minAreaRect(coords)[-1]
            
            # The angle logic in cv2.minAreaRect varies by version, specifically 4.5+ vs older
            # Normalizing angle to be -45 to 45
            if angle < -45:
                angle = -(90 + angle)
            elif angle > 45:
                angle = 90 - angle

            logger.debug(f"Detected skew angle: {angle:.2f} degrees")
            
            if abs(angle) < 0.5:
                # Negligible skew
                return image

            # 5. Rotate
            (h, w) = image.shape[:2]
            center = (w // 2, h // 2)
            M = cv2.getRotationMatrix2D(center, angle, 1.0)
            rotated = cv2.warpAffine(image, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
            
            return rotated

        except Exception as e:
            logger.error(f"Skew correction failed: {str(e)}")
            return image

    @staticmethod
    def enhance_image(image: np.ndarray) -> np.ndarray:
        """
        Applies a standard pipeline: Grayscale -> Denoise -> Adaptive Threshold.
        This prepares the image for OCR.
        """
        # 1. Grayscale
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image

        # 2. Rescaling if too small (Optional, skipping for now)

        # 3. Simple Binarization (Otsu) - Safer for general cases than Adaptive which can be noisy
        # But for now, let's just return the Grayscale image to Tesseract. 
        # Tesseract performs its own binarization internally which is usually very good.
        # Returning gray directly.
        
        return gray

    @staticmethod
    def get_layout_mask(image: np.ndarray) -> np.ndarray:
        """
        Heuristic to find text blocks. Returns a binary mask where blocks are white.
        """
        # Use dilation to merge words into lines/blocks
        gray = image if len(image.shape) == 2 else cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (15, 3)) # Wide kernel for horizontal text
        mask = cv2.dilate(thresh, kernel, iterations=1)
        return mask
