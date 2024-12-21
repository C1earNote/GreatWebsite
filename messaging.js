window.onload = function() {
    const loginStatusElement = document.getElementById("loginStatus");
    const username = localStorage.getItem("username"); // Assuming the username is saved in localStorage
    const logoutButton = document.getElementById("logoutButton");

    if (username) {
        loginStatusElement.textContent = `You are now logged in as ${username}.`;
        
        // Add an event listener to handle the logout
        logoutButton.onclick = function() {
            localStorage.removeItem("username"); // Remove the username from localStorage
            window.location.href = "index.html"; // Redirect to the login page
        };

        // Load the messages for the logged-in user
        loadMessages(username);
    } else {
        loginStatusElement.textContent = "You are not logged in.";
        logoutButton.style.display = "none"; // Hide the logout button if not logged in
    }
};

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
        const response = await fetch("https://greatwebsite.onrender.com/messages", {
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
            loadMessages(senderUsername); // Reload messages after sending
            clearMessageForm();  // Clear the message form fields
        } else {
            alert(`Error: ${data.message}`);
        }
    } catch (error) {
        alert("An error occurred. Please try again later.");
        console.error("Error:", error);
    }
});

// Clear the message form after sending the message
function clearMessageForm() {
    document.getElementById("receiver").value = "";
    document.getElementById("messageContent").value = "";
}

// Load messages function to reload the messages
async function loadMessages(username) {
    try {
        const response = await fetch(`https://greatwebsite.onrender.com/messages/${username}`);
        const data = await response.json();

        if (response.ok) {
            displayMessages(data);  // Display messages
        } else {
            alert("Error loading messages.");
        }
    } catch (error) {
        console.error("Error loading messages:", error);
    }
}

// Function to display the messages
function displayMessages(data) {
    const messagesList = document.getElementById("messagesList");
    
    // Clear previous messages
    messagesList.innerHTML = "";

    // Display received messages
    data.received.forEach(msg => {
        const messageDiv = document.createElement("div");
        messageDiv.classList.add("message");

        // Create the message content and timestamp separately
        const messageContent = document.createElement("span");
        messageContent.textContent = `${msg.sender}: ${msg.content}`;
        
        const timestamp = document.createElement("span");
        timestamp.textContent = ` (Sent at: ${msg.timestamp})`;
        timestamp.classList.add("timestamp");  // Apply a class for styling

        // Append both parts to the message div
        messageDiv.appendChild(messageContent);
        messageDiv.appendChild(timestamp);
        messagesList.appendChild(messageDiv);
    });

    // Display sent messages
    data.sent.forEach(msg => {
        const messageDiv = document.createElement("div");
        messageDiv.classList.add("message");

        // Create the message content and timestamp separately
        const messageContent = document.createElement("span");
        messageContent.textContent = `You: ${msg.content}`;
        
        const timestamp = document.createElement("span");
        timestamp.textContent = ` (Sent at: ${msg.timestamp})`;
        timestamp.classList.add("timestamp");  // Apply a class for styling

        // Append both parts to the message div
        messageDiv.appendChild(messageContent);
        messageDiv.appendChild(timestamp);
        messagesList.appendChild(messageDiv);
    });
}

// Socket.IO connection to listen for new messages
const socket = io("https://greatwebsite.onrender.com");

socket.on("new_message", function (messageData) {
    console.log("New message received:", messageData);
    loadMessages(localStorage.getItem("username"));
});
