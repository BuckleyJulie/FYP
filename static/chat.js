document.addEventListener("DOMContentLoaded", function () {
    const chatBox = document.getElementById("chat-box");
    const userInput = document.getElementById("user-input");
    const sendButton = document.getElementById("send-btn");
    const startForm = document.getElementById("start-form");
    const startButton = document.getElementById("start-btn");


    function updateChat(messages) {
        chatBox.innerHTML = ""; // Clear chat
        messages.forEach(msg => {
            let p = document.createElement("p");
            p.classList.add(msg.role);
            p.innerHTML = `<strong>${msg.role === 'user' ? 'User' : 'AI'}:</strong> ${msg.content}`;
            chatBox.appendChild(p);
        });
        chatBox.scrollTop = chatBox.scrollHeight; // Auto-scroll
    }

    // Handle the chat form (if this form is solely for starting the conversation)
    startForm.addEventListener("submit", function (event) {
        event.preventDefault();

        const employeeName = document.getElementById("employee-name").value;
        const scriptChoice = document.getElementById("script-choice").value;

        fetch("/start", {
            method: "POST",
            body: JSON.stringify({ employee_name: employeeName, script_choice: scriptChoice }),
            headers: { "Content-Type": "application/json" }
        })
        .then(response => response.json())
        .then(data => updateChat(data.conversation));
    });

    // Send message when send button is clicked
    sendButton.addEventListener("click", function () {
        const message = userInput.value.trim();
        if (!message) return;

        fetch("/chat", {
            method: "POST",
            body: JSON.stringify({ user_input: message }),
            headers: { "Content-Type": "application/json" }
        })
        .then(response => response.json())
        .then(data => updateChat(data.conversation));

        userInput.value = ""; // Clear input field
    });

    // Remove or comment out this keypress listener to avoid duplicate submissions:
    userInput.addEventListener("keypress", function (event) {
        if (event.key === "Enter") {
             event.preventDefault();
             sendButton.click();
        }
 });
});
