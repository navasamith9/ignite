document.addEventListener("DOMContentLoaded", () => {
    const userInput = document.getElementById("user-input");
    const sendBtn = document.getElementById("send-btn");
    const stopBtn = document.getElementById("stop-btn") || null;
    const chatHistory = document.getElementById("chat-history");

    let currentController = null;

    userInput.addEventListener("input", function() {
        this.style.height = "auto";
        this.style.height = (this.scrollHeight) + "px";
        if (this.value.trim() !== "") {
            sendBtn.style.background = "#667eea";
        } else {
            sendBtn.style.background = "#e4e6eb";
        }
    });

    userInput.addEventListener("keydown", (e) => {
        if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });

    sendBtn.addEventListener("click", sendMessage);
    if (stopBtn) {
    stopBtn.addEventListener("click", () => {
        if (currentController) {
            currentController.abort();
            resetButtons();
            removeTypingIndicator();
            appendMessage("Generation stopped by user.", "bot");
        }
    });
    }

    async function sendMessage() {
        const text = userInput.value.trim();
        if (!text) return;

        userInput.value = "";
        userInput.style.height = "auto";
        appendMessage(text, "user");
        
        sendBtn.classList.add("hidden");
        stopBtn.classList.remove("hidden");

        showTypingIndicator();

        currentController = new AbortController();
        const signal = currentController.signal;

        try {
            const response = await fetch("/helpdesk/api/chat/", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ message: text }),
                signal: signal
            });

            const data = await response.json();
            removeTypingIndicator();

            if (data.error) {
                appendMessage("Error: " + data.error, "bot");
            } else {
                let formattedResponse = data.response.replace(/\n/g, '<br>');
                formattedResponse = formattedResponse.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
                appendMessage(formattedResponse, "bot");
            }
        } catch (error) {
            if (error.name === 'AbortError') {
                console.log('Fetch aborted');
            } else {
                removeTypingIndicator();
                appendMessage("Connection error. Ensure the server and Ollama are running.", "bot");
            }
        } finally {
            resetButtons();
            currentController = null;
        }
    }

    function appendMessage(content, sender) {
        const messageDiv = document.createElement("div");
        messageDiv.classList.add("message", `${sender}-message`);
        
        const contentDiv = document.createElement("div");
        contentDiv.classList.add("message-content");
        contentDiv.innerHTML = content;
        
        messageDiv.appendChild(contentDiv);
        chatHistory.appendChild(messageDiv);
        scrollToBottom();
    }

    function showTypingIndicator() {
        const indicatorDiv = document.createElement("div");
        indicatorDiv.classList.add("message", "bot-message", "typing-msg");
        indicatorDiv.innerHTML = `
            <div class="typing-indicator">
                <span></span><span></span><span></span>
            </div>
        `;
        chatHistory.appendChild(indicatorDiv);
        scrollToBottom();
    }

    function removeTypingIndicator() {
        const indicator = document.querySelector(".typing-msg");
        if (indicator) {
            indicator.remove();
        }
    }

    function resetButtons() {
        sendBtn.classList.remove("hidden");
        stopBtn.classList.add("hidden");
        sendBtn.style.background = "#e4e6eb";
    }

    function scrollToBottom() {
        chatHistory.scrollTop = chatHistory.scrollHeight;
    }
});