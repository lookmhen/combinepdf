// State
let files = []; // Array of { id, file, thumbnailCanvas }

// DOM Elements
const dropArea = document.getElementById('drop-area');
const fileInput = document.getElementById('file-input');
const fileGrid = document.getElementById('file-grid');
const mergeBtn = document.getElementById('merge-btn');

// --- Event Listeners ---

// Click to browse
dropArea.addEventListener('click', () => fileInput.click());

fileInput.addEventListener('change', (e) => {
    handleFiles(e.target.files);
    fileInput.value = ''; // Reset
});

// Drag & Drop visual feedback
['dragenter', 'dragover'].forEach(eventName => {
    dropArea.addEventListener(eventName, (e) => {
        e.preventDefault();
        e.stopPropagation();
        dropArea.classList.add('drag-active');
    }, false);
});

['dragleave', 'drop'].forEach(eventName => {
    dropArea.addEventListener(eventName, (e) => {
        e.preventDefault();
        e.stopPropagation();
        dropArea.classList.remove('drag-active');
    }, false);
});

dropArea.addEventListener('drop', (e) => {
    const dt = e.dataTransfer;
    handleFiles(dt.files);
});

// Merge Action
mergeBtn.addEventListener('click', async () => {
    if (files.length < 2) {
        alert("Please add at least 2 PDF files."); // We'll upgrade this to a better UI alert later
        return;
    }

    const originalText = mergeBtn.innerText;
    mergeBtn.innerText = "Merging... ⏳";
    mergeBtn.disabled = true;

    try {
        const formData = new FormData();
        files.forEach(f => {
            formData.append('files[]', f.file);
        });

        const response = await fetch('/merge', {
            method: 'POST',
            body: formData
        });

        if (response.ok) {
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = "Merged_Document.pdf";
            document.body.appendChild(a);
            a.click();
            a.remove();
        } else {
            const err = await response.json();
            alert("Error: " + (err.error || "Unknown error"));
        }
    } catch (error) {
        console.error(error);
        alert("An error occurred.");
    } finally {
        mergeBtn.innerText = originalText;
        mergeBtn.disabled = false;
    }
});

// --- Logic ---

async function handleFiles(fileList) {
    for (const file of fileList) {
        if (file.type === 'application/pdf') {
            await addFile(file);
        } else {
            alert(`Skipped "${file.name}": Not a PDF`);
        }
    }
    updateUI();
}

async function addFile(file) {
    const id = Math.random().toString(36).substr(2, 9);
    const fileObj = {
        id,
        file,
        name: file.name
    };

    files.push(fileObj);

    // Render UI card immediately
    renderFileCard(fileObj);

    // Generate Thumbnail asynchronously
    generateThumbnail(fileObj);
}

function removeFile(id) {
    files = files.filter(f => f.id !== id);
    updateUI();
}

function updateUI() {
    fileGrid.innerHTML = '';
    files.forEach(f => renderFileCard(f));

    // Update button state
    mergeBtn.disabled = files.length === 0;
}

function renderFileCard(fileObj) {
    const card = document.createElement('div');
    card.className = 'file-card';
    card.draggable = true;
    card.dataset.id = fileObj.id;

    // Drag sorting logic (simple swap for now)
    card.addEventListener('dragstart', handleDragStart);
    card.addEventListener('dragover', handleDragOver);
    card.addEventListener('drop', handleDrop);
    card.addEventListener('dragend', handleDragEnd);

    const previewContainer = document.createElement('div');
    previewContainer.className = 'file-preview';
    // If we already have a canvas in memory, use it, else generic icon until fuzzy load
    if (fileObj.canvas) {
        previewContainer.appendChild(fileObj.canvas);
    } else {
        previewContainer.innerHTML = '<span style="font-size: 2rem;">⏳</span>';
    }

    const name = document.createElement('div');
    name.className = 'file-info';
    name.textContent = fileObj.name;

    const removeBtn = document.createElement('button');
    removeBtn.className = 'remove-btn';
    removeBtn.innerHTML = '×';
    removeBtn.onclick = (e) => {
        e.stopPropagation(); // prevent drag
        removeFile(fileObj.id);
    };

    card.appendChild(removeBtn);
    card.appendChild(previewContainer);
    card.appendChild(name);

    fileGrid.appendChild(card);
}

// --- Thumbnail Generation ---
async function generateThumbnail(fileObj) {
    if (!window.pdfjsLib) {
        console.error("PDF.js not loaded");
        return;
    }

    try {
        const arrayBuffer = await fileObj.file.arrayBuffer();
        const loadingTask = pdfjsLib.getDocument({ data: arrayBuffer });
        const pdf = await loadingTask.promise;
        const page = await pdf.getPage(1); // Get first page

        const scale = 0.5;
        const viewport = page.getViewport({ scale });

        const canvas = document.createElement('canvas');
        const context = canvas.getContext('2d');
        canvas.height = viewport.height;
        canvas.width = viewport.width;

        const renderContext = {
            canvasContext: context,
            viewport: viewport
        };

        await page.render(renderContext).promise;

        // Save canvas to object and re-render
        fileObj.canvas = canvas;
        updateUI(); // Re-render to show the thumbnail

    } catch (error) {
        console.error("Thumbnail error:", error);
    }
}

// --- Drag & Drop Sorting ---
let dragSrcEl = null;

function handleDragStart(e) {
    dragSrcEl = this;
    e.dataTransfer.effectAllowed = 'move';
    this.classList.add('dragging');
}

function handleDragOver(e) {
    if (e.preventDefault) e.preventDefault();
    return false;
}

function handleDrop(e) {
    e.stopPropagation();
    if (dragSrcEl !== this) {
        // Swap data in 'files' array
        const idx1 = files.findIndex(f => f.id === dragSrcEl.dataset.id);
        const idx2 = files.findIndex(f => f.id === this.dataset.id);

        if (idx1 > -1 && idx2 > -1) {
            // Swap array elements
            const temp = files[idx1];
            files[idx1] = files[idx2];
            files[idx2] = temp;
            updateUI();
        }
    }
    return false;
}

function handleDragEnd() {
    this.classList.remove('dragging');
}
