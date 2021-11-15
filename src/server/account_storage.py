import hashlib
from uuid import uuid4

from settings import SettingsProvider


class User:
    account_provider = None

    def __init__(
        self,
        uuid: str = "",
        username: str = "",
        email: str = "",
        passwd_hash: str = "",
        current_uid: str = "",
    ):
        self.uuid = uuid
        self.username = username
        self.email = email
        self.passwd_hash = passwd_hash
        self.current_uid = current_uid

    def is_valid_token(self, token: str, current_uid) -> bool:
        h = hashlib.sha256()
        h.update(self.username.encode("utf-8"))
        h.update(current_uid.encode("utf-8"))
        h.update(self.passwd_hash.encode("utf-8"))
        return token == h.hexdigest()

    def __dict__(self) -> dict:
        return {
            "username": self.username,
            "email": self.email,
            "passwd_hash": self.passwd_hash,
        }

    @staticmethod
    def create(
        username: str = "",
        email: str = "",
        password: str = "",
    ):
        passwd_hash = hashlib.sha256()
        passwd_hash.update(password.encode("utf-8"))
        return User(
            User.account_provider.get_uuid(), username, email, passwd_hash.hexdigest()
        )


class DefaultAccountProvider:
    """This class provides 2 default accounts, and does not store anything permanently"""

    def __init__(self, settings: SettingsProvider):
        self.settings = settings
        self.initialized = False
        settings.register_account_storage("default", self)

    def initialize(self):
        self._data = {
            "12345678-1234-1234-1234-1234567890ab": {
                "username": "johndoe",
                "email": "john.doe@example.com",
                "passwd_hash": "7c222fb2927d828af22f592134e8932480637c0d",  # "12345678"
            },
            "01234567-0123-0123-0123-01234567890a": {
                "username": "janedoe",
                "email": "jane.doe@example.com",
                "passwd_hash": "9cf95dacd226dcf43da376cdb6cbba7035218921",  # "azerty"
            },
        }
        User.account_provider = self

        self.initialized = True
        print("[I] Successfully initialized DefaultAccountProvider")

    def get_uuid(self) -> str:
        """Generates a unique identifier for a new user
        Can be overriden

        Returns:
            str: generated unique user id
        """
        return uuid4()

    def add_user(self, user: User) -> bool:
        """Save a user in the storage

        Args:
            user (User): The user to be saved

        Returns:
            bool: Return True if success
        """
        if not user.uuid in self._data:
            self._data[user.uuid] = dict(user)
            return True
        else:
            return False


def register_storages(settings):
    print("[I] Registering account storage providers")
    for c in [
        DefaultAccountProvider,
        # Add storage providers
    ]:
        try:
            c(settings)
        except Exception as e:
            print("[E] Failed to register", c.__name__, ":", type(e).__name__)
