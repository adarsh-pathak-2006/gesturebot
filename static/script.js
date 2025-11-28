// static/script.js → FINAL FIXED VERSION (TYPING WORKS AGAIN!)
document.addEventListener('DOMContentLoaded', () => {
    const chatWindow = document.getElementById('chat-window');
    const messageInput = document.getElementById('message');
    const sendButton = document.getElementById('send');
    const ttsCheckbox = document.getElementById('tts');
    const gestureDiv = document.getElementById('gesture');

    let currentGesture = 'None';
    let lastSentGesture = null;
    let stableFrames = 0;
    const REQUIRED_FRAMES = 2;
    const COOLDOWN_MS = 6000;
    let cooldownUntil = 0;

    const friendly = {
        'Thumb_Up': 'Yes! appreciate it',
        'Thumb_Down': 'No. I dissagree',
        'Victory': 'Great! peace',
        'Open_Palm': 'Hello!',
        'Closed_Fist': 'Stop it now.',
        'ILoveYou': 'Love it!',
        'Pointing_Up': 'More info?'
    };

    // Gesture polling
    setInterval(() => {
        fetch('/gesture')
            .then(r => r.json())
            .then(data => {
                currentGesture = data.gesture;
                const now = Date.now();

                if (now < cooldownUntil) {
                    const secs = Math.ceil((cooldownUntil - now) / 1000);
                    gestureDiv.textContent = `Cooldown (${secs}s)`;
                    return;
                }

                if (currentGesture === 'None') {
                    stableFrames = 0;
                    lastSentGesture = null;
                    gestureDiv.textContent = 'Ready';
                    return;
                }

                stableFrames = currentGesture === (gestureDiv.dataset.last || '') ? stableFrames + 1 : 1;
                gestureDiv.dataset.last = currentGesture;
                gestureDiv.textContent = `Detecting: ${currentGesture} (${stableFrames}/${REQUIRED_FRAMES})`;

                if (stableFrames >= REQUIRED_FRAMES && currentGesture !== lastSentGesture) {
                    sendGesture(currentGesture);
                    lastSentGesture = currentGesture;
                    cooldownUntil = now + COOLDOWN_MS;
                }
            })
            .catch(() => {});
    }, 500);

    function sendGesture(g) {
        const msg = friendly[g] || g;
        appendMessage('user', msg);
        sendToChat(g, ttsCheckbox.checked);
    }

    function sendText() {
        const msg = messageInput.value.trim();
        if (!msg) return;
        appendMessage('user', msg);
        sendToChat(msg, ttsCheckbox.checked);
        messageInput.value = '';
    }

    function sendToChat(message, tts) {
        fetch('/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message, tts })
        })
        .then(r => r.json())
        .then(data => {
            appendMessage('bot', data.response);
            if (tts && data.audio_url) {
                new Audio(data.audio_url).play().catch(() => {});
            }
        })
        .catch(() => alert('Connection error'));
    }

    function appendMessage(sender, text) {
        const div = document.createElement('div');
        div.className = sender + '-msg';
        const time = new Date().toLocaleTimeString([], {hour: '2-digit', minute: '2-digit'});
        div.innerHTML = `<span>${text}</span><div class="timestamp ${sender==='user'?'text-end':'text-start'}">${time}</div>`;
        chatWindow.appendChild(div);
        chatWindow.scrollTop = chatWindow.scrollHeight;
    }

    // FIXED: Proper event listeners — typing works again!
    sendButton.addEventListener('click', sendText);
    messageInput.addEventListener('keydown', e => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendText();
        }
    });
});