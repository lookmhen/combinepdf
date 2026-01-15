# PDF Suite 📦✨

A modern, powerful, and easy-to-use web application for managing your PDF files.
Currently features a robust **PDF Merger** with a drag-and-drop interface and visual previews.

> **Status**: Active Development & Modernization.

## Features 🚀

-   **Modern "Pastel Lively" UI**: A beautiful, friendly interface that supports both **Light** and **Dark** modes through a system-aware toggle.
-   **Visual Previews**: See thumbnails of your PDFs immediately upon dropping them, ensuring you are merging the right files.
-   **Drag & Drop Reordering**: Easily rearrange your files by dragging the cards.
-   **Secure & Private**: Temporary files are automatically cleaned up after 2 minutes. Unique session IDs ensure your data never overlaps with others.
-   **Modular Backend**: Built on **Flask** and **pypdf**, ready for future expansions like Split, Rotate, and Convert.

## Tech Stack 🛠️

-   **Backend**: Python, Flask, pypdf, Waitress
-   **Frontend**: HTML5, Modern CSS3 (Variables, Grids), JavaScript (ES modules)
-   **Libraries**: `pdf.js` for client-side rendering.

## Getting Started 🏃‍♂️

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/lookmhen/combinepdf.git
    cd combinepdf
    ```

2.  **Set up Virtual Environment**:
    ```bash
    # Windows
    python -m venv venv
    venv\Scripts\activate
    ```

3.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Run the Server**:
    ```bash
    python app.py
    ```
    Access the app at `http://localhost:80/merge`

## Roadmap 🗺️

-   [x] **Merge PDF**: Combine multiple files.
-   [ ] **Split PDF**: Extract pages or split into individual files.
-   [ ] **Rotate PDF**: Fix orientation of scanned documents.
-   [ ] **Convert**: Images to PDF and vice versa.

## Contributing 🤝

Contributions are welcome! Please feel free to open issues or submit pull requests for new features.

## License 📜

[MIT License](LICENSE)
