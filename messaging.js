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
        const response = await fetch("http://35.160.120.126:5000/messages", {  // Use the IP address
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
        } else {
            alert(`Error: ${data.message}`);
        }
    } catch (error) {
        alert("An error occurred. Please try again later.");
        console.error("Error:", error);
    }
});
