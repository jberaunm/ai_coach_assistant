// File Upload Handling
export function initializeFileUpload(websocket) {
    console.log('Initializing file upload...');
    const dropZone = document.querySelector('.drop-zone');
    const fileInput = document.getElementById('fileUpload');

    if (!dropZone || !fileInput) {
        console.error('Drop zone or file input not found!');
        return;
    }

    console.log('Drop zone and file input found!');

    dropZone.addEventListener('click', () => {
        console.log('Drop zone clicked');
        fileInput.click();
    });

    dropZone.addEventListener('dragover', (e) => {
        console.log('File dragged over');
        e.preventDefault();
        dropZone.classList.add('dragover');
    });

    dropZone.addEventListener('dragleave', () => {
        console.log('File dragged out');
        dropZone.classList.remove('dragover');
    });

    dropZone.addEventListener('drop', (e) => {
        console.log('File dropped');
        e.preventDefault();
        dropZone.classList.remove('dragover');
        
        const files = e.dataTransfer.files;
        handleFiles(files, websocket);
    });

    fileInput.addEventListener('change', (e) => {
        console.log('File selected via input');
        const files = e.target.files;
        handleFiles(files, websocket);
    });
}

function handleFiles(files, websocket) {
    console.log('Handling files:', files);
    if (files.length > 0) {
        const file = files[0];
        console.log('File selected:', file.name);
        
        // Create FormData and append the file
        const formData = new FormData();
        formData.append('file', file);
        
        // Get the session ID from the WebSocket URL
        const wsUrl = new URL(websocket.url);
        const sessionId = wsUrl.pathname.split('/').pop();
        console.log('Extracted session ID:', sessionId);
        console.log('WebSocket URL:', websocket.url);
        
        // Show loading state
        const dropZone = document.querySelector('.drop-zone');
        const originalText = dropZone.querySelector('p').textContent;
        dropZone.querySelector('p').textContent = 'Uploading...';
        dropZone.style.opacity = '0.7';
        
        // Send the file to the server
        const uploadUrl = `/upload?session_id=${sessionId}`;
        console.log('Uploading to URL:', uploadUrl);
        
        fetch(uploadUrl, {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            console.log('Upload response:', data);
            if (data.status === 'success') {
                dropZone.querySelector('p').textContent = 'File uploaded successfully!';
                dropZone.style.borderColor = 'var(--success-color, #4CAF50)';
            } else {
                throw new Error(data.message || 'Upload failed');
            }
        })
        .catch(error => {
            console.error('Upload error:', error);
            dropZone.querySelector('p').textContent = 'Upload failed. Please try again.';
            dropZone.style.borderColor = 'var(--error-color, #f44336)';
        })
        .finally(() => {
            // Reset the drop zone after 3 seconds
            setTimeout(() => {
                dropZone.querySelector('p').textContent = originalText;
                dropZone.style.opacity = '1';
                dropZone.style.borderColor = 'var(--gray-medium)';
            }, 3000);
        });
    }
} 