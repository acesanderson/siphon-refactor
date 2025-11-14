from googleapiclient.discovery import build
from google.oauth2 import service_account
from pathlib import Path
import pandas as pd
import json


# SCOPES specifies which Google APIs you want to authorize access to
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]
# Our credentials; I got this from following this tutorial from LI: https://iwww.corp.linkedin.com/wiki/cf/pages/viewpage.action?spaceKey=CIT&title=Service+Accounts+for+Google+APIs
dir_path = Path(__file__).parent
SERVICE_ACCOUNT_FILE = dir_path / ".service_credentials.json"
json_dict = json.loads(SERVICE_ACCOUNT_FILE.read_text())
breakpoint()

credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES
)
# Create the drive service with our credentials
sheet_service = build("sheets", "v4", credentials=credentials)
drive_service = build("drive", "v3", credentials=credentials)


def save_dataframe_to_new_sheet(df, title, user_email="bianderson@linkedin.com"):
    """Saves a Pandas DataFrame to a new Google Sheet with a given title.

    Args:
        df: The Pandas DataFrame to save.
        title: The title for the new Google Sheet.

    Returns:
        The ID of the newly created spreadsheet, or None if an error occurs.
    """
    try:
        # Create a new spreadsheet
        spreadsheet = {"properties": {"title": title}}
        new_spreadsheet = (
            sheet_service.spreadsheets().create(body=spreadsheet).execute()
        )
        spreadsheet_id = new_spreadsheet["spreadsheetId"]

        # Convert the DataFrame to a list of lists (required format for the API)
        data = [df.columns.values.tolist()] + df.values.tolist()  # Include header row

        # Write the data to the first sheet (default sheet)
        body = {"values": data}
        result = (
            sheet_service.spreadsheets()
            .values()
            .update(
                spreadsheetId=spreadsheet_id,
                range="Sheet1!A1",  # A1 notation for starting cell
                valueInputOption="USER_ENTERED",
                body=body,
            )
            .execute()
        )  # USER_ENTERED for formulas

        print(f"DataFrame saved to Google Sheet: {title}")
        print(f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}")

        # Share with the specified user
        permission = {"type": "user", "role": "writer", "emailAddress": user_email}
        drive_service.permissions().create(
            fileId=spreadsheet_id,
            body=permission,
            sendNotificationEmail=True,  # Optional: send an email notification
        ).execute()
        print(f"Spreadsheet shared with: {user_email}")

        return spreadsheet_id

    except Exception as e:
        print(f"An error occurred: {e}")
        return None


# def main():
#     example_df = pd.DataFrame({"a": [1, 2], "b": [3, 4]})
#     sheet_title = "Malarkey"
#     save_dataframe_to_new_sheet(example_df, sheet_title)
#
#
# if __name__ == "__main__":
#     main()
