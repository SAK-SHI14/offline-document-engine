import re
from typing import List
from app.models.schema import ExtractedEntities

class PostProcessingService:
    # Compile regex patterns once
    EMAIL_PATTERN = re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}')
    # Simple Currency finding $1,000.00 or 500 USD
    AMOUNT_PATTERN = re.compile(r'[\$€£]?\s?\d{1,3}(?:,\d{3})*(?:\.\d{2})?\s?(?:USD|EUR|GBP)?')
    # Simple Date finder YYYY-MM-DD or DD/MM/YYYY
    DATE_PATTERN = re.compile(r'\d{4}-\d{2}-\d{2}|\d{2}/\d{2}/\d{4}')

    @staticmethod
    def extract_entities(full_text: str) -> ExtractedEntities:
        """
        Extracts structured entities from unstructured text using Regex.
        In a production system, this could be swapped for a local SpaCy model.
        """
        entities = ExtractedEntities()
        
        if not full_text:
            return entities

        entities.emails = list(set(PostProcessingService.EMAIL_PATTERN.findall(full_text)))
        entities.dates = list(set(PostProcessingService.DATE_PATTERN.findall(full_text)))
        
        # Filter amounts to avoid capturing years or simple numbers
        raw_amounts = PostProcessingService.AMOUNT_PATTERN.findall(full_text)
        # Rudimentary filter: must contain currency symbol or decimal
        entities.amounts = [amt for amt in raw_amounts if '$' in amt or '.' in amt or 'USD' in amt]

        return entities

    @staticmethod
    def normalize_text(text: str) -> str:
        """
        Cleans up common OCR artifacts.
        """
        # Collapse multiple spaces
        text = re.sub(r'\s+', ' ', text)
        # Fix common OCR failures like | -> I or 0 -> O (context dependent, very risky without ML)
        # keeping it safe and simple for now.
        return text.strip()
