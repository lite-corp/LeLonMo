from typing import Any, Tuple


class SettingsProvider:
    def __init__(self) -> None:
        if not self.load():
            raise RuntimeError("Could not load configuration")
        self.account_storage_providers = {}
        self.valid_tokens = dict()

    def load(self):
        return False

    def __getitem__(self, key: str) -> Any:
        return self.settings[key]

    def __getattr__(self, name: str) -> Any:
        return self.settings[name]

    # Server-related things
    def get_address(self) -> Tuple[str, int]:
        return (self.settings["server_address"], self.settings["server_port"])

    def get_port(self) -> int:
        return self.settings["server_port"]

    def register_account_storage(self, key: str, storage):
        print(f"[I] Adding <{type(storage).__name__}> as '{key}'")
        if key in self.account_storage_providers:
            raise ValueError(f"'{key}' is already used by another storage provider")
        self.account_storage_providers[key] = storage

    def get_account_provider(self):
        if not self.settings["account_storage"] in self.account_storage_providers:
            print(
                f"{self.settings['account_storage']} is not available, using default value"
            )
            self.settings["account_storage"] = "default"

        if not self.account_storage_providers[
            self.settings["account_storage"]
        ].initialized:
            # Run a function to initialise the storage the first time it is used
            self.account_storage_providers[
                self.settings["account_storage"]
            ].initialize()

        return self.account_storage_providers[self.settings["account_storage"]]

    def add_token(self, token: str, uuid: str):
        self.valid_tokens[token] = uuid

    def is_valid_token(self, token: str):
        return token in self.valid_tokens

    def get_uuid(self, token: str):
        if self.is_valid_token(token):
            return self.valid_tokens[token]
        return "\0"


class DefaultProvider(SettingsProvider):
    def load(self):
        """Loads the data from settings

        Returns:
            bool: return False if something went wrong
        """
        self.settings = {
            # Server-related settings
            "server_port": 8080,
            "server_address": "0.0.0.0",
            "log_requests": False,
            "web_path": "src/web",
            # Game-related settings
            "letter_number": 7,
            "dict_path": "src/dict/fr.txt",
            "time_inactive": 3,
            # Security-related settings
            "account_storage": "sqlite",
            "login_page": "/html/login.html",
            "authenticated_pages": ["/html/index.html"],
            "cookies_pages": ["/html/index.html", "/html/login.html"],
            "sqlite_account_storage_path": "users.sqlite3",
            "token_validator_lenght": 8,  # Set to 0 to disable
        }
        return True  # return False if something wen wrong when loading the config
