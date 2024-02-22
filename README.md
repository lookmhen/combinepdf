![image](https://github.com/lookmhen/combinepdf/assets/29670155/d8edfacb-e720-4e64-9686-450f3a379bd2)


# PDF Merger Web Application 📚🔗

Welcome to the PDF Merger web app, where you can easily merge your PDF files with simplicity and convenience! 🚀

## Test Environment 🧪
Python 3.12

## Access From Any Device 🌐

The PDF Merger Web Application is designed to be accessible from any device connected to the same network. This means you can easily use the application from your computer, tablet, or even your smartphone.

## Features ✨

- **Drag and Drop PDF Upload** 📂: Effortlessly upload multiple PDF files for merging. You can also reorder the files by simply dragging and dropping.
  
  ![image](https://github.com/lookmhen/combinepdf/assets/29670155/d60c912a-321d-4d50-8070-42204373f1a4)

- **Automatic Cleanup** 🧹: Temporary files are automatically cleaned up after a set period, ensuring efficient resource management.
- **Unique Session Management** 🔒: Secure tokens are used for managing sessions, enhancing user privacy.
- **PDF Merging** 📎: Utilizes the powerful PyPDF2 library for seamless merging of PDF files.

## Getting Started 🚀

1. Clone this repository to your local machine.
2. Install the required dependencies using `pip install -r requirements.txt`.
3. Run the application using `python app.py` or `start.cmd`.
4. Access the application in your web browser at `http://localhost/merge`or `http://hostname/merge/`.

## Usage 📝

1. Access the homepage and click the "Merge PDFs" button.
2. Upload the PDF files you intend to merge.
3. Reorder the files using drag and drop if needed.
4. Click the "Merge" button to initiate the merging process.
5. Download the merged PDF file.

## Configuration ⚙️

- The `MAX_LIFETIME` variable in `app.py` sets the maximum lifetime (in seconds) of temporary files before they're automatically removed.

## Contributing 🤝

Contributions are welcomed! If you discover a bug or have an idea for a new feature, please open an issue or submit a pull request.

## Acknowledgements 🙌

- This project was inspired by the need for a straightforward PDF merging solution.
- The Flask framework and PyPDF2 library played a pivotal role in the development of this application.

## License 📜

This project is licensed under the [MIT License](LICENSE).
