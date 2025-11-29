/** Results display and export */
let currentResults = null;

function displayResults(results) {
    currentResults = results;
    
    const tbody = document.getElementById('results-tbody');
    if (!tbody) return;
    
    if (!results || !results.matching) {
        tbody.innerHTML = '<tr><td colspan="7" class="px-6 py-4 text-center">No results available</td></tr>';
        return;
    }
    
    // Get processed results if available, otherwise use raw matches
    const processedResults = results.matching.processed_results || [];
    const matches = results.matching.matches || [];
    
    // Use processed results if available
    if (processedResults.length > 0) {
        displayProcessedResults(processedResults, tbody);
        return;
    }
    
    // Fallback to raw matches
    tbody.innerHTML = matches.map((match, index) => {
        const bestMatch = match.best_match || {};
        const metadata = bestMatch.metadata || {};
        
        return `
            <tr class="bg-white border-b hover:bg-gray-50">
                <td class="px-6 py-4 font-medium text-gray-900">${match.query_spectrum?.feature_name || `Feature ${index}`}</td>
                <td class="px-6 py-4">${match.query_spectrum?.precursor_mz?.toFixed(4) || 'N/A'}</td>
                <td class="px-6 py-4">${match.query_spectrum?.retention_time?.toFixed(2) || 'N/A'}</td>
                <td class="px-6 py-4">${bestMatch.compound_name || 'Unknown'}</td>
                <td class="px-6 py-4">${bestMatch.score?.toFixed(4) || '0.0000'}</td>
                <td class="px-6 py-4">
                    <span class="px-2 py-1 text-xs rounded-full ${getConfidenceColor(bestMatch.score)}">
                        ${(bestMatch.score * 100).toFixed(1)}%
                    </span>
                </td>
                <td class="px-6 py-4">
                    <button class="text-blue-600 hover:underline mr-2" onclick="viewMatchDetails(${index})">
                        View
                    </button>
                    <button class="text-green-600 hover:underline" onclick="viewSpectrum(${index})">
                        Spectrum
                    </button>
                </td>
            </tr>
        `;
    }).join('');
}

function displayProcessedResults(processedResults, tbody) {
    tbody.innerHTML = processedResults.map((result, index) => {
        const bestMatch = result.best_match || {};
        const xcmsPeak = result.xcms_peak || {};
        
        return `
            <tr class="bg-white border-b hover:bg-gray-50">
                <td class="px-6 py-4 font-medium text-gray-900">${result.feature_name || `Feature ${index}`}</td>
                <td class="px-6 py-4">${xcmsPeak.mz?.toFixed(4) || result.precursor_mz?.toFixed(4) || 'N/A'}</td>
                <td class="px-6 py-4">${xcmsPeak.rt?.toFixed(2) || result.retention_time?.toFixed(2) || 'N/A'}</td>
                <td class="px-6 py-4">${bestMatch.compound_name || 'Unknown'}</td>
                <td class="px-6 py-4">${bestMatch.score?.toFixed(4) || '0.0000'}</td>
                <td class="px-6 py-4">
                    <span class="px-2 py-1 text-xs rounded-full ${getConfidenceColor(result.confidence_score || bestMatch.score || 0)}">
                        ${((result.confidence_score || bestMatch.score || 0) * 100).toFixed(1)}%
                    </span>
                </td>
                <td class="px-6 py-4">
                    <button class="text-blue-600 hover:underline mr-2" onclick="viewMatchDetails(${index})">
                        View
                    </button>
                    <button class="text-green-600 hover:underline" onclick="viewSpectrum(${index})">
                        Spectrum
                    </button>
                </td>
            </tr>
        `;
    }).join('');
}

function getConfidenceColor(score) {
    if (score >= 0.7) return 'bg-green-100 text-green-800';
    if (score >= 0.4) return 'bg-yellow-100 text-yellow-800';
    return 'bg-red-100 text-red-800';
}

