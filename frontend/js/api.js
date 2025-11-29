/** API client for backend communication */
const API_BASE_URL = 'http://localhost:8000';

class APIClient {
    constructor(baseURL = API_BASE_URL) {
        this.baseURL = baseURL;
    }

    async uploadXCMS(file) {
        const formData = new FormData();
        formData.append('file', file);
        
        const response = await fetch(`${this.baseURL}/api/upload/xcms`, {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            throw new Error(`Upload failed: ${response.statusText}`);
        }
        
        return await response.json();
    }

    async uploadMzXML(file) {
        const formData = new FormData();
        formData.append('file', file);
        
        const response = await fetch(`${this.baseURL}/api/upload/mzxml`, {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            throw new Error(`Upload failed: ${response.statusText}`);
        }
        
        return await response.json();
    }

    async uploadLibrary(file) {
        const formData = new FormData();
        formData.append('file', file);
        
        const response = await fetch(`${this.baseURL}/api/upload/library`, {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            throw new Error(`Upload failed: ${response.statusText}`);
        }
        
        return await response.json();
    }

    async getXCMSPeaks(xcmsFile) {
        const response = await fetch(`${this.baseURL}/api/xcms/peaks?xcms_file=${encodeURIComponent(xcmsFile)}`);
        
        if (!response.ok) {
            throw new Error(`Failed to get peaks: ${response.statusText}`);
        }
        
        return await response.json();
    }

    async extractMS2(mzxmlFile, xcmsFile, config) {
        const response = await fetch(`${this.baseURL}/api/extract/ms2`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                mzxml_file: mzxmlFile,
                xcms_file: xcmsFile,
                ...config
            })
        });
        
        if (!response.ok) {
            throw new Error(`MS2 extraction failed: ${response.statusText}`);
        }
        
        return await response.json();
    }

    async matchSpectra(mzxmlFile, xcmsFile, libraryFile, algorithm, config) {
        const response = await fetch(`${this.baseURL}/api/match/spectra`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                mzxml_file: mzxmlFile,
                xcms_file: xcmsFile,
                library_file: libraryFile,
                algorithm: algorithm,
                config: config
            })
        });
        
        if (!response.ok) {
            throw new Error(`Matching failed: ${response.statusText}`);
        }
        
        return await response.json();
    }
}

// Global API client instance
const api = new APIClient();

