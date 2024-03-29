from typing import Any, Tuple
import json


class SettingsProvider:
    def __init__(self) -> None:
        """Initialize the settings provider

        Raises:
            RuntimeError: If something went wrong while loading the settings into memory
        """
        self.settings: dict = {}
        self._default_settings: dict = {}
        if not self.load():
            raise RuntimeError("Could not load configuration")
        self.account_storage_providers = {}

    def load(self):
        """Load the settings from the file

        Returns:
            bool: True if the settings were loaded, False otherwise
        """
        return False

    def __getitem__(self, key: str) -> Any:
        """Returns the value of the setting with the given key
        Allows to use the settings as a dictionary

        Args:
            key (str): The key of the setting

        Returns:
            Any: The value of the requested setting
        """
        return self.settings[key]

    def __getattr__(self, name: str) -> Any:
        """Returns the value of the setting with the given name
        Allows to use the settings as a class

        Args:
            name (str): The name of the setting

        Returns:
            Any: The value of the requested setting
        """
        if name in self.settings:
            s = self.settings[name]
        else:
            DefaultProvider().load(to_temp_variable=True)
            if name in self._default_settings:
                print(
                    f"[W] Property {name} was not found in the settings, using default value"
                )
                s = self._default_settings[name]
            else:
                raise
        return s

    # Server-related things
    def get_address(self) -> Tuple[str, int]:
        """Returns the address for the server to listen on

        Returns:
            Tuple[str, int]: The address of the server
        """
        return (self.settings["server_address"], self.settings["server_port"])

    def get_port(self) -> int:
        """Returns the port for the server to listen on

        Returns:
            int: The port of the server
        """
        return self.settings["server_port"]

    def register_account_storage(self, key: str, storage: "DefaultAccountProvider"):
        """Register a storage provider for accounts

        Args:
            key (str): The key to be used to designate the storage provider
            storage (DefaultAccountProvider): The storage provider to be used

        Raises:
            RuntimeError: If the key is already in use
        """
        print(f"[I] Adding <{type(storage).__name__}> as '{key}'")
        if key in self.account_storage_providers:
            raise ValueError(f"'{key}' is already used by another storage provider")
        self.account_storage_providers[key] = storage

    def get_account_provider(self):
        """Returns the account storage provider

        Returns:
            DefaultAccountProvider: The storage provider to be used
        """
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
    def load(self, to_temp_variable=False):
        """Loads the data from settings

        Returns:
            bool: return False if something went wrong
        """
        self._default_settings = {
            # Server-related settings
            "server_port": 8080,
            "server_address": "0.0.0.0",
            "log_requests": False,
            "web_path": "src/web",
            # Game-related settings
            "letter_number": 7,
            "dict_path": "src/dict/fr.txt",
            "time_inactive": 3,
            "wait_admin_file": "wait_admin.txt",
            # Security-related settings
            "account_storage": "sqlite",
            "login_page": "/html/login.html",
            "authenticated_pages": ["/html/index.html"],
            "cookies_pages": ["/html/index.html", "/html/login.html"],
            "sqlite_account_storage_path": "users.sqlite3",
            "token_validator_length": 8,  # Set to 0 to disable token validation
            # SSL-related settings
            "ssl_enabled": False,
            "ssl_certificate": "cert.pem",
            "ssl_key": "key.pem",
        }

        if to_temp_variable:
            self.settings = self._default_settings

        return True  # return False if something wen wrong when loading the config


class JSONProvider(DefaultProvider):
    def load(self):
        super().load(to_temp_variable=True)
        try:
            with open("settings.json", "r") as f:
                self.settings = json.load(f)
            return True
        except FileNotFoundError:
            try:
                print("[W] settings.json not found, creating it ...")
                with open("settings.json", "w") as fw:
                    json.dump(self._default_settings, fw)
                return self.load()
            except:
                False
        except:
            return False
