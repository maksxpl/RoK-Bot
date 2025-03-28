import os
import sqlite3
from typing import Optional, Union

import gspread
import hikari
from data_manager import bot_dir
from oauth2client.service_account import ServiceAccountCredentials

db_path = os.path.join(bot_dir, "data", "rok.sqlite3")
connection = sqlite3.connect(db_path)
connection.row_factory = sqlite3.Row  # Enable named column access in query results
cursor = connection.cursor()


class GetUser:
    def gov_user(
        self, user_discord_id: int, acc_category: str, acc_type: str
    ) -> Optional[dict[str, int]]:
        """
        Fetches the Governor ID and Name associated with a Discord user ID based on the type.

        Args:
            user_discord_id (int): The Discord ID of the user.
            acc_category (str): The account category ('general' or 'kvk').
            acc_type (str): The account type ('main', 'alt', 'farm').

        Returns:
            user (dict): A dictionary containing 'name' and 'id' of the governor, or None if no valid ID is found.

            :format: {"name": str, "id": int}

        """
        # Determine the correct table based on the account category
        id_table = "basic_top_600" if acc_category == "general" else "kvk_top_600"

        if acc_type == "main":
            acc_id_type = "Governer ID"
        elif acc_type == "alt":
            acc_id_type = "ALT ID"
        elif acc_type == "farm":
            acc_id_type = "FARM ID"
        else:
            return None

        # Fetch the row corresponding to the user_discord_id
        cursor.execute(
            'SELECT * FROM accounts WHERE "Discord ID" = ?', (user_discord_id,)
        )
        row = cursor.fetchone()

        if row is None:
            return None

        # Retrieve the governor ID for the specified account type
        gov_id = row[acc_id_type]
        if not gov_id:
            return None

        # Query the appropriate table for the governor name
        cursor.execute(
            f'SELECT "Governor Name" FROM {id_table} WHERE "Governor ID" = ?',
            (gov_id,),
        )
        nickname_row = cursor.fetchone()

        if nickname_row:
            return {"name": nickname_row["Governor Name"], "id": gov_id}

        # Return None if no matching governor name is found
        return None

    def gov_ids(self, user_discord_id: int) -> Optional[dict[str, int]]:
        """
        Fetches the main, alt, and farm IDs associated with a Discord user ID.

        Args:
            user_discord_id (int): The Discord ID of the user.

        Returns:
            dict: A dictionary containing 'main', 'alt', and 'farm' IDs, or None if no valid ID is found.

            :format: {'main': int, 'alt': int, 'farm': int}
        """
        # Query the database for the user's account IDs
        cursor.execute(
            'SELECT "Governer ID", "ALT ID", "FARM ID" FROM accounts WHERE "Discord ID" = ?',
            (user_discord_id,),
        )
        row = cursor.fetchone()

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

    def discord_username(self, governor_id: int, stats: str) -> str:
        """
        Get the Discord username associated with a governor ID.

        Args:
            governor_id (int): Governor ID.
            stats (str): Indicates which table to use ('general' or 'kvk').

        Returns:
            str: Discord username if found, or None.
        """
        cursor = connection.cursor()

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

    def discord_id_from_gov_id(
        self, gov_id: Union[int, hikari.Snowflake]
    ) -> int | None:
        """
        Get Discord ID associated with a governor ID.

        Args:
            gov_id (int): Governor ID.

        Returns:
            int: Corresponding Discord ID or None if not found.
        """
        cursor.execute(
            'SELECT "Discord ID" FROM accounts WHERE "Governer ID" = ?', (str(gov_id),)
        )
        row = cursor.fetchone()
        if row:
            return int(row["Discord ID"])
        return None

    def get_gov_id_from_discord(self, author_id: int) -> int | None:
        """
        Get governor ID associated with a Discord ID.

        Args:
            author_id (int): Discord user ID.

        Returns:
            int: Corresponding governor ID or None if not found.
        """
        cursor.execute(
            'SELECT "Governer ID" FROM accounts WHERE "Discord ID" = ?',
            (str(author_id),),
        )
        row = cursor.fetchone()
        if row and row["Governer ID"]:
            return int(row["Governer ID"])
        return None


