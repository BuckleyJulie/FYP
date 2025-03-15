document.addEventListener("DOMContentLoaded", function () {
    const chatBox = document.getElementById("chat-box");
    const userInput = document.getElementById("user-input");
    const sendButton = document.getElementById("send-btn");
    const startForm = document.getElementById("start-form");
    const startButton = document.getElementById("start-btn");
    const recordButton = document.getElementById("record-btn");

    let mediaRecorder;
    let audioChunks = [];
    let isRecording = false;
    let recognition;
    let isListening = false;

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

    // Send text responses
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

    // Handle speech recording
    recordButton.addEventListener("click", function () {
        if (!isRecording) {
            startRecording();
        } else {
            stopRecording();
        }
    });

    async function startRecording() {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            mediaRecorder = new MediaRecorder(stream);
            audioChunks = [];

            mediaRecorder.ondataavailable = event => audioChunks.push(event.data);

            mediaRecorder.onstop = async () => {
                const audioBlob = new Blob(audioChunks, { type: "audio/wav" });
                const formData = new FormData();
                formData.append("audio", audioBlob);

                fetch("/speech-to-text", {
                    method: "POST",
                    body: formData
                })
                .then(response => response.json())
                .then(data => {
                    if (data.text) {
                        sendTextToChat(data.text);
                    } else {
                        console.error("Error in transcription:", data.error);
                    }
                })
                .catch(error => console.error("Error:", error));
            };

            mediaRecorder.start();
            isRecording = true;
            recordButton.textContent = "🛑 Stop Recording";
        } catch (error) {
            console.error("Error accessing microphone:", error);
        }
    }

    function stopRecording() {
        if (mediaRecorder) {
            mediaRecorder.stop();
            isRecording = false;
            recordButton.textContent = "🎤 Start Recording";
        }
    }

    function sendTextToChat(transcribedText) {
        fetch("/chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ "user_input": transcribedText })
        })
        .then(response => response.json())
        .then(data => updateChat(data.conversation))
        .catch(error => console.error("Error:", error));
    }

    // Continuous speech recognition setup
    function startSpeechRecognition() {
        if (!('webkitSpeechRecognition' in window)) {
            alert("Your browser does not support speech recognition.");
            return;
        }

        recognition = new webkitSpeechRecognition();
        recognition.continuous = true;  // Listen continuously
        recognition.interimResults = true;
        recognition.lang = "en-IE";  // Set the language

        recognition.onstart = function() {
            isListening = true;
            console.log("Speech recognition started.");
        };

        recognition.onresult = function(event) {
            let transcript = "";
            for (let i = event.resultIndex; i < event.results.length; i++) {
                transcript += event.results[i][0].transcript;
            }
            console.log("Recognized speech:", transcript);

            // Send audio input to backend for transcription
            fetch('/speech-to-text', {
                method: 'POST',
                body: createFormDataWithAudio(transcript),
            })
            .then(response => response.json())
            .then(data => {
                console.log("Server response:", data);
                if (data.listening) {
                    // Keep listening if the server is ready for more input
                    recognition.start();
                } else {
                    recognition.stop();
                }
            })
            .catch(error => {
                console.error("Error during speech-to-text:", error);
                recognition.stop();
            });

            transcript = "";  // Reset transcript
        };

        recognition.onerror = function(event) {
            console.log("Error with speech recognition:", event.error);
            recognition.stop();
        };

        recognition.onend = function() {
            console.log("Speech recognition ended.");
            isListening = false;
        };

        // Start listening for speech
        recognition.start();
    }

    function createFormDataWithAudio(transcript) {
        const formData = new FormData();
        formData.append('audio', new Blob([transcript], { type: 'text/plain' }));  // Normally you'd append an actual audio file here
        return formData;
    }

    // Begin continuous speech recognition when the page loads
    startSpeechRecognition();   
});
