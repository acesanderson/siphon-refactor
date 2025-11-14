from siphon_server.sources.drive.pipeline.drive_service import get_drive_service
import logging
from googleapiclient.discovery import Resource
from googleapiclient.errors import HttpError


# Assuming logger is set up
logger = logging.getLogger(__name__)


def get_documents(drive_service: Resource):
    """
    Retrieve all Google Docs from Drive with pagination support.

    Generator function that yields Google Docs files one at a time by iterating through
    paginated API results. Fetches only essential metadata (id, name, mimeType) to minimize
    bandwidth usage.

    Args:
        drive_service: An authenticated Google Drive API service resource.

    Yields:
        dict: File objects containing id, name, and mimeType for each Google Doc found.

    Raises:
        Logs HttpError exceptions but continues gracefully; stops iteration on API failures.

    Example:
        for doc in get_documents(drive_service):
            print(f"Found: {doc['name']} (ID: {doc['id']})")
    """
    page_token = None

    # MIME type for Google Docs
    query = "mimeType='application/vnd.google-apps.document'"

    # Use 'fields' to specify exactly what data you want.
    # This is more efficient than getting the default.
    # 'id, name, mimeType' are the basics you need.
    fields_to_get = "nextPageToken, files(id, name, mimeType)"

    while True:
        try:
            results = (
                drive_service.files()
                .list(
                    q=query,
                    pageSize=100,  # Max allowed is 1000, 100 is a good default
                    fields=fields_to_get,
                    pageToken=page_token,
                )
                .execute()
            )

            files = results.get("files", [])
            for file in files:
                # 'yield' turns this into a generator
                # The caller will get one file object at a time
                yield file

            page_token = results.get("nextPageToken", None)
            if page_token is None:
                # No more pages, exit the loop
                break

        except HttpError as error:
            logger.error(f"An error occurred: {error}")
            break


def doc_exists(id: str, drive_service: Resource) -> bool:
    """
    Check if a Google Drive document exists by file ID.

    Queries the Drive API to verify document existence without loading full metadata.
    Returns False for 404 (not found) and other HTTP errors; logs non-404 errors for debugging.

    Args:
        id: The Google Drive file ID to check (e.g., "1iA1SHQ2NYFlMh8qrQWXcc6idJmaSf3m7p8M2NBima6I").
        drive_service: An authenticated Google Drive API service resource.

    Returns:
        bool: True if the document exists, False if not found or inaccessible.
    """
    try:
        drive_service.files().get(fileId=id).execute()
        return True
    except HttpError as error:
        if error.resp.status == 404:
            return False
        else:
            logger.error(
                f"An error occurred while checking document existence: {error}"
            )
            return False


if __name__ == "__main__":
    drive_service = get_drive_service()
    #
    # if drive_service:
    #     logger.info("Fetching Google Docs...")
    #     # 2. 'get_documents' is a generator, so you loop over it
    #     doc_count = 0
    #     for document in get_documents(drive_service):
    #         doc_count += 1
    #         logger.info(f"Found: {document['name']} (ID: {document['id']})")
    #
    #     logger.info(f"Total docs found: {doc_count}")
    # else:
    #     logger.critical("Could not get Drive service.")
    #     pass
    #
    id = "1iA1SHQ2NYFlMh8qrQWXcc6idJmaSf3m7p8M2NBima6I"
    exists = doc_exists(id, drive_service)
    if exists:
        logger.info(f"Document with ID {id} exists.")
    else:
        logger.info(f"Document with ID {id} does not exist.")
