let sessionId = null;
const apiBase = "/api";
let hasUserInfo = false;
let userName = null;
let userEmail = null;

// Initialize
document.addEventListener("DOMContentLoaded", () => {
    loadPresets();
    loadConfig();

    // Initialize chat section when page loads
    initChatSection();

    // Initialize speech recognition
    initSpeechRecognition();
});

function initChatSection() {
    // Clear any existing chat content
    const chatWindow = document.getElementById("chat-window");
    chatWindow.innerHTML = "";

    // Reset user info state
    hasUserInfo = false;
    userName = null;
    userEmail = null;

    // Show name/email prompt
    showUserInfoPrompt();
}

function showUserInfoPrompt() {
    const chatWindow = document.getElementById("chat-window");
    chatWindow.style.justifyContent = "center";
    chatWindow.style.alignItems = "center";

    // Clear existing prompt if any
    const existingPrompt = document.getElementById("user-info-prompt");
    if (existingPrompt) {
        existingPrompt.remove();
    }

    const promptDiv = document.createElement("div");
    promptDiv.id = "user-info-prompt";
    promptDiv.className = "user-info-prompt";
    promptDiv.innerHTML = `
        <h3>Welcome! 👋</h3>
        <p>Please provide your name and email to get started:</p>
        <div class="user-info-form">
            <input type="text" id="user-name-input" placeholder="Your name">
            <input type="email" id="user-email-input" placeholder="Your email">
            <button onclick="saveUserInfo()">Start Chatting</button>
        </div>
        <p style="font-size: 0.8rem; color: var(--text-secondary); margin-top: 10px;">
            This helps us personalize your experience and follow up if needed.
        </p>
    `;
    chatWindow.appendChild(promptDiv);
}

function saveUserInfo() {
    const nameInput = document.getElementById("user-name-input");
    const emailInput = document.getElementById("user-email-input");

    const name = nameInput.value.trim();
    const email = emailInput.value.trim();

    if (!name || !email) {
        alert("Please enter both your name and email");
        return;
    }

    if (!validateEmail(email)) {
        alert("Please enter a valid email address");
        return;
    }

    userName = name;
    userEmail = email;
    hasUserInfo = true;

    // Remove the prompt
    const promptDiv = document.getElementById("user-info-prompt");
    if (promptDiv) {
        promptDiv.remove();
    }

    // Add welcome message from bot
    addWelcomeMessage();
}

function validateEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}

function addWelcomeMessage() {
    const chatWindow = document.getElementById("chat-window");
    chatWindow.style.justifyContent = "flex-start";
    chatWindow.style.alignItems = "stretch";

    const welcomeText = `Hello ${userName}! How can I assist you today?`;
    addMessage(welcomeText, "bot");
}

// --- Navigation ---
function showSection(sectionId) {
    document.querySelectorAll("section").forEach((el) => {
        el.classList.remove("active-section", "flex");
        el.classList.add("hidden-section");
    });

    const active = document.getElementById(`${sectionId}-section`);
    active.classList.remove("hidden-section");
    active.classList.add("active-section");

    document
        .querySelectorAll(".menu button")
        .forEach((btn) => btn.classList.remove("active"));
    const btn = document.querySelector(
        `.menu button[onclick="showSection('${sectionId}')"]`,
    );
    if (btn) btn.classList.add("active");

    if (sectionId === "analytics") loadAnalytics();
    if (sectionId === "config") loadConfig();
    if (sectionId === "chat") {
        loadConfig().then(() => {
            document.getElementById("agent-name-display").innerText =
                document.getElementById("conf-agent").value || "Assistant";

            // Check if we need to initialize chat
            if (!hasUserInfo) {
                initChatSection();
            }
        });
    }
}

// --- Presets ---
async function loadPresets() {
    try {
        const res = await fetch(`${apiBase}/presets`);
        const presets = await res.json();

        const container = document.getElementById("preset-container");
        container.innerHTML = "";

        presets.forEach((p) => {
            const div = document.createElement("div");
            div.className = "preset-card";
            div.innerHTML = `<h4>${p.industry}</h4><span>${p.company_name}</span>`;
            div.onclick = () => applyPreset(p.id, div);
            container.appendChild(div);
        });
    } catch (e) {
        console.error("Failed to load presets", e);
    }
}

