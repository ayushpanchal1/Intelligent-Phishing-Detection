chrome.storage.local.get('response', function(data) {
    if (chrome.runtime.lastError) {
        console.error(chrome.runtime.lastError.message);
        return;
    }

    var response = data.response;

    if (response) {
        var container = document.querySelector('.container');
        var heading = document.getElementById('heading');
        var message = document.getElementById('message');
        var responseText = document.getElementById('response');

        if (response === "Phishing") {
            container.classList.add('phishing');
            heading.textContent = "Warning: Potential phishing website detected";
            message.textContent = "Please proceed with caution";
            responseText.textContent = "The website appears to be a phishing site.";
        } else if (response === "Legitimate") {
            container.classList.add('legitimate');
            heading.textContent = "You are safe, the website seems legitimate";
            message.textContent = "Enjoy browsing!";
            responseText.textContent = "The website seems legitimate.";
        } else {
            // Handle other response types if needed
        }
    } else {
        console.error('No response data available.');
    }
});
