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

    switch (data.type) {
        case 'message':
            const user = data.username || 'Anonymous';
            const msg = data.content.replace(/\n/g, "<br>");

            const chatbox = document.getElementById('chatbox');
            const msgDiv = document.createElement('div');

            msgDiv.innerHTML = `<div class="msg">
                                 <b class="msg_name">${user}:</b>
                                 <div class="msg_content"> ${msg} </div>
                                </div>`;

            chatbox.appendChild(msgDiv);
            chatbox.scrollTop = chatbox.scrollHeight;
            break;
        case "status":
            const internetStatus = document.getElementById('internet-status');
            const antenna = document.getElementById('antenna');
            const topengine = document.getElementById('topengine');
            const bottomengine = document.getElementById('bottomengine');

            if (data.online) {
                internetStatus.textContent = "Internet is online";
                internetStatus.style.color = "green";
                for (const element of [antenna, topengine, bottomengine]) {
                    if (element.classList.contains('antenna_red')) {
                        element.classList.remove('antenna_red');
                    }
                    element.classList.add('antenna_green');
                }
                
                
            } else {
                internetStatus.textContent = "Internet is offline";
                internetStatus.style.color = "red";
                for (const element of [antenna, topengine, bottomengine]) {
                    if (element.classList.contains('antenna_green')) {
                        element.classList.remove('antenna_green');
                    }
                    element.classList.add('antenna_red');
                }
            }
            break;
        default:
            console.warn('Unknown message type:', data.type);
            console.log('Full message:', data);
            break;
    }


};

function sendMessage() {
    const message = document.getElementById('message').value;
    console.log('Sending message:', message);

    const username = document.getElementById('username').value || 'Anonymous';
    if (message.trim() === '') return;

    socket.send(JSON.stringify({ username, content: message }));
    document.getElementById('message').value = '';
}
