data_me = {}

window.getCookie = function(name) {
    var match = document.cookie.match(new RegExp('(^| )' + name + '=([^;]+)'));
    if (match) return match[2];
}

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

function join_game() {
    if (document.getElementById("username_input").value) {
        send_data('/llm', {
            "action": "join",
            "username": document.getElementById("username_input").value
        }, join_response)
    } else {
        document.getElementById("error-message-join").textContent = "Enter your username";
        document.getElementById("error-message-join").style.display = 'block';
        document.getElementById("username_input").style.borderColor = "#e03939"
    };
}

function join_response(status, data) {
    if (status == 200 && !data["kicked"]) {
        document.getElementById("join-box").style.display = 'none';
    } else if (status == 200 && !data["kicked"]) {
        document.getElementById("error-message-join").textContent = "You cannot join this game";
        document.getElementById("error-message-join").style.display = 'block';
    } else {
        console.log(data)
        document.getElementById("error-message-join").textContent = "Unknown error";
        document.getElementById("error-message-join").style.display = 'block';
    }
}

window.onload = function() {
    send_data('/llm', {

    })
}