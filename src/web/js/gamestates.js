var msg_template;
var player_template = null;
var player_template_admin = null;
var player_template_normal = null;
var game_in_progress = null;
var game_end_results_admin = null;
var game_end_results = null;
var game_not_started_admin = null;
var game_not_started = null;
var game_waiting_for_others = null;
var game_waiting_for_others_admin = null;
var default_game_panel = null;

var locked_game_state = false;
var last_game_state = '';
var last_admin_state = '';

function loaditems() {

    console.log("Loading game content ... ");

    fetch("templates/message.html").then((r) => { r.text().then((d) => { msg_template = d }) });
    fetch("templates/player.html").then((r) => {
        r.text().then((d) => {
            player_template = d;
            player_template_normal = d;
        })
    });
    fetch("templates/player_admin.html").then((r) => { r.text().then((d) => { player_template_admin = d }) });

    fetch("templates/game_in_progress.html").then((r) => { r.text().then((d) => { game_in_progress = d }) });
    fetch("templates/game_end_results_admin.html").then((r) => { r.text().then((d) => { game_end_results_admin = d }) });
    fetch("templates/game_end_results.html").then((r) => { r.text().then((d) => { game_end_results = d }) });
    fetch("templates/game_not_started_admin.html").then((r) => { r.text().then((d) => { game_not_started_admin = d }) });
    fetch("templates/game_not_started.html").then((r) => { r.text().then((d) => { game_not_started = d }) });
    fetch("templates/game_waiting_for_others.html").then((r) => { r.text().then((d) => { game_waiting_for_others = d }) });
    fetch("templates/game_waiting_for_others_admin.html").then((r) => { r.text().then((d) => { game_waiting_for_others_admin = d }) });
    fetch("templates/default_game_panel.html").then((r) => { r.text().then((d) => { default_game_panel = d }) });

    console.log("Checking player in game ... ");
    send_data('/llm', {
            'action': 'update'
        },
        function(status, data) {
            if (status == 200 && data["success"]) {
                if (data['in_game']) {
                    console.log("Player is already in the game.");
                    document.getElementById("join-box").style.display = 'none';
                }
            }
        });
    setInterval(() => {
        send_data('/llm', { 'action': 'update' }, update_callback);
    }, 1000);
}

function setGameContent(content, replaces = {}) {
    for (var key in replaces) {
        if (replaces.hasOwnProperty(key)) {
            content = content.replace('{' + key + '}', replaces[key]);
        }
    }
    game_panel = document.getElementById("game_panel");
    if (content != null) {
        game_panel.innerHTML = content;
        return true;
    } else {
        return false;
    }
}

function update_game_panel(player_status, admin, data) {
    var content_change_result = false;
    if (last_admin_state !== admin) {
        if (admin) {
            player_template = player_template_admin;
        } else {
            player_template = player_template_normal;
        }
    }
    if ((last_game_state !== player_status || last_admin_state !== admin) && !locked_game_state) {
        console.log("Changing game state to " + player_status);
        switch (player_status) {
            case "wait_for_start":
                if (admin) {
                    content_change_result = setGameContent(game_not_started_admin);
                } else {
                    content_change_result = setGameContent(game_not_started);
                }
                break;
            case "playing":
                var letters_dict = {};
                for (var i = 0; i < 7; i++) {
                    letters_dict[String(i + 1)] = data['letters'][i];
                }
                content_change_result = setGameContent(game_in_progress, letters_dict);
                break;
            case "finished":
                if (admin) {
                    content_change_result = setGameContent(game_waiting_for_others_admin);
                } else {
                    content_change_result = setGameContent(game_waiting_for_others);
                }
                break;
            case "game_ended":
                if (admin) {
                    content_change_result = setGameContent(game_end_results_admin);
                } else {
                    content_change_result = setGameContent(game_end_results);
                }
                populate_leaderboard(data);
                break;
            case "not_in_game":
                if (last_game_state === '') {
                    content_change_result = setGameContent(default_game_panel)
                } else {
                    window.location = window.location; // Reload page on server restart
                }
                break;
            default:
                content_change_result = setGameContent("ERROR : State is " + player_status);
                break;
        }
        if (content_change_result)
            last_game_state = player_status;
        last_admin_state = admin;
    }
}

function toggleGameLocked() {
    locked_game_state = !locked_game_state;
    if (locked_game_state) {
        console.log("Game state locked");
    } else {
        console.log("Game state unlocked");
    }
}

function forceGameChange(admin = false) {
    var game_state = ''
    switch (last_game_state) {
        case "wait_for_start":
            game_state = 'playing';
            break;
        case "playing":
            game_state = "finished";
            break;
        case "finished":
            game_state = "game_ended";
            break;
        case "game_ended":
            game_state = "not_in_game";
            break;
        case "not_in_game":
            game_state = "wait_for_start";
            break;
        default:
            game_state = "wait_for_start";
            break;
    }
    locked_game_state = false;
    update_game_panel(game_state, admin);
    locked_game_state = true;
}

function populate_leaderboard(data) {
    var sb_body = document.getElementById("results_table").getElementsByTagName("tbody")[0];
    let users = data.users.sort((a, b) => (a.latest_points > b.latest_points ? -1 : 1));
    for (var user in users) {
        var row = document.createElement("tr");
        row.innerHTML += `<td>${users[user].username}</td>`;
        row.innerHTML += `<td>${users[user].latest_word}</td>`;
        row.innerHTML += `<td>${users[user].points} (+${users[user].latest_points})</td>`;
        sb_body.appendChild(row);
    }
}