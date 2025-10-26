import re
import sqlite3
from pathlib import Path
from xdg_base_dirs import xdg_cache_home


class YouTubeTranscriptCache:
    """
    Minimal SQLite-backed cache for YouTube transcripts.

    Location: $XDG_CACHE_HOME/youtube/cache.db
    Schema:   transcripts(id TEXT PRIMARY KEY, transcript TEXT NOT NULL)
    """

    _ID_RE = re.compile(r"^[A-Za-z0-9]{11}$")

    def __init__(self):
        cache_root = Path(xdg_cache_home()) / "youtube"
        cache_root.mkdir(parents=True, exist_ok=True)
        self.path = cache_root / "cache.db"
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

    def close(self) -> None:
        try:
            self._con.close()
        except Exception:
            pass

    @staticmethod
    def _validate_id(video_id: str) -> None:
        if not YouTubeTranscriptCache._ID_RE.match(video_id):
            raise ValueError("video_id must be 11 chars of [A-Za-z0-9].")
