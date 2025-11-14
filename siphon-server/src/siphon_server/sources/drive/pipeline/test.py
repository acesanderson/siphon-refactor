import logging
import os
from pathlib import Path

# Imports from Gmail script
from dotenv import load_dotenv
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from siphon_server.sources.drive.pipeline.drive_type import DriveType
from pathlib import Path

# --- Logging Setup (from Gmail script) ---
log_level = int(os.getenv("PYTHON_LOG_LEVEL", "2"))
levels = {1: logging.WARNING, 2: logging.INFO, 3: logging.DEBUG}
logging.basicConfig(
    level=levels.get(log_level, logging.INFO),
    format="%(levelname)s: [%(asctime)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


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


CLIENT_SECRET_FILE = "client_secret.json"


def get_google_service(service_name: str, service_version: str, scopes: list[str]):
    """
    Authenticates with a Google API and returns a service object.
    Handles token creation, storage, and refresh.
    (Adapted from your get_gmail_service)
    """
    token_file = f"{service_name}_token.json"
    creds = None
    if Path(token_file).exists():
        try:
            creds = Credentials.from_authorized_user_file(token_file, scopes)
        except Exception as e:
            logger.warning(f"Could not load {token_file}: {e}. Re-authenticating.")
            creds = None

    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                logger.info(f"Refreshing expired {service_name} credentials...")
                creds.refresh(Request())
            except Exception as e:
                logger.warning(
                    f"Could not refresh {service_name} token: {e}. Need new login."
                )
                creds = None  # Force re-flow
        else:
            logger.info(f"No valid {service_name} credentials. Starting auth flow...")
            if not Path(CLIENT_SECRET_FILE).exists():
                logger.critical(f"FATAL: {CLIENT_SECRET_FILE} not found.")
                return None

            flow = InstalledAppFlow.from_client_secrets_file(
                CLIENT_SECRET_FILE, scopes, redirect_uri="urn:ietf:wg:oauth:2.0:oob"
            )
            # Generate the authorization URL
            auth_url, _ = flow.authorization_url(prompt="consent")

            print("Please go to this URL to authorize access:")
            print(auth_url)

            # Get the authorization code from the user
            code = input("Enter the authorization code: ")

            # Exchange the code for a token
            try:
                flow.fetch_token(code=code)
                creds = flow.credentials
            except Exception as e:
                logger.error(f"Error fetching token: {e}")
                return None

        # Save the credentials for the next run
        try:
            with open(token_file, "w") as token:
                token.write(creds.to_json())
            logger.info(f"Credentials saved to {token_file}")
        except Exception as e:
            logger.error(f"Could not write token file: {e}")

    try:
        service = build(service_name, service_version, credentials=creds)
        logger.info(f"{service_name.capitalize()} service object created successfully.")
        return service
    except Exception as e:
        logger.error(f"Failed to build {service_name} service: {e}")
        return None


# This main execution block is from your *first* (Drive) script
if __name__ == "__main__":
    doc = "https://docs.google.com/document/d/1L4rwvx5P33LbPcX2dawSYrE2Z38yXwBBRaPVJakHozU/edit?tab=t.0"
    # sheet_url = "https://docs.google.com/spreadsheets/d/1H7QTl1F7rJsVkCHtUyIzk1RSGnpyzZZf5nVNhRQdmyw/edit?gid=0#gid=0"

    # Simplified parsing. This assumes your siphon_server logic is not used
    # for authentication, only for type/ID extraction.
    # If DriveParser.parse() is complex, this will need adjustment.

    # A simple way to get the ID and type without the parser:
    file_id = doc.split("/d/")[1].split("/")[0]
    file_type = DriveType("docs")  # Hard-coded based on URL

    # This replaces the `DriveParser` and `parser.get_drive_service`
    service = get_google_service(
        service_name="sheets",
        service_version="v4",
        scopes=["https://www.googleapis.com/auth/spreadsheets.readonly"],
    )

    if service:
        sheet = service.spreadsheets()

        # Fixed the NameError: `tracker` is now `file_id`
        result = sheet.values().get(spreadsheetId=file_id, range="Net worth").execute()
        print(result)
    else:
        logger.error("Could not get Sheets service.")
