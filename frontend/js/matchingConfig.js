/** Matching configuration and execution */
let matchingResults = null;

document.getElementById('run-matching')?.addEventListener('click', async () => {
    if (!window.uploadedFiles) {
        alert('Please upload all required files first');
        return;
    }
    
    const { xcms, mzxml, library } = window.uploadedFiles;
    
    if (!xcms || !mzxml || mzxml.length === 0 || !library) {
        alert('Please upload XCMS results, mzXML files, and library file');
        return;
    }
    
    try {
        updateStatus('Extracting MS2 spectra...', 'processing');
        
        // Get configuration
        const config = {
            algorithm: document.getElementById('algorithm').value,
            mz_tolerance: parseFloat(document.getElementById('mz-tolerance').value),
            rt_tolerance: parseFloat(document.getElementById('rt-tolerance').value),
            min_score: parseFloat(document.getElementById('min-score').value),
            top_n: parseInt(document.getElementById('top-n').value)
        };
        
        // Extract MS2 spectra from first mzXML file
        const mzxmlFile = mzxml[0].filename;
        const xcmsFile = xcms.filename;
        
        const extractionConfig = {
            mz_tolerance: config.mz_tolerance,
            rt_tolerance: config.rt_tolerance,
            min_intensity: 100.0
        };
        
        const extractionResult = await api.extractMS2(mzxmlFile, xcmsFile, extractionConfig);
        
        updateStatus('Matching spectra...', 'processing');
        
        // Perform matching
        const libraryFile = library.filename;
        const matchResult = await api.matchSpectra(mzxmlFile, xcmsFile, libraryFile, config.algorithm, config);
        
        matchingResults = {
            extraction: extractionResult,
            matching: matchResult,
            config: config
        };
        
        updateStatus('Matching completed', 'ready');
        
        // Show results
        document.getElementById('step-results').classList.remove('hidden');
        
        // Use the global displayResults function
        if (window.displayResults) {
            window.displayResults(matchingResults);
        } else {
            console.error('displayResults function not found');
        }
        
    } catch (error) {
        updateStatus('Error during matching', 'error');
        alert(`Error: ${error.message}`);
        console.error('Matching error:', error);
    }
});

function displayResults(results) {
    // This is a placeholder - actual implementation would process the results
    const tbody = document.getElementById('results-tbody');
    if (!tbody) return;
    
    // For now, show a message that results are being processed
    tbody.innerHTML = `
        <tr>
            <td colspan="7" class="px-6 py-4 text-center text-gray-500">
                Results processing... Check console for details.
            </td>
        </tr>
    `;
    
    console.log('Matching results:', results);
}

function updateStatus(message, type) {
    const indicator = document.getElementById('status-indicator');
    if (indicator) {
        indicator.textContent = message;
        indicator.className = `text-sm ${type}`;
    }
}

// Export for use in other modules
window.matchingConfig = {
    getResults: () => matchingResults
};

