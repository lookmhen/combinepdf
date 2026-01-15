from flask import Flask, render_template, request, send_file, session, jsonify
from waitress import serve
import socket
import os
import secrets
import logging
from werkzeug.utils import secure_filename

# Import local modules
import shutil
import zipfile
import utils
import pdf_services

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)
app.config['UPLOAD_FOLDER'] = utils.TEMP_DIR
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB limit

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Ensure temp dir exists on startup
utils.ensure_temp_directory_exists()

@app.before_request
def run_cleanup():
    """Run cleanup before every request to keep temp folder clean."""
    utils.cleanup_temp_files()

@app.route('/')
def root():
    return render_template('index.html')

@app.route('/merge/')
def home():
    return render_template('index.html')

@app.route('/merge', methods=['POST'])
def merge():
    """
    Handle PDF merge request.
    Expects 'files[]' in the request.files.
    """
    uploaded_files = request.files.getlist("files[]")

    if not uploaded_files or uploaded_files[0].filename == '':
        return jsonify({"error": "No files selected"}), 400

    saved_paths = []
    
    try:
        # Create a unique session ID if not exists
        if 'session_id' not in session:
            session['session_id'] = secrets.token_hex(16)
            
        # Save uploaded files
        for file in uploaded_files:
            if file and file.filename.lower().endswith('.pdf'):
                # Secure the filename but preserve extension
                original_filename = secure_filename(file.filename)
                # Save with a unique name to prevent collisions
                temp_filename = f"{secrets.token_hex(8)}_{original_filename}"
                file_path = utils.get_temp_path(temp_filename)
                
                file.save(file_path)
                saved_paths.append(file_path)

        if not saved_paths:
            return jsonify({"error": "No valid PDF files found"}), 400

        # Output filename
        output_filename = f"merged_{secrets.token_hex(8)}.pdf"
        output_path = utils.get_temp_path(output_filename)

        # Perform Merge
        pdf_services.merge_pdfs(saved_paths, output_path)

        # Return the file
        return send_file(output_path, as_attachment=True, download_name="merged_document.pdf")

    except Exception as e:
        logger.error(f"Merge error: {e}")
        return jsonify({"error": str(e)}), 500
        
    finally:
        # Clean up the uploaded input files immediately? 
        # Or let the periodic cleanup handle it?
        # Let's clean up input files to save space immediately, keep output file for download
        for path in saved_paths:
            try:
                if os.path.exists(path):
                    os.remove(path)
            except Exception:
                pass

@app.route('/rotate')
def rotate_page():
    return render_template('rotate.html')

