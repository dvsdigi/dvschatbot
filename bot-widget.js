(function () {
    // Configuration
    const API_BASE_URL = "http://localhost:8001";
    let userToken = "";

    // Load Styles
    const link = document.createElement('link');
    link.rel = 'stylesheet';
    link.href = 'bot-styles.css';
    document.head.appendChild(link);

    // Create UI Structure
    const container = document.createElement('div');
    container.id = 'parent-bot-container';
    container.innerHTML = `
        <div id="parent-bot-window">
            <div id="parent-bot-header">
                <span>Parent Bot</span>
                <span id="close-bot" style="cursor:pointer">&times;</span>
            </div>
            <div id="parent-bot-messages">
                <div class="bot-msg">Welcome! Please provide your authentication token to start.</div>
            </div>
            <div id="parent-bot-input-area">
                <input type="text" id="parent-bot-input" placeholder="Type your message...">
                <button id="parent-bot-send">Send</button>
            </div>
        </div>
        <div id="parent-bot-launcher">
            <svg viewBox="0 0 24 24"><path d="M20 2H4c-1.1 0-2 .9-2 2v18l4-4h14c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2z"/></svg>
        </div>
    `;
    document.body.appendChild(container);

    // Elements
    const windowEl = document.getElementById('parent-bot-window');
    const launcherEl = document.getElementById('parent-bot-launcher');
    const closeEl = document.getElementById('close-bot');
    const inputEl = document.getElementById('parent-bot-input');
    const sendBtn = document.getElementById('parent-bot-send');
    const messagesEl = document.getElementById('parent-bot-messages');

    // Toggle Window
    launcherEl.onclick = () => windowEl.classList.toggle('active');
    closeEl.onclick = () => windowEl.classList.remove('active');

    // Add Message to UI
    function addMessage(text, type) {
        const msg = document.createElement('div');
        msg.className = type + '-msg';
        msg.innerText = text;
        messagesEl.appendChild(msg);
        messagesEl.scrollTop = messagesEl.scrollHeight;
    }

    // Handle Send
    async function handleSend() {
        const text = inputEl.value.trim();
        if (!text) return;

        addMessage(text, 'user');
        inputEl.value = '';

        // Case 1: Initial Authentication
        if (!userToken) {
            userToken = text;
            addMessage("Authenticating...", 'bot');
            try {
                console.log("Authenticating...");
                const res = await fetch(`${API_BASE_URL}/api/student/details`, {
                    headers: { 'Authorization': `Bearer ${userToken}` }
                });

                if (!res.ok) {
                    const errData = await res.json();
                    throw new Error(errData.detail || "Authentication failed");
                }

                const data = await res.json();
                console.log("Auth Success:", data);

                if (data.error) {
                    addMessage("Error: " + data.error, 'bot');
                    userToken = "";
                } else {
                    addMessage(`Authenticated as parent of ${data.name}. How can I help you?`, 'bot');
                }
            } catch (e) {
                console.error("Auth error:", e);
                addMessage("Auth Error: " + e.message, 'bot');
                userToken = "";
            }
            return;
        }

        // Case 2: Regular Chat
        try {
            const res = await fetch(`${API_BASE_URL}/api/chat`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${userToken}`
                },
                body: JSON.stringify({ text })
            });
            const data = await res.json();
            addMessage(data.reply, 'bot');
        } catch (e) {
            addMessage("Failed to send message.", 'bot');
        }
    }

    sendBtn.onclick = handleSend;
    inputEl.onkeypress = (e) => { if (e.key === 'Enter') handleSend(); };

})();
