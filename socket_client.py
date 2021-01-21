
import json
import socket
import threading
import persist_data
from consolemenu import *
from consolemenu.format import *
from time import sleep as wait
from main_offline import human_to_bool


PORT = 11111

def _send_data(data: str, host: str):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, PORT))

    s.send(bytearray(f"{persist_data.DATA['online']['uuid']}%{data}", "utf-8"))
    v = s.recv(1024)
    s.close()
    return v


def _status(host):
    return _send_data("status%", host).decode('utf-8')


def _wait_for_status(key, host):
    while not _status(host).startswith(key):
        wait(persist_data.DATA["online"]["update_speed"])


def join_game(ip="localhost"):
    player_id = _send_data("join%" + persist_data.DATA["online"]["name"], ip)
    if player_id == b"started":
        print("The game you tried to join already started")
        exit()
    else:
        return int(player_id)


tcpsock = None


class WhiteBoard:
    def __init__(self, format, text=""):
        self.text = text
        self.menu = ConsoleMenu(
            "LeLonMo X", "Online Mode", prologue_text=self.text, formatter=format)
        self.updatable = ""

    def add(self, *args, updatable="", invert=False):
        args = list(args)
        if not updatable:
            updatable = self.updatable
        self.updatable = updatable
        self.text = self.text + "\n" + " ".join(args)
        self.menu.prologue_text = self.text + updatable
        if invert:
            self.menu.prologue_text = updatable + self.text
        self.menu.clear_screen()
        self.menu.draw()

    def clear(self):
        self.text = str()
        self.menu.clear_screen()
        self.menu.draw()


class PlayerUpdate(threading.Thread):
    def __init__(self, board, host):
        self.enable = True
        self.board = board
        self.host = host
        self.invert = False
        threading.Thread.__init__(self)

    def run(self, run=False):
        while self.enable or run:
            status = _send_data("players%", self.host).decode("utf-8")
            self.board.add(updatable="Players :\n * " +
                           "\n * ".join(status.split("%")), invert=self.invert)
            if not run:
                wait(persist_data.DATA["online"]["update_speed"])
            run = False


def main(host="localhost"):
    global tcpsock
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
    if not persist_data.DATA["online"]["name"]:
        name = ""
        while (not name) or ("%" in name):
            name = input("Please enter your username : ")
        persist_data.update_key(master='online', key='name', value=name)
        wb.add("Username updated, go to Settings > Online Settings to change it")
    else:
        wb.add("You are logged in as", persist_data.DATA["online"]["name"])
    wb.add(f"Joining the game hosted at {host}")
    player_id = join_game(host)
    wb.add("Joined successfully")
    admin = False
    if player_id == 0:
        wb.add("You are the administrator, press [ENTER] to start the game")
        admin = True
    playerboard = PlayerUpdate(wb, host)
    playerboard.start()
    if admin:
        input()
        if _send_data("start%", host) == "ok":
            wb.add("Game started successfully")
        else:
            wb.add("")

    _wait_for_status("start", host)

    wb.clear()
    wb.add(
        "Game started\n",
        "You have to compose your word with these letters\n",
        " ".join(_status(host)[5:])
    )

    playerboard.enable = False
    playerboard.invert = True
    playerboard.run(True)  # Show the players once after update then stop
    while not _send_data(input("Enter your word : "), host).decode("utf-8").startswith("valid%"):
        print("Invalid, try again")
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


if __name__ == "__main__":
    host = input(
        "Please enter the IP of the server (leave empty for local) : ")
    if not host:
        host = "localhost"
    main(host)
    while human_to_bool("Do you want to play again ?\n"):
        main(host)
