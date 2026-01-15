from pypdf import PdfWriter, PdfReader
import os
import logging
from typing import List

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def merge_pdfs(file_paths: List[str], output_path: str) -> str:
    """
    Merge multiple PDF files into one.
    
    Args:
        file_paths: List of absolute paths to the PDF files to merge.
        output_path: Absolute path where the merged PDF should be saved.
        
    Returns:
        The path to the output file if successful.
    """
    merger = PdfWriter()
    
    try:
        for path in file_paths:
            if os.path.exists(path):
                merger.append(path)
            else:
                logger.warning(f"File not found during merge: {path}")

        # Write the merged PDF
        merger.write(output_path)
        logger.info(f"Successfully merged {len(file_paths)} files to {output_path}")
        return output_path
        
    except Exception as e:
        logger.error(f"Error merging PDFs: {e}")
        raise
    finally:
        merger.close()
