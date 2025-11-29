/** XCMS processing functionality */
let xcmsResults = null;

// Check XCMS availability on load
document.addEventListener('DOMContentLoaded', async () => {
    try {
        const response = await fetch(`${API_BASE_URL}/api/xcms/check`);
        const data = await response.json();
        
        if (data.r_xcms_available || data.pyopenms_available) {
            document.getElementById('xcms-processing-section').classList.remove('hidden');
            document.getElementById('step1-label').textContent = 'Upload/Process';
        } else {
            console.warn('XCMS processing not available');
        }
    } catch (error) {
        console.error('Error checking XCMS availability:', error);
    }
});

// Toggle XCMS configuration
document.getElementById('enable-xcms')?.addEventListener('change', (e) => {
    const configDiv = document.getElementById('xcms-config');
    if (e.target.checked) {
        configDiv.classList.remove('hidden');
    } else {
        configDiv.classList.add('hidden');
    }
});

// Run XCMS processing
document.getElementById('run-xcms')?.addEventListener('click', async () => {
    const statusDiv = document.getElementById('xcms-status');
    const mzxmlFiles = window.uploadedFiles?.mzxml || [];
    
    if (mzxmlFiles.length === 0) {
        statusDiv.textContent = 'Error: Please upload mzXML files first';
        statusDiv.className = 'mt-2 text-sm text-red-600';
        return;
    }
    
    try {
        statusDiv.textContent = 'Processing with XCMS... This may take several minutes.';
        statusDiv.className = 'mt-2 text-sm text-blue-600';
        updateStatus('Running XCMS processing...', 'processing');
        
        // Get configuration
        const config = {
            ppm: parseFloat(document.getElementById('xcms-ppm').value),
            peakwidth_min: parseFloat(document.getElementById('xcms-peakwidth-min').value),
            peakwidth_max: parseFloat(document.getElementById('xcms-peakwidth-max').value),
            snthresh: parseFloat(document.getElementById('xcms-snthresh').value),
            mzdiff: parseFloat(document.getElementById('xcms-mzdiff').value),
            bw: parseFloat(document.getElementById('xcms-bw').value),
            quant_method: "into",
            minfrac: 0.5,
            minsamp: 0,
            mzwid: 0.006,
            peak_detection_method: "centWave",
            peak_grouping_method: "density",
            rt_correction_method: "obiwarp",
            prefilter_min: 3,
            prefilter_max: 100
        };
        
        const mzxmlFileNames = mzxmlFiles.map(f => f.filename);
        const result = await api.processXCMS(mzxmlFileNames, config);
        
        if (result.success) {
            xcmsResults = result;
            statusDiv.textContent = `✓ XCMS processing completed! Peak table: ${result.peak_table}`;
            statusDiv.className = 'mt-2 text-sm text-green-600';
            updateStatus('XCMS processing completed', 'ready');
            
            // Automatically set the XCMS results as the uploaded XCMS file
            window.uploadedFiles = window.uploadedFiles || {};
            window.uploadedFiles.xcms = {
                filename: result.peak_table,
                path: result.peak_table,
                size: 0,
                processed: true
            };
            
            // Show success message
            if (window.showNotification) {
                window.showNotification('XCMS processing completed successfully!', 'info');
            }
        } else {
            throw new Error(result.message || 'XCMS processing failed');
        }
    } catch (error) {
        statusDiv.textContent = `Error: ${error.message}`;
        statusDiv.className = 'mt-2 text-sm text-red-600';
        updateStatus('XCMS processing failed', 'error');
        console.error('XCMS processing error:', error);
    }
});

// Add to API client
if (typeof api !== 'undefined') {
    api.processXCMS = async function(mzxmlFiles, config) {
        const response = await fetch(`${this.baseURL}/api/xcms/process`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                mzxml_files: mzxmlFiles,
                config: config
            })
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'XCMS processing failed');
        }
        
        return await response.json();
    };
    
    api.getXCMSResults = async function(resultId) {
        const response = await fetch(`${this.baseURL}/api/xcms/results/${resultId}`);
        
        if (!response.ok) {
            throw new Error('Failed to get XCMS results');
        }
        
        return await response.json();
    };
}

// Export for use in other modules
window.xcmsProcessor = {
    getResults: () => xcmsResults
};

