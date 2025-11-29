/** File upload handling */
let uploadedFiles = {
    xcms: null,
    mzxml: [],
    library: null
};

// XCMS file upload
document.getElementById('xcms-file').addEventListener('change', async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    
    try {
        updateStatus('Uploading XCMS file...', 'processing');
        const result = await api.uploadXCMS(file);
        uploadedFiles.xcms = result;
        
        document.getElementById('xcms-file-info').textContent = 
            `✓ ${file.name} (${formatFileSize(result.size)})`;
        
        updateStatus('XCMS file uploaded', 'ready');
        checkFilesReady();
    } catch (error) {
        updateStatus('Upload failed', 'error');
        alert(`Error uploading XCMS file: ${error.message}`);
    }
});

// mzXML files upload
document.getElementById('mzxml-files').addEventListener('change', async (e) => {
    const files = Array.from(e.target.files);
    if (files.length === 0) return;
    
    try {
        updateStatus('Uploading mzXML files...', 'processing');
        uploadedFiles.mzxml = [];
        
        for (const file of files) {
            const result = await api.uploadMzXML(file);
            uploadedFiles.mzxml.push(result);
        }
        
        const fileList = uploadedFiles.mzxml.map(f => f.filename).join(', ');
        document.getElementById('mzxml-files-info').textContent = 
            `✓ ${uploadedFiles.mzxml.length} file(s) uploaded: ${fileList}`;
        
        updateStatus('mzXML files uploaded', 'ready');
        checkFilesReady();
    } catch (error) {
        updateStatus('Upload failed', 'error');
        alert(`Error uploading mzXML files: ${error.message}`);
    }
});

// Library file upload
document.getElementById('library-file').addEventListener('change', async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    
    try {
        updateStatus('Uploading library file...', 'processing');
        const result = await api.uploadLibrary(file);
        uploadedFiles.library = result;
        
        const info = result.valid ? 
            `✓ ${file.name} (${result.spectra_count || 'unknown'} spectra)` :
            `✗ ${file.name} - Invalid format`;
        
        document.getElementById('library-file-info').textContent = info;
        
        updateStatus('Library file uploaded', 'ready');
        checkFilesReady();
    } catch (error) {
        updateStatus('Upload failed', 'error');
        alert(`Error uploading library file: ${error.message}`);
    }
});

function checkFilesReady() {
    const hasXCMS = uploadedFiles.xcms !== null;
    const hasMzXML = uploadedFiles.mzxml.length > 0;
    const hasLibrary = uploadedFiles.library !== null && uploadedFiles.library.valid;
    
    if (hasXCMS && hasMzXML && hasLibrary) {
        // Show configuration step
        document.getElementById('step-config').classList.remove('hidden');
    }
}

function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
}

function updateStatus(message, type) {
    const indicator = document.getElementById('status-indicator');
    indicator.textContent = message;
    indicator.className = `text-sm ${type}`;
}

// Export for use in other modules
window.uploadedFiles = uploadedFiles;

