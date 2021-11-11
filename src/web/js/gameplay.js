function add_letter(letter) {
    if (letter === 'Backspace') {
        document.getElementById("word").innerText = document.getElementById("word").innerText.slice(0, -1);
        document.getElementById("validation_btn").classList.remove('bad');
        return;
    } else if (document.getElementById("validation_btn").classList.contains('bad')) {
        document.getElementById("word").textContent = '';
        document.getElementById("validation_btn").classList.remove('bad');
    }
    if (letter === 'reset') {
        document.getElementById("word").textContent = '';
        document.getElementById("validation_btn").classList.remove('bad');
    } else {
        if (document.getElementById("word").textContent === '') {
            document.getElementById("word").textContent = letter.toUpperCase();
        } else {
            document.getElementById("word").textContent = document.getElementById("word").textContent + letter;
        }
    }
}


function submit_word() {
    send_data('/llm', {
        'action': 'submit_word',
        'word': document.getElementById('word').textContent
    }, (r, data) => {
        if (r == 200 && data['success']) {
            if (!data['valid']) {
                document.getElementById("validation_btn").classList.add('bad')
            } else {
                send_data('/llm', { 'action': 'update' }, update_callback);
            }
        }
    })
}

function start_game() {
    send_data("/llm", { 'action': 'start_game' }, (a, b) => {
        send_data('/llm', { 'action': 'update' }, update_callback)
    })
}

function restart_game() {
    send_data("/llm", { 'action': 'create_game' }, (a, b) => {
        send_data('/llm', { 'action': 'update' }, update_callback)
    })
}

function force_end_round(state, el) {
    if (state == 0) {
        el.innerText = "This is going to end the current round, click again to confirm.";
        el.onclick = function() { force_end_round(1, el); };
    } else if (state == 1) {
        el.innerText = "Reset in progress ...";
        send_data("/llm", { 'action': 'reset_game' }, () => {});
    }
}