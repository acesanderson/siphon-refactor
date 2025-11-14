from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
from google.oauth2 import service_account
from markdown2 import markdown
import io
import os
from pathlib import Path


# SCOPES specifies which Google APIs you want to authorize access to
SCOPES = [
    "https://www.googleapis.com/auth/drive.file",
]
# Our credentials; I got this from following this tutorial from LI: https://iwww.corp.linkedin.com/wiki/cf/pages/viewpage.action?spaceKey=CIT&title=Service+Accounts+for+Google+APIs
dir_path = Path(__file__).parent
SERVICE_ACCOUNT_FILE = dir_path / ".service_credentials.json"
credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES
)
# Create the drive service with our credentials
drive_service = build("drive", "v3", credentials=credentials)
folder_id = (
    "1Hx6KgyV_lXFLkiSrSyWBcIeArjhTfKh1"  # This is the Prof Cert Curations folder
)


def create_doc_from_markdown(
    title,
    markdown_content,
    users=["bianderson@linkedin.com"],
):
    """
    Converts the markdown string into html, then turns into in a bytes object, then uploads directly to Google Drive like it was a file upload.
    """
    # Convert markdown to html
    html = markdown(markdown_content)
    # Create a new Google Doc
    # file_metadata = {"name": title, "mimeType": "application/vnd.google-apps.document"}
    # Specify the target folder ID using the 'parents' key
    file_metadata = {
        "name": title,
        "mimeType": "application/vnd.google-apps.document",
        "parents": [folder_id],  # Add this line
    }
    media = MediaIoBaseUpload(
        io.BytesIO(html.encode("utf-8")), mimetype="text/html", resumable=True
    )
    # Upload the document to Google Drive
    file = (
        drive_service.files()
        .create(body=file_metadata, media_body=media, fields="id")
        .execute()
    )
    doc_id = file.get("id")
    doc_url = f"https://docs.google.com/document/d/{doc_id}"
    # Share with user(s)
    for user in users:
        permission = {"type": "user", "role": "writer", "emailAddress": user}
        drive_service.permissions().create(
            fileId=doc_id,
            body=permission,
            fields="id",
            sendNotificationEmail=False,
        ).execute()
    return doc_url


def main():
    OBSIDIAN_PATH = Path(os.getenv("OBSIDIAN_PATH"))
    PODCAST_FILE_PATH = OBSIDIAN_PATH / "Podcasts.md"
    assert PODCAST_FILE_PATH.exists(), f"File not found: {PODCAST_FILE_PATH}"
    with open(PODCAST_FILE_PATH, "r") as f:
        markdown_string = f.read()
    title = "Podcasts Collection"
    url = create_doc_from_markdown(title, markdown_string)
    print(f"Created and shared document with title: {title}")
    print(url)


if __name__ == "__main__":
    main()
