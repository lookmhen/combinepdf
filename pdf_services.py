from pypdf import PdfWriter, PdfReader
import fitz  # PyMuPDF
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

def rotate_pdf(file_path: str, output_path: str, rotations: dict) -> str:
    """
    Rotate specific pages of a PDF.
    
    Args:
        file_path: Path to the input PDF.
        output_path: Path to save the rotated PDF.
        rotations: Dictionary where key is page number (0-indexed) and value is rotation angle (90, 180, 270).
                   Example: {0: 90, 2: 180}
                   
    Returns:
        Path to output file.
    """
    reader = PdfReader(file_path)
    writer = PdfWriter()
    
    try:
        for i, page in enumerate(reader.pages):
            angle = rotations.get(str(i), 0) # JSON keys might be strings
            if angle != 0:
                # pypdf rotates clockwise
                page.rotate(angle)
            writer.add_page(page)
            
        with open(output_path, "wb") as f:
            writer.write(f)
            
        logger.info(f"Rotated PDF saved to {output_path}")
        return output_path
        
    except Exception as e:
        logger.error(f"Error rotating PDF: {e}")
        raise

def split_pdf(file_path: str, output_dir: str, page_selection: List[int] = None) -> List[str]:
    """
    Split PDF into multiple files or extract specific pages.
    
    Args:
        file_path: Path to input PDF.
        output_dir: Directory to save output files.
        page_selection: List of 0-indexed page numbers to extract. 
                        If None, splits all pages into individual files.
                        If provided, extracts those pages into a SINGLE new PDF.
        
    Returns:
        List of paths to generated files.
    """
    reader = PdfReader(file_path)
    generated_files = []
    
    try:
        if page_selection:
            # Extract specific pages into ONE new PDF
            writer = PdfWriter()
            for page_num in page_selection:
                if 0 <= page_num < len(reader.pages):
                    writer.add_page(reader.pages[page_num])
            
            output_filename = f"extracted_pages.pdf"
            output_path = os.path.join(output_dir, output_filename)
            
            with open(output_path, "wb") as f:
                writer.write(f)
            
            generated_files.append(output_path)
            logger.info(f"Extracted {len(page_selection)} pages to {output_path}")
            
        else:
            # Split ALL pages into individual files
            for i, page in enumerate(reader.pages):
                writer = PdfWriter()
                writer.add_page(page)
                
                output_filename = f"page_{i+1}.pdf"
                output_path = os.path.join(output_dir, output_filename)
                
                with open(output_path, "wb") as f:
                    writer.write(f)
                
                generated_files.append(output_path)
            logger.info(f"Split PDF into {len(generated_files)} individual files")
            
        return generated_files

    except Exception as e:
        logger.error(f"Error splitting PDF: {e}")
        raise

def pdf_to_images(file_path: str, output_dir: str) -> List[str]:
    """
    Convert each page of a PDF into a JPG image.
    
    Args:
        file_path: Path to input PDF.
        output_dir: Directory to save output images.
        
    Returns:
        List of paths to generated images.
    """
    generated_files = []
    
    try:
        doc = fitz.open(file_path)
        
        for i, page in enumerate(doc):
            pix = page.get_pixmap(matrix=fitz.Matrix(2, 2)) # 2x zoom for better quality
            
            output_filename = f"page_{i+1}.jpg"
            output_path = os.path.join(output_dir, output_filename)
            
            pix.save(output_path)
            generated_files.append(output_path)
            
        logger.info(f"Converted PDF to {len(generated_files)} images in {output_dir}")
        return generated_files
        
    except Exception as e:
        logger.error(f"Error converting PDF to images: {e}")
        raise

