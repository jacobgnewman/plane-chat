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

socket.onmessage = (event) => {
    console.log('Message received:', event.data);
    const data = JSON.parse(event.data);
    const chatbox = document.getElementById('chatbox');
    const msgDiv = document.createElement('div');
    msgDiv.innerHTML = `<b>${data.username}</b>: ${data.content}`;
    chatbox.appendChild(msgDiv);
    chatbox.scrollTop = chatbox.scrollHeight;
};

function sendMessage() {
    const message = document.getElementById('message').value;
    const username = document.getElementById('username').value || 'Anonymous';
    if (message.trim() === '') return;

    socket.send(JSON.stringify({ username, content: message }));
    document.getElementById('message').value = '';
}
