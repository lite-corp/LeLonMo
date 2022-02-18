import time
import uuid
import html

import game.lib_llm as lib_llm
from .chat import Chat


def getTime():
    return round(time.time())


class LeLonMo:
    def __init__(self, settings) -> None:
        self.chat = Chat()
        self.players = {}
        self.admin_uuid = ""
        self.settings = settings
        self.initialize_game()

    def initialize_game(self):
        """
        self.status :
            0 : Waiting for admin
            1 : Waiting for other players
            2 : Game started
            3 : Waiting for admin to restart (game finished)
        """
        if self.admin_uuid and self.players[self.admin_uuid]["banned"]:
            self.admin_uuid = ""
        self.status = 1 if self.admin_uuid else 0
        self.letters = list()
        for p in self.players:
            self.players[p]["latest_word"] = ""
            self.players[p]["status"] = "wait_for_start"
        print("[I] Game initialized")

    def add_user(
        self, player_uuid: str, username: str, log_in_chat: bool = True
    ) -> dict:
        if self.status == 0:
            self.admin_uuid = player_uuid
            self.status = 1
            return self.add_user(player_uuid, username)  # Add the admin
        elif self.status in [1, 3]:
            username = html.escape(username)
            self.players[player_uuid] = {
                "player_uuid": player_uuid,
                "public_uuid": str(uuid.uuid4())[:8],
                "username": username,
                "status": "wait_for_start",
                "last_update": getTime(),
                "banned": (
                    (player_uuid in self.players)
                    and self.players[player_uuid]["banned"]
                ),
                "points": 0,
                "latest_word": "",
                "latest_points": 0,
            }
            self.chat.add_user(
                player_uuid,
                self.players[player_uuid]["public_uuid"],
                username,
                log_in_chat,
            )
            return {
                "success": True,  # Easily tell JS that everything is ok
                **self.players[player_uuid],
            }

    def ban_user(self, player_uuid: str) -> None:
        self.players[player_uuid]["banned"] = True
        self.players[player_uuid]["status"] = "banned"

        self.chat.remove_user(player_uuid)

    def delete_user(self, player_uuid: str) -> None:
        print("[I] Removed player", self.players[player_uuid]["username"])
        if self.is_admin(player_uuid):
            if len(self.players) == 1:
                self.admin_uuid = ""
                self.initialize_game()
            else:

                self.admin_uuid = list(self.players.keys())[
                    1 if self.admin_uuid == list(self.players.keys())[0] else 0
                ]
                if self.players[self.admin_uuid]["banned"]:
                    self.admin_uuid = ""
                    self.initialize_game()
                print(
                    f'[I] The admin is now {self.players[self.admin_uuid]["username"]}'
                )
        try:
            self.chat.remove_user(player_uuid)
        except KeyError:
            pass
        del self.players[player_uuid]

    def is_admin(self, player_uuid: str) -> bool:
        return player_uuid == self.admin_uuid

    def is_banned(self, player_uuid: str) -> bool:
        return self.players[player_uuid]["banned"]

    def get_users(self) -> list:
        player_list = list()
        for k in self.players:
            if not self.players[k]["banned"]:
                player_list.append(
                    {
                        "public_uuid": self.players[k]["public_uuid"],
                        "username": self.players[k]["username"],
                        "status": self.players[k]["status"],
                        "points": self.players[k]["points"],
                        "latest_points": self.players[k]["latest_points"],
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
                self.players[p]["last_update"] + self.settings.time_inactive < getTime()
                and not self.players[p]["banned"]
            ):
                remove_players.append(p)
        for p in remove_players:
            self.delete_user(p)

    def validate_request(self, action: str) -> bool:
        if action == "submit_word":
            return self.status == 2, "cannot_submit_word"
        if action == "update":
            return True, "FATAL_ERROR"
        if action == "reset_game":
            return self.status in [2, 3], "game_not_started"
        if action == "create_game":
            return self.status == 3, "client_out_of_sync"
        if action == "start_game":
            return self.status in [1, 3], "client_out_of_sync"
        if action == "ban_player":
            return True, "FATAL_ERROR"
        print("[W] Unknown action :", action)
        return False, "unknown_action"

    def give_points(self):
        """
        With 5 players:
            1st gets 4 points
            2nd and 3rd are equal and get 3 points
            4th gets 1 points
            5th gets 0 point
        """
        wordlen_player = [
            (len(p["latest_word"]), p["player_uuid"])
            for p in self.players.values()
            if not p["banned"]
        ]
        wordlen_player.sort()

        scores = list()
        for s, u in wordlen_player:
            scores.append(s)
        scores.reverse()

        for s, u in wordlen_player:
            self.players[u]["latest_points"] = len(scores) - scores.index(s) - 1
            self.players[u]["points"] = (
                self.players[u]["points"] + self.players[u]["latest_points"]
            )

    def handle_updates(self, player_uuid: str, data: dict) -> dict:
        try:
            self.players[player_uuid]["last_update"] = getTime()
            if self.status == 2:
                if not self.players[player_uuid]["latest_word"]:
                    self.players[player_uuid]["status"] = "playing"
        except KeyError:
            pass
        self.check_timeouts()
        if self.status == 2:
            game_finished = True
            for player in self.players:
                if (
                    self.players[player]["status"] != "finished"
                    and not self.players[player]["banned"]
                ):
                    game_finished = False
            if game_finished:
                self.status = 3
                for player in self.players:
                    self.players[player]["status"] = "game_ended"
                self.give_points()
        for player in self.players:
            if self.players[player]["banned"]:
                self.players[player]["status"] = "banned"
        return {
            "success": True,
            "users": self.get_users(),
            "server_status": self.status,
            "letters": self.letters,
            "admin": player_uuid == self.admin_uuid,
            "in_game": player_uuid in self.players,
            "player_status": "not_in_game"
            if player_uuid not in self.players
            else self.players[player_uuid]["status"],
            "should_update_messages": self.chat.has_unread(player_uuid),
            "self": self.players[player_uuid] if player_uuid in self.players else {},
        }

    def handle_requests(self, player_uuid: str, data: dict) -> dict:

        try:
            if not (d := self.validate_request(data["action"]))[0]:
                if d == False:
                    return {
                        "success": False,
                        "message": "invalid_request",
                    }
                elif isinstance(d, tuple):
                    return {
                        "success": False,
                        "message": d[1],
                    }
            if data["action"] == "update":
                return self.handle_updates(player_uuid, data)

            if data["action"] == "start_game":
                if player_uuid == self.admin_uuid:
                    self.letters = lib_llm.generate_letters(
                        self.settings.letter_number
                    )
                    self.status = 2
                    print("[I] Game started")
                    return {"success": True}

            if data["action"] == "submit_word":
                if not lib_llm.check_list(data["word"], self.letters):
                    return {"success": True, "valid": False}
                if not lib_llm.check_dict(data["word"]):
                    return {"success": True, "valid": False}
                print(f"[I] {self.players[player_uuid]['username']} finished.")
                self.players[player_uuid]["latest_word"] = data["word"]
                self.players[player_uuid]["status"] = "finished"
                return {"success": True, "valid": True}
            if data["action"] == "create_game":
                if player_uuid == self.admin_uuid:
                    self.initialize_game()
                    return {"success": True}
                else:
                    return {
                        "success": False,
                        "message": "not_admin",
                    }
            if data["action"] == "reset_game":
                if player_uuid == self.admin_uuid:
                    self.initialize_game()
                    return {"success": True}
                else:
                    return {
                        "success": False,
                        "message": "not_admin",
                    }
            if data["action"] == "ban_player":
                if player_uuid == self.admin_uuid:
                    if (
                        lib_llm.pub_to_player_uuid(
                            data["public_uuid"], self.players
                        )
                        == self.admin_uuid
                    ):
                        return {"success": False, "message": "ban_admin"}
                    else:
                        self.ban_user(
                            lib_llm.pub_to_player_uuid(
                                data["public_uuid"], self.players
                            )
                        )
                        return {"success": True}
                else:
                    return {
                        "success": False,
                        "message": "not_admin",
                    }

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
