from googleapiclient.discovery import build
from google.oauth2 import service_account
from pathlib import Path
import pandas as pd

# Our document ID -- google user is already shared with it
tracker = "1Z0120fbBaBwE6DqF4GAuab2BzpNDTDuLFWmY5RZg97Y"

# SCOPES specifies which Google APIs you want to authorize access to
SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]
# Our credentials; I got this from following this tutorial from LI: https://iwww.corp.linkedin.com/wiki/cf/pages/viewpage.action?spaceKey=CIT&title=Service+Accounts+for+Google+APIs
dir_path = Path(__file__).parent
SERVICE_ACCOUNT_FILE = dir_path / ".service_credentials.json"
credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES
)
# Create the drive service with our credentials
sheets_service = build("sheets", "v4", credentials=credentials)


def get_certs_df() -> pd.DataFrame:
    sheet = sheets_service.spreadsheets()
    result = sheet.values().get(spreadsheetId=tracker, range="All Pro Certs").execute()
    values = result["values"]
    # This can break if people mess with the spreadsheet!
    columns, values = values[3], values[4:]
    df = pd.DataFrame(values, columns=columns)
    df["Title"] = df["Title"].apply(lambda x: x.strip() if x else x)
    # Remove the row with this Title: "Career Essentials in System Administration by Microsoft and LinkedIn"
    df = df[
        df.Title
        != "Career Essentials in System Administration by Microsoft and LinkedIn"
    ]
    return df


def main():
    df = get_certs_df()
    print(f"{len(df)} certs found")
    # # Ramped certs
    ramped = df[df.Status == "Ramped"].Title.tolist()
    for r in ramped:
        print(r)


if __name__ == "__main__":
    main()
