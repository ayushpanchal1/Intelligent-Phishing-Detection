chrome.webNavigation.onCompleted.addListener(function(details) {
    // Check if the navigation is in the main frame
    if (details.frameId === 0) {
        var url = details.url;
        if (url) {
            // Send API request only for the main frame URL
            fetch('http://127.0.0.1:5000/predict', { //http://13.233.89.104:5000/predict
                method: 'POST',
                body: JSON.stringify({ url: url }),
                headers: {
                    'Content-Type': 'application/json'
                }
            })
            .then(response => response.json())
            .then(data => {
                console.log(data);
                // Send message to content script with the result
                chrome.tabs.sendMessage(details.tabId, {result: data.result});
                // Store response in chrome.storage.local
                chrome.storage.local.set({response: data.result}, function() {
                    console.log('Response stored:', data);
                });
            })
            .catch(error => console.error('Error:', error));
        } else {
            console.error('Error: Unable to retrieve URL from webNavigation details.');
        }
    }
});
