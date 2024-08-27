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

    def get_gov_user(
        self, user_discord_id: int, acc_category: str, acc_type: str
    ) -> dict:
        """
        Fetches the Governor ID and Name associated with a Discord user ID based on the type.

        Args:
            user_discord_id (int): The Discord ID of the user.
            acc_category (str): The account category ('general' or 'kvk').
            acc_type (str): The account type ('main', 'alt', 'farm').

        Returns:
            dict: A dictionary containing 'name' and 'id' of the governor, or None if no valid ID is found.
        """
        # Determine the correct table based on the account category
        id_table = "basic_top_600" if acc_category == "general" else "kvk_top_600"

        if acc_type == "main":
            acc_id_type = "Governer ID"
        elif acc_type == "alt":
            acc_id_type = "ALT ID"
        elif acc_type == "farm":
            acc_id_type = "FARM ID"

        # Fetch the row corresponding to the user_discord_id
        self.cursor.execute(
            'SELECT * FROM accounts WHERE "Discord ID" = ?', (user_discord_id,)
        )
        row = self.cursor.fetchone()

        if row is None:
            return None

        # Retrieve the governor ID for the specified account type
        gov_id = row[acc_id_type]
        if not gov_id:
            return None

        # Query the appropriate table for the governor name
        self.cursor.execute(
            f'SELECT "Governor Name" FROM {id_table} WHERE "Governor ID" = ?',
            (gov_id,),
        )
        nickname_row = self.cursor.fetchone()

        if nickname_row:
            return {"name": nickname_row["Governor Name"], "id": gov_id}

        # Return None if no matching governor name is found
        return None

    def get_user_ids(self, user_discord_id: int) -> dict:
        """
        Fetches the main, alt, and farm IDs associated with a Discord user ID.

        Args:
            user_discord_id (int): The Discord ID of the user.

        Returns:
            dict: A dictionary containing 'main', 'alt', and 'farm' IDs, or None if no valid ID is found.
        """
        # Query the database for the user's account IDs
        self.cursor.execute(
            'SELECT "Governer ID", "ALT ID", "FARM ID" FROM accounts WHERE "Discord ID" = ?',
            (user_discord_id,),
        )
        row = self.cursor.fetchone()

        # Check if any results were returned
        if row is None:
            return None

        # Build and return the dictionary with account IDs
        user_ids = {
            "main": row["Governer ID"] if row["Governer ID"] else None,
            "alt": row["ALT ID"] if row["ALT ID"] else None,
            "farm": row["FARM ID"] if row["FARM ID"] else None,
        }

        return user_ids

    def get_kvk_stats(self, gov_id: int, account_category: str) -> dict:
        """
        Get KvK stats for a player with the given governor ID.

        Args:
            gov_id (int): Governor ID.
            account_category (str): Type of stats to retrieve ("general" or "kvk").

        Returns:
            dict: Dictionary containing the player's stats.
        """
        id_table = "basic_top_600" if account_category == "general" else "kvk_top_600"

        # Fetch the player's stats from the database
        self.cursor.execute(
            f'SELECT * FROM {id_table} WHERE "Governor ID" = ?', (gov_id,)
        )
        row = self.cursor.fetchone()
        if row is None:
            return None

        # Convert the row to a dictionary
        return dict(row)

    def get_discord_user(self, discord_id: int, governor_id: int, stats: str) -> str:
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
        self, user_id: int, user_name: str, governor_id: int, acc_type: str
    ) -> None:
        """
        Save or update a governor ID association for a given Discord user ID.

        Args:
            author_id (int): Discord user ID.
            author_name (str): Discord username
            governor_id (int): Governor ID.
            acctype (str): Account type ('main', 'alt', or 'farm').
        """
        author_id_str = str(user_id)
        gov_id_str = str(governor_id)
        column = None

        if acc_type == "main":
            column = "Governer ID"
        elif acc_type == "alt":
            column = "ALT ID"
        elif acc_type == "farm":
            column = "FARM ID"

        if column:
            # Check if the Discord ID already exists
            self.cursor.execute(
                'SELECT * FROM accounts WHERE "Discord ID" = ?', (user_id,)
            )
            row = self.cursor.fetchone()
            if row:
                # Update the existing row
                self.cursor.execute(
                    f'UPDATE accounts SET "Discord Username" = ?, "{column}" = ? WHERE "Discord ID" = ?',
                    (user_name, gov_id_str, user_id),
                )
            else:
                # Insert a new row
                self.cursor.execute(
                    f"INSERT INTO accounts ('Discord ID', '{column}', 'Discord Username') VALUES (?, ?, ?)",
                    (
                        author_id_str,
                        gov_id_str,
                        user_name,
                    ),
                )
            self.connection.commit()

    def remove_id(self, author_id: int, acc_type: str) -> None:
        """
        Remove a governor ID associated with a Discord user ID and account type.

        Args:
            author_id (int): Discord user ID.
            acctype (str): Account type ('main', 'alt', or 'farm').
        """
        author_id_str = str(author_id)
        acc_id_type = None

        if acc_type == "main":
            acc_id_type = "Governer ID"
        elif acc_type == "alt":
            acc_id_type = "ALT ID"
        elif acc_type == "farm":
            acc_id_type = "FARM ID"

        if acc_id_type:
            self.cursor.execute(
                f'UPDATE accounts SET "{acc_id_type}" = NULL WHERE "Discord ID" = ?',
                (author_id_str,),
            )
            self.connection.commit()
