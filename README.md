


![image](https://github.com/lookmhen/combinepdf/assets/29670155/836cafb6-b5ca-4c2b-809c-2457b235fba7)




# combinepdf
Web application built using Flask that allows upload multiple PDF files and merge them into a single PDF file.

Getting Started
Follow the steps below to get the application up and running on your local machine.

Test On Python 3.10.9

Installation
Clone or download this repository to your local machine.

Open a terminal or command prompt and navigate to the project directory:

pip install -r requirements.txt
Usage
Start the Flask development server:

python app.py
Open your web browser and navigate to http://localhost:8080

You will see the home page of the PDF Merger application. Click on the "Choose Files" button to select the PDF files you want to merge.

Once you have selected the files, click the "Merge Files" button. The application will merge the PDF files and provide a download link for the merged PDF.

You can download the merged PDF file and save it to your computer.

Cleanup
The application automatically cleans up temporary files that are generated during the merging process. Temporary files are removed after 1 minute.
