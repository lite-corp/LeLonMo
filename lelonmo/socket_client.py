import atexit
import json
import socket
import sys
import threading
from time import sleep as wait

from lelonmo import persist_data
from lelonmo.async_input import Input
from lelonmo.colors.colors import *
from lelonmo.consolemenu import *
from lelonmo.consolemenu.format import *
from lelonmo.main_offline import human_to_bool

PORT = 11111
BUFFER_SIZE = 4096


def _send_data(data: str, host: str):
    socket.timeout = 2
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect((host, PORT))

        # Allow identifying users at anytime
        s.send(
            bytearray(
                "%llm_client%"
                f"{persist_data.DATA['version'].replace('.', str())}%"
                f"{persist_data.DATA['online']['uuid']}%"
                f"{data}",
                "utf-8"
            )
        )
        # UUID is never shared with other players
        v = s.recv(BUFFER_SIZE)
        s.close()
        return v
    except ConnectionRefusedError:
        print("Server error : Connexion refused")
        s.close()
        exit()
    except Exception as e:
        s.close()
        print("Server error :", e)
        exit(0)


def _status(host):  # Small function to get server status
    return _send_data("status%", host).decode('utf-8')


def _wait_for_status(key, host):  # Wait for a specific status in order to continue
    while not _status(host).startswith(key):
        # Avoid spamming the server
        wait(persist_data.DATA["online"]["update_speed"])


def _join_game(wb, ip="localhost"):  # Initiate the connexion between client and server
    player_id = _send_data("join%" + persist_data.DATA["online"]["name"], ip)
    if player_id == b"started":
        wb.clear()
        wb.update("The game you tried to join already started", status=red("Connection failed"))
        wb.update("Press [ENTER] to try again")
        wait(1)  # Avoid spam
        input()
        return _join_game(wb, ip)
    elif player_id == b"wait%":
        wb.update("Waiting for admin to restart the game ...", status=yellow("Waiting ..."))
        while player_id == b"wait%":
            wait(persist_data.DATA["online"]["update_speed"])
            player_id = _send_data(
                "join%" + persist_data.DATA["online"]["name"], ip)
        return int(player_id)
    elif player_id == b"":
        wb.update("Error while joining, try again later", status=red("Unknown error"))
    elif player_id == b"outdated%":
        wb.update("Your client is outdated, please download the latest version", status=red("Client outdated"))
        import webbrowser
        webbrowser.open(persist_data.DATA["update_url"])
        exit_server()
    elif player_id == b"outdated%update":
        wb.update(f"You are about to receive an update from {ip}.", status=red("Client outdated"))
        if human_to_bool("Do you trust this server ?\n"):
            import lelonmo.updater as updater
            updater.auto_update(ip, wb)
        else:
            wb.update("Aborted update, you cannot play on this server. ")
        exit_server()

    else:
        try:
            int(player_id)
        except:
            wb.update("Error while joining, try again later", status=red("Unknown error"))
            exit()
        if int(player_id) >= 0:
            return int(player_id)
        else:
            name = ""
            while not int(player_id) >= 0:
                wb.clear()
                wb.update({
                    -1: "Please enter a username",
                    -2: "Username cannot be a space",
                    -3: "Username contains forbiden words or characters",
                    -4: "This username is already taken"
                }[int(player_id)], status=red("Invalid username"))
                name = input("Please enter your username : ")
                try:
                    player_id = int(_send_data("join%" + name, ip))
                except ValueError:
                    wb.update("Error while joining, try again later", status=red("Unknown error"))
                    exit()
            persist_data.update_key('name', name, "online")
            return int(player_id)


class WhiteBoard:  # Manages the menu on screen, used to update things unig threads
    def __init__(self, status="Initializing"):

        self.menu = ConsoleMenu(
            f"{blue('LeLonMo')} {red('Online')}", status,
            formatter=MenuFormatBuilder()
            .set_border_style_type(MenuBorderStyleType.DOUBLE_LINE_OUTER_LIGHT_INNER_BORDER)
            .set_prompt("")
            .set_title_align('center')
            .set_subtitle_align('center')
            .set_left_margin(4)
            .set_right_margin(4)
            .show_header_bottom_border(True)
            .set_prologue_text_align('left')
        )
        # Text on the menu
        self.text = str()
        self.status = status

        # Part of the data that will be overwritten on updates (player list and status)
        self.updatable = ""
        self.updatable_2 = ""
        self.invert = False
        self.clear()

    def update(self, add=None, updatable=None, updatable_2=None, status=None, invert=None):

        update_screen = False
        if updatable is not None and self.updatable != updatable:
            update_screen = True
            self.updatable = updatable
        if updatable_2 is not None and self.updatable_2 != updatable_2:
            update_screen = True
            self.updatable_2 = updatable_2
        if status is not None and self.status != status:
            update_screen = True
            self.status = status
        if add is not None:
            update_screen = True
            self.text += "\n" + str(add)
        if invert is not None and self.invert != invert:
            update_screen = True
            self.invert = invert

        if invert:
            self.menu.prologue_text = \
                self.updatable +\
                "\n\n" + \
                self.text
        else:
            self.menu.prologue_text = \
                self.text +\
                "\n" + \
                self.updatable
        self.menu.subtitle = self.status
        self.menu.epilogue_text = self.updatable_2

        if update_screen:
            self.menu.clear_screen()
            self.menu.draw()

    def update_letter(self, letters):
        self.update(updatable_2="Enter your word : \n "+"".join(letters), invert=True)

    def update_status(self, status):
        self.update(status=status)

    def clear(self):  # Clear and update the menu, removes the text and the updates
        self.text = str()
        self.updatable = str()
        self.updatable_2 = str()
        self.menu.epilogue_text = str()
        self.menu.prologue_text = str()
        self.menu.clear_screen()
        self.menu.draw()


