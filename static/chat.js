document.addEventListener("DOMContentLoaded", function () {
    const chatBox = document.getElementById("chat-box");
    const userInput = document.getElementById("user-input");
    const sendButton = document.getElementById("send-btn");
    const startForm = document.getElementById("start-form");
    const recordButton = document.getElementById("record-btn");
    
    let mediaRecorder;
    let audioChunks = [];
    let isRecording = false;

    function updateChat(messages) {
        chatBox.innerHTML = ""; // Clear chat
        messages.forEach(msg => {
            const messageDiv = document.createElement("div");
            if (msg.role === 'user') {
                messageDiv.innerHTML = `<strong>User:</strong> ${msg.content}`;
            } else if (msg.role === 'assistant' || msg.role === 'system') {
                messageDiv.innerHTML = `<strong>AI:</strong> ${msg.content}`;
            }
            chatBox.appendChild(messageDiv);
            chatBox.appendChild(document.createElement("br"));
        });
        chatBox.scrollTop = chatBox.scrollHeight; // Auto-scroll
    }

    // Start conversation
    startForm.addEventListener("submit", function (event) {
        event.preventDefault();

        const formData = new FormData(this);
        fetch("/start", {
            method: "POST",
            body: JSON.stringify({
                employee_name: formData.get("employee_name"),
                gender: formData.get("gender"),
                job_description: formData.get("job_description"),
                company_name: formData.get("company_name"),
                location: formData.get("location")
            }),
            headers: { "Content-Type": "application/json" }
        })
        .then(response => response.json())
        .then(data => updateChat(data.conversation))
        .catch(error => console.error("Error starting chat:", error));
    });

    // Send text input to the chat
    sendButton.addEventListener("click", function () {
        const message = userInput.value.trim();
        if (!message) return;

        fetch("/chat", {
            method: "POST",
            body: JSON.stringify({ user_input: message }),
            headers: { "Content-Type": "application/json" }
        })
        .then(response => response.json())
        .then(data => updateChat(data.conversation))
        .catch(error => console.error("Error sending message:", error));

        userInput.value = "";
    });

    // Record audio input
    recordButton.addEventListener("click", async function () {
        if (!isRecording) {
            try {
                const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
                mediaRecorder = new MediaRecorder(stream);
                audioChunks = [];

                mediaRecorder.ondataavailable = event => audioChunks.push(event.data);

                mediaRecorder.onstop = () => {
                    const audioBlob = new Blob(audioChunks, { type: "audio/webm" });
                    uploadAudio(audioBlob);
                };

                mediaRecorder.start();
                isRecording = true;
                recordButton.textContent = "🛑 Stop Recording";
            } catch (error) {
                console.error("Microphone access error:", error);
            }
        } else {
            mediaRecorder.stop();
            isRecording = false;
            recordButton.textContent = "🎤 Start Recording";
        }
    });

    // Upload audio for transcription and send to chat
    function uploadAudio(audioBlob) {
        const formData = new FormData();
        formData.append('audio', audioBlob, 'audio.webm');

        fetch('/speech-to-text', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.conversation) {
                updateChat(data.conversation);
            } else {
                console.error("Transcription error:", data.error);
            }
        })
        .catch(error => console.error('Error uploading audio:', error));
    }

    function updateChat(messages) {
        chatBox.innerHTML = ""; // Clear chat
        messages.forEach(msg => {
            const messageDiv = document.createElement("div");
            if (msg.role === 'user') {
                messageDiv.innerHTML = `<strong>User:</strong> ${msg.content}`;
            } else if (msg.role === 'assistant' || msg.role === 'system') {
                messageDiv.innerHTML = `<strong>AI:</strong> ${msg.content}`;
            }
            chatBox.appendChild(messageDiv);
            chatBox.appendChild(document.createElement("br"));
        });
        chatBox.scrollTop = chatBox.scrollHeight; // Auto-scroll
    }
});