@app.route('/rotate', methods=['POST'])
def rotate():
    """
    Handle PDF rotation.
    Expects 'file' and 'rotations' (JSON string) in request.
    """
    if 'file' not in request.files:
         return jsonify({"error": "No file uploaded"}), 400
         
    file = request.files['file']
    rotations_json = request.form.get('rotations', '{}')
    
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400
        
    import json
    try:
        rotations = json.loads(rotations_json)
    except:
        return jsonify({"error": "Invalid rotation data"}), 400

    saved_path = None
    try:
        # Save input
        original_width = secure_filename(file.filename)
        temp_filename = f"rotate_in_{secrets.token_hex(8)}_{original_width}"
        saved_path = utils.get_temp_path(temp_filename)
        file.save(saved_path)
        
        # Prepare output
        output_filename = f"rotated_{secrets.token_hex(8)}.pdf"
        output_path = utils.get_temp_path(output_filename)
        
        # Rotate
        pdf_services.rotate_pdf(saved_path, output_path, rotations)
        
        return send_file(output_path, as_attachment=True, download_name="rotated_document.pdf")
        
    except Exception as e:
        logger.error(f"Rotation error: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        if saved_path and os.path.exists(saved_path):
            os.remove(saved_path)

@app.route('/split')
def split_page():
    return render_template('split.html')

@app.route('/split', methods=['POST'])
def split():
    """
    Handle PDF split.
    Expects 'file' and 'pages' (JSON list or 'all') in request.
    """
    if 'file' not in request.files:
         return jsonify({"error": "No file uploaded"}), 400
         
    file = request.files['file']
    pages_json = request.form.get('pages', '[]')
    
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400
        
    import json
    try:
        pages = json.loads(pages_json) # List of ints or string "all"
    except:
        return jsonify({"error": "Invalid pages data"}), 400

    saved_path = None
    output_dir = None
    
    try:
        # Save input
        original_name = secure_filename(file.filename)
        temp_filename = f"split_in_{secrets.token_hex(8)}_{original_name}"
        saved_path = utils.get_temp_path(temp_filename)
        file.save(saved_path)
        
        # Prepare output directory
        session_id = secrets.token_hex(8)
        output_dir = os.path.join(utils.TEMP_DIR, f"split_out_{session_id}")
        os.makedirs(output_dir, exist_ok=True)
        
        # Perform Split
        # Helper: if pages is "all", pass None to service
        selection = None if pages == "all" else [int(p) for p in pages]
        
        generated_files = pdf_services.split_pdf(saved_path, output_dir, selection)
        
        if not generated_files:
             return jsonify({"error": "No pages generated"}), 400

        # Decide return format
        if len(generated_files) == 1 and generated_files[0].endswith('.pdf'):
            # Return single PDF
            return send_file(generated_files[0], as_attachment=True, download_name=f"extracted_{original_name}")
        else:
            # Zip multiple files
            zip_filename = f"split_files_{session_id}.zip"
            zip_path = utils.get_temp_path(zip_filename)
            
            with zipfile.ZipFile(zip_path, 'w') as zipf:
                 for file_path in generated_files:
                     zipf.write(file_path, os.path.basename(file_path))
            
            return send_file(zip_path, as_attachment=True, download_name="split_pages.zip")

    except Exception as e:
        logger.error(f"Split error: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        # Cleanup input
        if saved_path and os.path.exists(saved_path):
            os.remove(saved_path)
            
        # Cleanup output dir (files are zipped or sent)
        # Note: If we use send_file, we can't delete immediately unless we use a background task or stream.
        # But for now, we leave them for periodic cleanup or implement a smarter cleanup.
        # For this MVP, we'll rely on periodic cleanup for the output files/zip.
        pass

@app.route('/pdf-to-jpg')
def pdf_to_jpg_page():
    return render_template('pdf_to_jpg.html')

@app.route('/pdf-to-jpg', methods=['POST'])
def pdf_to_jpg():
    """Convert PDF to JPGs (Zip download)."""
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
        
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400

    saved_path = None
    output_dir = None
    
    try:
        # Save input
        original_name = secure_filename(file.filename)
        temp_filename = f"conv_in_{secrets.token_hex(8)}_{original_name}"
        saved_path = utils.get_temp_path(temp_filename)
        file.save(saved_path)
        
        # Prepare output dir
        session_id = secrets.token_hex(8)
        output_dir = os.path.join(utils.TEMP_DIR, f"conv_out_{session_id}")
        os.makedirs(output_dir, exist_ok=True)
        
        # Convert
        generated_files = pdf_services.pdf_to_images(saved_path, output_dir)
        
        if not generated_files:
            return jsonify({"error": "No images generated"}), 400
            
        # Zip images
        zip_filename = f"images_{original_name}.zip"
        zip_path = utils.get_temp_path(zip_filename)
        
        with zipfile.ZipFile(zip_path, 'w') as zipf:
            for file_path in generated_files:
                zipf.write(file_path, os.path.basename(file_path))
                
        return send_file(zip_path, as_attachment=True, download_name=zip_filename)
        
    except Exception as e:
        logger.error(f"Convert error: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
         if saved_path and os.path.exists(saved_path):
            os.remove(saved_path)

@app.route('/jpg-to-pdf')
def jpg_to_pdf_page():
    return render_template('jpg_to_pdf.html')

@app.route('/jpg-to-pdf', methods=['POST'])
def jpg_to_pdf():
    """Convert multiple Images to PDF."""
    uploaded_files = request.files.getlist("files[]")
    
    if not uploaded_files or uploaded_files[0].filename == '':
        return jsonify({"error": "No files selected"}), 400

    saved_paths = []
    
    try:
        # Save uploaded images
        for file in uploaded_files:
            if file and file.filename.lower().endswith(('.jpg', '.jpeg', '.png')):
                filename = secure_filename(file.filename)
                temp_filename = f"img_{secrets.token_hex(8)}_{filename}"
                file_path = utils.get_temp_path(temp_filename)
                file.save(file_path)
                saved_paths.append(file_path)
                
        if not saved_paths:
            return jsonify({"error": "No valid image files found"}), 400

        # Output filename
        output_filename = f"converted_images_{secrets.token_hex(8)}.pdf"
        output_path = utils.get_temp_path(output_filename)

        # Convert
        pdf_services.images_to_pdf(saved_paths, output_path)

        return send_file(output_path, as_attachment=True, download_name="converted_images.pdf")

    except Exception as e:
        logger.error(f"Convert error: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        for path in saved_paths:
             if os.path.exists(path):
                os.remove(path)

@app.route('/watermark')
def watermark_page():
    return render_template('watermark.html')

@app.route('/watermark', methods=['POST'])
def watermark():
    """Apply watermark to PDF."""
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    
    file = request.files['file']
    config_json = request.form.get('config', '{}')
    
    import json
    try:
        config = json.loads(config_json)
    except:
        return jsonify({"error": "Invalid config"}), 400
        
    saved_path = None
    output_path = None
    
    saved_path = None
    output_path = None
    image_path = None # Initialize image_path here
    
    try:
        original_name = secure_filename(file.filename)
        temp_filename = f"wm_in_{secrets.token_hex(8)}_{original_name}"
        saved_path = utils.get_temp_path(temp_filename)
        file.save(saved_path) # Save the main PDF file
        
        config = json.loads(request.form.get('config', '{}'))
        
        # Handle Image Upload if present
        if 'image_file' in request.files:
            img_file = request.files['image_file']
            if img_file.filename != '':
                img_name = secure_filename(img_file.filename)
                image_path = utils.get_temp_path(f"wm_img_{secrets.token_hex(4)}_{img_name}")
                img_file.save(image_path)
        
        output_filename = f"watermarked_{secrets.token_hex(4)}_{original_name}"
        output_path = utils.get_temp_path(output_filename)
        
        pdf_services.add_watermark(saved_path, output_path, config, image_path)
        
        return send_file(output_path, as_attachment=True, download_name=output_filename)
        
    except Exception as e:
        logger.error(f"Watermark error: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        if saved_path and os.path.exists(saved_path):
            os.remove(saved_path)
        if image_path and os.path.exists(image_path):
            os.remove(image_path)

@app.route('/compress')
def compress_page():
    return render_template('compress.html')

@app.route('/compress', methods=['POST'])
def compress():
    """Compress PDF."""
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400
        
    saved_path = None
    output_path = None
    
    try:
        original_name = secure_filename(file.filename)
        temp_filename = f"comp_in_{secrets.token_hex(8)}_{original_name}"
        saved_path = utils.get_temp_path(temp_filename)
        file.save(saved_path)
        
        output_filename = f"compressed_{original_name}"
        output_path = utils.get_temp_path(output_filename)
        
        # Compress
        pdf_services.compress_pdf(saved_path, output_path)
        
        # Calculate savings
        original_size = os.path.getsize(saved_path)
        new_size = os.path.getsize(output_path)
        saving_pct = 0
        if original_size > 0:
            saving_pct = round((1 - (new_size / original_size)) * 100, 1)
            
        logger.info(f"Compressed: {original_size} -> {new_size} ({saving_pct}%)")
        
        response = send_file(output_path, as_attachment=True, download_name=output_filename)
        response.headers["X-Compression-Ratio"] = str(saving_pct)
        return response
        
    except Exception as e:
        logger.error(f"Compress error: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        if saved_path and os.path.exists(saved_path):
            os.remove(saved_path)


def start_server():
    """Start the Waitress server."""
    host = socket.gethostbyname(socket.gethostname())
    port = int(os.environ.get('PORT', 80))
    
    logger.info(f"Starting server on http://{host}:{port}")
    serve(app, host=host, port=port)

if __name__ == '__main__':
    start_server()
