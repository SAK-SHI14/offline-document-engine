import pytesseract
from pytesseract import Output
import numpy as np
from typing import List, Dict, Any, Tuple
from app.core.config import settings
from app.core.logging import logger
from app.models.schema import Word, Line, TextContent, BoundingBox

# Configure Tesseract Path globally
pytesseract.pytesseract.tesseract_cmd = settings.TESSERACT_CMD

class OCRService:
    @staticmethod
    def run_ocr(image: np.ndarray, lang: str = "eng") -> TextContent:
        """
        Executes Tesseract with 'image_to_data' to get granular info (words, boxes, conf).
        Parses the raw dict result into structured Pydantic models.
        """
            # Check if binary exists
            import os
            if not os.path.exists(settings.TESSERACT_CMD):
                error_msg = f"Tesseract not found at {settings.TESSERACT_CMD}. Please install Tesseract-OCR."
                logger.error(error_msg)
                # Raise specific exception that will be caught and shown as 500
                raise FileNotFoundError(error_msg)

            # PSM 3 is default (Fully automatic page segmentation, but no OSD)
            custom_config = r'--oem 3 --psm 3'
            
            logger.debug(f"Starting OCR with lang={lang}, config={custom_config}")
            
            # image_to_data returns a dict with lists: 'text', 'left', 'top', 'width', 'height', 'conf', 'level', 'page_num', 'block_num', 'par_num', 'line_num', 'word_num'
            data = pytesseract.image_to_data(image, lang=lang, config=custom_config, output_type=Output.DICT)
            
            words: List[Word] = []
            lines_map: Dict[Tuple[int, int, int], List[Word]] = {} # (block, par, line) -> [Words]
            full_text_builder = []

            n_boxes = len(data['text'])
            for i in range(n_boxes):
                text_content = data['text'][i].strip()
                confidence = float(data['conf'][i])
                
                # Tesseract returns conf -1 for empty blocks/structure
                if confidence > 0 and text_content:
                    x, y, w, h = data['left'][i], data['top'][i], data['width'][i], data['height'][i]
                    bbox = [x, y, x + w, y + h]
                    
                    word_obj = Word(text=text_content, bbox=bbox, confidence=confidence)
                    words.append(word_obj)
                    
                    # Grouping logic
                    block_num = data['block_num'][i]
                    par_num = data['par_num'][i]
                    line_num = data['line_num'][i]
                    
                    key = (block_num, par_num, line_num)
                    if key not in lines_map:
                        lines_map[key] = []
                    lines_map[key].append(word_obj)

            # Reconstruct Lines
            lines_list: List[Line] = []
            sorted_keys = sorted(lines_map.keys()) # Sort by block, then par, then line
            
            for key in sorted_keys:
                line_words = lines_map[key]
                if not line_words:
                    continue
                
                # Compute line bounding box (min x/y, max x/y of words)
                x1 = min(w.bbox[0] for w in line_words)
                y1 = min(w.bbox[1] for w in line_words)
                x2 = max(w.bbox[2] for w in line_words)
                y2 = max(w.bbox[3] for w in line_words)
                
                # Join text
                line_str = " ".join([w.text for w in line_words])
                full_text_builder.append(line_str)
                
                # Avg confidence
                avg_conf = sum(w.confidence for w in line_words) / len(line_words)
                
                lines_list.append(Line(
                    text=line_str,
                    words=line_words,
                    bbox=[x1, y1, x2, y2],
                    confidence=avg_conf
                ))

            full_text = "\n".join(full_text_builder)
            
            logger.info(f"OCR Complete. Found {len(lines_list)} lines, {len(words)} words.")
            
            return TextContent(
                full_text=full_text,
                lines=lines_list,
                words=words
            )

        except Exception as e:
            logger.error(f"OCR Execution failed: {str(e)}")
            # Re-raise so the pipeline knows it failed
            raise e
