from pathlib import Path
from siphon_api.requests import SiphonFile, SiphonRequest
from siphon_api.enums import SourceOrigin
import hashlib
import base64
import mimetypes


def create_siphon_request(file_path: Path) -> SiphonRequest:
    data = file_path.read_bytes()
    checksum = hashlib.sha256(data).hexdigest()
    mime_type, _ = mimetypes.guess_type(file_path.name)
    extension = file_path.suffix.lower()

    siphon_file = SiphonFile(
        data=base64.b64encode(data).decode(),
        checksum=checksum,
        mime_type=mime_type or "application/octet-stream",
        extension=extension,
    )

    return SiphonRequest(
        source=str(file_path.resolve()),
        origin=SourceOrigin.FILE_PATH,
        file=siphon_file,
    )


if __name__ == "__main__":
    from siphon_client.client.example import EXAMPLE_MP3, EXAMPLE_WAV
