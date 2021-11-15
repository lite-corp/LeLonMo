from typing import Any, Tuple


class SettingsProvider:
    def __init__(self) -> None:
        if not self.load():
            raise RuntimeError("Could not load configuration")
        self.account_storage_providers = {}

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


class DefaultProvider(SettingsProvider):
    def load(self):
        self.settings = {
            "server_port": 8080,
            "server_address": "0.0.0.0",
            "web_path": "src/web",
            "letter_number": 7,
            "dict_path": "src/dict/fr.txt",
            "time_inactive": 3,
            "log_requests": False,
            "account_storage": "default",
        }
        return True  # return False if something wen wrong when loading the config
