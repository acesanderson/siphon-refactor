from siphon_server.sources.drive.pipeline.drive_service import get_drive_service
from siphon_api.metadata import DriveMetadata
from googleapiclient.discovery import Resource
from googleapiclient.errors import HttpError
import logging

# Assuming logger is set up
logger = logging.getLogger(__name__)


def _get_metadata_by_id(file_id: str, drive_service: Resource) -> dict | None:
    """
    Retrieves all available metadata for a specific file.

    Args:
        file_id: The ID of the file.
        drive_service: An authorized Google Drive v3 service object.

    Returns:
        A dictionary (File resource) containing all metadata, or None on error.
    """
    try:
        # 'fields="*"' tells the API to return all fields for this resource.
        # 'supportsAllDrives=True' is good practice to include
        # in case you use this with Shared Drives (enterprise).
        file_meta = (
            drive_service.files()
            .get(fileId=file_id, fields="*", supportsAllDrives=True)
            .execute()
        )
        return file_meta

    except HttpError as error:
        logger.error(f"Error fetching metadata for file {file_id}: {error}")
        return None
    except Exception as e:
        logger.error(f"An unexpected error occurred for {file_id}: {e}")
        return None


def get_metadata_by_id(file_id: str, drive_service: Resource) -> DriveMetadata | None:
    """
    Wrapper function to retrieve metadata for a specific file.
    Returns a DriveMetadata object.
    """
    metadata_dict = _get_metadata_by_id(file_id, drive_service)
    if metadata_dict is None:
        return None
    return DriveMetadata(**metadata_dict)


if __name__ == "__main__":
    drive_service = get_drive_service()
    # sheet_url = "https://docs.google.com/spreadsheets/d/1H7QTl1F7rJsVkCHtUyIzk1RSGnpyzZZf5nVNhRQdmyw/edit?gid=0#gid=0"
    doc = "https://docs.google.com/document/d/1L4rwvx5P33LbPcX2dawSYrE2Z38yXwBBRaPVJakHozU/edit?tab=t.0"
    doc_id = doc.split("/d/")[1].split("/")[0]
    drive_service = get_drive_service()
    metadata = get_metadata_by_id(doc_id, drive_service)
