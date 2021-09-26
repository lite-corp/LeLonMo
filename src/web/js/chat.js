var chat_messages = [];
var messages = document.getElementById('chat_messages');

function setupChat() {
    var input = document.getElementById("message");
    input.addEventListener("keyup", function(event) {
        if (event.keyCode === 13) {
            sendMessage(document.getElementById("message").value)
            document.getElementById("message").value = "";
        }
    });
    setInterval(() => {
        send_data("/chat", { "action": "get_msg" }, messages_update_callback);
    }, 1000);
}

const scrollToBottom = (node) => {
    node.scrollTop = node.scrollHeight;
}

function sendMessage(message) {
    if (message !== "") {
        send_data(
            "/chat", {
                'action': 'send_msg',
                'content': message
            },
            (a, b) => {}
        )
        send_data("/chat", { "action": "get_msg" }, messages_update_callback);
    }
}

function messages_update_callback(status, data) {
    if (status == 200 && data["success"]) {
        size = chat_messages.length
        console.log(chat_messages);
        data.messages.forEach(message => {
            chat_messages.push(message)
        });
        if (size != chat_messages.length) {
            update_messages_display();
        }
    }
}

function update_messages_display() {
    shouldScroll = messages.scrollTop + messages.clientHeight === messages.scrollHeight;
    messages.innerHTML = "";
    chat_messages.forEach(message => {
        messages.innerHTML += msg_template.replace(
            "{username}",
            message['username']
        ).replace("{text}", message['text']);
    });
    if (shouldScroll) {
        scrollToBottom(messages);
    }
}