"""
Stateless, Poll-Based Gmail Ingestion Script

This script is designed to be run as a one-off job (e.g., via cron) to
ingest Gmail messages. It uses a timestamp-based checkpoint to fetch
only new messages since the last successful run.

Required Environment Variables:
- GMAIL_QUERY: The Gmail search query (e.g., "label:my-label").
- INGEST_FORMAT: "metadata" (save full message object as JSON) or
                 "raw" (save decoded MIME as .eml).
- PYTHON_LOG_LEVEL: 1 (WARNING), 2 (INFO), 3 (DEBUG).

Required Files:
- client_secret.json: Your Google Cloud OAuth 2.0 Client ID credentials.
- .env: File containing the environment variables.
"""

import logging
import os
import json
import base64
import time
from pathlib import Path

from dotenv import load_dotenv
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# --- Logging Setup (as requested) ---
log_level = int(os.getenv("PYTHON_LOG_LEVEL", "2"))
levels = {1: logging.WARNING, 2: logging.INFO, 3: logging.DEBUG}
logging.basicConfig(
    level=levels.get(log_level, logging.INFO),
    format="%(levelname)s: [%(asctime)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# --- Configuration ---
_ = load_dotenv()  # Load .env file, ignore return value

# Google API
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]
CLIENT_SECRET_FILE = "client_secret.json"
TOKEN_FILE = "token.json"

# Script Configuration
BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "gmail_ingest"
CHECKPOINT_FILE = BASE_DIR / "gmail_checkpoint.json"

# Environment-driven settings
GMAIL_QUERY = os.getenv("GMAIL_QUERY")
INGEST_FORMAT = os.getenv("INGEST_FORMAT", "metadata").lower()


def get_gmail_service():
    """
    Authenticates with the Gmail API and returns a service object.
    Handles token creation, storage, and refresh.
    """
    creds = None
    if Path(TOKEN_FILE).exists():
        try:
            creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
        except Exception as e:
            logger.warning(f"Could not load token file: {e}. Re-authenticating.")
            creds = None

    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                logger.info("Refreshing expired credentials...")
                creds.refresh(Request())
            except Exception as e:
                logger.warning(f"Could not refresh token: {e}. Need new login.")
                creds = None  # Force re-flow
        else:
            logger.info("No valid credentials found. Starting auth flow...")
            if not Path(CLIENT_SECRET_FILE).exists():
                logger.critical(f"FATAL: {CLIENT_SECRET_FILE} not found.")
                logger.critical("Please download from Google Cloud Console.")
                return None

            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
            # Use console-based auth flow
            creds = flow.run_local_server()

        # Save the credentials for the next run
        try:
            with open(TOKEN_FILE, "w") as token:
                token.write(creds.to_json())
            logger.info(f"Credentials saved to {TOKEN_FILE}")
        except Exception as e:
            logger.error(f"Could not write token file: {e}")

    try:
        service = build("gmail", "v1", credentials=creds)
        logger.info("Gmail service object created successfully.")
        return service
    except Exception as e:
        logger.error(f"Failed to build Gmail service: {e}")
        return None


def load_checkpoint():
    """
    Loads the last processed Unix timestamp from the checkpoint file.
    Returns 0 if the file doesn't exist.
    """
    if not CHECKPOINT_FILE.exists():
        logger.warning(f"Checkpoint file not found. Will query all messages.")
        return 0

    try:
        with open(CHECKPOINT_FILE, "r") as f:
            data = json.load(f)
            timestamp = int(data.get("last_processed_timestamp", 0))
            logger.info(f"Loaded checkpoint timestamp: {timestamp}")
            return timestamp
    except (json.JSONDecodeError, IOError) as e:
        logger.error(f"Could not read checkpoint file: {e}. Resetting to 0.")
        return 0


def save_checkpoint(timestamp):
    """Saves the given Unix timestamp to the checkpoint file."""
    try:
        with open(CHECKPOINT_FILE, "w") as f:
            json.dump({"last_processed_timestamp": timestamp}, f)
        logger.info(f"New checkpoint timestamp saved: {timestamp}")
    except IOError as e:
        logger.error(f"Could not write to checkpoint file: {e}")


