from googleapiclient.discovery import Resource
from googleapiclient.http import MediaIoBaseDownload
from googleapiclient.errors import HttpError
from siphon_server.sources.drive.pipeline.drive_service import get_drive_service
from siphon_server.sources.drive.pipeline.drive_discovery import get_documents
from pathlib import Path
import logging
import io

# Assuming logger is set up in your main script
logger = logging.getLogger(__name__)

# A set of common Google-native MIME types that require 'export_media'
GOOGLE_NATIVE_MIMETYPES = {
    "application/vnd.google-apps.document",
    "application/vnd.google-apps.spreadsheet",
    "application/vnd.google-apps.presentation",
    "application/vnd.google-apps.drawing",
    "application/vnd.google-apps.form",
    "application/vnd.google-apps.jam",
    "application/vnd.google-apps.script",
}


def _download_drive_file(
    drive_service: Resource,
    file_id: str,
    sink: io.BufferedIOBase,
    export_mime_type: str = "text/plain",
) -> tuple[bool, str]:
    """
    Core download logic. Fetches a file from Drive and streams it
    into a provided file-like object (sink).

    Args:
        drive_service: An authorized Google Drive v3 service object.
        file_id: The ID of the file to download.
        sink: A writeable, binary file-like object (e.g., io.BytesIO()
              or a file handle from open(..., "wb")).
        export_mime_type: The target MIME type for Google-native exports.

    Returns:
        A tuple of (bool_success, file_name_str).
    """
    file_name = file_id  # Default to ID if metadata fails
    try:
        # Step 1: Get file metadata to check its MIME type
        logger.info(f"Fetching metadata for file: {file_id}")
        file_meta = (
            drive_service.files().get(fileId=file_id, fields="mimeType, name").execute()
        )

        mime_type = file_meta.get("mimeType")
        file_name = file_meta.get("name", file_id)

        request = None
        if mime_type in GOOGLE_NATIVE_MIMETYPES:
            # Step 2a: It's a Google-native file. We must EXPORT it.
            logger.info(
                f"'{file_name}' is Google-native ({mime_type}). "
                f"Exporting as '{export_mime_type}'."
            )
            request = drive_service.files().export_media(
                fileId=file_id, mimeType=export_mime_type
            )
        else:
            # Step 2b: It's a standard file. We can GET it directly.
            logger.info(f"'{file_name}' is a standard file ({mime_type}). Downloading.")
            request = drive_service.files().get_media(fileId=file_id)

        # Step 3: Create downloader with the provided sink
        downloader = MediaIoBaseDownload(sink, request)

        # Step 4: Execute the download
        done = False
        while not done:
            status, done = downloader.next_chunk()
            if status:
                logger.debug(
                    f"Download progress for '{file_name}': {int(status.progress() * 100)}%"
                )

        # Note: We don't close the sink, the caller is responsible for it
        return True, file_name

    except HttpError as error:
        logger.error(f"Error downloading file {file_id} ('{file_name}'): {error}")
        return False, file_name
    except Exception as e:
        logger.error(f"An unexpected error occurred for {file_id} ('{file_name}'): {e}")
        return False, file_name


def get_document_by_id(
    file_id: str,
    drive_service: "Resource",
    export_mime_type: str = "text/plain",
) -> io.BytesIO | None:
    """
    Downloads a file from Drive by its ID to an in-memory buffer.
    """
    try:
        fh = io.BytesIO()
        success, file_name = _download_drive_file(
            drive_service, file_id, fh, export_mime_type
        )

        if success:
            logger.info(f"Successfully downloaded '{file_name}' to memory.")
            fh.seek(0)  # Rewind buffer to the beginning for reading
            return fh
        else:
            fh.close()
            return None
    except Exception as e:
        logger.error(f"Error preparing in-memory download for {file_id}: {e}")
        return None


def save_document_by_id(
    file_id: str,
    drive_service: "Resource",
    filepath: str | Path,
    export_mime_type: str = "text/plain",
) -> bool:
    """
    Downloads a file from Drive by its ID and saves it to a disk file.
    """
    try:
        # Create the file handle (sink)
        with open(filepath, "wb") as f:
            success, file_name = _download_drive_file(
                drive_service, file_id, f, export_mime_type
            )

        if success:
            logger.info(
                f"Successfully downloaded and saved '{file_name}' to {filepath}"
            )
        else:
            logger.warning(f"Download failed for '{file_name}'.")
            # Clean up the (likely empty) file on failure
            if Path(filepath).exists():
                Path(filepath).unlink()

        return success

    except IOError as e:
        logger.error(f"Could not open or write to file {filepath}: {e}")
        return False
    except Exception as e:
        logger.error(f"Error preparing disk download for {file_id}: {e}")
        return False


if __name__ == "__main__":
    drive_service = get_drive_service()

    if drive_service:
        logger.info("Fetching first Google Doc...")
        try:
            # Use the generator to get the first doc
            first_doc = next(get_documents(drive_service))
            doc_id = first_doc["id"]
            doc_name = first_doc["name"]

            logger.info(f"Downloading content for: {doc_name} ({doc_id})")

            # Download the doc as plain text
            file_buffer = get_document_by_id(doc_id, drive_service, "text/plain")

            if file_buffer:
                content = file_buffer.read().decode("utf-8")
                logger.info(f"--- Content for {doc_name} ---")
                logger.info(content[:500] + "...")
                logger.info("--- End Content ---")
                file_buffer.close()

        except StopIteration:
            logger.warning("No Google Docs found in this account.")
        except Exception as e:
            logger.error(f"An error occurred in main: {e}")

    else:
        logger.critical("Could not get Drive service.")
