// Элементы интерфейса
const sendButton = document.getElementById("send-button");
const userInput = document.getElementById("user-input");
const messages = document.getElementById("messages");

// История чата
let chatHistory = [];
let isWaitingForResponse = false; // Флаг состояния ожидания ответа

// Функция рендеринга Markdown
const renderMarkdown = (text) => {
    return marked.parse(text, { sanitize: true }); // sanitize для предотвращения XSS
};

// Функция обновления состояния кнопки "Send"
const updateSendButtonState = () => {
    sendButton.disabled = userInput.value.trim() === "" || isWaitingForResponse;
};

// Изначально блокируем кнопку
updateSendButtonState();

// Обработчик изменения текста в поле ввода
userInput.addEventListener("input", updateSendButtonState);

// Обработчик нажатия кнопки "Send"
sendButton.addEventListener("click", async () => {
    const message = userInput.value.trim();
    if (!message || isWaitingForResponse) return;

    // Добавление пользовательского сообщения
    const userMessage = document.createElement("div");
    userMessage.textContent = message;
    userMessage.className = "user-message";
    messages.appendChild(userMessage);
    messages.scrollTop = messages.scrollHeight;

    chatHistory.push({ question: message, answer: "" });

    userInput.value = "";
    updateSendButtonState(); // Обновляем состояние кнопки

    try {
        // Устанавливаем флаг ожидания ответа
        isWaitingForResponse = true;
        updateSendButtonState();

        // Отправка сообщения на сервер
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

        // Чтение ответа с сервера
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

            // Рендеринг Markdown
            botMessage.innerHTML = renderMarkdown(botReply);
            messages.scrollTop = messages.scrollHeight;
        }

        // Сохранение ответа в истории
        chatHistory[chatHistory.length - 1].answer = botReply;

    } catch (error) {
        console.error(error);

        // Отображение ошибки
        const errorMessage = document.createElement("div");
        errorMessage.textContent = "Error communicating with the server.";
        errorMessage.className = "bot-message";
        messages.appendChild(errorMessage);
        messages.scrollTop = messages.scrollHeight;
    } finally {
        // Сбрасываем флаг ожидания ответа
        isWaitingForResponse = false;
        updateSendButtonState();
    }
});

// Обработка нажатия Enter для отправки сообщения
userInput.addEventListener("keydown", (event) => {
    if (event.key === "Enter" && !event.shiftKey) {
        event.preventDefault();
        sendButton.click();
    }
});
