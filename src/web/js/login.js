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

function getCookie(name) {
    var nameEQ = name + "=";
    var ca = document.cookie.split(';');
    for (var i = 0; i < ca.length; i++) {
        var c = ca[i];
        while (c.charAt(0) == ' ') c = c.substring(1, c.length);
        if (c.indexOf(nameEQ) == 0) return c.substring(nameEQ.length, c.length);
    }
    return null;
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
            if (event.target.id == "login_btn") {
                auth_token = sha256(
                    document.getElementById("login_username").value +
                    getCookie('private_uuid') +
                    document.getElementById("login_password").value
                )
                send_data("/account", {
                    'action': 'login',
                    'username': document.getElementById('login_username').value,
                    'token': auth_token
                }, (status, data) => {
                    if (data.success) {
                        window.location = '/html/index.html'
                    } else {
                        // something went wrong
                        console.error('Something went wrong while trying to login');
                        console.error(status, data);
                    }

                })
            } else if (event.target.id == "signin_btn") {
                send_data("/account", {
                    'action': 'signin',
                    'username': document.getElementById('signin_username').value,
                    'email': document.getElementById('signin_email').value,
                    'password': document.getElementById('signin_password').value
                }, (status, data) => {
                    if (data.success) {
                        window.location = '/html/index.html'
                    } else {
                        // something went wrong
                        console.error('Something went wrong while trying to sign in');
                        console.error(status, data);
                    }
                })
            }

        })
    }

    window.onload = function() {
        document.getElementById("loading").style.display = 'none';
    };
}

main();