class PlayerUpdate(threading.Thread):  # Thread dedicated to player list update
    def __init__(self, board: WhiteBoard, host: str, reconnect_if_missing=False, invert=False):
        self.enable = True
        self.board = board
        self.host = host
        self.invert = invert
        self.reconnect_if_missing = reconnect_if_missing
        threading.Thread.__init__(self)
        self.setDaemon(True)
        self.setName("Playerboard")

    def run(self, run=False):  # Run is set to prevent the thread from looping if only one run is needed
        while self.enable or run:
            players = json.loads(_send_data("players%", self.host).decode("utf-8"))
            player_list_str = str()
            for i in players:
                player_list_str += f"\n  * {i['name']} ({i['status']})"

            self.board.update(updatable="Players :" + player_list_str, invert=self.invert)

            # Reconnect to the server if name is not in player list
            if self.reconnect_if_missing:
                if not persist_data.DATA["online"]['name'] in [i["name"] for i in players if i]:
                    self.enable = False
                    from lelonmo.main_online import main_online
                    main_online(self.host)

            if not run:
                wait(persist_data.DATA["online"]["update_speed"])
            run = False


server_ip = "localhost"
wb = WhiteBoard()

def main(host="localhost"):
    global server_ip
    global wb
    wb.clear()
    server_ip = host

    wb.update_status(yellow(f"Joining {host}"))
    player_id = _join_game(wb, host)
    wb.update_status(green("Connected"))
    admin = False
    if player_id == 0:  # Admin detection
        wb.update("You are the administrator, press [ENTER] to start the game")
        admin = True
    playerboard = PlayerUpdate(wb, host, True)
    playerboard.start()
    if admin:
        input()
        if _send_data("start%", host) == "ok%":
            wb.update("Game started successfully")
        else:
            wb.update(red("Unauthorized")) # Should not happen with non-modded client
            _wait_for_status("start", host)
    else:
        _wait_for_status("start", host)

    wb.clear()
    wb.update(
        green("Game started\n\n")+
        "You have to compose your word with these letters\n"+
        bold(" ".join(_status(host)[5:])), 
        updatable_2="Enter your word : ",
        status=green("Playing"),
        invert=True
    )
    playerboard.invert = True

    input_method = input if not persist_data.DATA["online"]["async_input"] else Input(
        wb.update_letter).run
    if input_method is input:
        playerboard.enable = False
    else:
        wb.update_letter("Start typing your word")
    while not _send_data(input_method(), host).decode("utf-8").startswith("valid%"):
        wb.update(updatable_2='Your word is not valid', invert=True)
    playerboard.enable = False
    wb.clear()
    wb.update("Waiting for other players to finish")
    playerboard = PlayerUpdate(wb, host)
    playerboard.start()
    _wait_for_status("results", host)
    wait(0.25)  # Avoid replay spam for the last player if it has low ping
    playerboard.enable = False
    wb.updatable = ""

    result_data = json.loads(_status(host)[7:])
    wb.clear()
    wb.update(
        add="Winner(s):\n * " + "\n  * ".join([i[0] +
        " : " + i[1] for i in result_data["best"]]) +
        "\n\n Scores :\n * " + "\n  * ".join([i["name"] +
        " : " +
        i["word"]for i in result_data["players"]]),
        status=bold("Finished")
    )


def exit_server():
    global server_ip
    global wb
    print("Exiting ...", end="\r")
    socket.timeout = persist_data.DATA["online"]["update_speed"]
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect((server_ip, PORT))
        s.send(
            bytearray(f"%llm_client%{persist_data.DATA['version'].replace('.', str())}%{persist_data.DATA['online']['uuid']}%leave%", "utf-8"))
        s.close()
    except:
        pass
    finally:
        s.close()
        #wb.update_status(red("Disconnected"))
        #wb.update(updatable_2="You left the game")
        sys.exit()


if __name__ == "__main__":
    print("Cannot run from here, run main.py")
