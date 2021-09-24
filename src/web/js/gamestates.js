var msg_template;
var player_template;
var game_in_progress;

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
                    join_response(200, { 'kicked': false });
                }
            }
        });
    setInterval(() => {
        send_data('/llm', { 'action': 'update' }, update_callback);
    }, 500);
}

function setGameContent(content) {
    game_panel = document.getElementById("game_panel");
    game_panel.innerHTML = content;
}

function update_game_panel(player_status, admin) {
    switch (player_status) {
        case "wait_for_start":
            if (admin) {
                setGameContent(game_not_started_admin);
            } else {
                setGameContent(game_not_started);
            }
            break;
        case "playing":
            setGameContent(game_in_progress);
            break;
        case "finished":
            if (admin) {
                setGameContent(game_waiting_for_others);
            } else {
                setGameContent(game_waiting_for_others_admin);
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
            setGameContent(default_game_panel);
            break;
        default:
            setGameContent("ERROR : State is " + player_status)
            break;
    }
}