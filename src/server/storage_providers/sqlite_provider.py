import hashlib
import sqlite3
import re

from settings import SettingsProvider
from __version__ import __version__

from .default_provider import DefaultAccountProvider, User


class SQLiteAccountProvider(DefaultAccountProvider):
    def __init__(self, settings: SettingsProvider):
        """Create the storage provider

        Args:
            settings (SettingsProvider): The settings provider to be used for the storage
        """
        self.settings = settings
        self.initialized = False
        settings.register_account_storage("sqlite", self)

    def initialize(self):
        """Initialize the storage provider"""
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
        """Get the database version"""
        try:
            self._cursor.execute("""SELECT version FROM DatabaseInfo""")
            v = self._cursor.fetchone()[0]
        except sqlite3.OperationalError:
            v = 0
        return v

    def _set_database_version(self, version):
        """Set the database version

        Args:
            version (int): The version to set
        """
        self._cursor.execute("DELETE FROM DatabaseInfo;")
        self._cursor.execute(
            "INSERT INTO DatabaseInfo(version) VALUES (?);", (str(version),)
        )
        self._database.commit()

    def _upgrade_database(self):
        """Upgrade the database to the current program version version"""
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
        elif self._get_database_version() < 213:
            # Add all users to metadata db
            self._cursor.execute("SELECT uuid FROM Users;")
            for uuid in self._cursor.fetchall():
                uuid = uuid[0]
                self._cursor.execute("INSERT INTO UserMeta(uuid) VALUES (?);", (uuid,))
            self._set_database_version(213)
        else:
            self._set_database_version(__version__)

    def add_user(self, username: str, email: str, password: str) -> bool:
        """Add a user to the database"""
        if len(password) < 4:
            return dict(success=False, message="Password too short")
        if len(username) < 4:
            return dict(success=False, message="Username too short")
        if re.match(r"^[a-zA-Z0-9_]*$", username) is None:
            return dict(success=False, message="Username contains invalid characters")
        p = hashlib.sha256()
        p.update(password.encode("utf-8"))
        try:
            uuid = self.get_uuid()
            self._cursor.execute(
                """
                INSERT INTO Users(uuid, username, email, passwd_hash) VALUES (?, ?, ?, ?);
                """,
                (uuid, username, email, p.hexdigest()),
            )
            # Add users to metadata table
            self._cursor.execute(
                """
                INSERT INTO UserMeta(uuid) VALUES (?);
                """,
                (uuid,),
            )
            self._database.commit()
            return dict(success=True)
        except sqlite3.IntegrityError:
            return dict(success=False, message="This username already exists")

    def get_user(self, username: str = "", uuid: str = "") -> User:
        """Get a user from the database"""
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
        """Close the database"""
        print("[I] Closing database")
        self._database.commit()
        self._database.close()
