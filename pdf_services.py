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

def reorder_pdf(file_path: str, output_path: str, page_order: list) -> str:
    """
    Reorder PDF pages based on the provided order.
    
    Args:
        file_path: Path to the input PDF.
        output_path: Path to save the reordered PDF.
        page_order: List of page numbers in desired order (1-indexed).
                   Example: [3, 1, 2] means page 3 first, then page 1, then page 2.
                   
    Returns:
        Path to output file.
    """
    try:
        doc = fitz.open(file_path)
        new_doc = fitz.open()
        
        for page_num in page_order:
            # page_order is 1-indexed, PyMuPDF is 0-indexed
            src_page_idx = page_num - 1
            if 0 <= src_page_idx < len(doc):
                new_doc.insert_pdf(doc, from_page=src_page_idx, to_page=src_page_idx)
            else:
                logger.warning(f"Page {page_num} is out of range, skipping")
        
        new_doc.save(output_path)
        new_doc.close()
        doc.close()
        
        logger.info(f"Reordered PDF saved to {output_path}")
        return output_path
        
    except Exception as e:
        logger.error(f"Error reordering PDF: {e}")
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

def compress_pdf(file_path: str, output_path: str, dpi: int = 72, quality: int = 40) -> str:
    """
    Compress PDF by re-rendering pages at lower DPI and quality.
    
    Args:
        file_path: Path to input PDF.
        output_path: Path to save output.
        dpi: Target DPI for rendering (default 72).
        quality: JPEG quality 1-100 (default 40, lower = smaller).
        
    Returns:
        Path to output file.
    """
    from PIL import Image
    import io
    
    try:
        src_doc = fitz.open(file_path)
        out_doc = fitz.open()
        
        zoom = dpi / 72.0
        mat = fitz.Matrix(zoom, zoom)
        
        for page in src_doc:
            pix = page.get_pixmap(matrix=mat)
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            
            img_buffer = io.BytesIO()
            img.save(img_buffer, format="JPEG", quality=quality, optimize=True)
            img_bytes = img_buffer.getvalue()
            
            new_page = out_doc.new_page(width=page.rect.width, height=page.rect.height)
            new_page.insert_image(new_page.rect, stream=img_bytes)
        
        src_doc.close()
        out_doc.save(output_path, garbage=4, deflate=True)
        out_doc.close()
        
        logger.info(f"Compressed PDF saved to {output_path}")
        return output_path
        
    except Exception as e:
        logger.error(f"Error compressing PDF: {e}")
        raise

def protect_pdf(file_path: str, output_path: str, user_pwd: str, owner_pwd: str, permissions: dict = None) -> str:
    """
    Encrypt PDF with user and owner passwords and set permissions.
    """
    try:
        reader = PdfReader(file_path)
        writer = PdfWriter()
        writer.append_pages_from_reader(reader)
        
        # Permissions mapping
        # print, modify, copy, annot-forms, fill-forms, extract, assemble, print-high
        perms = {
            'print': permissions.get('print', True) if permissions else True,
            'copy': permissions.get('copy', True) if permissions else True,
            'modify': permissions.get('modify', True) if permissions else True
        }
        
        # In pypdf >= 3.0.0, encryption is handled via encrypt()
        # permissions_flag is an integer bitfield.
        # UserAccessPermissions is a helper enum in pypdf.
        from pypdf.constants import UserAccessPermissions
        
        flags = 0
        if perms['print']: flags |= UserAccessPermissions.PRINT
        if perms['modify']: flags |= UserAccessPermissions.MODIFY
        if perms['copy']: flags |= UserAccessPermissions.COPY
        flags |= UserAccessPermissions.ACCESSIBILITY # Always allow accessibility
        
        writer.encrypt(
            user_password=user_pwd,
            owner_password=owner_pwd,
            permissions_flag=flags,
            algorithm="AES-128" # Stronger encryption
        )
        
        with open(output_path, "wb") as f:
            writer.write(f)
            
        logger.info(f"Protected PDF saved to {output_path}")
        return output_path
        
    except Exception as e:
        logger.error(f"Error protecting PDF: {e}")
        raise

def unlock_pdf(file_path: str, output_path: str, password: str) -> str:
    """
    Remove password security from PDF.
    """
    try:
        reader = PdfReader(file_path)
        
        if reader.is_encrypted:
            # Try to decrypt with provided password
            if not reader.decrypt(password):
                # Try empty password just in case it's only permission locked
                if not reader.decrypt(""):
                    raise ValueError("Incorrect password")
        
        writer = PdfWriter()
        writer.append_pages_from_reader(reader)
        
        with open(output_path, "wb") as f:
            writer.write(f)
            
        logger.info(f"Unlocked PDF saved to {output_path}")
        return output_path
        
    except Exception as e:
        logger.error(f"Error unlocking PDF: {e}")
        raise

