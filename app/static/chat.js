const socket = new WebSocket("ws://dusk:6789");

socket.onopen = () => {
    console.log('WebSocket connected');
};
socket.onerror = (e) => {
    console.error('WebSocket error:', e);
};

window.onload = function () {
    const chatbox = document.getElementById("chatbox");
    chatbox.scrollTop = chatbox.scrollHeight;
};

document.addEventListener("DOMContentLoaded", () => {
    const messageInput = document.getElementById("message");

    messageInput.addEventListener("keydown", (event) => {
        if (event.key === "Enter" && !event.shiftKey) {
            event.preventDefault();  // prevent newline
            sendMessage();
        }
    });
});


socket.onmessage = (event) => {
    console.log('Message received:', event.data);
    const data = JSON.parse(event.data);
    const user = data.username || 'Anonymous';
    const msg = data.content.replace(/\n/g, "<br>");

    const chatbox = document.getElementById('chatbox');
    const msgDiv = document.createElement('div');

    msgDiv.innerHTML = `<b>${user}</b>: ${msg}`;
    chatbox.appendChild(msgDiv);
    chatbox.scrollTop = chatbox.scrollHeight;

};

function sendMessage() {
    const message = document.getElementById('message').value;
    console.log('Sending message:', message);

    const username = document.getElementById('username').value || 'Anonymous';
    if (message.trim() === '') return;

    socket.send(JSON.stringify({ username, content: message }));
    document.getElementById('message').value = '';
}
