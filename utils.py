import os
import time
import logging
import uuid
from typing import List

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TEMP_DIR = 'temp'
MAX_LIFETIME = 3600  # 1 hour

def ensure_temp_directory_exists() -> None:
    """Ensure the temporary directory exists."""
    if not os.path.exists(TEMP_DIR):
        os.makedirs(TEMP_DIR)

def get_temp_path(filename: str = None) -> str:
    """
    Get a full path for a temporary file.
    If filename is not provided, generating a unique one.
    """
    ensure_temp_directory_exists()
    if not filename:
        filename = f"{uuid.uuid4()}.pdf"
    return os.path.join(TEMP_DIR, filename)

def cleanup_temp_files() -> None:
    """Remove expired temporary files."""
    if not os.path.exists(TEMP_DIR):
        return

    current_time = time.time()
    
    for file_name in os.listdir(TEMP_DIR):
        file_path = os.path.join(TEMP_DIR, file_name)
        
        # Skip if it's not a file
        if not os.path.isfile(file_path):
            continue
            
        try:
            file_age = current_time - os.path.getctime(file_path)
            if file_age > MAX_LIFETIME:
                os.remove(file_path)
                logger.info("Removed expired file: %s", file_path)
        except Exception as e:
            logger.error("Error removing file %s: %s", file_path, e)
            
    # Optional: cleanup empty directory if needed, but usually keeping it is fine
    try:
        if not os.listdir(TEMP_DIR):
            os.rmdir(TEMP_DIR)
    except OSError:
        pass
