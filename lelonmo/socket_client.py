
import json
import sys
import socket
import threading
from time import sleep as wait
import atexit

from lelonmo.async_input import Input
from lelonmo import PACKAGE_PARENT, persist_data
from lelonmo.consolemenu import *
from lelonmo.consolemenu.format import *
from lelonmo.main_offline import human_to_bool

PORT = 11111


def _send_data(data: str, host: str):
    socket.timeout = 2
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect((host, PORT))

        # Allow identifying users at anytime
        s.send(
            bytearray(f"{persist_data.DATA['online']['uuid']}%{data}", "utf-8"))
        # UUID is never shared with other players
        v = s.recv(1024)
        s.close()
        return v
    except ConnectionRefusedError:
        print("Server error : Connexion refused")
        exit_server()
        s.close()
        sys.exit()
    except Exception as e:
        exit_server()
        s.close()
        print("Server error :", e)
        sys.exit(0)


def _status(host):  # Small function to get server status
    return _send_data("status%", host).decode('utf-8')


def _wait_for_status(key, host):  # Wait for a specific status in order to continue
    while not _status(host).startswith(key):
        # Avoid spamming the server
        wait(persist_data.DATA["online"]["update_speed"])


def _join_game(wb, ip="localhost"):  # Initiate the connexion between client and server
    player_id = _send_data("join%" + persist_data.DATA["online"]["name"], ip)
    if player_id == b"started":
        wb.add("The game you tried to join already started")
        exit()
    elif player_id == b"wait%":
        wb.add("Waiting for admin to restart the game ...")
        while player_id == b"wait%":
            wait(persist_data.DATA["online"]["update_speed"])
            player_id = _send_data(
                "join%" + persist_data.DATA["online"]["name"], ip)
        return int(player_id)
    elif player_id == b"":
        wb.add("Error while joining, try again later")
    else:
        try:
            int(player_id)
        except:
            wb.add("Error while joining, try again later")
            exit()
        if int(player_id) >= 0:
            return int(player_id)
        else:
            name = ""
            while not int(player_id) >= 0:
                wb.clear()
                wb.add({
                    -1 : "Please enter a username",
                    -2 : "Username cannot be a space",
                    -3 : "Username contains forbiden words or characters",
                    -4 : "This username is already taken"
                }[int(player_id)])
                name = input("Please enter your username : ")
                try:
                    player_id = int(_send_data("join%" + name, ip))
                except ValueError:
                    wb.add("Error while joining, try again later")
                    exit()
            persist_data.update_key('name', name, "online")
            return int(player_id)


class WhiteBoard:  # Manages the menu on screen, used to update things unig threads
    def __init__(self, format, text=""):
        self.text = text  # Text on the menu
        self.menu = ConsoleMenu(
            "LeLonMo X", "Online Mode", prologue_text=self.text, formatter=format)
        # Part of the data that will be overwritten on updates (player list and status)
        self.updatable = ""
        self.updatable_2 = ""

    def add(self, *args, updatable="", invert=False, updatable_2=""):  # Add a line to the menu
        args = list(args)
        if not updatable:
            updatable = self.updatable
        if not updatable_2:
            updatable_2 = self.updatable_2
        self.updatable_2 = updatable_2
        self.updatable = updatable
        self.text = self.text + "\n" + " ".join(args)
        self.menu.prologue_text = self.text + updatable
        # invert updatable text and normal text (used during the game itself)
        if invert:
            self.menu.prologue_text = updatable + self.text
        self.menu.prologue_text = self.menu.prologue_text + updatable_2
        self.menu.clear_screen()
        self.menu.draw()
    def update_letter(self, letters):
        self.add(updatable_2="".join(letters), invert=True)
    def clear(self):  # Clear and update the menu, removes the text and the updates
        self.text = str()
        self.updatable = str()
        self.updatable_2 = str()
        self.menu.clear_screen()
        self.menu.draw()


