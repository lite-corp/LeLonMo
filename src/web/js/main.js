var data_last = null;

var player_list = document.getElementById("player_list");
var msg_template = ""
var player_template = ""
var logged = false;



function updatesEqual(a, b) {
    if (a == null || b == null) {
        return false;
    }
    a.self.last_update = 0;
    b.self.last_update = 0;
    return JSON.stringify(a) == JSON.stringify(b);
}


function send_data(page, data, callback) {
    var xhr = new XMLHttpRequest();

    xhr.open("POST", page, true);
    xhr.setRequestHeader("Content-Type", "application/json");
    xhr.onreadystatechange = function () {
        if (xhr.readyState === 4) {
            var json = JSON.parse(xhr.responseText);
            callback(xhr.status, json);
        }
    };
    var data_formated = JSON.stringify(data);
    xhr.send(data_formated);
}

function set_cookie(name, value, days) {
    var expires = "";
    if (days) {
        var date = new Date();
        date.setTime(date.getTime() + (days * 24 * 60 * 60 * 1000));
        expires = "; expires=" + date.toUTCString();
    }
    document.cookie = name + "=" + (value || "") + expires + "; path=/; SameSite=Strict";
}

function update_callback(status, data) {
    if (status == 200 && data["success"] && !updatesEqual(data_last, data)) {
        data_last = data;
        update_game_panel(data["player_status"], data["admin"], data);
        if (data["should_update_messages"]) {
            send_data("/chat", { "action": "get_msg" }, messages_update_callback)
        }
        if (!logged) {
            toast("Welcome " + data["self"]["username"] + " to LeLonMo !", false);
            logged = true;
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

    document.addEventListener('keydown', function (event) {
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
    })

    setupChat();

    window.onload = function () {
        setVisible('#page', true);
        setVisible('#loading', false);
        update();
    };
}

function ban_player(public_uuid) {
    if (public_uuid === data_last["self"]["public_uuid"]) {
        toast("You cannot kick yourself", true, 3);
        return
    }
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

function logout() {
    set_cookie("auth_token");
    console.log("User logged out");
    window.location.replace("/html/login.html");
}

function update() {
    send_data('/llm', { 'action': 'update' }, update_callback)
}

main();