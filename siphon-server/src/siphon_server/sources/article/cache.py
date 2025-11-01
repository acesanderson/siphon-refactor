"""
One cache, for trafilatura article fetch results.
"""

import sqlite3
from pathlib import Path
from xdg_base_dirs import xdg_cache_home


class ArticleCache:
    """
    Minimal SQLite-backed cache for Article extraction.
    Trafilatura's fetch_url() method takes a URL and returns raw HTML, so this is a simple cache.
    Location: $XDG_CACHE_HOME/siphon/trafilatura/fetch_cache.db
    Schema:   url TEXT PRIMARY KEY, downloaded TEXT NOT NULL
    """

    def __init__(self):
        cache_root = Path(xdg_cache_home()) / "siphon" / "trafilatura"
        cache_root.mkdir(parents=True, exist_ok=True)
        self.path = cache_root / "fetch.db"
        self._con = sqlite3.connect(self.path)
        _ = self._con.execute(
            "CREATE TABLE IF NOT EXISTS fetch ("
            "url TEXT PRIMARY KEY, "
            "downloaded TEXT NOT NULL"
            ")"
        )
        self._con.commit()

    # Getters and setters
    def get(self, url: str) -> str | None:
        # Fetch row from database
        row = self._con.execute(
            "SELECT * FROM fetch WHERE url = ?",
            (url,),
        ).fetchone()
        if row:
            return row[1]  # downloaded
        return None

    def set(self, url: str, downloaded: str) -> None:
        self._con.execute(
            "INSERT OR REPLACE INTO fetch (url, downloaded) VALUES (?, ?)",
            (url, downloaded),
        )
        self._con.commit()

    def wipe(self) -> None:
        self._con.execute("DELETE FROM fetch")
        self._con.commit()