class PlayerUpdate(threading.Thread):  # Thread dedicated to player list update
    def __init__(self, board: WhiteBoard, host: str):
        self.enable = True
        self.board = board
        self.host = host
        self.invert = False
        threading.Thread.__init__(self)
        self.setDaemon(True)

    def run(self, run=False):  # Run is set to prevent the thread from looping if only one run is needed
        while self.enable or run:
            status = _send_data("players%", self.host).decode("utf-8")
            self.players = status
            self.board.add(updatable="Players :\n * " +
                           "\n * ".join(status.split("%")), invert=self.invert)
            if not run:
                wait(persist_data.DATA["online"]["update_speed"])
            run = False


server_ip = "localhost"


def main(host="localhost"):
    global server_ip
    server_ip = host
    menu_format = MenuFormatBuilder() \
        .set_border_style_type(MenuBorderStyleType.DOUBLE_LINE_OUTER_LIGHT_INNER_BORDER) \
        .set_prompt("") \
        .set_title_align('center') \
        .set_subtitle_align('center') \
        .set_left_margin(4) \
        .set_right_margin(4) \
        .show_header_bottom_border(True) \
        .set_prologue_text_align('left')

    wb = WhiteBoard(menu_format)

    wb.add(f"Joining the game hosted at {host}")
    player_id = _join_game(wb, host)
    wb.add("Joined successfully")
    admin = False
    if player_id == 0:  # Admin detection
        wb.add("You are the administrator, press [ENTER] to start the game")
        admin = True
    playerboard = PlayerUpdate(wb, host)
    playerboard.start()
    if admin:
        input()
        if _send_data("start%", host) == "ok%":
            wb.add("Game started successfully")
        else:
            wb.add("Unauthorized")
            if not persist_data.DATA["online"]["name"] in playerboard.players:
                playerboard.enable = False
                del admin
                del wb
                del player_id
                from lelonmo.main_online import main_online
                main_online(host)
    else:
        status = _status(host)
        while not status.startswith("start"):
            status = _status(host)
            # Avoid spamming the server
            if not persist_data.DATA["online"]["name"] in _send_data("players%", host).decode("utf-8"):
                playerboard.enable = False
                del admin
                del wb
                del player_id
                from lelonmo.main_online import main_online
                main_online(host)
            wait(persist_data.DATA["online"]["update_speed"])

    wb.clear()
    playerboard.invert = True
    wb.add(
        "Game started\n",
        "You have to compose your word with these letters\n",
        " ".join(_status(host)[5:]),
        "\n Enter your word : "
    )
    
    input_method = Input(wb.update_letter, "_").run if persist_data.DATA["online"]["async_input"] else input
    if input_method is input: 
        playerboard.enable = False
    while not _send_data(''.join(input_method()), host).decode("utf-8").startswith("valid%"):
        wb.add(updatable_2='Your word is not valid', invert=True)
    sys.stdin.flush() # Clear the buffer
    playerboard.enable = False
    wb.clear()
    wb.add("Waiting for other players to finish")
    playerboard = PlayerUpdate(wb, host)
    playerboard.start()
    _wait_for_status("results", host)
    playerboard.enable = False
    wb.updatable = ""

    result_data = json.loads(_status(host)[7:])
    wb.clear()
    wb.add(
        "Results : \n Winner(s):\n * " + "\n  * ".join([i[0] + " : " + i[1] for i in result_data["best"]]) +
        "\n\n Scores :\n * " +
        "\n  * ".join([i["name"] + " : " + i["word"]
                       for i in result_data["players"]])
    )


def exit_server():
    global server_ip
    socket.timeout = persist_data.DATA["online"]["update_speed"]
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect((server_ip, PORT))
        s.send(
            bytearray(f"{persist_data.DATA['online']['uuid']}%{'leave%'}", "utf-8"))
        s.close()
    except:
        pass


atexit.register(exit_server)


if __name__ == "__main__":
    host = input(
        "Please enter the IP of the server (leave empty for local) : ")
    if not host:
        host = "localhost"
    main(host)
    while human_to_bool("Do you want to play again ?\n"):
        main(host)
