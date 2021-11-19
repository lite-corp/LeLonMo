import random


def getHex(n):
    return "".join([random.choice(list("0123456789abcdef")) for _ in range(n)])


class AccontManager:
    def __init__(self, settings):
        self.settings = settings
        self.account_storage = settings.get_account_provider()
        self.valid_tokens: list[tuple[str, str]] = []
        self.token_validator: str = getHex(8)

    def get_token_validator(self):
        return self.token_validator

    def is_authenticated(self, private_uuid, token):
        if private_uuid in self.valid_tokens:
            return self.valid_tokens[private_uuid] == token
        return False

    def handle_requests(self, private_uuid: str, data: dict):
        if data["action"] == "login":
            if self.settings.get_account_provider().authenticate_user(
                username=data["username"],
                token=data["token"],
                validator=self.token_validator,
                current_uid=private_uuid,
            ):
                return {"success": True}
            else:
                print("[W] Failed to log in user", data["username"])
                return {"success": False}
        return {"success": False, "message": "not_implemented"}
