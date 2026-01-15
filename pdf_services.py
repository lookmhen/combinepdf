from pypdf import PdfWriter, PdfReader
import fitz  # PyMuPDF
import os
import math
import logging
from typing import List, Tuple, Union

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

def add_watermark(file_path: str, output_path: str, watermark_config: dict, image_path: str = None) -> str:
    """
    Add watermark (text or image) to PDF.
    
    Args:
        file_path: Input PDF
        output_path: Output PDF
        watermark_config: Config dict (text, x, y, size, rotation, etc.)
        image_path: Path to image file for 'image' mode
    """
    try:
        doc = fitz.open(file_path)
        
        mode = watermark_config.get('mode', 'text')
        x_pct = float(watermark_config.get('x', 0))
        y_pct = float(watermark_config.get('y', 0))
        rotate = int(watermark_config.get('rotation', 0))
        opacity = float(watermark_config.get('opacity', 0.5))
        size_val = float(watermark_config.get('size', 40)) # Fontsize or Scale factor
        
        # Load image once if needed
        img_rect = None
        if mode == 'image' and image_path:
            img = fitz.open(image_path)
            # Size logic: Frontend sends "percentage of page width" (0.05 - 1.0)
            # We calculate this later PER PAGE because pages might vary in width.
            # Just keep the aspect ratio here.
            img_ratio = img[0].rect.height / img[0].rect.width
        
        for page in doc:
            rect = page.rect
            x_pos = rect.width * x_pct
            y_pos = rect.height * y_pct
            
            if mode == 'text':
                # Text logic remains same (size_val is fontsize in points)
                text = watermark_config.get('text', 'Watermark')
                color = watermark_config.get('color', '#000000')
                if color.startswith('#'):
                    color = tuple(int(color.lstrip('#')[i:i+2], 16)/255 for i in (0, 2, 4))
                
                # Use standard page.insert_text with morph for rotation
                font = fitz.Font("helv")
                text_width = font.text_length(text, int(size_val))
                text_height = int(size_val)
                
                start_x = x_pos - (text_width / 2)
                start_y = y_pos + (text_height / 3) 
                
                mat = fitz.Matrix(-rotate)
                pivot = fitz.Point(x_pos, y_pos)
                
                page.insert_text(
                    (start_x, start_y),
                    text,
                    fontsize=int(size_val),
                    color=color,
                    fontname="helv",
                    morph=(pivot, mat),
                    overlay=True,
                    fill_opacity=opacity
                )
                
            elif mode == 'image' and image_path:
                # Hybrid Approach:
                # 1. Use Pixmap to apply Opacity (Pixel manipulation).
                # 2. Save as PNG bytes.
                # 3. Use show_pdf_page for Rotation (Robust).
                
                pix = fitz.Pixmap(image_path)
                
                # Apply Opacity if needed
                if opacity < 1.0:
                    try:
                        # Ensure alpha channel exists
                        if not pix.alpha:
                            pix = fitz.Pixmap(fitz.csRGB, pix, 1)
                        
                        # Apply constant alpha mask
                        # Use fitz.csGRAY (UPPERCASE)
                        mask = fitz.Pixmap(fitz.csGRAY, pix.irect, False)
                        mask.clear_with(int(255 * opacity))
                        pix.set_alpha(mask.samples)
                    except Exception as e:
                        logger.warning(f"Opacity error: {e}")
                
                # Convert modified pixmap to PDF stream
                img_bytes = pix.tobytes("png")
                img_doc = fitz.open("png", img_bytes)
                pdf_bytes = img_doc.convert_to_pdf()
                img_doc.close()
                src_doc = fitz.open("pdf", pdf_bytes)
                
                # Calculate Dimensions
                # Original Image Aspect Ratio (from pixmap)
                img_ratio = pix.height / pix.width if pix.width > 0 else 1.0
                
                # Target Width (based on page width %)
                w = rect.width * size_val
                h = w * img_ratio
                
                # Scale Correction for Rotation (Prevent Shrinking)
                if rotate != 0:
                    rad = math.radians(-rotate)
                    c = abs(math.cos(rad))
                    s = abs(math.sin(rad))
                    
                    w_bb = (w * c) + (h * s)
                    h_bb = (w * s) + (h * c)
                else:
                    w_bb = w
                    h_bb = h
                
                target_rect = fitz.Rect(
                    x_pos - w_bb/2,
                    y_pos - h_bb/2,
                    x_pos + w_bb/2,
                    y_pos + h_bb/2
                )
                
                page.show_pdf_page(target_rect, src_doc, 0, rotate=-rotate)
                src_doc.close()
            
        doc.save(output_path)
        logger.info(f"Watermarked PDF saved to {output_path}")
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
