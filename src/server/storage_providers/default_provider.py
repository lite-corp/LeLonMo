import hashlib
from uuid import uuid4

from settings import SettingsProvider


class User:
    """This class is used to store user data outside of the storage provider (the database)
    and make operations on them like authentication"""

    account_provider = None

    def __init__(
        self,
        uuid: str = "",
        username: str = "",
        email: str = "",
        passwd_hash: str = "",
        token_validator: str = "",
    ):
        """Initialize a user object

        Args:
            uuid (str, optional): User ID for the stored user
            username (str, optional): Username of the stored user.
            email (str, optional): Email of the stored user.
            passwd_hash (str, optional): Password hash of the stored user.
            token_validator (str, optional): Token validator used for authentication (it's a salt).
        """
        self.uuid: str = uuid
        self.username: str = username
        self.email: str = email
        self.passwd_hash: str = passwd_hash
        self.token_validator: str = token_validator

    def set_token_validator(self, validator: str):
        """Set the salt for authentication

        Args:
            validator (str): The salt to use for authentication
        """
        self.token_validator = validator

    def is_valid_token(self, token: str) -> bool:
        """Check if the token provided by the client is valid
        It is composed of :
            - The user's username encoded as utf-8
            - The user's password hash encoded as utf-8
            - The salt used for authentication encoded as utf-8
        Returns:
            bool: True if the token is valid, False otherwise"""
        h = hashlib.sha256()
        h.update(self.username.encode("utf-8"))
        h.update(self.passwd_hash.encode("utf-8"))
        h.update(self.token_validator.encode("utf-8"))
        return token == h.hexdigest()

    def __dict__(self) -> dict:
        """Provides a dictionary representation of the user object

        Returns:
            dict: A dictionary representation of the user object
        """
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
        """Create a new user object and return it

        Args:
            username (str, optional): The username of the user. Defaults to "".
            email (str, optional): Email used for the account . Defaults to "".
            password (str, optional): The clear password. Defaults to "".

        Returns:
            User: The created user object
        """
        passwd_hash = hashlib.sha256()
        passwd_hash.update(password.encode("utf-8"))
        return User(
            User.account_provider.get_uuid(), username, email, passwd_hash.hexdigest()
        )


class DefaultAccountProvider:
    """This class provides 2 default accounts, and does not store anything permanently"""

    def __init__(self, settings: SettingsProvider):
        """Create the storage provider

        Args:
            settings (SettingsProvider): The settings provider to be used for the storage
        """
        self.settings = settings
        self.initialized = False
        settings.register_account_storage("default", self)

    def initialize(self):
        """Initialize the storage provider with accounts
        This provider only has 2 default (unsecure) accounts. These are not stored permanently
        Any account added will be deleted after the next restart of the server
        Everything is stored in memory"""
        self._data = {
            "12345678-1234-1234-1234-1234567890ab": {
                "username": "johndoe",
                "email": "john.doe@example.com",
                "passwd_hash": "ef797c8118f02dfb649607dd5d3f8c7623048c9c063d532cc95c5ed7a898a64f",  # "12345678"
            },
            "01234567-0123-0123-0123-01234567890a": {
                "username": "janedoe",
                "email": "jane.doe@example.com",
                "passwd_hash": "f2d81a260dea8a100dd517984e53c56a7523d96942a834b9cdc249bd4e8c7aa9",  # "azerty"
            },
        }

        self.initialized = True
        print("[I] Successfully initialized DefaultAccountProvider")

    def get_uuid(self) -> str:
        """Generates a unique identifier for a new user
        Can be overriden

        Returns:
            str: generated unique user id
        """
        return str(uuid4())

    def add_user(self, username: str, email: str, password: str) -> dict:
        """Save a user in the storage

        Args:
            uuid (str): Unique identifier
            username (str): unique name
            email (str): email of the user
            password (str): password for the user

        Returns:
            dict: success and message
        """
        uuid = self.get_uuid()
        p = hashlib.sha256()
        p.update(password.encode("utf-8"))

        self._data[uuid] = dict(
            username=username, email=email, passwd_hash=p.hexdigest()
        )
        return dict(success=True)

    def get_user(
        self,
        username: str = "",
        uuid: str = "",
    ) -> User:
        """Get a user from the storage"""
        if uuid:
            try:
                return self._data[uuid]
            except KeyError:
                return None
        elif username:
            for u in self._data:
                if self._data[u]["username"] == username:
                    return User(
                        uuid=u,
                        username=username,
                        email=self._data[u]["email"],
                        passwd_hash=self._data[u]["passwd_hash"],
                    )
            print("[W] Did not find user", username)
            return None
        return None

    def authenticate_user(self, username: str, token: str, validator: str):
        """Checks if the user is authenticated correctly"""
        u = self.get_user(username=username)
        if u is None:
            return False, None, "This user does not exist"
        u.set_token_validator(validator)
        return u.is_valid_token(token), u, "Your password is incorrect"

    def delete(self):
        """Delete the storage"""
        pass