def images_to_pdf(image_paths: List[str], output_path: str) -> str:
    """
    Convert a list of images into a single PDF using PyMuPDF.
    
    Args:
        image_paths: List of absolute paths to images.
        output_path: Path to save the output PDF.
        
    Returns:
        Path to output file.
    """
    try:
        if not image_paths:
            raise ValueError("No images provided")

        doc = fitz.open()
        
        for path in image_paths:
            img = fitz.open(path) # Open image as document
            rect = img[0].rect # Get image dimensions
            pdfbytes = img.convert_to_pdf() # Convert to PDF stream
            img.close()
            
            imgPdf = fitz.open("pdf", pdfbytes) # Open stream as PDF
            page = doc.new_page(width = rect.width, height = rect.height)
            page.show_pdf_page(rect, imgPdf, 0) # Draw image PDF onto page
            
        doc.save(output_path)
        logger.info(f"Converted {len(image_paths)} images to PDF at {output_path}")
        return output_path
        
    except Exception as e:
        logger.error(f"Error converting images to PDF: {e}")
        raise

def add_watermark(file_path: str, output_path: str, watermark_config: dict) -> str:
    """
    Add a text watermark to a PDF.
    
    Args:
        file_path: Path to input PDF.
        output_path: Path to save output.
        watermark_config: Dict containing:
            - text: str
            - x_pct: float (0-1) position percent X
            - y_pct: float (0-1) position percent Y
            - font_size: int
            - rotation: int (degrees)
            - color: str (hex "#RRGGBB")
            - opacity: float (0-1) - Note: pymupdf verify support for text opacity, else ignore.
    """
    try:
        doc = fitz.open(file_path)
        
        # Parse color
        hex_color = watermark_config.get('color', '#000000')
        r = int(hex_color[1:3], 16) / 255.0
        g = int(hex_color[3:5], 16) / 255.0
        b = int(hex_color[5:7], 16) / 255.0
        color = (r, g, b)
        
        text = watermark_config.get('text', 'Watermark')
        fontsize = int(watermark_config.get('font_size', 24))
        rotate = int(watermark_config.get('rotation', 0))
        x_pct = float(watermark_config.get('x', 0))
        y_pct = float(watermark_config.get('y', 0))
        opacity = float(watermark_config.get('opacity', 0.5))
        
        logger.info(f"Watermark Config: Text='{text}', Color={color}, Rot={rotate}, Opacity={opacity}, Pos=({x_pct}, {y_pct})")
        
        for page in doc:
            rect = page.rect
            x_pos = rect.width * x_pct
            y_pos = rect.height * y_pct
            
            logger.info(f"Page Rect: {rect}, Insert Pos: ({x_pos}, {y_pos})")

            logger.info(f"Page Rect: {rect}, Insert Pos: ({x_pos}, {y_pos})")

            # Use standard page.insert_text with morph for rotation
            # Calculate centered pivot point from text size
            font = fitz.Font("helv")
            text_width = font.text_length(text, fontsize)
            text_height = fontsize 
            
            # We want visual center at (x_pos, y_pos).
            # Text normally starts at the insertion point.
            # So, initial insertion point (unrotated) should be:
            start_x = x_pos - (text_width / 2)
            start_y = y_pos + (text_height / 3) 
            
            # Setup Matrix for rotation
            # User reported "Mirror" effect on angles (likely direction mismatch).
            # Inverting the rotation to align with expectations.
            mat = fitz.Matrix(-rotate)
            
            # Pivot point for the rotation should be the visual center (x_pos, y_pos)
            pivot = fitz.Point(x_pos, y_pos)
            
            # Pass pivot and matrix to morph
            page.insert_text(
                (start_x, start_y),
                text,
                fontsize=fontsize,
                color=color,
                fontname="helv",
                morph=(pivot, mat),
                overlay=True,
                fill_opacity=opacity
            )

            
        doc.save(output_path)
        return output_path
        
    except Exception as e:
        logger.error(f"Error adding watermark: {e}")
        raise

def compress_pdf(file_path: str, output_path: str) -> str:
    """
    Compress PDF using PyMuPDF optimization.
    
    Args:
        file_path: Path to input PDF.
        output_path: Path to save output.
        
    Returns:
        Path to output file.
    """
    try:
        doc = fitz.open(file_path)
        
        # garbage=4: Check for identical objects and remove them.
        # deflate=True: Compress streams.
        doc.save(output_path, garbage=4, deflate=True)
        
        logger.info(f"Compressed PDF saved to {output_path}")
        return output_path
        
    except Exception as e:
        logger.error(f"Error compressing PDF: {e}")
        raise