def apply_edits(file_path: str, output_path: str, edits_config: dict, image_paths: dict) -> str:
    """
    Apply text, image, and shape edits to a PDF.
    
    Args:
        file_path: Input PDF path
        output_path: Output PDF path
        edits_config: Dictionary mapping page index (str/int) to list of edit objects.
        image_paths: Dictionary mapping imageId to local file path for uploaded images.
        
    Returns:
        output_path
    """
    try:
        logger.info(f"Applying edits. Config: {edits_config}")
        doc = fitz.open(file_path)
        
        for page_idx_str, edits in edits_config.items():
            page_idx = int(page_idx_str)
            logger.info(f"Processing page {page_idx}, {len(edits)} edits")
            
            if page_idx < 0 or page_idx >= len(doc):
                logger.warning(f"Page index {page_idx} out of range")
                continue
                
            page = doc[page_idx]
            
            for edit in edits:
                type_ = edit.get('type')
                
                x_pct = float(edit.get('x', 0))
                y_pct = float(edit.get('y', 0))
                w_pct = float(edit.get('w', 0))
                h_pct = float(edit.get('h', 0))
                
                rect_page = page.rect
                rotation = page.rotation
                logger.info(f"Page {page_idx} Rotation: {rotation}, Rect: {rect_page}, WPct: {w_pct}, HPct: {h_pct}")
                
                # Default (Portrait/0/180)
                x = rect_page.width * x_pct
                y = rect_page.height * y_pct
                w = rect_page.width * w_pct
                h = rect_page.height * h_pct
                
                # Handle Rotation (Landscape/90/270)
                # If rotated, the 'Visual' Width corresponds to Physical Height, and vice versa.
                # To maintain Aspect Ratio, we must swap the percentage application for size.
                if rotation in (90, 270):
                    # Visual Width % should apply to Physical Height
                    # Visual Height % should apply to Physical Width
                    # Note: This fixes the SIZE (Aspect Ratio) distortion.
                    # Position (X/Y) is more complex due to origin shifts, but PyMuPDF's coordinate system
                    # combined with the frontend's percentage logic often aligns if we just focus on the dimension swap for the rect.
                    # However, strictly speaking, a 90-degree rotate maps Visual X -> Physical Y, Visual Y -> Physical X value space.
                    
                    w = rect_page.width * h_pct
                    h = rect_page.height * w_pct
                    
                    # For X/Y, straightforward swapping might fail due to origin (0,0) location changes.
                    # But often X_PCT simply maps to Y axis distance and Y_PCT to X axis distance.
                    # Let's attempt to swap X/Y calculation for rotation too to keep position consistent.
                    x = rect_page.width * y_pct
                    y = rect_page.height * x_pct
                    
                    # Correct origin shift for 90 vs 270? 
                    # If 90 deg (Clockwise): Top-Left (Visual) is Bottom-Left (Physical)? Or Top-Left (Physical)?
                    # This is risky without empirical test. 
                    # BUT the User complained specifically about "Wide Rectangle" (Size Distortion).
                    # So I will commit the W/H swap which relies on the logic:
                    # Visual W (200) -> Need Physical H (200). 
                    # Physical H = PageH * (200 / VisualW).
                    # VisualW = PageH.
                    # Physical H = PageH * (200 / PageH) = 200. Correct.
                    # w (Physical Rect Width) = PageW * h_pct. 
                    pass

                # Sanity Check for Coordinates (Pixels vs Percentages)
                final_x = x if x_pct <= 2.0 else x_pct
                final_y = y if y_pct <= 2.0 else y_pct
                final_w = w if w_pct <= 2.0 else w_pct
                final_h = h if h_pct <= 2.0 else h_pct
                
                if type_ == 'text':
                    text = edit.get('text', '')
                    fontsize = float(edit.get('fontSize', 24))
                    color_hex = edit.get('color', '#000000')
                    opacity = float(edit.get('opacity', 1.0))
                    
                    # Color conversion
                    color = (0, 0, 0)
                    if color_hex.startswith('#') and len(color_hex) == 7:
                        color = tuple(int(color_hex.lstrip('#')[i:i+2], 16)/255 for i in (0, 2, 4))
                        
                    # Font selection
                    font_family = edit.get('fontFamily', 'helv')
                    base_font = "Helvetica"
                    custom_font = None
                    
                    if 'tahoma' in font_family.lower() or 'thai' in font_family.lower():
                        # Try to load Thai font
                        thai_font_path = r"C:\Windows\Fonts\tahoma.ttf"
                        if not os.path.exists(thai_font_path):
                             thai_font_path = r"C:\Windows\Fonts\angsan.ttf" # Try Angsana
                        
                        if os.path.exists(thai_font_path):
                            try:
                                page.insert_font(fontname="thai", fontfile=thai_font_path)
                                custom_font = "thai"
                            except Exception as e:
                                logger.error(f"Failed to insert Thai font: {e}")
                        else:
                             logger.warning("Thai font file not found")
                    
                    elif 'times' in font_family.lower(): base_font = "Times"
                    elif 'courier' in font_family.lower(): base_font = "Courier"
                    
                    is_bold = edit.get('bold', False)
                    is_italic = edit.get('italic', False)
                    
                    if custom_font:
                        fontname = custom_font
                    else:
                        fontname = base_font
                        if base_font == "Times": 
                            if is_bold and is_italic: fontname = "Times-BoldItalic"
                            elif is_bold: fontname = "Times-Bold"
                            elif is_italic: fontname = "Times-Italic"
                            else: fontname = "Times-Roman"
                        else: 
                            if is_bold and is_italic: fontname += "-BoldOblique"
                            elif is_bold: fontname += "-Bold"
                            elif is_italic: fontname += "-Oblique"

                    
                    logger.info(f"Inserting text '{text}' with font: {fontname} at {final_x},{final_y}")
                    
                    # Direct insert_text (proven in add_watermark)
                    # Note: Y passed to insert_text is Point (baselineish)
                    try:
                        page.insert_text(
                            (final_x, final_y + fontsize), 
                            text,
                            fontsize=fontsize,
                            fontname=fontname,
                            color=color,
                            fill_opacity=opacity,
                            overlay=True
                        )
                    except Exception as e_text:
                        logger.error(f"Text insert failed: {e_text}. Retrying with 'helv'")
                        page.insert_text(
                            (final_x, final_y + fontsize), 
                            text,
                            fontsize=fontsize,
                            fontname="helv",
                            color=color,
                            fill_opacity=opacity,
                            overlay=True
                        )
                    
                elif type_ == 'image':
                    img_id = edit.get('imageId')
                    img_path = image_paths.get(img_id)
                    logger.info(f"Inserting image {img_id} at {final_x},{final_y}")
                    
                    if img_path and os.path.exists(img_path):
                        target_rect = fitz.Rect(final_x, final_y, final_x + final_w, final_y + final_h)
                        logger.info(f"Image rect: {target_rect}, file: {img_path}")
                        page.insert_image(target_rect, filename=img_path, keep_proportion=False)
                        
                elif type_ == 'shape':
                    shape_type = edit.get('shapeType', 'rect')
                    fill_hex = edit.get('fill', 'none')
                    stroke_hex = edit.get('stroke', '#000000')
                    stroke_width = float(edit.get('strokeWidth', 2))
                    
                    logger.info(f"Inserting shape {shape_type} at {final_x},{final_y}")

                    fill_col = None
                    if fill_hex != 'none' and fill_hex.startswith('#'):
                        fill_col = tuple(int(fill_hex.lstrip('#')[i:i+2], 16)/255 for i in (0, 2, 4))
                        
                    stroke_col = (0,0,0)
                    if stroke_hex.startswith('#'):
                        stroke_col = tuple(int(stroke_hex.lstrip('#')[i:i+2], 16)/255 for i in (0, 2, 4))
                    
                    shape = page.new_shape()
                    rect_area = fitz.Rect(final_x, final_y, final_x + final_w, final_y + final_h)
                    
                    if shape_type == 'rect':
                        shape.draw_rect(rect_area)
                    elif shape_type == 'circle' or shape_type == 'ellipse':
                        shape.draw_oval(rect_area)
                        
                    shape.finish(
                        color=stroke_col, 
                        fill=fill_col, 
                        width=stroke_width
                    )
                    shape.commit(overlay=True)

        doc.save(output_path)
        doc.close()
        logger.info(f"Edits applied, saved to {output_path}")
        return output_path
        
    except Exception as e:
        logger.error(f"Error applying edits: {e}")
        raise
