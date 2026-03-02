let demoShown = false;   // Controls first bot reply only

async function sendMessage() {

    const input = document.getElementById("message-input");
    const message = input.value.trim();

    if (!message) return;

    const chatBody = document.getElementById("chat-body");

    // ---------------------------
    // ADD USER MESSAGE
    // ---------------------------
    const userDiv = document.createElement("div");
    userDiv.className = "user-message";
    userDiv.innerText = message;
    chatBody.appendChild(userDiv);

    input.value = "";
    chatBody.scrollTop = chatBody.scrollHeight;

    // ---------------------------
    // ADD LOADING MESSAGE
    // ---------------------------
    const loadingDiv = document.createElement("div");
    loadingDiv.className = "bot-message";
    loadingDiv.innerText = "Typing...";
    chatBody.appendChild(loadingDiv);
    chatBody.scrollTop = chatBody.scrollHeight;

    try {

        const response = await fetch(`/chat/${encodeURIComponent(message)}`);

        if (!response.ok) {
            throw new Error("Server error");
        }

        const data = await response.json();

        // Remove loading
        chatBody.removeChild(loadingDiv);

        // ---------------------------
        // ADD BOT MESSAGE
        // ---------------------------
        const botDiv = document.createElement("div");
        botDiv.className = "bot-message";
        botDiv.innerText = data.reply;
        chatBody.appendChild(botDiv);

        // ---------------------------
        // ADD LIVE DEMO (ONLY FIRST BOT RESPONSE)
        // ---------------------------
        if (!demoShown) {

            const demoDiv = document.createElement("div");
            demoDiv.className = "bot-message";

            demoDiv.innerHTML = `
                <hr style="margin:10px 0;">
                🎯 <b>Want to see a LIVE DEMO session?</b><br><br>
                <a href="https://calendly.com/abduljaheer142/abduljaheer142"
                   target="_blank"
                   style="display:inline-block;
                          padding:10px 15px;
                          background:#25D366;
                          color:white;
                          border-radius:20px;
                          text-decoration:none;
                          font-weight:bold;">
                    Register for Live Demo
                </a>
            `;

            chatBody.appendChild(demoDiv);
            demoShown = true;
        }

        chatBody.scrollTop = chatBody.scrollHeight;

    } catch (error) {

        chatBody.removeChild(loadingDiv);

        const errorDiv = document.createElement("div");
        errorDiv.className = "bot-message";
        errorDiv.innerText = "⚠️ Unable to connect to server.";
        chatBody.appendChild(errorDiv);

        chatBody.scrollTop = chatBody.scrollHeight;
    }
}


// ---------------------------------
// ENTER KEY SUPPORT
// ---------------------------------
document.getElementById("message-input").addEventListener("keypress", function (e) {
    if (e.key === "Enter") {
        sendMessage();
    }
});