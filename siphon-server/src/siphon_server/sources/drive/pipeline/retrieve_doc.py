"""
metadata = {"title": "Sample Drive Document", "author": "Author Name"}
text = "This is the extracted text from the Drive document."
"""

from siphon_server.sources.drive.parser import DriveParser
from siphon_server.sources.drive.pipeline.drive_type import DriveType
from pathlib import Path
# from googleapiclient.discovery import build
# from google.oauth2 import service_account

DRIVE_TYPE_MAPPING = {
    DriveType.DOCS: {
        "scope": "https://www.googleapis.com/auth/documents.readonly",
        "service": "docs",
    },
    DriveType.SHEETS: {
        "scope": "https://www.googleapis.com/auth/spreadsheets.readonly",
        "service": "sheets",
    },
    DriveType.SLIDES: {
        "scope": "https://www.googleapis.com/auth/presentations.readonly",
        "service": "slides",
    },
    DriveType.FORMS: {
        "scope": "https://www.googleapis.com/auth/forms.responses.readonly",
        "service": "forms",
    },
}


# def get_drive_service(drive_type: DriveType):
#     drive_info = DRIVE_TYPE_MAPPING[drive_type]
#     scope = drive_info["scope"]
#     service_name = drive_info["service"]
#
#     dir_path = Path(__file__).parent
#     SERVICE_ACCOUNT_FILE = dir_path / ".service_credentials.json"
#     credentials = service_account.Credentials.from_service_account_file(
#         SERVICE_ACCOUNT_FILE, scopes=[scope]
#     )
#     service = build(service_name, "v4", credentials=credentials)
#     return service


if __name__ == "__main__":
    doc = "https://docs.google.com/document/d/1L4rwvx5P33LbPcX2dawSYrE2Z38yXwBBRaPVJakHozU/edit?tab=t.0"
    sheet = "https://docs.google.com/spreadsheets/d/1H7QTl1F7rJsVkCHtUyIzk1RSGnpyzZZf5nVNhRQdmyw/edit?gid=0#gid=0"
    parser = DriveParser()
    source_info = parser.parse(sheet)
    type, id = source_info.uri.split("///")[1].split("/")
    drive_type = DriveType(type)
    service = parser.get_drive_service(drive_type)

    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=tracker, range="All Pro Certs").execute()
