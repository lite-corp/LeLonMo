import random


def getHex(n):
    return "".join([random.choice(list("0123456789abcdef")) for _ in range(n)])


class AccontManager:
    def __init__(self, settings, game):
        self.settings = settings
        self.game = game
        self.account_storage = settings.get_account_provider()
        self.valid_tokens: list[tuple[str, str]] = []
        self.token_validator: str = getHex(8)

    def get_token_validator(self):
        return self.token_validator

    def handle_requests(self, data: dict):
        if data["action"] == "login":
            valid, user = self.settings.get_account_provider().authenticate_user(
                username=data["username"],
                token=data["token"],
                validator=self.token_validator,
            )
            if valid:
                self.settings.add_token(data["token"], user.uuid)
                self.game.add_user(user.uuid, user.username, True)
                return {"success": True}
            else:
                print("[W] Failed to log in user", data["username"])
                return {"success": False}
        elif data["action"] == "signin":
            status = self.settings.get_account_provider().add_user(
                username=data["username"],
                email=data["email"],
                password=data["password"],
            )
            if status["success"]:
                data["action"] = "login"
                self.handle_requests(data)

            return status
        return {"success": False, "message": "not_implemented"}