class KvK:
    def user_stats(self, gov_id: int, account_category: str) -> Optional[dict]:
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
        cursor.execute(f'SELECT * FROM {id_table} WHERE "Governor ID" = ?', (gov_id,))
        row = cursor.fetchone()
        if row is None:
            return None

        # Convert the row to a dictionary
        return dict(row)

    def kvk_top_300_global_stats(self) -> dict:
        """
        Sums top 300 numbers from the 'T4 Kills', 'T5 Kills', and 'Deaths' columns
        from the 'kvk_top_600'.

        Returns:
            dict: A dictionary with the column names as keys and their sums as values.
        """
        cursor.execute(
            """
            SELECT 
                SUM(CAST(REPLACE("T4 Kills", ',', '') AS INTEGER)) AS "T4 Kills",
                SUM(CAST(REPLACE("T5 Kills", ',', '') AS INTEGER)) AS "T5 Kills",
                SUM(CAST(REPLACE("Deaths", ',', '') AS INTEGER)) AS "Deaths"
            FROM (
                SELECT * FROM kvk_top_600 ORDER BY "Power" DESC LIMIT 300 
            )
            """
        )

        # Fetch the result which will contain the sums of each column
        result = cursor.fetchone()

        # Construct the dictionary from the fetched result
        sums = {
            "T4 Kills": result["T4 Kills"] if result["T4 Kills"] is not None else 0,
            "T5 Kills": result["T5 Kills"] if result["T5 Kills"] is not None else 0,
            "Deaths": result["Deaths"] if result["Deaths"] is not None else 0,
        }

        return sums

    def kvk_top_x_player_stats(self, stat: str) -> dict:
        """
        Gets top 10 players in selected category

        Returns:
            dict: A dictionary with the top 10 players with assigned chosen stat.

            format: {player_name: {"player_id": player_id, "score": score}}
        """

        query = f"""
        SELECT "Governor Name", "Governor ID", "{stat}"
        FROM "kvk_top_600"
        ORDER BY CAST(REPLACE("{stat}", ',', '') AS INTEGER) DESC
        LIMIT 10
        """

        cursor.execute(query)
        result = cursor.fetchall()

        top_players = {
            player_name: {"player_id": player_id, "score": score}
            for player_name, player_id, score in result
        }

        return top_players


