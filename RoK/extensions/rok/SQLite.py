import sqlite3
import os
from data_manager import bot_dir


class Db:
    def __init__(self):
        self.db_path = os.path.join(bot_dir, "data", "rok.sqlite3")
        self.connection = sqlite3.connect(self.db_path)
        self.connection.row_factory = (
            sqlite3.Row
        )  # Enable named column access in query results
        self.cursor = self.connection.cursor()

    def get_gov_user(self, user_discord_id: int, stats: str) -> dict:
        id_table = "basic_top_600" if stats == "general" else "kvk_top_600"

        # Fetch the row corresponding to the author_id
        self.cursor.execute(
            'SELECT * FROM accounts WHERE "Discord ID" = ?', (user_discord_id,)
        )
        row = self.cursor.fetchone()

        if row is None:
            return None

        # Collect IDs and their associated nicknames
        gov_user_dict = {}
        gov_id_columns = ["Governer ID", "ALT ID", "FARM ID"]
        types = ["main", "alt", "farm"]

        for idx, gov_id_col in enumerate(gov_id_columns):
            gov_id = row[gov_id_col]
            if gov_id:
                self.cursor.execute(
                    f'SELECT "Governor Name" FROM {id_table} WHERE "Governor ID" = ?',
                    (gov_id,),
                )
                nickname_row = self.cursor.fetchone()
                if nickname_row:
                    gov_user_dict[types[idx]] = {
                        "name": nickname_row["Governor Name"],
                        "id": gov_id,
                    }

        return gov_user_dict

    def get_kvk_stats(self, gov_id: int, stats: str) -> dict:
        """
        Get KvK stats for a player with the given governor ID.

        Args:
            gov_id (int): Governor ID.
            stats (str): Type of stats to retrieve ("general" or "specific").

        Returns:
            dict: Dictionary containing the player's stats.
        """
        id_table = "basic_top_600" if stats == "general" else "kvk_top_600"

        # Fetch the player's stats from the database
        self.cursor.execute(
            f'SELECT * FROM {id_table} WHERE "Governor ID" = ?', (gov_id,)
        )
        row = self.cursor.fetchone()
        if row is None:
            return None

        # Convert the row to a dictionary
        return dict(row)

    def get_discord_id(self, discord_id: int, governor_id: int, stats: str) -> str:
        """
        Get the Discord username associated with a governor ID.

        Args:
            discord_id (int): Discord user ID.
            governor_id (int): Governor ID.
            stats (str): Indicates which table to use ('general' or other).

        Returns:
            str: Discord username if found, or None.
        """
        cursor = self.connection.cursor()

        gov_id_str = str(governor_id)
        id_table = "basic_top_600" if stats == "general" else "kvk_top_600"

        # Ensure the column name is correctly referenced without extra quotes
        cursor.execute(
            f'SELECT "Governor Name" FROM {id_table} WHERE "Governor ID" = ?',
            (gov_id_str,),
        )
        row = cursor.fetchone()["Governor Name"]
        cursor.close()
        return row

    def get_discord_from_id(self, gov_id: int) -> int | None:
        """
        Get Discord ID associated with a governor ID.

        Args:
            gov_id (int): Governor ID.

        Returns:
            int: Corresponding Discord ID or None if not found.
        """
        self.cursor.execute(
            "SELECT 'Discord ID' FROM accounts WHERE 'Governer ID' = ?", (str(gov_id),)
        )
        row = self.cursor.fetchone()
        if row:
            return int(row["Discord ID"])
        return None

    def get_id_from_discord(self, author_id: int) -> int | None:
        """
        Get governor ID associated with a Discord ID.

        Args:
            author_id (int): Discord user ID.

        Returns:
            int: Corresponding governor ID or None if not found.
        """
        self.cursor.execute(
            "SELECT 'Governer ID' FROM accounts WHERE 'Discord ID' = ?",
            (str(author_id),),
        )
        row = self.cursor.fetchone()
        if row and row["Governer ID"]:
            return int(row["Governer ID"])
        return None

    def save_id(
        self, author_id: int, author_name: str, governor_id: int, acctype: str
    ) -> None:
        """
        Save or update a governor ID association for a given Discord user ID.

        Args:
            author_id (int): Discord user ID.
            author_name (str): Discord username
            governor_id (int): Governor ID.
            acctype (str): Account type ('main', 'alt', or 'farm').
        """
        author_id_str = str(author_id)
        gov_id_str = str(governor_id)
        column = None

        if acctype == "main":
            column = "Governer ID"
        elif acctype == "alt":
            column = "ALT ID"
        elif acctype == "farm":
            column = "FARM ID"

        if column:
            # Check if the Discord ID already exists
            self.cursor.execute(
                'SELECT * FROM accounts WHERE "Discord ID" = ?', (author_id,)
            )
            row = self.cursor.fetchone()
            if row:
                # Update the existing row
                self.cursor.execute(
                    f"UPDATE accounts SET '{column}' = ? WHERE 'Discord ID' = ?",
                    (gov_id_str, author_id_str),
                )
            else:
                # Insert a new row
                self.cursor.execute(
                    f"INSERT INTO accounts ('Discord ID', '{column}', 'Discord Username') VALUES (?, ?, ?)",
                    (
                        author_id_str,
                        gov_id_str,
                        author_name,
                    ),
                )
            self.connection.commit()

    def remove_id(self, author_id: int, acctype: str) -> None:
        """
        Remove a governor ID associated with a Discord user ID and account type.

        Args:
            author_id (int): Discord user ID.
            acctype (str): Account type ('main', 'alt', or 'farm').
        """
        author_id_str = str(author_id)
        column = None

        if acctype == "main":
            column = "Governer ID"
        elif acctype == "alt":
            column = "ALT ID"
        elif acctype == "farm":
            column = "FARM ID"

        if column:
            self.cursor.execute(
                f"UPDATE accounts SET '{column}' = NULL WHERE 'Discord ID' = ?",
                (author_id_str,),
            )
            self.connection.commit()
