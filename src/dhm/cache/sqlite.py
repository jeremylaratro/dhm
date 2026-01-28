"""
SQLite-based cache implementation.

Provides persistent caching for API responses with TTL-based expiration
and ETag support for conditional requests.
"""

import json
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Generator, Optional

from dhm.core.exceptions import CacheError


class CacheLayer:
    """SQLite-based cache for API responses.

    Stores cached data with TTL-based expiration and optional ETag
    support for conditional HTTP requests.
    """

    DEFAULT_TTL = 3600  # 1 hour

    def __init__(
        self,
        db_path: Optional[Path] = None,
        default_ttl: int = DEFAULT_TTL,
    ):
        """Initialize the cache layer.

        Args:
            db_path: Path to SQLite database file. Defaults to ~/.dhm/cache.db
            default_ttl: Default time-to-live in seconds for cached entries.
        """
        if db_path is None:
            db_path = Path.home() / ".dhm" / "cache.db"

        self.db_path = db_path
        self.default_ttl = default_ttl

        # Ensure parent directory exists
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        # Initialize database
        self._init_db()

    def _init_db(self) -> None:
        """Initialize the cache database schema."""
        try:
            with self._connection() as conn:
                conn.executescript("""
                    CREATE TABLE IF NOT EXISTS cache (
                        key TEXT PRIMARY KEY,
                        value TEXT NOT NULL,
                        etag TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        expires_at TIMESTAMP NOT NULL
                    );

                    CREATE INDEX IF NOT EXISTS idx_expires
                    ON cache(expires_at);

                    CREATE INDEX IF NOT EXISTS idx_key_prefix
                    ON cache(key);
                """)
        except sqlite3.Error as e:
            raise CacheError("initialization", str(e))

    @contextmanager
    def _connection(self) -> Generator[sqlite3.Connection, None, None]:
        """Get a database connection context manager.

        Yields:
            sqlite3.Connection that auto-commits on success.
        """
        conn = sqlite3.connect(
            self.db_path,
            detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES,
        )
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except sqlite3.Error as e:
            conn.rollback()
            raise CacheError("database operation", str(e))
        finally:
            conn.close()

    def get(self, key: str) -> Optional[tuple[Any, Optional[str]]]:
        """Get cached value and ETag if not expired.

        Args:
            key: Cache key.

        Returns:
            Tuple of (value, etag) or None if not found or expired.
        """
        try:
            with self._connection() as conn:
                row = conn.execute(
                    """
                    SELECT value, etag FROM cache
                    WHERE key = ? AND expires_at > datetime('now')
                    """,
                    (key,),
                ).fetchone()

                if row:
                    value = json.loads(row["value"])
                    return value, row["etag"]
                return None

        except (sqlite3.Error, json.JSONDecodeError) as e:
            raise CacheError("get", str(e))

    def get_value(self, key: str) -> Optional[Any]:
        """Get cached value only (without ETag).

        Args:
            key: Cache key.

        Returns:
            Cached value or None if not found or expired.
        """
        result = self.get(key)
        return result[0] if result else None

    def set(
        self,
        key: str,
        value: Any,
        ttl_seconds: Optional[int] = None,
        etag: Optional[str] = None,
    ) -> None:
        """Store value in cache with TTL.

        Args:
            key: Cache key.
            value: Value to cache (must be JSON-serializable).
            ttl_seconds: Time-to-live in seconds. Uses default if not specified.
            etag: Optional ETag for conditional requests.
        """
        if ttl_seconds is None:
            ttl_seconds = self.default_ttl

        try:
            value_json = json.dumps(value)

            with self._connection() as conn:
                conn.execute(
                    """
                    INSERT OR REPLACE INTO cache (key, value, etag, expires_at)
                    VALUES (?, ?, ?, datetime('now', ? || ' seconds'))
                    """,
                    (key, value_json, etag, str(ttl_seconds)),
                )

        except (sqlite3.Error, json.JSONEncodeError) as e:
            raise CacheError("set", str(e))

    def delete(self, key: str) -> bool:
        """Delete a specific cache entry.

        Args:
            key: Cache key to delete.

        Returns:
            True if entry was deleted, False if not found.
        """
        try:
            with self._connection() as conn:
                cursor = conn.execute(
                    "DELETE FROM cache WHERE key = ?",
                    (key,),
                )
                return cursor.rowcount > 0

        except sqlite3.Error as e:
            raise CacheError("delete", str(e))

    def invalidate(self, pattern: str) -> int:
        """Invalidate cache entries matching pattern.

        Args:
            pattern: SQL LIKE pattern (e.g., "pypi:%" for all PyPI entries).

        Returns:
            Number of entries deleted.
        """
        try:
            with self._connection() as conn:
                cursor = conn.execute(
                    "DELETE FROM cache WHERE key LIKE ?",
                    (pattern,),
                )
                return cursor.rowcount

        except sqlite3.Error as e:
            raise CacheError("invalidate", str(e))

    def cleanup(self) -> int:
        """Remove expired entries.

        Returns:
            Number of entries removed.
        """
        try:
            with self._connection() as conn:
                cursor = conn.execute(
                    "DELETE FROM cache WHERE expires_at < datetime('now')"
                )
                return cursor.rowcount

        except sqlite3.Error as e:
            raise CacheError("cleanup", str(e))

    def clear(self) -> int:
        """Clear all cache entries.

        Returns:
            Number of entries removed.
        """
        return self.invalidate("%")

    def stats(self) -> dict[str, Any]:
        """Get cache statistics.

        Returns:
            Dict with cache statistics including size and entry counts.
        """
        try:
            with self._connection() as conn:
                # Total entries
                total = conn.execute("SELECT COUNT(*) FROM cache").fetchone()[0]

                # Valid entries
                valid = conn.execute(
                    "SELECT COUNT(*) FROM cache WHERE expires_at > datetime('now')"
                ).fetchone()[0]

                # Expired entries
                expired = total - valid

                # Size by key prefix
                prefixes = conn.execute(
                    """
                    SELECT
                        SUBSTR(key, 1, INSTR(key || ':', ':') - 1) as prefix,
                        COUNT(*) as count
                    FROM cache
                    WHERE expires_at > datetime('now')
                    GROUP BY prefix
                    """
                ).fetchall()

                # Database file size
                db_size = self.db_path.stat().st_size if self.db_path.exists() else 0

                return {
                    "total_entries": total,
                    "valid_entries": valid,
                    "expired_entries": expired,
                    "db_size_bytes": db_size,
                    "db_path": str(self.db_path),
                    "entries_by_prefix": {row["prefix"]: row["count"] for row in prefixes},
                }

        except sqlite3.Error as e:
            raise CacheError("stats", str(e))

    def get_or_set(
        self,
        key: str,
        factory: callable,
        ttl_seconds: Optional[int] = None,
    ) -> Any:
        """Get cached value or compute and cache it.

        Args:
            key: Cache key.
            factory: Callable that produces the value if not cached.
            ttl_seconds: Time-to-live in seconds.

        Returns:
            Cached or computed value.
        """
        result = self.get_value(key)
        if result is not None:
            return result

        value = factory()
        self.set(key, value, ttl_seconds)
        return value

    async def async_get_or_set(
        self,
        key: str,
        factory: callable,
        ttl_seconds: Optional[int] = None,
    ) -> Any:
        """Async version of get_or_set.

        Args:
            key: Cache key.
            factory: Async callable that produces the value if not cached.
            ttl_seconds: Time-to-live in seconds.

        Returns:
            Cached or computed value.
        """
        result = self.get_value(key)
        if result is not None:
            return result

        value = await factory()
        self.set(key, value, ttl_seconds)
        return value

    @staticmethod
    def make_key(*parts: str) -> str:
        """Create a cache key from multiple parts.

        Args:
            *parts: Key components to join.

        Returns:
            Colon-separated cache key.
        """
        return ":".join(str(p) for p in parts)
