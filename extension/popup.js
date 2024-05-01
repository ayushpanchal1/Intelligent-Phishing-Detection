// chrome.storage.local.get('response', function(data) {
//     if (chrome.runtime.lastError) {
//         console.error(chrome.runtime.lastError.message);
//         return;
//     }

//     var response = data.response;

//     if (response) {
//         var container = document.querySelector('.container');
//         var heading = document.getElementById('heading');
//         var message = document.getElementById('message');
//         var responseText = document.getElementById('response');

//         if (response === "Phishing") {
//             container.classList.add('phishing');
//             heading.textContent = "Warning: Potential phishing website detected";
//             message.textContent = "Please proceed with caution";
//             responseText.textContent = "The website appears to be a phishing site.";
//         } else if (response === "Legitimate") {
//             container.classList.add('legitimate');
//             heading.textContent = "You are safe, the website seems legitimate";
//             message.textContent = "Enjoy browsing!";
//             responseText.textContent = "The website seems legitimate.";
//         } else {
//             // Handle other response types if needed
//         }
//     } else {
//         console.error('No response data available.');
//     }
// });

chrome.storage.local.get('response', function (data) {
    if (chrome.runtime.lastError) {
        console.error(chrome.runtime.lastError.message);
        return;
    }

    var response = data.response;

    if (response) {
        var container = document.querySelector('.container');
        var heading = document.getElementById('heading');
        var message = document.getElementById('message');

        if (response === "Phishing") {
            container.classList.add('phishing');
            heading.textContent = "Warning: Potential phishing website detected";
            message.textContent = "Please proceed with caution";

            // Show user input section
            document.getElementById('userInput').style.display = 'block';

            // Submit button event listener
            // Submit button event listener
            document.getElementById('submitBelief').addEventListener('click', function () {
                var userInput = document.querySelector('input[name="userBelief"]:checked');
                if (userInput) {
                    var belief = userInput.value;

                    // Get the current URL
                    chrome.tabs.query({ active: true, currentWindow: true }, function (tabs) {
                        var url = tabs[0].url;

                        // Send belief and URL to backend
                        fetch('http://127.0.0.1:5000/feedback', {
                            method: 'POST',
                            body: JSON.stringify({ belief: belief, url: url }),
                            headers: {
                                'Content-Type': 'application/json'
                            }
                        })
                            .then(response => response.json())
                            .then(data => {
                                console.log('Belief and URL submitted:', data);
                            })
                            .catch(error => console.error('Error:', error));
                    });
                } else {
                    alert('Please select an option.');
                }
            });


        } else if (response === "Legitimate") {
            container.classList.add('legitimate');
            heading.textContent = "You are safe, the website seems legitimate";
            message.textContent = "Enjoy browsing!";
        } else {
            // Handle other response types if needed
        }
    } else {
        console.error('No response data available.');
    }
});
