
![image](https://github.com/lookmhen/combinepdf/assets/29670155/836cafb6-b5ca-4c2b-809c-2457b235fba7)

# PDF Merger Web Application 📚🔗

This is a simple web application built using Flask that allows users to upload PDF files and merge them into a single PDF file.

## Test Environment 🧪
Python 3.10.9

## Features ✨

- Drag and Drop file 📂: Upload multiple PDF files for merging and change the sequence of files by dragging and dropping.
  
![image](https://github.com/lookmhen/combinepdf/assets/29670155/d60c912a-321d-4d50-8070-42204373f1a4)

- Automatic cleanup of temporary files after a certain period. 🧹
- Unique session management using secure tokens. 🔒
- PDF merging using PyPDF2 library. 📎
- Basic error handling and logging. 🛠️

## Getting Started 🚀

1. Clone this repository to your local machine.
2. Install the required dependencies using `pip install -r requirements.txt`.
3. Run the application using `python app.py` or `start.cmd`.
4. Access the application in your web browser at `http://localhost:8080`.

## Usage 📝

1. Visit the homepage and click on the "Merge PDFs" button.
2. Upload the PDF files you want to merge.
3. Click the "Merge" button to merge the uploaded files.
4. Download the merged PDF file.

## Configuration ⚙️

- The `MAX_LIFETIME` variable in `app.py` sets the maximum lifetime (in seconds) of temporary files before they're cleaned up.

## Contributing 🤝

Contributions are welcome! If you find a bug or want to add a new feature, please feel free to open an issue or submit a pull request.

## Acknowledgements 🙌

- This project was inspired by the need to merge PDF files easily.
- The Flask framework and PyPDF2 library were crucial for building this application.
