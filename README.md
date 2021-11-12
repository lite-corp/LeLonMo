# LeLonMo 2.0
[![Python 3.6](https://img.shields.io/badge/Works_with_python-v3.9-blue.svg)](https://www.python.org/downloads/release/python-390/)
## Rules
This is a multiplayer game where you have to find the largest possible word with the given letters (7 of them).

You can use the same letter several times. 

## Playing
Open your browser and enter the ip of the server you want to play on. Make sure to connect on the port 8080, by adding :8080 to the ip address.

For example if you want to play on the server with the ip 192.168.1.16, you have to go to http://192.168.1.16:8080/

You will have to choose a username, which will be visible to other players. The first person to join gains control over the server, and is the one who decides when the game starts and end.

Note that visiting other pages (even the Rules or About pages) might disconnect you from the server.

## Installation
If you want to install the server on your machine, you need to clone this repository

	git clone https://github.com/lite-corp/LeLonMo

Then execute the file

	start_win32.bat

if you are on Windows or `cd` to `LeLonMo` and run

	./start_unix.sh

Additionally you can start the server by running the file located in `src/server/server.py` with the python interpreter. Always make sure that you are running this file from the root of the clonned repository to avoid errors.

### Customizable Settings
The game will soon include more customizations, but for now you can edit some of the settings by modifying [`src/server/settings.py`](https://github.com/lite-corp/LeLonMo/blob/llm2/src/server/settings.py), and edit the [`DefaultProvider`](https://github.com/lite-corp/LeLonMo/blob/f006fdfaeb86ad30ddb983f6fd2e41254b85187c/src/server/settings.py#L23) class.

## Contributors
 - [@FXCourel](https://github.com/FXCourel)
 - [@MI6-Pikes00](https://github.com/MI6-Pikes00)
 - [@LiteApplication](https://github.com/LiteApplication)
