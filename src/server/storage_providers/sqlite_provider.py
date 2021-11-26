import hashlib
import sqlite3

from settings import SettingsProvider
from __version__ import __version__

from .default_provider import DefaultAccountProvider, User


class SQLiteAccountProvider(DefaultAccountProvider):
    def __init__(self, settings: SettingsProvider):
        self.settings = settings
        self.initialized = False
        settings.register_account_storage("sqlite", self)

    def initialize(self):

        self._database = sqlite3.connect(
            self.settings.sqlite_account_storage_path, check_same_thread=False
        )
        self._cursor = self._database.cursor()
        while self._get_database_version() < __version__:
            print(
                f"[D] Database version is {self._get_database_version()}, upgrading to",
                end=" ",
            )
            self._upgrade_database()
            print(self._get_database_version())

        self._database.commit()
        self.initialized = True
        print(
            f"[I] SQLite account storage initialized, database version is {self._get_database_version()}"
        )

    def _get_database_version(self):
        try:
            self._cursor.execute("""SELECT version FROM DatabaseInfo""")
            v = self._cursor.fetchone()[0]
        except sqlite3.OperationalError:
            v = 0
        return v

    def _set_database_version(self, version):
        self._cursor.execute("DELETE FROM DatabaseInfo;")
        self._cursor.execute(
            "INSERT INTO DatabaseInfo(version) VALUES (?);", (str(version),)
        )
        self._database.commit()

    def _upgrade_database(self):
        if self._get_database_version() < 210:

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
            self._cursor.execute(
                "CREATE TABLE IF NOT EXISTS DatabaseInfo(version INTEGER NOT NULL);"
            )
            self._set_database_version(210)
        elif self._get_database_version() < 211:
            self._cursor.execute(
                """
                CREATE TABLE UserMeta(
                    uuid CHAR(36) REFERENCES User PRIMARY KEY NOT NULL,
                    profile_image BLOB
                );
                """
            )
            self._set_database_version(211)
        else:
            self._set_database_version(__version__)

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
                (uuid,),
            )
            if (userdata := self._cursor.fetchone()) is not None:
                uuid, username, email, passwd_hash = userdata
                return User(uuid, username, email, passwd_hash)
        elif username:
            self._cursor.execute(
                """
                SELECT uuid, username, email, passwd_hash FROM Users
                WHERE username = ?;
                """,
                (username,),
            )
            if (userdata := self._cursor.fetchone()) is not None:
                uuid, username, email, passwd_hash = userdata
                return User(uuid, username, email, passwd_hash)
        return None

    def delete(self):
        print("[I] Closing database")
        self._database.commit()
        self._database.close()
