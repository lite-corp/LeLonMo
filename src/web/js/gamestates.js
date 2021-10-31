var msg_template;
var player_template;
var game_in_progress;
var game_end_results_admin;
var game_end_results;
var game_not_started_admin;
var game_not_started;
var game_waiting_for_others;
var game_waiting_for_others_admin;
var default_game_panel;

var locked_game_state = false;
var last_game_state = '';
var last_admin_state = '';

function loaditems() {

    console.log("Loading game content ... ");

    fetch("templates/message.html").then((r) => { r.text().then((d) => { msg_template = d }) });
    fetch("templates/player.html").then((r) => { r.text().then((d) => { player_template = d }) });
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
    game_panel.innerHTML = content;
}

function update_game_panel(player_status, admin, data) {
    if ((last_game_state !== player_status || last_admin_state !== admin) && !locked_game_state) {
        console.log("Changing game state to " + player_status);
        switch (player_status) {
            case "wait_for_start":
                if (admin) {
                    setGameContent(game_not_started_admin);
                } else {
                    setGameContent(game_not_started);
                }
                break;
            case "playing":
                var letters_dict = {};
                for (var i = 0; i < 7; i++) {
                    letters_dict[String(i + 1)] = data['letters'][i];
                }
                setGameContent(game_in_progress, letters_dict);
                break;
            case "finished":
                if (admin) {
                    setGameContent(game_waiting_for_others_admin);
                } else {
                    setGameContent(game_waiting_for_others);
                }
                break;
            case "game_ended":
                if (admin) {
                    setGameContent(game_end_results_admin);
                } else {
                    setGameContent(game_end_results);
                }
                break;
            case "not_in_game":
                if (last_game_state === '') {
                    setGameContent(default_game_panel)
                } else {
                    window.location = window.location;
                }
                break;
            default:
                setGameContent("ERROR : State is " + player_status);
                break;
        }
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