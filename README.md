# PDF Management Suite

A modern, web-based tool for managing PDF files. Built with Python (Flask) and a clean, responsive interface.
Features include merging, rotating, splitting, converting, watermarking, and compressing PDFs.

## Features

### 1. Merge PDF
Combine multiple PDF files into a single document.
- **Drag & Drop** interface.
- **Reorder** files before merging.

### 2. Rotate PDF
Rotate specific pages of a PDF document.
- Interactive page preview.
- Rotate individual pages left or right.

### 3. Split PDF
Extract specific pages or split an entire PDF into individual files.
- Select specific pages to extract.
- Or split all pages at once (downloads as a Zip).

### 4. Convert Tools
- **PDF to JPG**: Convert PDF pages into high-quality images (Zip download).
- **JPG to PDF**: Combine multiple images into a single PDF document.

### 5. Watermark PDF
Add text watermarks to your PDF documents.
- **Interactive Editor**: Drag, rotate, and resize text on a live preview.
- Customizable color, font size, and rotation.

### 6. Compress PDF
Reduce the file size of your PDF documents while maintaining quality.
- Uses advanced optimization (garbage collection, stream deflation).

---

## Installation & Setup

### Prerequisites
- Python 3.9 or higher.

### Steps
1.  **Clone or Download** this repository.
2.  **Create a Virtual Environment** (Recommended):
    ```bash
    python -m venv venv
    # Windows
    venv\Scripts\activate
    # Mac/Linux
    source venv/bin/activate
    ```
3.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

### Running the Application
1.  **Start the Server**:
    ```bash
    python app.py
    ```
2.  **Access the App**:
    Open your browser and navigate to:
    `http://localhost:80` (or the port displayed in the terminal).

---

## Tech Stack
- **Backend**: Python, Flask, Waitress (WSGI Server).
- **PDF Processing**: 
  - `pypdf`: Merging, Rotating, Splitting.
  - `pymupdf` (fitz): Rendering previews, Watermarking, Compression, Image Conversion.
- **Frontend**: HTML5, CSS3 (Modern Variables), JavaScript (Vanilla), PDF.js.

## Project Structure
```
.
├── app.py              # Main Flask Application
├── pdf_services.py     # Core PDF Operations logic
├── utils.py            # File utilities
├── requirements.txt    # Project dependencies
├── static/             # Static assets (PDF.js, CSS, JS)
└── templates/          # HTML Templates
    ├── base.html       # Base layout
    ├── index.html      # Merge tool
    ├── rotate.html     # Rotate tool
    ├── split.html      # Split tool
    ├── watermark.html  # Watermark tool
    ├── compress.html   # Compress tool
    └── ...
```

## Troubleshooting
- **Missing Utilities**: If you see errors about missing `zlib` or `headers` when installing, ensure you have the latest `pip` and are installing the binary wheels for `pymupdf`.
- **Large Files**: The app is configured to handle files up to 100MB. This can be adjusted in `app.py`.
