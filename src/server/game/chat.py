import html


class Chat:
    def __init__(self) -> None:
        self.userlist = dict()
        self.messagelist = list()

    def add_user(self, private_uuid: str, public_uuid, username):
        self.userlist[private_uuid] = {
            "priv_uuid": private_uuid,
            "pub_uuid": public_uuid,
            "username": username,
            "last_read": 0,
        }
        print(f"[I] Added user {username}")
        self.send_message(private_uuid, "joined the game")

    def remove_user(self, private_uuid: str):
        self.send_message(private_uuid, "left the game")
        del self.userlist[private_uuid]

    def get_messages(self, private_uuid: str):
        if private_uuid in self.userlist:
            messages = self.messagelist[
                self.userlist[private_uuid]["last_read"] : len(self.messagelist)
            ]
            self.userlist[private_uuid]["last_read"] = len(self.messagelist)
            return messages

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
                self.send_message(private_uuid, data["content"])
                return {"success": True}
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
