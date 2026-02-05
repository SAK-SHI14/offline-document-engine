import logging
import sys
from .config import settings

def setup_logging():
    logger = logging.getLogger("document_engine")
    logger.setLevel(logging.DEBUG if settings.DEBUG_MODE else logging.INFO)
    
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    # Console Handler
    ch = logging.StreamHandler(sys.stdout)
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    
    return logger

logger = setup_logging()
