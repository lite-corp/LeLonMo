
import json
import re
import threading
import socket

from server import letter_generator
from server import word_check


class Game():
    def __init__(self, LANGUAGE):
        self.state = 0
        print("[I] Waiting for admin ...")
        self.game_data = dict(players=list())
        self.LANGUAGE = LANGUAGE

    def _new_player(self, uuid, name, ip, status="Connected"):
        self.game_data["players"].append(
            dict(uuid=uuid, name=name, ip=ip, word="", status=status, computer_afk="false"))
        print("[I] Added player", name, "with uuid", uuid)
        return len(self.game_data["players"])-1

    def _delete_player(self, player_id: int, admin: bool):
        if not player_id==-1:
            print(f"[I] Player {self.game_data['players'][player_id]['name']} left.")
            del self.game_data["players"][player_id]
            if admin:
                try:
                    self.game_data["admin"] = self.game_data["players"][0]
                except IndexError:
                    self._reset()

    def _answer(self, msg, socket):
        socket.send(bytearray(str(msg), "utf-8"))

    def _get_player_id(self, uuid):
        for i, j in enumerate(self.game_data["players"]):
            if j["uuid"] == uuid:
                return i
        return -1

    def _get_results(self):
        result = dict(letters=self.game_data["letters"], best=[
                      ("", "")], players=list())
        for i in self.game_data["players"]:
            if len(i["word"]) > len(result["best"][0][1]):
                result["best"] = [(i["name"], i["word"])]
            elif len(i["word"]) == len(result["best"][0][1]):
                result["best"].append((i["name"], i["word"]))
        for i in self.game_data["players"]:
            result["players"].append(dict(
                name=i["name"],
                word=i["word"]
            ))
        return json.dumps(result)

    def _get_points(self):
        results = list()
        for i in self.game_data["players"]:
            if not results:
                results.append(i)
            for k, j in enumerate(results):
                if len(i["word"]) > len(j["word"]):
                    results.insert(k, i)
        for i, j in enumerate(results):
            print("j: ", json.dumps(j, indent=2))

    def _reset(self):
        self.state = 0
        print("[I] Reseting game")
        self.game_data = dict(players=list())

    def handle_data(self, data: str, client_socket, client_thread):
        r = re.search("(.{36})%(.*)", data)
        uuid = r.group(1)
        msg = r.group(2)
        try:
            admin = uuid == self.game_data["admin"]["uuid"]
        except KeyError:
            admin = True
        if msg == "players%":
            try:
                self._answer(
                    "%".join(
                        [f'{i["name"]} ({i["status"]})' for i in self.game_data["players"]]),
                    client_socket
                )
            except:
                self._answer("Nobody", client_socket)
        elif msg == "leave%":
            self._delete_player(self._get_player_id(uuid), admin)
        elif self.state == 0 and msg.startswith("join%"):
            self.state = 1
            self.game_data["admin"] = dict(
                uuid=uuid, ip=client_thread.ip, username=msg.split("%")[1])
            self._answer(self._new_player(
                uuid, msg.split("%")[1], client_thread.ip, "Admin"), client_socket)
        elif self.state == 1:
            if msg == "status%":
                self._answer("", client_socket)
            elif admin and msg == "start%":
                self.state = 2
                self.game_data["letters"] = ''.join(
                    letter_generator.generate(letter_range=(97, 122)))
                self._answer('ok%', client_socket)
                print("[I] Game started")
            elif msg == "%start":
                self._answer('unauthorized%', client_socket)
            else:
                if self._get_player_id(uuid) == -1 and msg.startswith("join%"):
                    self._answer(self._new_player(
                        uuid, msg.split("%")[1], client_thread.ip), client_socket)
        elif self.state == 2:
            if msg == "status%":
                self._answer(
                    f"start{self.game_data['letters']}", client_socket)
                if "" == self.game_data["players"][self._get_player_id(uuid)]["word"]:
                    self.game_data["players"][self._get_player_id(
                        uuid)]["status"] = "Playing"
            elif msg.startswith("join%"):
                self._answer("started", client_socket)
            elif not self._get_player_id(uuid) == -1:
                if self.game_data["players"][self._get_player_id(uuid)]["status"] != "Finished":
                    if word_check.check_dict(msg, self.LANGUAGE) and word_check.check_list(msg, self.game_data["letters"]):
                        self._answer("valid%", client_socket)
                        self.game_data["players"][self._get_player_id(
                            uuid)]["status"] = "Finished"
                        self.game_data["players"][self._get_player_id(
                            uuid)]["word"] = msg
                        print(
                            f'[I] {self.game_data["players"][self._get_player_id(uuid)]["name"]} finished')
                        all_finished = True
                        for i in self.game_data["players"]:
                            if i["status"] != "Finished":
                                all_finished = False
                                break
                        if all_finished:
                            self.state = 3
                    else:
                        self._answer("invalid", client_socket)
                else:
                    self._answer("valid%", client_socket)
            elif msg.startswith("join%"):
                self._answer("wait%", client_socket)
            else:
                self._answer("valid%", client_socket)
        elif self.state == 3:
            if msg == "status%":
                self._answer("results"+self._get_results(), client_socket)
            elif msg.startswith("join%") and admin:
                self._reset()
                self.handle_data(data, client_socket, client_thread)
            elif msg.startswith("join%"):
                self._answer("wait%", client_socket)


class ClientThread(threading.Thread):
    def __init__(self, ip, port, clientsocket, game):
        threading.Thread.__init__(self)
        self.ip = ip
        self.port = port
        self.game = game
        self.clientsocket = clientsocket

    def run(self):
        data = self.clientsocket.recv(1024)
        self.game.handle_data(data.decode("utf-8"), self.clientsocket, self)


class MainThread(threading.Thread):
    def __init__(self, port):
        threading.Thread.__init__(self)
        print("[I] Started server thread")
        self.port = port

    def run(self):
        try:
            print("[I] Server started, listening...")
            print("[V] Use portmapper for UPnP : link port 11111 to 11111. ")
            self.tcpsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.tcpsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.tcpsock.bind(("", self.port))
            game = Game("fr")
            while True:
                self.tcpsock.listen(10)
                (self.clientsocket, (ip, port)) = self.tcpsock.accept()

                newthread = ClientThread(ip, port, self.clientsocket, game)
                newthread.start()
        except OSError:
            print("[I] Exiting")
