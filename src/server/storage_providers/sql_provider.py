import hashlib
import sqlite3

from settings import SettingsProvider

from .default_provider import DefaultAccountProvider, User


class SQLiteAccountProvider(DefaultAccountProvider):
    def __init__(self, settings: SettingsProvider):
        self.settings = settings
        self.initialized = False
        settings.register_account_storage("sqlite", self)

    def initialize(self):

        self._database = sqlite3.connect(self.settings.sqlite_account_storage_path, check_same_thread=False)
        self._cursor = self._database.cursor()
        self._cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS Users(
                uuid CHAR(36) PRIMARY KEY NOT NULL, 
                username VARCHAR(32) UNIQUE NOT NULL,
                passwd_hash CHAR(32) NOT NULL,
                email TEXT
                );
            """
        )
        self._database.commit()
        self.initialized = True
        print("[I] SQLite account storage initialized")

    def add_user(self, username: str, email: str, password: str) -> bool:
        if len(password) < 4:
            return dict(success=False, message="Password too short")
        p = hashlib.sha256()
        p.update(password.encode("utf-8"))
        try:
            self._cursor.execute(
                """
                INSERT INTO Users(uuid, username, email, passwd_hash) VALUES (?, ?, ?, ?);
                """,
                (self.get_uuid(), username, email, p.hexdigest()),
            )
        except sqlite3.IntegrityError:
            return dict(success=False, message="This username already exists")
        self._database.commit()
        return dict(success=True)

    def get_user(self, username: str = "", uuid: str = "") -> User:
        if uuid:
            self._cursor.execute(
                """
                SELECT uuid, username, email, passwd_hash FROM Users
                WHERE uuid=?;
                """,
                (uuid,)
            )
            if (userdata := self._cursor.fetchone()) is not None:
                uuid, username, email, passwd_hash = userdata
                return User(uuid, username, email, passwd_hash)
            else:
                return User()
        elif username:
            self._cursor.execute(
                """
                SELECT uuid, username, email, passwd_hash FROM Users
                WHERE username = ?;
                """,
                (username,)
            )
            if (userdata := self._cursor.fetchone()) is not None:
                uuid, username, email, passwd_hash = userdata
                return User(uuid, username, email, passwd_hash)
            else:
                return User()

    def delete(self):
        print("[I] Closing database")
        self._database.commit()
        self._database.close()
