const sendButton = document.getElementById("send-button");
const userInput = document.getElementById("user-input");
const messages = document.getElementById("messages");

let chatHistory = [];

sendButton.addEventListener("click", async () => {
    const message = userInput.value.trim();
    if (!message) return;

    const userMessage = document.createElement("div");
    userMessage.textContent = message;
    userMessage.className = "user-message";
    messages.appendChild(userMessage);
    messages.scrollTop = messages.scrollHeight;

    chatHistory.push({ question: message, answer: "" });

    userInput.value = "";

    try {
        const response = await fetch("/chat", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ message, history: chatHistory }),
        });

        if (!response.ok) {
            throw new Error("Failed to connect to server.");
        }

        const reader = response.body.getReader();
        const decoder = new TextDecoder("utf-8");
        let botMessage = document.createElement("div");
        botMessage.className = "bot-message";
        messages.appendChild(botMessage);

        let botReply = "";

        while (true) {
            const { value, done } = await reader.read();
            if (done) break;
            const chunk = decoder.decode(value);
            botReply += chunk;
            botMessage.textContent += chunk;
            messages.scrollTop = messages.scrollHeight;
        }

        chatHistory[chatHistory.length - 1].answer = botReply;
    } catch (error) {
        console.error(error);
        const errorMessage = document.createElement("div");
        errorMessage.textContent = "Error communicating with the server.";
        errorMessage.className = "bot-message";
        messages.appendChild(errorMessage);
        messages.scrollTop = messages.scrollHeight;
    }
});

userInput.addEventListener("keydown", (event) => {
    if (event.key === "Enter" && !event.shiftKey) {
        event.preventDefault();
        sendButton.click();
    }
});