async function applyPreset(id, cardEl) {
    try {
        const res = await fetch(`${apiBase}/presets/apply`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ preset_id: id }),
        });
        const data = await res.json();

        alert(`Switched to: ${data.message.split(": ")[1]}`);

        // Visual feedback
        document
            .querySelectorAll(".preset-card")
            .forEach((c) => c.classList.remove("active"));
        if (cardEl) cardEl.classList.add("active");

        // Reload config to update sidebar title
        await loadConfig();
    } catch (e) {
        alert("Failed to apply preset");
        console.error(e);
    }
}

// --- Chat ---
async function sendMessage() {
    // Check if user has provided info
    if (!hasUserInfo) {
        alert("Please enter your name and email first");
        return;
    }

    const inputEl = document.getElementById("user-input");
    const message = inputEl.value.trim();
    if (!message) return;

    addMessage(message, "user");
    inputEl.value = "";

    try {
        const response = await fetch(`${apiBase}/chat`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                message: message,
                session_id: sessionId,
                user_name: userName,
                user_email: userEmail,
            }),
        });
        const data = await response.json();
        sessionId = data.session_id;

        // Check for automatic actions (e.g. download)
        if (data.tool_executed) {
            try {
                const actionData = JSON.parse(data.tool_executed);
                if (actionData.action === "download" && actionData.url) {
                    const link = document.createElement("a");
                    link.href = actionData.url;
                    link.download = actionData.url.split("/").pop();
                    document.body.appendChild(link);
                    link.click();
                    document.body.removeChild(link);
                }
            } catch (e) {
                /* Not a JSON action, ignore */
            }
        }

        let reply = data.response;
        reply = parseMarkdown(reply);
        addMessage(reply, "bot");
    } catch (error) {
        addMessage("Server connection error.", "bot");
    }
}

function handleEnter(e) {
    if (e.key === "Enter") sendMessage();
}

function addMessage(text, sender) {
    const chatWindow = document.getElementById("chat-window");
    const msgDiv = document.createElement("div");
    msgDiv.classList.add("message", sender);

    const bubble = document.createElement("div");
    bubble.classList.add("bubble");
    bubble.innerHTML = text;

    msgDiv.appendChild(bubble);
    chatWindow.appendChild(msgDiv);
    chatWindow.scrollTop = chatWindow.scrollHeight;
}

function parseMarkdown(text) {
    const linkRegex = /\[([^\]]+)\]\(([^)]+)\)/g;
    return text
        .replace(
            linkRegex,
            '<a href="$2" target="_blank" style="color: #60a5fa; text-decoration: underline;">$1</a>',
        )
        .replace(/\n/g, "<br>");
}

// --- Analytics ---
async function loadAnalytics() {
    try {
        const res = await fetch(`${apiBase}/analytics`);
        const data = await res.json();

        document.getElementById("total-sessions").innerText =
            data.total_sessions;
        document.getElementById("avg-duration").innerText =
            data.average_duration_minutes.toFixed(1) + " min";

        const tbody = document.getElementById("users-table-body");
        tbody.innerHTML = "";
        data.users.slice(0, 10).forEach((u) => {
            // Limit to 10 for UI
            const tr = `<tr>
                <td>${u.name || "-"}</td>
                <td>${u.email || "-"}</td>
                <td>${u.mobile || "-"}</td>
                <td>${u.last_topic || "-"}</td>
            </tr>`;
            tbody.innerHTML += tr;
        });
    } catch (e) {
        console.error(e);
    }
}

