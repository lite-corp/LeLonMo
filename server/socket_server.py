
import json
import re
import sys
import threading
import socket
import os

from server import letter_generator, persist_data
from server import word_check

BUFFER_SIZE = 4096
class Game():
    def __init__(self, LANGUAGE, MAX_PLAYERS = 10):
        """Initialize the game
        """
        self.state = 0
        print("\r\r[I] Waiting for admin ...")
        self.game_data = dict(players=list())
        self.LANGUAGE = LANGUAGE
        self.MAX_PLAYERS = MAX_PLAYERS
        self.update_file = f'server{os.path.sep}LeLonMo_client_v{persist_data.DATA["client_version"]}.zip'
        self.scores = {}

    def _new_player(self, uuid: str, name: str, ip: str, status="Connected") -> int:
        """Add a new player to the game
        return values : 
        -5 : game full 
        -4 : duplicate username
        -3 : name contains forbidden parts
        -2 : name.isspace()
        -1 : empty name
         0 : success, player is admin
        >0 : success, player is a normal player
        """
        if len(self.game_data["players"]) > self.MAX_PLAYERS:
            print("[W]Refused", uuid, ": Too many people")
            return -5
        elif name in [i['name'] for i in self.game_data["players"]]:
            print("\r[W] Refused", uuid, "with name", name)
            return -4
        elif [0 for i in ["admin", "%", "connected", " ", "\t", "\n", "playing"] if i in name.lower()]:
            print("\r[W] Refused", uuid, "with name", name)
            return -3
        elif name.isspace():
            print("\r[V] Refused", uuid, ": isspace")
            return -2
        elif name == "":
            print("\r[V] Refused", uuid, ": Empty name")
            return -1
        else: 
            self.game_data["players"].append(
                dict(uuid=uuid, name=name, ip=ip, word="", status=status, computer_afk=False))
            print("\r[I] Added player", name, "with uuid", uuid)
            return len(self.game_data["players"])-1

    def _delete_player(self, uuid: str, admin: bool):
        """Delete a player if it exists
        Replace the admin if needed
        """
        player_id = self._get_player_id(uuid)
        if not player_id == -1:
            print(f"\r[I] Player {self.game_data['players'][player_id]['name']} left.")
            del self.game_data["players"][player_id]
            if admin:
                try:
                    self.game_data["admin"] = self.game_data["players"][0]
                except IndexError:
                    self._reset()

    def _answer(self, msg, socket):
        """Transmit data to the client
        """
        socket.send(bytearray(str(msg), "utf-8"))
        socket.close()

    def _get_player_id(self, uuid):
        "Get the player id from uuid"
        for i, j in enumerate(self.game_data["players"]):
            if j["uuid"] == uuid:
                return i
        return -1

    def _get_results(self):
        """Dump results to JSON string
        """
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
                word=i["word"],
                points=i["points"],
                total_points=self.scores[i['uuid']]
            ))
        return json.dumps(result)

    def _calculate_points(self):
        """With 5 players:
            1st has 4 points
            2nd and 3rd are equal and get 3 points
            4th gets 1 points
            5th gets 0 point

        """
        player_word_len = [(len(j["word"]), i) for i, j in enumerate(self.game_data["players"])]
        player_word_len.sort(reverse=True)

        word_len = []
        for j, i in player_word_len:
            word_len.append(j)
            self.game_data["players"][i]["points"] =\
                len(player_word_len) - word_len.index(j) - 1
            #print(f"\r[V] Gave {len(player_word_len) - word_len.index(j) - 1} to player {i}") 
            if self.game_data["players"][i]['uuid'] in self.scores.keys():
                self.scores[self.game_data["players"][i]['uuid']] += self.game_data["players"][i]["points"]
            else:
                self.scores[self.game_data["players"][i]['uuid']] = self.game_data["players"][i]["points"]

    def _reset(self):
        """Restart the game
        Does not reset points
        """
        self.state = 0
        print("\r[I] Reseting game")
        self.game_data = dict(players=list())

    def handle_data(self, data: str, client_socket, client_thread):
        """Main function of the game
        data : data received from the client in the format
            "%llm_client%version%uid%message
        """
        try:
            r = re.search("%llm_client%(.{4})%(.{36})%(.*)", data)
            version = r.group(1)
            uuid = r.group(2)
            msg = r.group(3)
            if not msg:
                print("\r[W] Empty message from", uuid)
        except:
            print("\r[W] Invalid request :", data)
            return data, client_socket, client_socket
        
        # Allow updates
        try:
            if not msg in ['size%', 'latest_file%']:
                if int(version) < int(persist_data.DATA["client_version"]) and os.path.exists(self.update_file):
                    self._answer("outdated%update", client_socket)
                    return
                elif int(version) < int(persist_data.DATA["client_version"]):
                    self._answer("outdated%", client_socket)
                    return
        except:
            self._answer("outdated%", client_socket)
            return
        
        
        try:
            admin = uuid == self.game_data["admin"]["uuid"]
        except KeyError:
            admin = True
        if msg == "players%":
            try:
                self._answer(json.dumps(
                    [dict(name=i['name'], status=i['status']) for i in self.game_data["players"]]
                ),client_socket)
            except:
                self._answer("Nobody", client_socket)
        elif msg == "leave%":
            self._delete_player(uuid, admin)
        
        # Update sending part
        elif msg == "latest_file%":
            try:
                print("\r[I] Uploading update")
                f = open(self.update_file,'rb')
                l = f.read(BUFFER_SIZE)
                while (l):
                   client_socket.send(l)
                   l = f.read(BUFFER_SIZE)
                f.close()
                client_socket.close()
                print("\r[I] Update done")
            except Exception as e:
                print("\r[E] Error while sending update :", e)
        elif msg == "size%":
            try:
                f = open(self.update_file,'rb')
                self._answer(len(f.read()), client_socket)
                f.close()
            except Exception as e:
                print("\r[E] Error while calculating update :", e)
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
                print("\r[I] Game started")
            elif msg == "%start":
                self._answer('unauthorized%', client_socket)
            else:
                if self._get_player_id(uuid) == -1 and msg.startswith("join%"):
                    self._answer(self._new_player(uuid, msg.split("%")[1], client_thread.ip), client_socket)
        elif self.state == 2:
            if msg == "status%":
                self._answer(f"start{self.game_data['letters']}", client_socket)
                if "" == self.game_data["players"][self._get_player_id(uuid)]["word"]:
                    self.game_data["players"][self._get_player_id(uuid)]["status"] = "Playing"
            elif msg.startswith("join%"):
                self._answer("started", client_socket)
            elif not self._get_player_id(uuid) == -1:
                if self.game_data["players"][self._get_player_id(uuid)]["status"] != "Finished":
                    if word_check.check_dict(msg, self.LANGUAGE) and word_check.check_list(msg, self.game_data["letters"]):
                        self._answer("valid%", client_socket)
                        self.game_data["players"][self._get_player_id(uuid)]["status"] = "Finished"
                        self.game_data["players"][self._get_player_id(uuid)]["word"] = msg
                        print(f'\r[I] {self.game_data["players"][self._get_player_id(uuid)]["name"]} finished')
                        all_finished = True
                        for i in self.game_data["players"]:
                            if i["status"] != "Finished" and not i["computer_afk"]:
                                all_finished = False
                                break
                        if all_finished:
                            self.state = 3
                            self._calculate_points()
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
        return


class ClientThread(threading.Thread):
    def __init__(self, ip, port, clientsocket, game):
        threading.Thread.__init__(self)
        self.ip = ip
        self.port = port
        self.game = game
        self.clientsocket = clientsocket

    def run(self):
        data = self.clientsocket.recv(BUFFER_SIZE).decode("utf-8")
        if data.startswith("%llm_client%"):
            self.game.handle_data(data, self.clientsocket, self)
        else:
            self.game._answer("outdated%", self.clientsocket)


class MainThread(threading.Thread):
    def __init__(self, port):
        threading.Thread.__init__(self)
        print("\r[I] Started server thread")
        self.port = port
        self.update = False
        self.enabled = True
        self.game = None

    def run(self):
        try:
            print("\r[I] Server started, listening...")
            #print("\r[V] Use portmapper for UPnP : link port 11111 to 11111. ")
            self.tcpsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.tcpsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.tcpsock.bind(("", self.port))
            self.game = Game("fr")
            while self.enabled:
                self.tcpsock.listen(10)
                (self.clientsocket, (ip, port)) = self.tcpsock.accept()
                newthread = ClientThread(ip, port, self.clientsocket, self.game)
                newthread.start()
        except OSError:
            print("\r[I] Exiting")
