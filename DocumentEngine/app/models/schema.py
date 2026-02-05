from typing import List, Optional, Dict, Any, Union
from enum import Enum
from pydantic import BaseModel, Field, HttpUrl

# --- Enums ---
class DocumentType(str, Enum):
    UNKNOWN = "unknown"
    INVOICE = "invoice"
    FORM = "form"
    ID_CARD = "id"
    LETTER = "letter"

class BlockType(str, Enum):
    HEADER = "header"
    PARAGRAPH = "paragraph"
    TABLE = "table"
    KEY_VALUE = "key_value"
    IMAGE = "image"
    UNKNOWN = "unknown"

# --- Shared Structures ---
class BoundingBox(BaseModel):
    x1: int
    y1: int
    x2: int
    y2: int

class ConfidenceScore(BaseModel):
    score: float = Field(..., ge=0.0, le=100.0, description="Confidence score 0-100")

# --- Content Components ---
class Word(BaseModel):
    text: str
    bbox: List[int] = Field(..., min_items=4, max_items=4, description="[x1, y1, x2, y2]")
    confidence: float

class Line(BaseModel):
    text: str
    words: List[Word]
    bbox: List[int]
    confidence: float

class BlockContent(BaseModel):
    """Polymorphic content container for different block types"""
    text: Optional[str] = None
    key: Optional[str] = None
    value: Optional[str] = None
    # For tables, we might store simplified representation here or link to Table object
    row_index: Optional[int] = None
    col_index: Optional[int] = None

class LayoutBlock(BaseModel):
    type: BlockType
    id: str = Field(..., description="Unique block ID")
    bbox: List[int]
    confidence: float
    content: BlockContent
    children: Optional[List[str]] = Field(default=[], description="IDs of child blocks if hierarchical")

# --- Table Structures ---
class TableCell(BaseModel):
    text: str
    row_span: int = 1
    col_span: int = 1
    bbox: List[int]

class Table(BaseModel):
    id: str
    rows: List[List[TableCell]]
    confidence: float
    bbox: List[int]

# --- Entities ---
class ExtractedEntities(BaseModel):
    dates: List[str] = []
    amounts: List[str] = []
    ids: List[str] = []
    emails: List[str] = []
    phones: List[str] = []

# --- Metadata ---
class ImageMetadata(BaseModel):
    width: int
    height: int
    dpi: int = 0
    format: str
    color_space: str

class ProcessingMetadata(BaseModel):
    ocr_engine: str = "tesseract"
    model_type: str = "lstm"
    language: str = "eng"
    runtime_ms: float
    processed_offline: bool = True
    version: str = "1.0.0"

class TextContent(BaseModel):
    full_text: str
    lines: List[Line] = []
    words: List[Word] = []

# --- TOP LEVEL RESPONSE ---
class DocumentResponse(BaseModel):
    document_id: str
    document_type: DocumentType = DocumentType.UNKNOWN
    processing_mode: str = "offline"
    image_metadata: ImageMetadata
    layout: Dict[str, List[LayoutBlock]] = Field(default_factory=lambda: {"blocks": []})
    text_content: TextContent
    tables: List[Table] = []
    entities: ExtractedEntities = Field(default_factory=ExtractedEntities)
    processing_metadata: ProcessingMetadata
