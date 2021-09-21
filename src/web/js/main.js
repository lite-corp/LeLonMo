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
    if (window.location.pathname == '/') {
        window.location.replace("/html/index.html");
    }
    console.log("Checking player in game ... ");
    send_data('/llm', {
            'action': 'update'
        },
        function(status, data) {
            if (status == 200 && data["success"]) {
                if (data['in_game']) {
                    console.log("Player is already in the game.");
                    join_response(200, { 'kicked': false });
                }
            }
        });
}

// Press enter to trigger button in text field
var input = document.getElementById("username_input");
input.addEventListener("keyup", function(event) {
    if (event.keyCode === 13) {
        document.getElementById("join_btn").click();
    }
});

var input = document.getElementById("message");
input.addEventListener("keyup", function(event) {
    if (event.keyCode === 13) {
        document.getElementById("message").value = "";
    }
});