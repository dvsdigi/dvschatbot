(function () {
    const API_BASE_URL = `${window.location.protocol}//${window.location.host}`;
    let userToken = "";

    // Load marked.js with a reliable check
    if (!window.marked) {
        const script = document.createElement('script');
        script.src = "https://cdn.jsdelivr.net/npm/marked/marked.min.js";
        script.async = true;
        document.head.appendChild(script);
    }

    // Load Styles
    const link = document.createElement('link');
    link.rel = 'stylesheet';
    link.href = '/static/bot-styles.css';
    document.head.appendChild(link);

    // Create UI Structure
    const container = document.createElement('div');
    container.id = 'parent-bot-container';
    container.innerHTML = `
        <div id="parent-bot-window">
            <div id="parent-bot-header">
                <div class="bot-info">
                    <div class="bot-title">Parent Bot</div>
                    <div class="bot-status"><span class="status-dot"></span> Online</div>
                </div>
                <span id="close-bot" style="cursor:pointer; font-size: 24px;">&times;</span>
            </div>
            <div id="parent-bot-messages">
                <div class="bot-msg">Welcome! 👋 Please provide your authentication token to begin.</div>
            </div>
            <div id="parent-bot-input-area">
                <input type="text" id="parent-bot-input" placeholder="Type a message..." autocomplete="off">
                <button id="parent-bot-send">Send</button>
            </div>
        </div>
        <div id="parent-bot-launcher">
            <svg viewBox="0 0 24 24"><path d="M20 2H4c-1.1 0-2 .9-2 2v18l4-4h14c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2z"/></svg>
        </div>
    `;
    document.body.appendChild(container);

    const windowEl = document.getElementById('parent-bot-window');
    const launcherEl = document.getElementById('parent-bot-launcher');
    const closeEl = document.getElementById('close-bot');
    const inputEl = document.getElementById('parent-bot-input');
    const sendBtn = document.getElementById('parent-bot-send');
    const messagesEl = document.getElementById('parent-bot-messages');

    launcherEl.onclick = () => windowEl.classList.toggle('active');
    closeEl.onclick = () => windowEl.classList.remove('active');

    function addMessage(text, type) {
        const msg = document.createElement('div');
        msg.className = type + '-msg';
        
        // Wait for marked to be available if needed
        if (type === 'bot' && window.marked) {
            try {
                msg.innerHTML = marked.parse(text);
            } catch (e) {
                console.error("Markdown parse error:", e);
                msg.innerText = text;
            }
        } else {
            msg.innerText = text;
        }
        
        messagesEl.appendChild(msg);
        messagesEl.scrollTop = messagesEl.scrollHeight;
        return msg;
    }

    function showTyping() {
        const typing = document.createElement('div');
        typing.id = 'bot-typing';
        typing.className = 'typing';
        typing.innerHTML = '<span></span><span></span><span></span>';
        messagesEl.appendChild(typing);
        messagesEl.scrollTop = messagesEl.scrollHeight;
    }

    function hideTyping() {
        const typing = document.getElementById('bot-typing');
        if (typing) typing.remove();
    }

    async function handleSend() {
        const text = inputEl.value.trim();
        if (!text) return;

        addMessage(text, 'user');
        inputEl.value = '';

        if (!userToken) {
            userToken = text;
            showTyping();
            try {
                const res = await fetch(`${API_BASE_URL}/api/student/details`, {
                    headers: { 'Authorization': `Bearer ${userToken}` }
                });
                hideTyping();
                if (!res.ok) throw new Error("Auth failed");
                const data = await res.json();
                if (data.error) throw new Error(data.error);
                
                addMessage(`Authenticated as parent of **${data.name}**. How can I assist you today?`, 'bot');
            } catch (e) {
                hideTyping();
                addMessage("Authentication Error: Please check your token.", 'bot');
                userToken = "";
            }
            return;
        }

        showTyping();
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
            hideTyping();
            addMessage(data.reply, 'bot');
        } catch (e) {
            hideTyping();
            addMessage("I'm sorry, I'm having trouble connecting right now.", 'bot');
        }
    }

    sendBtn.onclick = handleSend;
    inputEl.onkeypress = (e) => { if (e.key === 'Enter') handleSend(); };
})();