def fetch_messages(service, query):
    """
    Fetches message IDs matching the query.
    Paginates through results if necessary.
    """
    message_ids = []
    try:
        logger.info(f"Executing query: {query}")
        request = service.users().messages().list(userId="me", q=query)

        while request:
            response = request.execute()
            messages = response.get("messages", [])
            message_ids.extend([msg["id"] for msg in messages])

            request = (
                service.users()
                .messages()
                .list_next(previous_request=request, previous_response=response)
            )

            if request:
                logger.info("Paginating to next page of results...")

        logger.info(f"Found {len(message_ids)} messages matching query.")
        return message_ids

    except HttpError as error:
        logger.error(f"An error occurred fetching message list: {error}")
        return []
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        return []


def process_and_save_message(service, msg_id):
    """
    Fetches a single message, saves it based on INGEST_FORMAT,
    and returns its internalDate (in seconds) for checkpointing.
    """
    try:
        # Request 'raw' format if needed, 'full' otherwise for metadata
        api_format = "raw" if INGEST_FORMAT == "raw" else "full"

        message = (
            service.users()
            .messages()
            .get(userId="me", id=msg_id, format=api_format)
            .execute()
        )

        # Gmail internalDate is ms timestamp as string. Convert to int seconds.
        internal_date_ms = int(message["internalDate"])
        internal_date_sec = internal_date_ms // 1000

        if INGEST_FORMAT == "raw":
            if "raw" not in message:
                logger.warning(f"INGEST_FORMAT is 'raw' but no raw data for {msg_id}")
                return None

            raw_data = message["raw"]
            decoded_data = base64.urlsafe_b64decode(raw_data).decode("utf-8")

            filename = f"{internal_date_sec}_{msg_id}.eml"
            filepath = OUTPUT_DIR / filename
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(decoded_data)

        else:  # "metadata"
            filename = f"{internal_date_sec}_{msg_id}.json"
            filepath = OUTPUT_DIR / filename
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(message, f, indent=2)

        logger.debug(f"Saved message {msg_id} to {filepath}")
        return internal_date_sec

    except HttpError as error:
        logger.error(f"An error occurred fetching message {msg_id}: {error}")
        return None
    except Exception as e:
        logger.error(f"An error saving message {msg_id}: {e}")
        return None


def main():
    """Main execution logic."""
    start_time = time.time()
    logger.info("--- Gmail Ingestion Run Started ---")

    if not GMAIL_QUERY:
        logger.critical("FATAL: GMAIL_QUERY environment variable is not set.")
        return

    # Ensure output directory exists
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    service = get_gmail_service()
    if not service:
        logger.critical("Failed to get Gmail service. Exiting.")
        return

    # 1. Load checkpoint
    last_timestamp = load_checkpoint()

    # 2. Build query
    # Add timestamp only if we have one. +1 to avoid re-fetching last message.
    query = GMAIL_QUERY
    if last_timestamp > 0:
        query = f"{GMAIL_QUERY} after:{last_timestamp + 1}"

    # 3. Fetch message IDs
    message_ids = fetch_messages(service, query)
    if not message_ids:
        logger.info("No new messages found. Run complete.")
        return

    # 4. Process messages and find new checkpoint
    # Messages are listed newest first. The first one we process
    # will be the new checkpoint.

    new_checkpoint_timestamp = 0
    processed_count = 0

    for i, msg_id in enumerate(message_ids):
        logger.debug(f"Processing message {i + 1}/{len(message_ids)} (ID: {msg_id})")

        message_timestamp = process_and_save_message(service, msg_id)

        if message_timestamp:
            processed_count += 1
            # The first successfully processed message is the newest
            if new_checkpoint_timestamp == 0:
                new_checkpoint_timestamp = message_timestamp

    # 5. Save new checkpoint
    if new_checkpoint_timestamp > last_timestamp:
        save_checkpoint(new_checkpoint_timestamp)
    else:
        logger.info("No new messages processed, checkpoint remains unchanged.")

    end_time = time.time()
    logger.info(f"--- Gmail Ingestion Run Finished ---")
    logger.info(f"Processed {processed_count} messages in {end_time - start_time:.2f}s")


if __name__ == "__main__":
    main()
