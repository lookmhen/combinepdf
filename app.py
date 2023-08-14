from flask import Flask, render_template, request, send_file, session
from PyPDF2 import PdfMerger
import os
import uuid
import secrets
import time

# Define the maximum lifetime of a temporary file in seconds
MAX_LIFETIME = 120  # 2 min

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)
app.config['UPLOAD_FOLDER'] = 'temp'


# #--------Configure SSL context
# cert_dir = '/path/to/cert_directory'
# cert_file = os.path.join(cert_dir, 'server.crt')
# key_file = os.path.join(cert_dir, 'server.key')
# ssl_context = (cert_file, key_file)
# #---------------------



@app.route('/')
def home():
    return render_template('index.html')

@app.route('/merge', methods=['POST'])
def merge():
    uploaded_files = request.files.getlist("files[]")

    if not uploaded_files:
        return "No files selected for merging."

    merger = PdfMerger()
    temp_files = []

    try:
        session_id = secrets.token_hex(16)  # Generate a unique session ID
        session['session_id'] = session_id  # Store session ID in Flask session

        # Create the temp directory if it doesn't exist
        if not os.path.exists(app.config['UPLOAD_FOLDER']):
            os.makedirs(app.config['UPLOAD_FOLDER'])

        # Save uploaded files to the temp directory with unique names
        for file in uploaded_files:
            if file.filename.endswith(".pdf"):
                filename = str(uuid.uuid4()) + ".pdf"
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)
                temp_files.append(file_path)
                merger.append(file_path)

        if not merger.pages:
            return "No PDF files found in the selected files for merging."

        output_filename = session['session_id'] + ".pdf"  # Use session ID in the output filename
        output_path = os.path.join(app.config['UPLOAD_FOLDER'], output_filename)
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
            if os.path.exists(app.config['UPLOAD_FOLDER']) and not os.listdir(app.config['UPLOAD_FOLDER']):
                os.rmdir(app.config['UPLOAD_FOLDER'])

        except Exception as cleanup_error:
            # Handle exceptions that might occur during cleanup
            print("Error occurred during cleanup:", cleanup_error)

# Define a cleanup function
def cleanup_temp_files():
    current_time = time.time()

    for file_name in os.listdir(app.config['UPLOAD_FOLDER']):
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file_name)
        file_age = current_time - os.path.getctime(file_path)

        if file_age > MAX_LIFETIME:
            try:
                os.remove(file_path)
            except Exception as e:
                print("Error removing file:", e)

# Run the cleanup function periodically
@app.before_request
def run_cleanup():
    cleanup_temp_files()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
