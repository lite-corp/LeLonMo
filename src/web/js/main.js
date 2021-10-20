var data_me = {}

var player_list = document.getElementById("player_list");
var msg_template = ""
var player_template = ""

window.getCookie = function(name, default_value = null) {
    var match = document.cookie.match(new RegExp('(^| )' + name + '=([^;]+)'));
    if (match) return match[2];
    return default_value;
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

function update_callback(status, data) {
    if (status == 200 && data["success"]) {
        player_list.innerHTML = "";
        data["users"].forEach(function(item, i) {
            player_list.innerHTML += player_template.replace(
                "{name}",
                item['username']
            ).replace("{points}", item['points']);
        })
        update_game_panel(data["player_status"], data["admin"], data);
    }
}


function onReady(callback) {
    var intervalId = window.setInterval(function() {
        if (document.getElementsByTagName('body')[0] !== undefined) {
            window.clearInterval(intervalId);
            callback.call(this);
        }
    }, 1000);
}

function setVisible(selector, visible) {
    document.querySelector(selector).style.display = visible ? 'block' : 'none';
}


function main() {
    if (window.location.pathname == '/') {
        window.location.replace("/html/index.html");
    }

    loaditems();
    // Press enter to trigger button in text field
    var input = document.getElementById("username_input");
    input.addEventListener("keyup", function(event) {
        if (event.keyCode === 13) {
            document.getElementById("join_btn").click();
        }
    });

    setupChat();

    onReady(function() {
        setVisible('.page', true);
        setVisible('#loading', false);
    });
}
main();