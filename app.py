from flask import Flask, render_template, request, send_file, session
from PyPDF2 import PdfMerger
from waitress import serve
import socket
import os
import uuid
import secrets
import time
import logging

# Define the maximum lifetime of a temporary file in seconds
MAX_LIFETIME = 120  # 2 min

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)
tempdir=app.config['UPLOAD_FOLDER'] = 'temp'

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# #--------Configure SSL context
# cert_dir = '/path/to/cert_directory'
# cert_file = os.path.join(cert_dir, 'server.crt')
# key_file = os.path.join(cert_dir, 'server.key')
# ssl_context = (cert_file, key_file)
# #---------------------



@app.route('/merge/')
def home():
    return render_template('index.html')

def ensure_temp_directory_exists():
    """
    Ensure the temporary directory exists.
    """
    if not os.path.exists(tempdir):
        os.makedirs(tempdir)



@app.route('/merge', methods=['POST'])
def merge():
    
    """
    Merge uploaded PDF files and return the merged PDF.
    """
    
    uploaded_files = request.files.getlist("files[]")

    if not uploaded_files:
        return "No files selected for merging."

    merger = PdfMerger()
    temp_files = []

    try:
        session_id = secrets.token_hex(16)  # Generate a unique session ID
        session['session_id'] = session_id  # Store session ID in Flask session

        ensure_temp_directory_exists() # Ensure temp directory exists

        # Save uploaded files to the temp directory with unique names
        for file in uploaded_files:
            if file.filename.endswith(".pdf"):
                filename = str(uuid.uuid4()) + ".pdf"
                file_path = os.path.join(tempdir, filename)
                file.save(file_path)
                temp_files.append(file_path)
                merger.append(file_path)

        if not merger.pages:
            return "No PDF files found in the selected files for merging."

        output_filename = session['session_id'] + ".pdf"  # Use session ID in the output filename
        output_path = os.path.join(tempdir, output_filename)
        merger.write(output_path)

        return send_file(output_path, as_attachment=True, download_name=output_filename)

    finally:
        # Close the PDF merger
        merger.close()

        try:
            # Clean up uploaded files after processing
            for file_path in temp_files:
                if os.path.isfile(file_path):
                    os.remove(file_path)

            # Remove the temp directory if it's empty
            if os.path.exists(tempdir) and not os.listdir(tempdir):
                os.rmdir(tempdir)

        except Exception as cleanup_error:
            # Handle exceptions that might occur during cleanup
            print("Error occurred during cleanup:", cleanup_error)

# Define a cleanup function
def cleanup_temp_files():
    
    """
    Remove expired temporary files.
    
    """
    
    current_time = time.time()
    
    for file_name in os.listdir(tempdir):
        file_path = os.path.join(tempdir, file_name)
        file_age = current_time - os.path.getctime(file_path)

        if file_age > MAX_LIFETIME:
            try:
                os.remove(file_path)
                logger.info("Removed expired file: %s", file_path)
            except Exception as e:
                logger.error("Error removing file: %s", e)

# Run the cleanup function periodically
@app.before_request
def run_cleanup():
    cleanup_temp_files()

def start_server():
    """
    Start the Waitress server.
    """
    host = socket.gethostbyname(socket.gethostname())
    port = int(os.environ.get('PORT', 80))

    ensure_temp_directory_exists()

    logger.info("Starting the Mergepdf server on %s:%d%s", host, port, '/merge')

    serve(app, host=host, port=port)

if __name__ == '__main__':
    start_server()

# Configuration for Gunicorn (not use for now next large scale)
# Gunicorn: The number of worker processes and concurrency is configurable, allowing you to fine-tune its behavior based on your application's requirements.

#     host = os.environ.get('HOST', '0.0.0.0')
#     port = int(os.environ.get('PORT', 8080))
#     workers = int(os.environ.get('WORKERS', 4))
#     worker_class = os.environ.get('WORKER_CLASS', 'sync')

#     # Start Gunicorn with your app
#     cmd = f"gunicorn -w {workers} -b {host}:{port} -k {worker_class} app:app"
#     os.system(cmd)
