function set_content(content) {
    console.log('Changing content to', content);
    if (content === 'login' && (document.getElementById('login').style.display === 'none' || document.getElementById('signin').style.display === '')) {
        console.log('Changed content to login');
        document.getElementById('signin').style.display = 'none';
        document.getElementById('login').style.display = 'block';
        document.getElementById('title_1').style.borderBottomStyle = 'none';
        document.getElementById('title_2').style.borderBottomStyle = 'solid';
    } else if (content === 'signin' && (document.getElementById('signin').style.display === 'none' || document.getElementById('signin').style.display === '')) {
        console.log('Changed content to signin');
        document.getElementById('login').style.display = 'none';
        document.getElementById('signin').style.display = 'block';
        document.getElementById('title_2').style.borderBottomStyle = 'none';
        document.getElementById('title_1').style.borderBottomStyle = 'solid';
    }
}


function main() {
    set_content('login')



    var buttons = document.getElementsByClassName("validation_btn");
    for (var i = 0; i < buttons.length; i++) {
        buttons[i].addEventListener("click", function(event) {
            event.target.classList.add("active");
            setTimeout(() => {
                event.target.classList.remove("active");
            }, 400);
        })
    }

    window.onload = function() {
        document.getElementById("loading").style.display = 'none';
    };
}

main();