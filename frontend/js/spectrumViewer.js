/** Spectrum visualization */
let spectrumChart = null;

function displaySpectrum(spectrumData, title = 'Spectrum') {
    const modal = document.getElementById('spectrum-modal');
    const canvas = document.getElementById('spectrum-chart');
    const titleElement = document.getElementById('spectrum-title');
    
    if (!modal || !canvas || !titleElement) return;
    
    titleElement.textContent = title;
    modal.classList.remove('hidden');
    
    // Destroy existing chart if it exists
    if (spectrumChart) {
        spectrumChart.destroy();
    }
    
    // Prepare data for Chart.js
    const mz = spectrumData.mz || [];
    const intensities = spectrumData.intensities || [];
    
    // Create bar chart
    const ctx = canvas.getContext('2d');
    spectrumChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: mz.map(m => m.toFixed(4)),
            datasets: [{
                label: 'Intensity',
                data: intensities,
                backgroundColor: 'rgba(59, 130, 246, 0.5)',
                borderColor: 'rgba(59, 130, 246, 1)',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            scales: {
                x: {
                    title: {
                        display: true,
                        text: 'm/z'
                    },
                    ticks: {
                        maxRotation: 90,
                        minRotation: 90
                    }
                },
                y: {
                    title: {
                        display: true,
                        text: 'Intensity'
                    },
                    beginAtZero: true
                }
            },
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return `m/z: ${context.label}, Intensity: ${context.parsed.y.toExponential(2)}`;
                        }
                    }
                }
            }
        }
    });
}

function displayComparisonSpectrum(querySpectrum, librarySpectrum, title = 'Spectrum Comparison') {
    const modal = document.getElementById('spectrum-modal');
    const canvas = document.getElementById('spectrum-chart');
    const titleElement = document.getElementById('spectrum-title');
    
    if (!modal || !canvas || !titleElement) return;
    
    titleElement.textContent = title;
    modal.classList.remove('hidden');
    
    // Destroy existing chart if it exists
    if (spectrumChart) {
        spectrumChart.destroy();
    }
    
    // Prepare data
    const queryMz = querySpectrum.mz || [];
    const queryIntensities = querySpectrum.intensities || [];
    const libraryMz = librarySpectrum.mz || [];
    const libraryIntensities = librarySpectrum.intensities || [];
    
    // Combine m/z values and align intensities
    const allMz = [...new Set([...queryMz, ...libraryMz])].sort((a, b) => a - b);
    const alignedQuery = allMz.map(mz => {
        const idx = queryMz.findIndex(m => Math.abs(m - mz) < 0.01);
        return idx >= 0 ? queryIntensities[idx] : 0;
    });
    const alignedLibrary = allMz.map(mz => {
        const idx = libraryMz.findIndex(m => Math.abs(m - mz) < 0.01);
        return idx >= 0 ? libraryIntensities[idx] : 0;
    });
    
    const ctx = canvas.getContext('2d');
    spectrumChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: allMz.map(m => m.toFixed(4)),
            datasets: [
                {
                    label: 'Query',
                    data: alignedQuery,
                    backgroundColor: 'rgba(59, 130, 246, 0.5)',
                    borderColor: 'rgba(59, 130, 246, 1)',
                    borderWidth: 1
                },
                {
                    label: 'Library',
                    data: alignedLibrary,
                    backgroundColor: 'rgba(239, 68, 68, 0.5)',
                    borderColor: 'rgba(239, 68, 68, 1)',
                    borderWidth: 1
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            scales: {
                x: {
                    title: {
                        display: true,
                        text: 'm/z'
                    }
                },
                y: {
                    title: {
                        display: true,
                        text: 'Intensity'
                    },
                    beginAtZero: true
                }
            }
        }
    });
}

// Close modal
document.getElementById('close-spectrum')?.addEventListener('click', () => {
    const modal = document.getElementById('spectrum-modal');
    if (modal) {
        modal.classList.add('hidden');
    }
});

// Export for use in other modules
window.spectrumViewer = {
    displaySpectrum,
    displayComparisonSpectrum
};

