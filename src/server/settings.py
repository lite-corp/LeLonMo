from typing import Any, Tuple


class SettingsProvider:
    def __init__(self) -> None:
        if not self.load():
            raise RuntimeError("Could not load configuration")

    def load(self):
        return False

    def __getitem__(self, key: str) -> Any:
        return self.settings[key]

    # Server-related things
    def get_address(self) -> Tuple[str, int]:
        return (self.settings["server_address"], self.settings["server_port"])

    def get_port(self) -> int:
        return self.settings["server_port"]


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
        }
        return True  # return False if something wen wrong when loading the config
