var data_me = {}

var player_list = document.getElementById("player_list");
var msg_template = ""
var player_template = ""


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

    document.addEventListener('keydown', function(event) {
        if (document.querySelector("#message") === document.activeElement) {
            return;
        }
        if (event.key === 'Enter') {
            document.getElementsByClassName("validation_btn")[0].click()
        }
        if (!document.getElementById("game_panel").contains(document.getElementById("panel_ingame"))) {
            return;
        }
        if (event.key === document.getElementById("lt1").innerText.toLowerCase()) {
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
    });

    setupChat();

    window.onload = function() {
        setVisible('#page', true);
        setVisible('#loading', false);
        update();
    };
}

function ban_player(public_uuid) {
    send_data("/llm", { 'action': 'ban_player', 'public_uuid': public_uuid }, (a, b) => {
        update()
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

function update() {
    send_data('/llm', { 'action': 'update' }, update_callback)
}

main();