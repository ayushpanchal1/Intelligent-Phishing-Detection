// This script will be injected into the webpage to show an overlay indicating phishing

// Function to create overlay
function createOverlay() {
    // Check if the overlay already exists
    if (document.getElementById('phishing-overlay')) {
        return; // Overlay already exists, so exit the function
    }

    var overlayDiv = document.createElement('div');
    overlayDiv.id = 'phishing-overlay';
    overlayDiv.style.position = 'fixed';
    overlayDiv.style.top = '50%';
    overlayDiv.style.left = '50%';
    overlayDiv.style.transform = 'translate(-50%, -50%)';
    overlayDiv.style.width = '300px'; 
    overlayDiv.style.height = '150px'; 
    overlayDiv.style.background = 'rgb(143 18 18 / 80%)'; 
    overlayDiv.style.color = '#fff';
    overlayDiv.style.fontFamily = 'Roboto';
    overlayDiv.style.fontSize = '18px';
    overlayDiv.style.textAlign = 'center';
    overlayDiv.style.borderRadius = '10px'; 
    overlayDiv.style.boxShadow = '0 4px 8px rgba(0, 0, 0, 0.4)'; 

    // Center the text vertically and horizontally within the overlay
    overlayDiv.style.display = 'flex';
    overlayDiv.style.flexDirection = 'column';
    overlayDiv.style.alignItems = 'center';
    overlayDiv.style.justifyContent = 'center';

    overlayDiv.textContent = 'Potential Phishing Website Detected';

    var closeButton = document.createElement('span');
    closeButton.textContent = 'x';
    closeButton.style.position = 'absolute';
    closeButton.style.top = '5px';
    closeButton.style.right = '8px';
    closeButton.style.cursor = 'pointer';
    closeButton.style.fontWeight = 'bold';
    closeButton.style.fontSize = '20px';
    closeButton.style.color = '#fff';
    closeButton.addEventListener('click', function() {
        // Remove the overlay when the close button is clicked
        overlayDiv.remove();
    });
    overlayDiv.appendChild(closeButton);

    // Add the overlay to the document body
    document.body.appendChild(overlayDiv);
}






// Function to remove overlay
function removeOverlay() {
    var overlayDiv = document.getElementById('phishing-overlay');
    if (overlayDiv) {
        overlayDiv.remove();
    }
}

// Listen for messages from the background script
chrome.runtime.onMessage.addListener(function(message, sender, sendResponse) {
    if (message.result === "Phishing") {
        createOverlay();
    } else {
        removeOverlay();
    }
});

// Check if the initial message indicates phishing
chrome.storage.local.get('response', function(data) {
    if (data.response && data.response === "Phishing") {
        createOverlay();
    }
});
