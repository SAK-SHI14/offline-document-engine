import cv2
import numpy as np
from typing import List, Dict, Any, Tuple
from app.models.schema import LayoutBlock, BlockType, BlockContent, Table, TableCell
from app.core.logging import logger
import uuid

class LayoutEngine:
    @staticmethod
    def detect_tables(image: np.ndarray) -> List[Table]:
        """
        Detects tables using morphological operations to find grid lines.
        """
        tables = []
        try:
            gray = image if len(image.shape) == 2 else cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            # Binary threshold
            thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY_INV, 11, 2)
            
            # Detect horizontal lines
            horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (25, 1))
            detect_horizontal = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, horizontal_kernel, iterations=2)
            
            # Detect vertical lines
            vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 25))
            detect_vertical = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, vertical_kernel, iterations=2)
            
            # Combine
            mask = detect_horizontal + detect_vertical
            
            # Find contours of the grid
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            for i, cnt in enumerate(contours):
                x, y, w, h = cv2.boundingRect(cnt)
                # Filter small noise
                if w > 50 and h > 50:
                    # This is likely a table area
                    tables.append(Table(
                        id=f"table_{uuid.uuid4().hex[:8]}",
                        rows=[], # Cell extraction would require analyzing intersections inside this ROI
                        confidence=0.8,
                        bbox=[x, y, x+w, y+h]
                    ))
            
            logger.debug(f"Detected {len(tables)} potential tables.")
            return tables

        except Exception as e:
            logger.error(f"Table detection failed: {str(e)}")
            return []

    @staticmethod
    def classify_blocks(ocr_lines: List[Any]) -> List[LayoutBlock]:
        """
        Classifies lines into Headers, Paragraphs, etc. based on font properties.
        Expects a list of 'Line' objects from the OCR service.
        """
        blocks = []
        if not ocr_lines:
            return blocks

        # 1. Calc median height to establish "body text" size
        heights = [(line.bbox[3] - line.bbox[1]) for line in ocr_lines]
        median_height = np.median(heights) if heights else 10
        
        # 2. Iterate and classify
        for line in ocr_lines:
            h = line.bbox[3] - line.bbox[1]
            conf = line.confidence
            
            # Heuristic: Header if significantly larger (1.5x) or all caps (and not tiny)
            is_header = False
            if h > median_height * 1.5:
                is_header = True
            elif line.text.isupper() and len(line.text) < 50 and h > median_height: 
                # Short all-caps lines are often section headers
                is_header = True

            block_type = BlockType.HEADER if is_header else BlockType.PARAGRAPH
            
            blocks.append(LayoutBlock(
                type=block_type,
                id=f"blk_{uuid.uuid4().hex[:8]}",
                bbox=line.bbox,
                confidence=conf,
                content=BlockContent(text=line.text)
            ))
            
        return blocks
