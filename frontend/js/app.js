/** Main application initialization and coordination */
document.addEventListener('DOMContentLoaded', () => {
    console.log('XCMS Metabolite MS2 Matching Tool initialized');
    
    // Initialize status indicator
    updateStatus('Ready', 'ready');
    
    // Check API connection
    checkAPIConnection();
});

async function checkAPIConnection() {
    try {
        const response = await fetch(`${API_BASE_URL}/health`);
        if (response.ok) {
            console.log('API connection successful');
        } else {
            console.warn('API health check failed');
            showNotification('Warning: API connection issue', 'warning');
        }
    } catch (error) {
        console.error('API connection failed:', error);
        showNotification('Error: Cannot connect to backend API. Please ensure the server is running.', 'error');
    }
}

function showNotification(message, type = 'info') {
    // Create a simple notification
    const notification = document.createElement('div');
    notification.className = `fixed top-4 right-4 p-4 rounded-lg shadow-lg z-50 ${
        type === 'error' ? 'bg-red-500 text-white' :
        type === 'warning' ? 'bg-yellow-500 text-black' :
        'bg-blue-500 text-white'
    }`;
    notification.textContent = message;
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.remove();
    }, 5000);
}

function updateStatus(message, type) {
    const indicator = document.getElementById('status-indicator');
    if (indicator) {
        indicator.textContent = message;
        indicator.className = `text-sm ${type}`;
    }
}

// Export for global use
window.showNotification = showNotification;
window.updateStatus = updateStatus;

