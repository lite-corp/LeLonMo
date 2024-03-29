function set_content(content) {
    if (content === 'login') {
        console.log('Changed content to login');
        document.getElementById('signin').style.display = 'none';
        document.getElementById('login').style.display = 'block';
        document.getElementById('title_1').style.borderBottomStyle = 'none';
        document.getElementById('title_2').style.borderBottomStyle = 'solid';
        bad_input(false);
        document.getElementById('error_login').style.display = 'none';
        document.getElementById('error_signin').style.display = 'none';
    } else if (content === 'signin') {
        console.log('Changed content to signin');
        document.getElementById('login').style.display = 'none';
        document.getElementById('signin').style.display = 'block';
        document.getElementById('title_2').style.borderBottomStyle = 'none';
        document.getElementById('title_1').style.borderBottomStyle = 'solid';
        bad_input(false);
        document.getElementById('error_login').style.display = 'none';
        document.getElementById('error_signin').style.display = 'none';
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

function get_cookie(name) {
    var nameEQ = name + "=";
    var ca = document.cookie.split(';');
    for (var i = 0; i < ca.length; i++) {
        var c = ca[i];
        while (c.charAt(0) == ' ') c = c.substring(1, c.length);
        if (c.indexOf(nameEQ) == 0) return c.substring(nameEQ.length, c.length);
    }
    return null;
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

function bad_input(bool, msg = null) {
    var inputs = document.getElementsByClassName('form')
    if (bool) {
        for (var i = 0; i < inputs.length; i++) {
            inputs[i].classList.add('bad');
            if (document.getElementById('login').style.display === 'block') {
                document.getElementById('error_login').style.display = 'block';
                document.getElementById('error_login').innerText = msg;
            } else if (document.getElementById('signin').style.display === 'block') {
                document.getElementById('error_signin').style.display = 'block';
                document.getElementById('error_signin').innerText = msg;
            }
        }
    } else if (!bool) {
        for (var i = 0; i < inputs.length; i++) {
            inputs[i].classList.remove('bad');
        }
    }
}

function main() {
    set_content('login')



    var buttons = document.getElementsByClassName("validation_btn");
    document.addEventListener('keydown', function(event) {
        if (event.key === 'Enter') {
            if (document.getElementById('login').style.display === 'block') {
                document.getElementById("login_btn").click();
            } else if (document.getElementById('signin').style.display === 'block') {
                document.getElementById("signin_btn").click();
            }
        }
    })
    for (var i = 0; i < buttons.length; i++) {
        buttons[i].addEventListener("click", function(event) {
            event.target.classList.add("active");
            setTimeout(() => {
                event.target.classList.remove("active");
            }, 400);
            if (event.target.id == "login_btn") {
                auth_token = sha256(
                    document.getElementById("login_username").value +
                    sha256(document.getElementById("login_password").value) +
                    get_cookie('token_validator')
                )
                send_data("/auth", {
                    'action': 'login',
                    'username': document.getElementById('login_username').value,
                    'token': auth_token
                }, (status, data) => {
                    if (data.success) {
                        set_cookie("auth_token", auth_token, 365)
                        window.location = '/html/index.html'
                    } else {
                        // something went wrong
                        console.error('Something went wrong while trying to login');
                        console.error(status, data);
                        if (data.validator_token !== get_cookie('token_validator')) {
                            // Retry with new token validator if the first one is wrong
                            console.warn("Frist token validator was outdated, retrying")
                            set_cookie("token_validator", data.validator_token, 0)
                            auth_token = sha256(
                                document.getElementById("login_username").value +
                                sha256(document.getElementById("login_password").value) +
                                get_cookie('token_validator')
                            )
                            send_data("/auth", {
                                'action': 'login',
                                'username': document.getElementById('login_username').value,
                                'token': auth_token
                            }, (status, data) => {
                                if (data.success) {
                                    set_cookie("auth_token", auth_token, 365)
                                    window.location = '/html/index.html'
                                } else {
                                    console.error(data);
                                    bad_input(true, data.message);
                                }
                            })
                        } else {
                            bad_input(true, data.message);
                        }
                    }

                })
            } else if (event.target.id == "signin_btn") {
                auth_token = sha256(
                    document.getElementById("signin_username").value +
                    sha256(document.getElementById("signin_password").value) +
                    get_cookie('token_validator')
                );
                send_data("/auth", {
                    'action': 'signin',
                    'username': document.getElementById('signin_username').value,
                    'email': document.getElementById('signin_email').value,
                    'password': document.getElementById('signin_password').value,
                    'token': auth_token
                }, (status, data) => {
                    if (data.success) {
                        set_cookie("auth_token", auth_token, 365)
                        window.location = '/html/index.html'
                    } else {
                        // something went wrong
                        console.error('Something went wrong while trying to sign in');
                        console.error(status, data);
                        bad_input(true, data.message);
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