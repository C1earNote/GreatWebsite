document.getElementById("messageForm").addEventListener("submit", async function (event) {
    event.preventDefault(); // Prevent the form from refreshing the page

    const receiver = document.getElementById("receiver").value;
    const content = document.getElementById("messageContent").value;
    const senderUsername = localStorage.getItem("username"); // Get the sender's username from localStorage

    if (!senderUsername || !receiver || !content) {
        alert("Sender, receiver, and content are required.");
        return;
    }

    try {
        // Send a POST request to the backend to save the message
        const response = await fetch("http://127.0.0.1:5000/messages", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                sender: senderUsername,
                receiver: receiver,
                content: content,
            }),
        });

        const data = await response.json();

        if (response.ok) {
            //alert("Message sent successfully!");
            loadMessages(senderUsername); // Reload messages after sending
        } else {
            alert(`Error: ${data.message}`);
        }
    } catch (error) {
        alert("An error occurred. Please try again later.");
        console.error("Error:", error);
    }
});

// Function to load messages for the logged-in user
async function loadMessages(username) {
    if (!username) {
        alert("Username not found. Please log in again.");
        return;
    }

    try {
        // Send a GET request to the backend to fetch messages for the user
        const response = await fetch(`http://127.0.0.1:5000/messages/${username}`, {
            method: "GET",
        });

        const data = await response.json();

        if (response.ok) {
            const messagesList = document.getElementById("messagesList");
            messagesList.innerHTML = ''; // Clear existing messages

            // Loop through and display each message
            data.messages.forEach(msg => {
                const messageElement = document.createElement('div');
                messageElement.classList.add('message');
                messageElement.innerHTML = `<strong>${msg.sender}:</strong> ${msg.content} <em>(${msg.timestamp})</em>`;
                messagesList.appendChild(messageElement);
            });
        } else {
            alert(`Error: ${data.message}`);
        }
    } catch (error) {
        alert("An error occurred. Please try again later.");
        console.error("Error:", error);
    }
}

// On page load, check if the user is logged in and load their messages
const username = localStorage.getItem("username"); // Retrieve the username from localStorage
if (username) {
    loadMessages(username);
} else {
    alert("You are not logged in. Redirecting to login page.");
    window.location.href = "login.html";
}
