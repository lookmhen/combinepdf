
    // JavaScript for Night Mode Toggle
    let nightModeCheckbox = document.getElementById('night-mode');
    let nightModeLabel = document.getElementById('night-mode-label');

    nightModeCheckbox.addEventListener('change', function () {
        document.body.classList.toggle('night-mode', this.checked);
    });

    // Check the night mode preference if saved
    let nightModePreference = localStorage.getItem('nightModePreference');
    if (nightModePreference === 'true') {
        nightModeCheckbox.checked = true;
        document.body.classList.add('night-mode');
    }

    // Save night mode preference
    nightModeCheckbox.addEventListener('change', function () {
        localStorage.setItem('nightModePreference', this.checked);
    });

	
    let fileList = [];
    let dropArea = document.getElementById('drop-area');
    let fileListContainer = document.getElementById('file-list');
    let moveDescription = document.getElementById('move-description');
    let mergeForm = document.getElementById('merge-form');
    let draggedIndex;

    function handleFileUpload(file) {
    if (file.type !== 'application/pdf') {
        alert("Please select a PDF file.");
        return;
    }

    fileList.push(file);
    renderFileList();
}


    function removeFile(index) {
        fileList.splice(index, 1);
        renderFileList();
    }

    function swapFiles(index1, index2) {
        let temp = fileList[index1];
        fileList[index1] = fileList[index2];
        fileList[index2] = temp;
        renderFileList();
    }

    function renderFileList() {
    fileListContainer.innerHTML = '';
    fileList.forEach(function(file, index) {
        let fileEntry = document.createElement('div');
        fileEntry.className = 'file-entry';
        fileEntry.setAttribute('draggable', true);
        fileEntry.addEventListener('dragstart', function(e) {
            draggedIndex = index;
        });
        fileEntry.addEventListener('dragover', function(e) {
            e.preventDefault();
        });
        fileEntry.addEventListener('dragenter', function(e) {
            e.preventDefault();
            this.style.borderLeft = '2px solid #ff90a6';
        });
        fileEntry.addEventListener('dragleave', function(e) {
            e.preventDefault();
            this.style.borderLeft = '2px solid #ffc0cb';
        });
        fileEntry.addEventListener('drop', function(e) {
            e.preventDefault();
            this.style.borderLeft = '2px solid #ffc0cb';
            swapFiles(draggedIndex, index);
        });

        let fileNumber = document.createElement('span');
		fileNumber.className = 'file-number';

		let star = document.createElement('span');
		star.className = 'star';
		star.textContent = index + 1;

		fileNumber.appendChild(star);




        let fileName = document.createElement('span');
        fileName.className = 'file-name';
        fileName.textContent = file.name;

        let removeButton = document.createElement('button');
        removeButton.className = 'remove-file';
        removeButton.textContent = 'Remove';
        removeButton.addEventListener('click', function() {
            removeFile(index);
        });

        fileEntry.appendChild(fileNumber);
        fileEntry.appendChild(fileName);
        fileEntry.appendChild(removeButton);
        fileListContainer.appendChild(fileEntry);
    });
}





    function browseFiles() {
        let fileInput = document.createElement('input');
        fileInput.type = 'file';
        fileInput.multiple = true;
        fileInput.accept = '.pdf';
        fileInput.addEventListener('change', function(e) {
            let files = e.target.files;
            for (let i = 0; i < files.length; i++) {
                handleFileUpload(files[i]);
            }
        });
        fileInput.click();
    }

    dropArea.addEventListener('dragover', function(e) {
        e.preventDefault();
        dropArea.style.backgroundColor = '#fff';
        dropArea.style.border = '2px dashed #ffc0cb';
        dropArea.style.boxShadow = '0 2px 5px rgba(255, 192, 203, 0.3)';
    });

    dropArea.addEventListener('dragleave', function(e) {
        e.preventDefault();
        dropArea.style.backgroundColor = '#fff';
        dropArea.style.border = '2px dashed #ffc0cb';
        dropArea.style.boxShadow = '0 2px 5px rgba(255, 192, 203, 0.3)';
    });

    dropArea.addEventListener('drop', function(e) {
        e.preventDefault();
        dropArea.style.backgroundColor = '#fff';
        dropArea.style.border = '2px dashed #ffc0cb';
        dropArea.style.boxShadow = '0 2px 5px rgba(255, 192, 203, 0.3)';
        let files = e.dataTransfer.files;
        for (let i = 0; i < files.length; i++) {
            handleFileUpload(files[i]);
        }
    });

    

    mergeForm.addEventListener('submit', function(e) {
        e.preventDefault();
        if (fileList.length === 0) {
            alert("No files selected for merging.");
            return;
        }
    
        let mergeButton = document.getElementById('merge-button');
    
        // Store the original text
        let originalText = mergeButton.value;
    
        // Disable the merge button and change the text
        mergeButton.disabled = true;
        mergeButton.value = 'Merging...';
    
        let formData = new FormData();
        for (let i = 0; i < fileList.length; i++) {
            formData.append('files[]', fileList[i]);
        }
    
        fetch('/merge', {
            method: 'POST',
            body: formData
        })
        .then(response => response.blob())
        .then(blob => {
            let url = window.URL.createObjectURL(blob);
            let a = document.createElement('a');
            a.href = url;
            a.download = 'merged.pdf';
            a.click();
        })
        .catch(error => {
            console.error('Error:', error);
            alert('An error occurred during merging.');
        })
        .finally(() => {
            // Re-enable the merge button and restore the original text
            mergeButton.disabled = false;
            mergeButton.value = originalText;
        });
    });
