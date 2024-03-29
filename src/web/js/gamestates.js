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
var game_banned = null;
var default_game_panel = null;

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
    fetch("templates/game_banned.html").then((r) => { r.text().then((d) => { game_banned = d }) });
    fetch("templates/default_game_panel.html").then((r) => { r.text().then((d) => { default_game_panel = d }) });

    setInterval(() => {
        update();
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

    player_list.innerHTML = "";
    data["users"].forEach(function (player, i) {
        is_finished = player["status"] === "finished";
        player_list.innerHTML += player_template.replace(
            "{name}", player['username'] + (is_finished ? " ✓" : ""),
        ).replace(
            "{points}", player['points']
        ).replace(
            "{public_uuid}", player["public_uuid"]
        );
    })


    if ((last_game_state !== player_status || last_admin_state !== admin)) {
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
                    content_change_result = setGameContent(default_game_panel);
                } else {
                    window.location = window.location; // Reload page on server restart
                }
                break;
            case "banned":
                content_change_result = setGameContent(game_banned);
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