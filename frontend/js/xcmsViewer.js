/** XCMS data viewer */
let xcmsData = null;

async function loadXCMSData(filename) {
    try {
        const response = await api.getXCMSPeaks(filename);
        xcmsData = response.peaks;
        return xcmsData;
    } catch (error) {
        console.error('Error loading XCMS data:', error);
        throw error;
    }
}

function filterPeaks(peaks, filters) {
    if (!peaks) return [];
    
    return peaks.filter(peak => {
        if (filters.mzMin && peak.mz < filters.mzMin) return false;
        if (filters.mzMax && peak.mz > filters.mzMax) return false;
        if (filters.rtMin && peak.rt < filters.rtMin) return false;
        if (filters.rtMax && peak.rt > filters.rtMax) return false;
        if (filters.search && !peak.name.toLowerCase().includes(filters.search.toLowerCase())) {
            return false;
        }
        return true;
    });
}

function displayPeaksTable(peaks, containerId) {
    const container = document.getElementById(containerId);
    if (!container) return;
    
    if (peaks.length === 0) {
        container.innerHTML = '<tr><td colspan="7" class="px-6 py-4 text-center">No peaks found</td></tr>';
        return;
    }
    
    container.innerHTML = peaks.map(peak => `
        <tr class="bg-white border-b hover:bg-gray-50">
            <td class="px-6 py-4 font-medium text-gray-900">${peak.name}</td>
            <td class="px-6 py-4">${peak.mz.toFixed(4)}</td>
            <td class="px-6 py-4">${peak.rt.toFixed(2)}</td>
            <td class="px-6 py-4">${peak.npeaks}</td>
            <td class="px-6 py-4">${Object.keys(peak.intensities || {}).length}</td>
            <td class="px-6 py-4">${getMaxIntensity(peak.intensities).toExponential(2)}</td>
            <td class="px-6 py-4">
                <button class="text-blue-600 hover:underline" onclick="viewPeakDetails('${peak.name}')">
                    View
                </button>
            </td>
        </tr>
    `).join('');
}

function getMaxIntensity(intensities) {
    if (!intensities || Object.keys(intensities).length === 0) return 0;
    return Math.max(...Object.values(intensities));
}

function viewPeakDetails(peakName) {
    if (!xcmsData) return;
    
    const peak = xcmsData.find(p => p.name === peakName);
    if (!peak) return;
    
    // Show peak details in a modal or side panel
    console.log('Peak details:', peak);
    // TODO: Implement detailed view
}

// Export for use in other modules
window.xcmsViewer = {
    loadXCMSData,
    filterPeaks,
    displayPeaksTable,
    getData: () => xcmsData
};

