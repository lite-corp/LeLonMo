import random


def generate_validator(n=0):
    """Generate a random string of length n"""
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
        """Destroy the storage provider before exit"""
        self.account_storage.delete()

    def add_token(self, token: str, uuid: str):
        """Save the token for the user with the given uuid for the current session"""
        self.valid_tokens[token] = uuid

    def is_valid_token(self, token: str) -> bool:
        """Check if the token provided by the client is valid

        Args:
            token (str): The token provided by the client

        Returns:
            bool: True if the token is valid, False otherwise
        """
        return token in self.valid_tokens

    def get_uuid(self, token: str) -> str:
        """Retrieve the uuid associated with the token provided by the client

        Args:
            token (str): The token provided by the client

        Returns:
            str : The uuid associated with the token if the token is valid, None otherwise
        """
        if self.is_valid_token(token):
            return self.valid_tokens[token]
        return None

    def get_token_validator(self) -> str:
        """Salt for the clients to generate a token that is session-specific

        Returns:
            str: The salt
        """
        return self.token_validator

    def handle_auth_requests(self, data: dict) -> dict:
        """This method handles the authentication requests

        Args:
            data (dict): The data provided by the client (action, and optional username, token, email, password)

        Returns:
            dict: A dictionary containing the result of the request
        """
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
            print(f"[I] Trying to log in as {data['username']}, success={valid}")
            if valid:
                self.add_token(data["token"], user.uuid)

                result = self.game.add_user(user.uuid, user.username, True)
                result["validator_token"] = self.token_validator
                return result
            else:
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
            print(f"[I] Creating user account {data['username']}, {status=}")
            if status["success"]:
                data["action"] = "login"
                self.handle_auth_requests(data)
            return status
        return {"success": False, "message": "Invalid request"}

    def handle_user_requests(self, player_uuid: str, data: dict):
        """This method handles the user requests about user metadata and settings
        Nothing is implemented yet"""
        if player_uuid is None:
            return {"success": False, "message": "Unauthenticated user"}
        return {"success": False, "message": "Invalid request"}