// --- Configuration ---
async function loadConfig() {
    try {
        const res = await fetch(`${apiBase}/config`);
        const conf = await res.json();

        // Update Sidebar Brand
        const brand = conf.company_name || "Agent AI";
        document.getElementById("brand-name").innerText = brand;
        document.getElementById("agent-name-display").innerText =
            conf.agent_name || "Assistant";

        // Form fields
        document.getElementById("conf-company").value = conf.company_name || "";
        document.getElementById("conf-agent").value = conf.agent_name || "";
        document.getElementById("conf-ceo").value = conf.ceo_email || "";
        document.getElementById("conf-prompt").value = conf.system_prompt || "";

        const standardKeys = [
            "company_name",
            "agent_name",
            "ceo_email",
            "system_prompt",
        ];
        const extras = {};
        for (let key in conf) {
            if (!standardKeys.includes(key)) extras[key] = conf[key];
        }
        document.getElementById("conf-extra").value = JSON.stringify(
            extras,
            null,
            2,
        );
    } catch (e) {
        console.error(e);
    }
}

async function saveConfig() {
    const company = document.getElementById("conf-company").value;
    const agent = document.getElementById("conf-agent").value;
    const ceo = document.getElementById("conf-ceo").value;
    const prompt = document.getElementById("conf-prompt").value;
    let extras = {};
    try {
        extras = JSON.parse(document.getElementById("conf-extra").value);
    } catch (e) {
        alert("Invalid JSON data");
        return;
    }

    const payload = {
        company_name: company,
        agent_name: agent,
        ceo_email: ceo,
        system_prompt: prompt,
        extra_config: extras,
    };

    await fetch(`${apiBase}/config`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
    });

    alert("Configuration Saved!");
    loadConfig();
}

async function uploadBrochure() {
    const fileInput = document.getElementById("brochure-upload");
    const statusP = document.getElementById("upload-status");

    if (!fileInput.files.length) {
        alert("Please select a file first.");
        return;
    }

    const file = fileInput.files[0];
    const formData = new FormData();
    formData.append("file", file);

    statusP.innerText = "Uploading...";

    try {
        const res = await fetch(`${apiBase}/config/upload_brochure`, {
            method: "POST",
            body: formData,
        });

        if (!res.ok) {
            const err = await res.json();
            throw new Error(err.detail || "Upload failed");
        }

        const data = await res.json();
        statusP.innerText = `Success: ${data.message} (${data.extracted_chars} chars extract)`;
        statusP.style.color = "var(--accent)";

        // Clear input
        fileInput.value = "";
    } catch (e) {
        console.error(e);
        statusP.innerText = `Error: ${e.message}`;
        statusP.style.color = "red";
    }
}

// --- Voice Query ---
let recognition;
let isListening = false;

function initSpeechRecognition() {
    const micBtn = document.getElementById('mic-btn');
    // Check for browser support
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        recognition = new SpeechRecognition();
        recognition.continuous = false;
        recognition.interimResults = false;
        recognition.lang = 'en-US';

        recognition.onstart = function() {
            isListening = true;
            if (micBtn) {
                micBtn.dataset.originalColor = micBtn.style.backgroundColor;
                micBtn.style.backgroundColor = '#ef4444'; // Red to indicate recording
                micBtn.classList.add('recording');
            }
        };

        recognition.onend = function() {
            isListening = false;
            if (micBtn) {
                micBtn.style.backgroundColor = micBtn.dataset.originalColor || ''; // Reset color
                micBtn.classList.remove('recording');
            }
        };

        recognition.onresult = function(event) {
            const transcript = event.results[0][0].transcript;
            const inputEl = document.getElementById("user-input");
            if (inputEl) {
                inputEl.value = transcript;
                sendMessage(); // Automatically send
            }
        };

        recognition.onerror = function(event) {
            console.error('Speech recognition error', event.error);
            isListening = false;
            if (micBtn) {
                micBtn.style.backgroundColor = micBtn.dataset.originalColor || '';
                micBtn.classList.remove('recording');
            }
        };
    } else {
        console.warn('Speech recognition not supported in this browser.');
        if (micBtn) micBtn.style.display = 'none';
    }
}

function toggleVoiceInput() {
    if (!recognition) {
        initSpeechRecognition();
    }
    
    if (!recognition) return; 

    if (isListening) {
        recognition.stop();
    } else {
        try {
            recognition.start();
        } catch (e) {
            console.error("Failed to start recognition:", e);
        }
    }
}