class Id:
    def save(
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
            cursor.execute('SELECT * FROM accounts WHERE "Discord ID" = ?', (user_id,))
            row = cursor.fetchone()
            if row:
                # Update the existing row
                cursor.execute(
                    f'UPDATE accounts SET "Discord Username" = ?, "{column}" = ? WHERE "Discord ID" = ?',
                    (user_name, gov_id_str, user_id),
                )
            else:
                # Insert a new row
                cursor.execute(
                    f"INSERT INTO accounts ('Discord ID', '{column}', 'Discord Username') VALUES (?, ?, ?)",
                    (
                        author_id_str,
                        gov_id_str,
                        user_name,
                    ),
                )
            connection.commit()

    def remove(self, author_id: int, acc_type: str) -> None:
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
            cursor.execute(
                f'UPDATE accounts SET "{acc_id_type}" = NULL WHERE "Discord ID" = ?',
                (author_id_str,),
            )
            connection.commit()


class GSheet:
    def __init__(self, sheet_id: str):
        self.sheet_id = sheet_id
        self.sheet = self.setup_google_sheets()

    def setup_google_sheets(self):
        """
        Initializes the Google Sheets API client using credentials from a JSON file.
        """
        credentials_path = os.path.join(bot_dir, "data", "creds.json")

        # Set the Google Sheets API scope and authorize
        scope = [
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/drive",
        ]
        creds = ServiceAccountCredentials.from_json_keyfile_name(
            credentials_path, scope
        )
        client = gspread.authorize(creds)

        # Open the Google Sheet by ID
        return client.open_by_key(self.sheet_id)

    def normalize_headers(self, headers):
        """Normalize headers by stripping spaces and converting to lowercase."""
        return [header.strip().lower() for header in headers]

    def fetch_sheet_data(self, worksheet_title: str, expected_headers: list):
        worksheet = self.sheet.worksheet(worksheet_title)
        records = worksheet.get_all_records()

        # Normalize the expected headers and the headers in the sheet
        normalized_expected_headers = self.normalize_headers(expected_headers)
        normalized_sheet_headers = self.normalize_headers(records[0].keys())

        # Check if all expected headers are present in the sheet headers
        missing_headers = set(normalized_expected_headers) - set(
            normalized_sheet_headers
        )
        if missing_headers:
            raise ValueError(f"Missing headers in the sheet: {missing_headers}")

        # Only keep records with expected headers
        filtered_records = []
        for record in records:
            filtered_record = {
                k: v
                for k, v in record.items()
                if k.strip().lower() in normalized_expected_headers
            }
            filtered_records.append(filtered_record)

        return filtered_records

    def sync_db_with_sheets(self):
        create_accounts_table = """
        CREATE TABLE IF NOT EXISTS accounts (
            "Discord ID" TEXT,
            "Discord Username" TEXT,
            "Governor ID" TEXT,
            "ALT ID" TEXT,
            "FARM ID" TEXT
        );
        """

        create_basic_top_600_table = """
        CREATE TABLE IF NOT EXISTS basic_top_600 (
            "Governor Name" TEXT,
            "Governor ID" TEXT,
            "Power" INTEGER,
            "Kill Points" INTEGER,
            "Deaths" INTEGER,
            "T4 Kills" INTEGER,
            "T5 Kills" INTEGER,
            "Alliance" TEXT
        );
        """

        create_kvk_top_600_table = """
        CREATE TABLE IF NOT EXISTS kvk_top_600 (
            "Governor Name" TEXT,
            "Governor ID" TEXT,
            "Power" INTEGER,
            "Rank" INTEGER,
            "DKP Required" INTEGER,
            "DKP Achieved" INTEGER,
            "Deaths" INTEGER,
            "T4 Kills" INTEGER,
            "T5 Kills" INTEGER,
            "Alliance" TEXT
        );
        """

        cursor.execute("DROP TABLE IF EXISTS accounts;")
        cursor.execute("DROP TABLE IF EXISTS basic_top_600;")
        cursor.execute("DROP TABLE IF EXISTS kvk_top_600;")

        cursor.execute(create_accounts_table)
        cursor.execute(create_basic_top_600_table)
        cursor.execute(create_kvk_top_600_table)

        # Define the expected headers for each sheet
        accounts_headers = [
            "Discord ID",
            "Discord Username",
            "Governor ID",
            "ALT ID",
            "FARM ID",
        ]
        basic_top_600_headers = [
            "Governor Name",
            "Governor ID",
            "Power",
            "Kill Points",
            "Deaths",
            "T4 Kills",
            "T5 Kills",
            "Alliance",
        ]
        kvk_top_600_headers = [
            "Governor Name",
            "Governor ID",
            "Power",
            "Rank",
            "DKP Required",
            "DKP Achieved",
            "Deaths",
            "T4 Kills",
            "T5 Kills",
            "Alliance",
        ]

        # Fetch and insert data for "accounts" table
        accounts_data = self.fetch_sheet_data(
            "ACCOUNTS LINKED TO BOTS", accounts_headers
        )
        for row in accounts_data:
            cursor.execute(
                """
                INSERT INTO accounts ("Discord ID", "Discord Username", "Governor ID", "ALT ID", "FARM ID")
                VALUES (?, ?, ?, ?, ?)
            """,
                (
                    row.get("Discord ID"),
                    row.get("Discord Username"),
                    row.get("Governor ID"),
                    row.get("ALT ID"),
                    row.get("FARM ID"),
                ),
            )

        # Fetch and insert data for "basic_top_600" table
        basic_top_600_data = self.fetch_sheet_data(
            "🤖BASIC STATS TOP 600 13-02-2024", basic_top_600_headers
        )
        for row in basic_top_600_data:
            cursor.execute(
                """
                INSERT INTO basic_top_600 ("Governor Name", "Governor ID", "Power", "Kill Points", "Deaths", "T4 Kills", "T5 Kills", "Alliance")
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    row.get("Governor Name"),
                    row.get("Governor ID"),
                    row.get("Power"),
                    row.get("Kill Points"),
                    row.get("Deaths"),
                    row.get("T4 Kills"),
                    row.get("T5 Kills"),
                    row.get("Alliance"),
                ),
            )

        # Fetch and insert data for "kvk_top_600" table
        kvk_top_600_data = self.fetch_sheet_data(
            "KVK 2 STATS TOP 600", kvk_top_600_headers
        )
        for row in kvk_top_600_data:
            cursor.execute(
                """
                INSERT INTO kvk_top_600 ("Governor Name", "Governor ID", "Power", "Rank", "DKP Required", "DKP Achieved", "Deaths", "T4 Kills", "T5 Kills", "Alliance")
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    row.get("Governor Name"),
                    row.get("Governor ID"),
                    row.get("Power"),
                    row.get("Rank"),
                    row.get("DKP Required"),
                    row.get("DKP Achieved"),
                    row.get("Deaths"),
                    row.get("T4 Kills"),
                    row.get("T5 Kills"),
                    row.get("Alliance"),
                ),
            )

        connection.commit()
        print("Database has been synced with Google Sheets.")
