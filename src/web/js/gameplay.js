function addLetter(letter) {
    if (letter === 'reset') {
        document.getElementById("word").textContent = ''
    } else {
        document.getElementById("word").textContent = document.getElementById("word").textContent + letter
    }
}


function submitWord() {
    console.log(document.getElementById('word').textContent);
    send_data('/llm', {
        'action': 'submit_word',
        'word': document.getElementById('word').textContent
    }, (r, data) => {
        console.log(data);
        if (r == 200 && data['success']) {
            if (!data['valid']) {
                document.getElementById("validation_btn").classList.add('bad')
            }
        }
    })
}

function start_game() {
    send_data("/llm", { 'action': 'start_game' }, (a, b) => { console.log(b) })
}