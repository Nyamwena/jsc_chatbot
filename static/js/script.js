document.getElementById("send-btn").addEventListener("click", () => {
    const userInput = document.getElementById("user-input").value;
    const chatBox = document.getElementById("chat-box");
    const loadingIndicator = `<div class="bot-msg" id="thinking-msg">🤖: Thinking...</div>`;

    // Display the user's message
    const userMessage = `<div class="user-msg"> 😊: ${userInput}</div>`;
    chatBox.innerHTML += userMessage;

    // Display the 'Thinking...' message
    chatBox.innerHTML += loadingIndicator;
    chatBox.scrollTop = chatBox.scrollHeight;

    fetch("/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: userInput })
    })
    .then(response => response.json())
    .then(data => {
        // Remove the 'Thinking...' message
        const thinkingMsg = document.getElementById("thinking-msg");
        if (thinkingMsg) thinkingMsg.remove();

        // Display the bot's response
        const botResponse = data.response || "Sorry, something went wrong!";
        const botMessage = `<div class="bot-msg">🤖: ${botResponse}</div>`;
        chatBox.innerHTML += botMessage;

        // Scroll to the bottom of the chat box
        chatBox.scrollTop = chatBox.scrollHeight;
    })
    .catch(error => {
        console.error('Error:', error);

        // Remove the 'Thinking...' message
        const thinkingMsg = document.getElementById("thinking-msg");
        if (thinkingMsg) thinkingMsg.remove();

        // Display an error message
        chatBox.innerHTML += `<div class="bot-msg">Sorry, there was an issue processing your request. 🤖</div>`;

        // Scroll to the bottom of the chat box
        chatBox.scrollTop = chatBox.scrollHeight;
    });

    // Clear the input field
    document.getElementById("user-input").value = "";
});
