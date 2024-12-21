document.getElementById("loginForm").addEventListener("submit", async function (event) {
    event.preventDefault(); // Prevent the form from refreshing the page

    const username = document.getElementById("username").value;
    const password = document.getElementById("password").value;

    if (!username || !password) {
        alert("Username and password are required.");
        return;
    }

    try {
        const response = await fetch("http://35.160.120.126:5000/login", {  // Use the IP address
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ username, password }),
        });

        const data = await response.json();

        if (response.ok) {
            // Store the username in localStorage
            localStorage.setItem("username", username);
            window.location.href = "main.html"; // Redirect to the main page
        } else {
            alert(`Error: ${data.message}`);
        }
    } catch (error) {
        alert("An error occurred. Please try again later.");
        console.error("Error:", error);
    }
});
