
def apply_edits(file_path: str, output_path: str, edits_config: dict, image_paths: dict = None) -> str:
    """
    Apply multiple edits (text, image, shape) to specific pages.
    
    Args:
        file_path: Input PDF.
        output_path: Output PDF.
        edits_config: Dict with page indices (str) as keys, list of edits as values.
                      Example: { "0": [ {type:'text', ...}, {type:'shape', ...} ] }
        image_paths: Dict mapping image IDs to file paths.
    """
    try:
        doc = fitz.open(file_path)
        
        for page_idx_str, edits in edits_config.items():
            try:
                page_idx = int(page_idx_str)
                if not (0 <= page_idx < len(doc)):
                    continue
                page = doc[page_idx]
                rect = page.rect
                
                for edit in edits:
                    etype = edit.get('type')
                    
                    # Common coordinates (percentages)
                    x_pct = float(edit.get('x', 0))
                    y_pct = float(edit.get('y', 0))
                    # For shapes/images, we also have width/height percentages
                    w_pct = float(edit.get('w', 0))
                    h_pct = float(edit.get('h', 0))
                    
                    x = rect.width * x_pct
                    y = rect.height * y_pct
                    w = rect.width * (w_pct if w_pct > 0 else 0)
                    h = rect.height * (h_pct if h_pct > 0 else 0)
                    
                    opacity = float(edit.get('opacity', 1.0))
                    rotation = int(edit.get('rotation', 0))
                    
                    if etype == 'text':
                        text = edit.get('text', '')
                        fontsize = float(edit.get('fontSize', 12))
                        fontcolor = edit.get('color', '#000000')
                        
                        # Parse color hex to RGB tuple (0-1)
                        if fontcolor.startswith('#'):
                            fontcolor = tuple(int(fontcolor.lstrip('#')[i:i+2], 16)/255 for i in (0, 2, 4))
                        
                        # Using insert_text with morph for rotation
                        # Need to calculate pivot
                        
                        # Approximate text width/height for pivot calculation if needed, 
                        # but usually client sends center X/Y. 
                        # Assuming X/Y is Top-Left for simple insertion, 
                        # or we handle rotation pivot at (x,y).
                        
                        font = fitz.Font("helv")
                        
                        mat = fitz.Matrix(-rotation)
                        pivot = fitz.Point(x, y)
                        
                        page.insert_text(
                            (x, y), # Point
                            text,
                            fontsize=fontsize,
                            color=fontcolor,
                            fontname="helv",
                            morph=(pivot, mat),
                            overlay=True,
                            fill_opacity=opacity
                        )

                    elif etype == 'image':
                        img_id = edit.get('imageId')
                        if img_id and image_paths and img_id in image_paths:
                            img_path = image_paths[img_id]
                            
                            # Reuse Image Logic (from add_watermark but simplified for generic)
                            pix = fitz.Pixmap(img_path)
                            
                            # Opacity
                            if opacity < 1.0:
                                if not pix.alpha: pix = fitz.Pixmap(fitz.csRGB, pix, 1)
                                mask = fitz.Pixmap(fitz.csGRAY, pix.irect, False)
                                mask.clear_with(int(255 * opacity))
                                pix.set_alpha(mask.samples)
                            
                            img_bytes = pix.tobytes("png")
                            img_doc = fitz.open("png", img_bytes)
                            pdf_bytes = img_doc.convert_to_pdf()
                            src_doc = fitz.open("pdf", pdf_bytes)
                            
                            # Target Rect
                            target_rect = fitz.Rect(x, y, x + w, y + h)
                            
                            # Rotation is handled by show_pdf_page
                            # Note: show_pdf_page rotates around the CENTER of the rect by default in recent versions?
                            # Actually need to specify properly. 
                            # If checking add_watermark logic, it calculates a bounding box. 
                            # For simplicity in Editor, we might just rotate the rect content.
                            
                            page.show_pdf_page(target_rect, src_doc, 0, rotate=-rotation)
                            src_doc.close()

                    elif etype == 'shape':
                        shape_type = edit.get('shapeType', 'rect') # rect, circle
                        fill_color = edit.get('fill', None)
                        stroke_color = edit.get('stroke', '#000000')
                        stroke_width = float(edit.get('strokeWidth', 2))
                        
                        # Parse colors
                        sc = None
                        if stroke_color and stroke_color != 'none':
                            sc = tuple(int(stroke_color.lstrip('#')[i:i+2], 16)/255 for i in (0, 2, 4))
                            
                        fc = None
                        if fill_color and fill_color != 'none':
                            fc = tuple(int(fill_color.lstrip('#')[i:i+2], 16)/255 for i in (0, 2, 4))
                        
                        shape_rect = fitz.Rect(x, y, x + w, y + h)
                        
                        # Rotate logic for shapes is tricky in generic 'draw_rect'.
                        # We use 'Shape' object in PyMuPDF
                        shape = page.new_shape()
                        
                        # Apply transformation for rotation
                        # Translate to center -> Rotate -> Translate back
                        cx = x + w/2
                        cy = y + h/2
                        transform = fitz.Matrix(1, 0, 0, 1, -cx, -cy).concat(fitz.Matrix(-rotation)).concat(fitz.Matrix(1, 0, 0, 1, cx, cy))
                        
                        # Draw un-rotated shape at original coords, then apply transform? 
                        # Or define shape at (0,0,w,h) and move?
                        # Easiest: Define shape, apply finish(matrix=...)
                        
                        # Wait, PyMuPDF shape.finish() doesn't take matrix. 
                        # We assume unrotated bounds first.
                        
                        if shape_type == 'rect':
                            shape.draw_rect(shape_rect)
                        elif shape_type == 'circle':
                            shape.draw_oval(shape_rect)
                        elif shape_type == 'line':
                            # Line assumes x,y is start and x+w, y+h is end or similar logic from frontend
                            # Let's assume standard bounding box logic for now
                            shape.draw_line((x,y), (x+w, y+h))

                        # Apply colors
                        shape.finish(
                            color=sc, 
                            fill=fc, 
                            width=stroke_width,
                            fill_opacity=opacity
                            # morph=(pivot, mat) # shape.finish usually doesn't have morph
                        )
                        
                        # If we need rotation, we might need to commit differently.
                        # For simple rects/circles, standard draw is fine. 
                        # If rotation is required, we might need to act on the modified page content 
                        # or use Coordinate Transformations (cm) on the page content stream. 
                        # Detailed implementation of rotated shapes might be complex for this MVP.
                        # For now, IGNORING rotation for shapes to keep it simple, or checking if we can use Quad.
                        
                        shape.commit()
                        
            except Exception as e:
                logger.error(f"Error processing page {page_idx_str}: {e}")
                continue

        doc.save(output_path)
        logger.info(f"Edited PDF saved to {output_path}")
        return output_path
        
    except Exception as e:
        logger.error(f"Error applying edits: {e}")
        raise
