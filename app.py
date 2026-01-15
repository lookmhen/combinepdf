from flask import Flask, render_template, request, send_file, session, jsonify
from waitress import serve
import socket
import os
import secrets
import logging
from werkzeug.utils import secure_filename

# Import local modules
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

def start_server():
    """Start the Waitress server."""
    host = socket.gethostbyname(socket.gethostname())
    port = int(os.environ.get('PORT', 80))
    
    logger.info(f"Starting server on http://{host}:{port}")
    serve(app, host=host, port=port)

if __name__ == '__main__':
    start_server()
