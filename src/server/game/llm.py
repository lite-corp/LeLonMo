import time
import uuid
import html

import game.lib_llm

from settings import DefaultProvider
from game.chat import Chat


def getTime():
    return round(time.time())


class LeLonMo:
    def __init__(self) -> None:
        self.chat = Chat()
        self.initialize_game()

    def initialize_game(self):
        """
        self.status :
            0 : Waiting for admin
            1 : Waiting for other players
            2 : Game started
            3 : Waiting for admin to restart (game finished)
        """
        self.status = 0
        self.admin_uuid = str()
        self.letters = list()
        self.players = dict()
        self.settings = DefaultProvider()

    def add_user(self, private_uuid: str, username: str) -> dict:
        if self.status == 0:
            self.admin_uuid = private_uuid
            self.status = 1
            return self.add_user(private_uuid, username)
        elif self.status == 1:
            username = html.escape(username)
            self.players[private_uuid] = {
                "private_uuid": private_uuid,
                "public_uuid": str(uuid.uuid4())[:8],
                "username": username,
                "status": "wait_for_start",
                "last_update": getTime(),
                "kicked": False,
                "points": 0,
                "latest_word": "",
                "latest_points": "",
            }
            self.chat.add_user(
                private_uuid, self.players[private_uuid]["public_uuid"], username
            )
            print(f"[I] Added user {username}")
            return self.players[private_uuid]

    def kick_user(self, private_uuid: str) -> None:
        self.players[private_uuid]["kicked"] = True
        self.chat.remove_user(private_uuid)

    def delete_user(self, private_uuid: str) -> None:
        print("[I] Removed player", self.players[private_uuid]["username"])
        if self.is_admin(private_uuid):
            if len(self.players) == 0:
                self.initialize_game()
            else:
                self.admin_uuid = list(self.players.keys())[0]
        self.chat.remove_user(private_uuid)
        del self.players[private_uuid]

    def is_admin(self, private_uuid: str) -> bool:
        return private_uuid == self.admin_uuid

    def is_kicked(self, private_uuid: str) -> bool:
        return self.players[private_uuid]["kicked"]

    def get_users(self) -> list:
        player_list = list()
        for k in self.players:
            if not self.players[k]["kicked"]:
                player_list.append(
                    {
                        "public_uuid": self.players[k]["public_uuid"],
                        "username": self.players[k]["username"],
                        "status": self.players[k]["status"],
                        "points": self.players[k]["points"],
                        "latest_word": self.players[k]["latest_word"]
                        if self.status == 3
                        else None,
                        "admin": k == self.admin_uuid,
                    }
                )
        return player_list

    def check_timeouts(self):
        remove_players = list()
        for p in self.players:
            if (
                self.players[p]["last_update"] + self.settings["time_inactive"]
                < getTime()
            ):
                remove_players.append(p)
        for p in remove_players:
            self.delete_user(p)

    def validate_request(self, action: str) -> bool:
        if action == "join":
            return self.status == 0 or self.status == 1
        if action == "submit_word":
            return self.status == 2
        if action == "update":
            return True
        if action == "create_game":
            return self.status == 3
        if action == "start_game":
            return self.status == 1
        print("Unknown action :", action)
        return False

    def handle_updates(self, private_uuid: str, data: dict) -> dict:
        try:
            self.players[private_uuid]["last_update"] = getTime()
            if self.status == 2:
                if not self.players[private_uuid]["latest_word"]:
                    self.players[private_uuid]["status"] = "playing"
        except KeyError:
            pass
        if self.status == 2:
            game_finished = True
            for player in self.players:
                if (
                    self.players[player]["status"] != "finished"
                    and not self.players[player]["kicked"]
                ):
                    game_finished = False
            if game_finished:
                for player in self.players:
                    self.players[player]["player_status"] = "game_ended"
        self.check_timeouts()
        return {
            "success": True,
            "users": self.get_users(),
            "server_status": self.status,
            "letters": self.letters,
            "admin": private_uuid == self.admin_uuid,
            "in_game": private_uuid in self.players,
            "player_status": "not_in_game"
            if private_uuid not in self.players
            else self.players[private_uuid]["status"],
        }

    def handle_requests(self, private_uuid: str, data: dict) -> dict:

        try:
            if not self.validate_request(data["action"]):
                return {"success": False, "message": "invalid_request"}

            if data["action"] == "join":
                return self.add_user(private_uuid, data["username"])

            if data["action"] == "update":
                return self.handle_updates(private_uuid, data)

            if data["action"] == "start_game":
                if self.status == 1:
                    self.letters = game.lib_llm.generate_letters(
                        self.settings["letter_number"]
                    )
                    self.status = 2
                    print("[I] Game started")
                    return {"success": True}
                else:
                    return {"success": False, "message": "game already started"}

            if data["action"] == "submit_word":
                print(data)
                if not game.lib_llm.check_list(data["word"], self.letters):
                    return {"success": True, "valid": False}
                if not game.lib_llm.check_dict(data["word"]):
                    return {"success": True, "valid": False}
                print(f"[I] {self.players[private_uuid]['username']} finished.")
                self.players[private_uuid]["latest_word"] = data["word"]
                self.players[private_uuid]["status"] = "finished"
                return {"success": True, "valid": True}
            if data["action"] == "create_game":
                if private_uuid == self.admin_uuid:
                    self.__init__()
                    return {"success": True}
                else:
                    return {"success": False, "message": "not_admin"}

        except KeyError as e:
            raise
            field = str(e).replace("KeyError: '", "").replace("'", "")
            print(f"[E] Missing required field : " + field)
            return {
                "success": False,
                "message": "missing_field",
                "detail": "Missing field " + field,
            }

        except:
            import traceback

            traceback.print_exc()
            return {
                "success": False,
                "message": "server_error",
                "detail": traceback.format_exc(),
            }
