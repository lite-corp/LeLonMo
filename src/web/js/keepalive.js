var message_received = false;

function send_data(page, data, callback) {
    var xhr = new XMLHttpRequest();

    xhr.open("POST", page, true);
    xhr.setRequestHeader("Content-Type", "application/json");
    xhr.onreadystatechange = function() {
        if (xhr.readyState === 4) {
            var json = JSON.parse(xhr.responseText);
            callback(xhr.status, json);
        }
    };
    var data_formated = JSON.stringify(data);
    xhr.send(data_formated);
}

function update() {
    send_data('/llm', { 'action': 'update' }, (status, data) => {
        if (status == 200 && data["success"]) {
            if (data["should_update_messages"] && !message_received) {
                toast("You have new messages in chat, click <a href=\"/html/index.html\" id=\"link-chat\">here</a> to see them", false, 10);
                message_received = true;
            }
        }
    })
}

function toast(text, blink, duration = 5) {
    var toast_element = document.createElement("div")
    toast_element.classList.add('notif')
    toast_element.innerHTML = text
    if (blink) {
        toast_element.classList.add('blink')
    }
    page = document.getElementById("page")
    page.appendChild(toast_element)
    setTimeout(() => {
        toast_element.classList.add("active")
    }, 50);
    setTimeout(() => {
        toast_element.classList.toggle("active")
        setTimeout(() => {
            page.removeChild(toast_element)
        }, 2000)
    }, duration * 1000)

}

setInterval(update, 1000);