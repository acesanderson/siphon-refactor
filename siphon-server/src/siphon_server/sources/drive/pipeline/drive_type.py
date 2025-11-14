from enum import Enum


# Enumeration for different Google Drive file types
class DriveType(Enum):
    DOCS = "docs"
    SHEETS = "sheets"
    SLIDES = "slides"
    FORMS = "forms"
    DRIVE = "drive"


# Registry mapping for Google Drive API services
DRIVE_TYPE_MAPPING = {
    DriveType.DRIVE: {
        "scope": "https://www.googleapis.com/auth/drive.readonly",
        "service-name": "drive",
        "service-version": "v3",
    },
    DriveType.DOCS: {
        "scope": "https://www.googleapis.com/auth/documents.readonly",
        "service-name": "docs",
        "service-version": "v1",
    },
    DriveType.SHEETS: {
        "scope": "https://www.googleapis.com/auth/spreadsheets.readonly",
        "service-name": "sheets",
        "service-version": "v4",
    },
    DriveType.SLIDES: {
        "scope": "https://www.googleapis.com/auth/presentations.readonly",
        "service-name": "slides",
        "service-version": "v1",
    },
    DriveType.FORMS: {
        "scope": "https://www.googleapis.com/auth/forms.responses.readonly",
        "service-name": "forms",
        "service-version": "v1",
    },
}
