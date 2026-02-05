import os

class Settings:
    APP_NAME: str = "Offline Document Engine"
    API_V1_STR: str = "/api/v1"
    
    # OCR Settings
    TESSERACT_CMD: str = os.getenv("TESSERACT_CMD", r"C:\Program Files\Tesseract-OCR\tesseract.exe")
    TESSDATA_DIR: str = os.getenv("TESSDATA_DIR", r"C:\Program Files\Tesseract-OCR\tessdata")
    
    # Processing Defaults
    DEFAULT_DPI: int = 300
    DEBUG_MODE: bool = False

settings = Settings()
