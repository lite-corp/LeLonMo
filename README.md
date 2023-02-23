# LeLonMo 2.0
[![Python 3.6](https://img.shields.io/badge/Works_with_python-v3.9-blue.svg)](https://www.python.org/downloads/release/python-390/)
## Rules
This is a multiplayer game where you have to find the largest possible word with the given letters (7 of them).

You can use the same letter several times. 

## Playing
Open your browser and enter the ip of the server you want to play on. Make sure to connect on the port 8080, by adding :8080 to the ip address.

For example if you want to play on the server with the ip 192.168.1.16, you have to go to http://192.168.1.16:8080/

You will have to login with an username and your password, or create your account if you don't have one. Note that each server has its accounts database. Your username will be visible to other players. The first person to join gains control over the server, and is the one who decides when the game starts and end.

Note that visiting other pages (except the Rules or About pages) might disconnect you from the server.

## Installation
If you want to install the server on your machine, you need to clone this repository

	git clone https://github.com/lite-corp/LeLonMo

Then execute the file

	start_win32.bat

if you are on Windows or `cd` to `LeLonMo` and run

	./start_unix.sh

Additionally you can start the server by running the file located in `src/server/server.py` with the python interpreter. Always make sure that you are running this file from the root of the cloned repository to avoid errors.

### Customizable Settings
The game now includes support for settings modification. This can be done by editing `settings.json`. Keep in mind that you will need to restart the server for modifications to take effect. \
Here are the default settings in JSON with some informations :
```jsonc
{
    "server_port": 8080, // The port on which the server is available
	// Some ports like 80 require an elevation, in that case launch the server as root 
    "server_address": "0.0.0.0", // The address of the server, leave it that way if you want it to be accessible from everywhere
    "log_requests": false, // Should the server log every http request 
    "web_path": "src/web", // Path for the web server files
    "letter_number": 7, // WIP : Number of letters available to the player 
    "dict_path": "src/dict/fr.txt", // List of all valid words, you can add your own
    "time_inactive": 3, // Number of seconds of inactivity from the client before being kicked out,
	// The client is normally sending update packets every seconds
    "account_storage": "sqlite", // Method used to store user accounts, use default when testing
    "login_page": "/html/login.html", // Path to the login page relative to $web_path
    "authenticated_pages": [ // Pages where the user needs to be authenticated
        "/html/index.html"
    ],
    "cookies_pages": [ // Pages where the user will get authentication cookies
        "/html/index.html",
        "/html/login.html"
    ],
    "sqlite_account_storage_path": "users.sqlite3", // Account storage path for sqlite provider
    "token_validator_length": 8 // Lenght of the salt for the username/password authentication
    "wait_admin_file": "wait_admin.txt" // File that contains the id of the only player that can be admin
    // if the file is empty or non-existant, the first player to join will be admin
}
```

## Contributors
 - [@FXCourel](https://github.com/FXCourel)
 - [@MI6-Pikes00](https://github.com/MI6-Pikes00)
 - [@LiteApplication](https://github.com/LiteApplication)
