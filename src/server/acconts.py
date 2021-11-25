import random


def generate_validator(n=0):
    if n:
        return "".join(
            [
                random.choice(list("0123456789abcdefghijklmnopqrstuvwxyz"))
                for _ in range(n)
            ]
        )
    else:
        return "0"


class AccontManager:
    def __init__(self, settings, game):
        self.settings = settings
        self.game = game
        self.account_storage = settings.get_account_provider()
        self.valid_tokens: dict = {}
        self.token_validator: str = generate_validator(settings.token_validator_lenght)

    def delete(self):
        self.account_storage.delete()

    def add_token(self, token: str, uuid: str):
        self.valid_tokens[token] = uuid

    def is_valid_token(self, token: str):
        return token in self.valid_tokens

    def get_uuid(self, token: str):
        if self.is_valid_token(token):
            return self.valid_tokens[token]
        return None

    def get_token_validator(self):
        return self.token_validator

    def handle_auth_requests(self, data: dict):
        if data["action"] == "login":
            (
                valid,
                user,
                message,
            ) = self.settings.get_account_provider().authenticate_user(
                username=data["username"],
                token=data["token"],
                validator=self.token_validator,
            )
            if valid:
                self.add_token(data["token"], user.uuid)
                self.game.add_user(user.uuid, user.username, True)
                return {"success": True}
            else:
                print("[W] Failed to log in user", data["username"])
                return {
                    "success": False,
                    "validator_token": self.token_validator,
                    "message": message,
                }
        elif data["action"] == "signin":
            status = self.settings.get_account_provider().add_user(
                username=data["username"],
                email=data["email"],
                password=data["password"],
            )
            if status["success"]:
                data["action"] = "login"
                self.handle_auth_requests(data)
            return status
        return {"success": False, "message": "Invalid request"}

    def handle_user_requests(self, player_uuid: str, data: dict):
        if player_uuid is None:
            return {"success": False, "message": "Unauthenticated user"}
        return {"success": False, "message": "Invalid request"}
