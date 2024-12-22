window.onload = function () {
    const socket = io("https://greatwebsite.onrender.com");

    // Emit the join event with the username
    const username = localStorage.getItem("username");
    if (username) {
        socket.emit("join", { username: username });
    }

    // Listen for the message_sent event
    socket.on("message_sent", function (messageData) {
        console.log("Message sent event received:", messageData);

        // Check if the message involves the logged-in user
        if (messageData.sender === username || messageData.receiver === username) {
            loadMessages(username); // Reload messages for the involved user
        }
    });
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
            // Notify both sender and receiver about the new message
            const socket = io("https://greatwebsite.onrender.com");
            socket.emit("message_sent", { sender: senderUsername, receiver: receiver });

            loadMessages(senderUsername); // Reload messages for sender
            clearMessageForm(); // Clear the message form fields
        } else {
            alert(`BRUHError: ${data.message}`); // Personalized error handling
        }
    } catch (error) {
        console.error("Error:", error);
    }
});

// Clear the message form after sending the message
function clearMessageForm() {
    document.getElementById("messageContent").value = "";
}

// Load messages function to reload the messages
async function loadMessages(username) {
    try {
        const response = await fetch(`https://greatwebsite.onrender.com/messages/${username}`);
        const data = await response.json();

        if (response.ok) {
            displayMessages(data); // Display messages
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

    // Combine received and sent messages into a single array and sort by timestamp
    const allMessages = [...data.received.map(msg => ({ ...msg, type: "received" })),
                         ...data.sent.map(msg => ({ ...msg, type: "sent" }))];

    // Sort messages by timestamp
    allMessages.sort((a, b) => new Date(a.timestamp) - new Date(b.timestamp));

    // Loop through all messages and display them in order
    allMessages.forEach(msg => {
        const messageDiv = document.createElement("div");
        messageDiv.classList.add("message");

        // Add classes for styling based on whether the message was sent or received
        if (msg.type === "received") {
            messageDiv.classList.add("received");
        } else {
            messageDiv.classList.add("sent");
        }

        const messageContent = document.createElement("span");
        const timestamp = document.createElement("span");

        if (msg.type === "received") {
            messageContent.textContent = `${msg.sender}: ${msg.content}`;
        } else {
            messageContent.textContent = `You: ${msg.content}`;
        }

        timestamp.textContent = ` (Sent at: ${msg.timestamp})`;
        timestamp.classList.add("timestamp"); // Apply a class for styling

        // Append both parts to the message div
        messageDiv.appendChild(messageContent);
        messageDiv.appendChild(timestamp);
        messagesList.appendChild(messageDiv);
    });
}
