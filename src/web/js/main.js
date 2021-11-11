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
            },
            (status, player_data) => {
                if (player_data.success) {
                    if (player_data.banned) {
                        document.getElementById("error-message-join").textContent = "You cannot join this game";
                        document.getElementById("error-message-join").style.display = 'block';
                    } else {
                        document.getElementById("join-box").style.display = 'none';
                    }
                } else {
                    if (player_data.message == "game_already_started") {
                        document.getElementById("error-message-join").textContent = "This game already started";
                        document.getElementById("error-message-join").style.display = 'block';
                    } else {
                        document.getElementById("error-message-join").textContent = `Something unexpected happened : ${player_data.message}`;
                        document.getElementById("error-message-join").style.display = 'block';
                    }
                }
            }
        )
    } else {
        document.getElementById("error-message-join").textContent = "Enter your username";
        document.getElementById("error-message-join").style.display = 'block';
        document.getElementById("username_input").style.borderColor = "#e03939"
    };
}

function update_callback(status, data) {
    if (status == 200 && data["success"]) {
        player_list.innerHTML = "";
        data["users"].forEach(function(player, i) {
            player_list.innerHTML += player_template.replace(
                "{name}", player['username']
            ).replace(
                "{points}", player['points']
            ).replace(
                "{public_uuid}", player["public_uuid"]
            );
        })
        update_game_panel(data["player_status"], data["admin"], data);
        if (data["should_update_messages"]) {
            send_data("/chat", { "action": "get_msg" }, messages_update_callback)
        }
    }
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
        if (event.key === 'Enter') {
            if (document.getElementById("join-box").style.display != 'none') {
                document.getElementById("join_btn").click();
            }
        }
    });

    document.addEventListener('keydown', function(event) {
        if (!document.getElementById("game_panel").contains(document.getElementById("panel_ingame"))) {
            return;
        }
        if (document.querySelector("#message") === document.activeElement){
            return;
        }
        if(event.key === document.getElementById("lt1").innerText.toLowerCase()){
            add_letter(event.key);
        }
        if (event.key === document.getElementById("lt2").innerText.toLowerCase()) {
            add_letter(event.key);
        }
        if (event.key === document.getElementById("lt3").innerText.toLowerCase()) {
            add_letter(event.key);
        }
        if (event.key === document.getElementById("lt4").innerText.toLowerCase()) {
            add_letter(event.key);
        }
        if (event.key === document.getElementById("lt5").innerText.toLowerCase()) {
            add_letter(event.key);
        }
        if (event.key === document.getElementById("lt6").innerText.toLowerCase()) {
            add_letter(event.key);
        }
        if (event.key === document.getElementById("lt7").innerText.toLowerCase()) {
            add_letter(event.key);
        }
        if (event.key === 'Backspace') {
            add_letter('Backspace');
        }
        if (event.key === 'Enter') {
            document.getElementById("validation_btn").click()
        }
    });

    setupChat();

    window.onload = function() {
        setVisible('#page', true);
        setVisible('#loading', false);
    };
}

function ban_player(public_uuid) {
    send_data("/llm", { 'action': 'ban_player', 'public_uuid': public_uuid }, (a, b) => {
        send_data('/llm', { 'action': 'update' }, update_callback)
    })
}

function toast(text, blink, duration = 5) {
    var toast_element = document.createElement("div")
    toast_element.classList.add('notif')
    toast_element.innerText = text
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

main();