import html
import __version__


class Chat:
    def __init__(self) -> None:
        self.userlist = dict()
        self.messagelist = []

    def add_user(
        self, private_uuid: str, public_uuid: str, username: str, log: bool = True
    ):
        if private_uuid not in self.userlist:
            self.userlist[private_uuid] = {
                "priv_uuid": private_uuid,
                "pub_uuid": public_uuid,
                "username": username,
                "last_read": 0,
            }
            if log:
                print(f"[I] Added user {username}")
                self.send_message(private_uuid, "joined the game")
        else:
            self.userlist[private_uuid]["username"] = username

    def remove_user(self, private_uuid: str):
        self.send_message(private_uuid, "left the game")
        del self.userlist[private_uuid]

        if not self.userlist:  # No player online
            self.messagelist = []

    def get_messages(self, private_uuid: str):
        if private_uuid in self.userlist:
            messages = self.messagelist[
                self.userlist[private_uuid]["last_read"] : len(self.messagelist)
            ]
            self.userlist[private_uuid]["last_read"] = len(self.messagelist)
            return messages

    def has_unread(self, private_uuid: str):
        if private_uuid in self.userlist:
            return self.userlist[private_uuid]["last_read"] != len(self.messagelist)
        return False

    def send_message(self, private_uuid: str, message: str):
        if message.startswith("[html]"):
            message = message[6:]
        else:
            message = html.escape(message)
        if message.isspace():
            return
        self.messagelist.append(
            {
                "text": message,
                "username": self.userlist[private_uuid]["username"],
                "uuid": self.userlist[private_uuid]["pub_uuid"],
            }
        )
        print(
            html.unescape(f'[I] <{self.userlist[private_uuid]["username"]}> {message}')
        )

    def get_users(self):
        users = list()
        for user in self.userlist:
            users.append(
                {
                    "uuid": self.userlist[user]("pub_uuid"),
                    "username": self.userlist[user]["username"],
                }
            )
        return users

    def handle_requests(self, private_uuid: str, data):
        try:
            if data["action"] == "get_msg":
                return {"success": True, "messages": self.get_messages(private_uuid)}
            elif data["action"] == "send_msg":
                try:
                    self.send_message(private_uuid, data["content"])
                    return {"success": True}
                except KeyError:
                    print("[W] An unregistered player tried to send a message")
            else:
                raise ValueError("Wrong action")
        except KeyError as e:
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
