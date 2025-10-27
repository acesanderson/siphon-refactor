"""
Two caches:
- youtube metadata
- youtube transcripts
"""

import re
import sqlite3
from pathlib import Path
from xdg_base_dirs import xdg_cache_home
from typing import Any
import json


class YouTubeMetadataCache:
    """
    Minimal SQLite-backed cache for YouTube video metadata.
    Location: $XDG_CACHE_HOME/youtube/metadata_cache.db
    Schema:   id TEST PRIMARY KEY, metadata fields as columns"

    Validates video_id format and metadata schema on set.
    Should flag if schema drifts.
    """

    _ID_RE = re.compile(r"^[A-Za-z0-9]{11}$")

    def __init__(self):
        cache_root = Path(xdg_cache_home()) / "siphon" / "youtube"
        cache_root.mkdir(parents=True, exist_ok=True)
        self.path = cache_root / "metadata_cache.db"
        self._con = sqlite3.connect(self.path)
        self._con.execute(
            "CREATE TABLE IF NOT EXISTS metadata ("
            "id TEXT PRIMARY KEY, "
            "url TEXT, "
            "domain TEXT, "
            "title TEXT, "
            "published_date TEXT, "
            "video_id TEXT, "
            "channel TEXT, "
            "duration TEXT, "
            "description TEXT, "
            "tags TEXT)"
        )
        self._con.commit()

    # Getters and setters
    def get(self, video_id: str) -> dict[str, Any] | None:
        self._validate_id(video_id)
        # Original fetch logic
        row = self._con.execute(
            "SELECT * FROM metadata WHERE id = ?",
            (video_id,),
        ).fetchone()
        if row:
            columns = [
                column[0] for column in self._con.execute("PRAGMA table_info(metadata)")
            ]
            metadata_dict = dict(zip(columns, row))

            # --- Convert tags JSON string back to list ---
            tags_value = metadata_dict.get("tags")
            if isinstance(tags_value, str):
                try:
                    parsed_tags = json.loads(tags_value)
                    # Only replace if parsing results in a list
                    if isinstance(parsed_tags, list):
                        metadata_dict["tags"] = parsed_tags
                except json.JSONDecodeError:
                    # If it's not valid JSON, leave the original string
                    pass
            return metadata_dict  # Return the potentially modified dictionary
        return None  # Return None if row wasn't found

    def set(self, video_id: str, metadata: dict[str, str]) -> None:
        self._validate_id(video_id)
        self._validate_schema(metadata)
        # --- Convert tags list to JSON string ---
        tags_value = metadata.get("tags")
        if isinstance(tags_value, list):
            tags_json = json.dumps(tags_value)  # Serialize list to JSON string
        elif tags_value is None:
            tags_json = None  # Keep None as None
        else:
            tags_json = str(tags_value)  # Convert other types just in case
        # ----------------------------------------

        self._con.execute(
            "INSERT OR REPLACE INTO metadata (id, url, domain, title, published_date, "
            "video_id, channel, duration, description, tags) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                video_id,
                metadata.get("url"),
                metadata.get("domain"),
                metadata.get("title"),
                metadata.get("published_date"),
                metadata.get("video_id"),
                metadata.get("channel"),
                metadata.get("duration"),
                metadata.get("description"),
                tags_json,
            ),
        )
        self._con.commit()

    # Validation methods
    @staticmethod
    def _validate_schema(metadata: dict[str, str]) -> None:
        """
        Validate that metadata contains expected fields.
        Should be 1:1 mapping to the schema defined in __init__;
        if not, flag schema drift.
        """
        expected_fields = {
            "url",
            "domain",
            "title",
            "published_date",
            "video_id",
            "channel",
            "duration",
            "description",
            "tags",
        }
        metadata_fields = set(metadata.keys())
        if not expected_fields.issubset(metadata_fields):
            missing = expected_fields - metadata_fields
            raise ValueError(f"Metadata is missing expected fields: {missing}")
        # Detect extra fields (schema drift)
        extra = metadata_fields - expected_fields
        if extra:
            raise ValueError(
                f"Metadata contains unexpected fields (schema drift): {extra}"
            )

    @staticmethod
    def _validate_id(video_id: str) -> None:
        if not YouTubeMetadataCache._ID_RE.match(video_id):
            raise ValueError("video_id must be 11 chars of [A-Za-z0-9].")


class YouTubeTranscriptCache:
    """
    Minimal SQLite-backed cache for YouTube transcripts.

    Location: $XDG_CACHE_HOME/youtube/transcript_cache.db
    Schema:   transcripts(id TEXT PRIMARY KEY, transcript TEXT NOT NULL)
    """

    _ID_RE = re.compile(r"^[A-Za-z0-9]{11}$")

    def __init__(self):
        cache_root = Path(xdg_cache_home()) / "siphon" / "youtube"
        cache_root.mkdir(parents=True, exist_ok=True)
        self.path = cache_root / "transcript_cache.db"
        self._con = sqlite3.connect(self.path)
        self._con.execute(
            "CREATE TABLE IF NOT EXISTS transcripts ("
            "id TEXT PRIMARY KEY, "
            "transcript TEXT NOT NULL)"
        )
        self._con.commit()

    def get(self, video_id: str) -> str | None:
        self._validate_id(video_id)
        row = self._con.execute(
            "SELECT transcript FROM transcripts WHERE id = ?",
            (video_id,),
        ).fetchone()
        return row[0] if row else None

    def set(self, video_id: str, transcript: str) -> None:
        self._validate_id(video_id)
        self._con.execute(
            "INSERT OR REPLACE INTO transcripts (id, transcript) VALUES (?, ?)",
            (video_id, transcript),
        )
        self._con.commit()

    @staticmethod
    def _validate_id(video_id: str) -> None:
        if not YouTubeTranscriptCache._ID_RE.match(video_id):
            raise ValueError("video_id must be 11 chars of [A-Za-z0-9].")