function viewMatchDetails(index) {
    if (!currentResults || !currentResults.matching) return;
    
    // Try processed results first
    const processedResults = currentResults.matching.processed_results || [];
    if (processedResults.length > index) {
        const result = processedResults[index];
        const bestMatch = result.best_match || {};
        const metadata = bestMatch.metadata || {};
        
        const details = `
Feature: ${result.feature_name || 'Unknown'}
Compound: ${bestMatch.compound_name || 'Unknown'}
Score: ${bestMatch.score?.toFixed(4) || '0.0000'}
Confidence: ${(result.confidence_score * 100).toFixed(1)}%
Matched Peaks: ${bestMatch.matched_peaks || 0}
Total Peaks: ${bestMatch.total_peaks || 0}
Algorithm: ${result.algorithm || currentResults.config?.algorithm || 'Unknown'}
Precursor m/z: ${metadata.precursor_mz || 'N/A'}
SMILES: ${metadata.smiles || 'N/A'}
InChI: ${metadata.inchi || 'N/A'}
        `.trim();
        
        alert(details);
        return;
    }
    
    // Fallback to raw matches
    const matches = currentResults.matching.matches || [];
    if (matches.length > index) {
        const match = matches[index];
        const bestMatch = match.best_match || {};
        const metadata = bestMatch.metadata || {};
        
        const details = `
Feature: ${match.query_spectrum?.feature_name || 'Unknown'}
Compound: ${bestMatch.compound_name || 'Unknown'}
Score: ${bestMatch.score?.toFixed(4) || '0.0000'}
Matched Peaks: ${bestMatch.matched_peaks || 0}
Total Peaks: ${bestMatch.total_peaks || 0}
Algorithm: ${currentResults.config?.algorithm || 'Unknown'}
Precursor m/z: ${metadata.precursor_mz || 'N/A'}
        `.trim();
        
        alert(details);
    }
}

function viewSpectrum(index) {
    if (!currentResults) return;
    
    // Get spectrum data and display
    const extraction = currentResults.extraction;
    if (extraction && extraction.spectra && extraction.spectra[index]) {
        const spectrum = extraction.spectra[index];
        const featureName = spectrum.feature_name || spectrum.matched_xcms_peak || `Feature ${index}`;
        
        if (window.spectrumViewer && window.spectrumViewer.displaySpectrum) {
            window.spectrumViewer.displaySpectrum(
                { mz: spectrum.mz, intensities: spectrum.intensities },
                `Spectrum: ${featureName}`
            );
        } else {
            console.error('Spectrum viewer not available');
            alert('Spectrum viewer not initialized');
        }
    } else {
        alert('Spectrum data not available for this feature');
    }
}

// Export CSV
document.getElementById('export-csv')?.addEventListener('click', () => {
    if (!currentResults) {
        alert('No results to export');
        return;
    }
    
    // Convert results to CSV
    const csv = convertToCSV(currentResults);
    downloadFile(csv, 'matching_results.csv', 'text/csv');
});

// Export JSON
document.getElementById('export-json')?.addEventListener('click', () => {
    if (!currentResults) {
        alert('No results to export');
        return;
    }
    
    const json = JSON.stringify(currentResults, null, 2);
    downloadFile(json, 'matching_results.json', 'application/json');
});

function convertToCSV(results) {
    if (!results || !results.matching) return '';
    
    const headers = ['Feature', 'm/z', 'RT', 'Compound', 'Score', 'Algorithm', 'Confidence'];
    const rows = [headers.join(',')];
    
    // Use processed results if available
    const processedResults = results.matching.processed_results || [];
    if (processedResults.length > 0) {
        processedResults.forEach(result => {
            const bestMatch = result.best_match || {};
            const xcmsPeak = result.xcms_peak || {};
            const row = [
                result.feature_name || '',
                (xcmsPeak.mz || result.precursor_mz || '').toString(),
                (xcmsPeak.rt || result.retention_time || '').toString(),
                bestMatch.compound_name || '',
                (bestMatch.score || '').toString(),
                result.algorithm || '',
                ((result.confidence_score || bestMatch.score || 0) * 100).toFixed(1) + '%'
            ];
            rows.push(row.join(','));
        });
    } else {
        // Fallback to raw matches
        const matches = results.matching.matches || [];
        matches.forEach(match => {
            const bestMatch = match.best_match || {};
            const row = [
                match.query_spectrum?.feature_name || '',
                (match.query_spectrum?.precursor_mz || '').toString(),
                (match.query_spectrum?.retention_time || '').toString(),
                bestMatch.compound_name || '',
                (bestMatch.score || '').toString(),
                results.config?.algorithm || '',
                ((bestMatch.score || 0) * 100).toFixed(1) + '%'
            ];
            rows.push(row.join(','));
        });
    }
    
    return rows.join('\n');
}

function downloadFile(content, filename, contentType) {
    const blob = new Blob([content], { type: contentType });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}

// Export functions for global use
window.viewMatchDetails = viewMatchDetails;
window.viewSpectrum = viewSpectrum;
window.displayResults = displayResults;

