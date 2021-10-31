function addLetter(letter) {
    if (document.getElementById("validation_btn").classList.contains('bad')) {
        document.getElementById("word").textContent = ''
        document.getElementById("validation_btn").classList.remove('bad')
    }
    if (letter === 'reset') {
        document.getElementById("word").textContent = ''
        document.getElementById("validation_btn").classList.remove('bad')
    } else {
        if (document.getElementById("word").textContent === '') {
            document.getElementById("word").textContent = letter.toUpperCase()
        } else {
            document.getElementById("word").textContent = document.getElementById("word").textContent + letter
        }
    }
}


function submitWord() {
    send_data('/llm', {
        'action': 'submit_word',
        'word': document.getElementById('word').textContent
    }, (r, data) => {
        if (r == 200 && data['success']) {
            if (!data['valid']) {
                document.getElementById("validation_btn").classList.add('bad')
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