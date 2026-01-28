"""
Abstract base class for data collectors.

Defines the interface that all collectors must implement.
"""

from abc import ABC, abstractmethod
from typing import Any, Optional

import aiohttp


class Collector(ABC):
    """Abstract base class for data collectors.

    All collectors share common functionality like session management
    and error handling. Specific collectors implement the fetch methods
    for their respective data sources.
    """

    def __init__(
        self,
        session: Optional[aiohttp.ClientSession] = None,
        timeout: int = 30,
    ):
        """Initialize the collector.

        Args:
            session: Optional aiohttp session. If not provided, one will
                     be created when needed.
            timeout: Request timeout in seconds.
        """
        self._session = session
        self._owns_session = session is None
        self.timeout = aiohttp.ClientTimeout(total=timeout)

    @property
    def session(self) -> aiohttp.ClientSession:
        """Get or create the aiohttp session."""
        if self._session is None:
            self._session = aiohttp.ClientSession(timeout=self.timeout)
            self._owns_session = True
        return self._session

    async def close(self) -> None:
        """Close the session if we own it."""
        if self._owns_session and self._session is not None:
            await self._session.close()
            self._session = None

    async def __aenter__(self) -> "Collector":
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Async context manager exit."""
        await self.close()

    @abstractmethod
    async def fetch(self, identifier: str) -> Any:
        """Fetch data for the given identifier.

        Args:
            identifier: The package name, repository URL, or other identifier.

        Returns:
            The fetched data, specific to each collector type.

        Raises:
            DHMError: If the fetch fails.
        """
        pass

    def _build_headers(self) -> dict[str, str]:
        """Build common request headers.

        Override in subclasses to add authentication or other headers.
        """
        return {
            "User-Agent": "DependencyHealthMonitor/0.1.0",
            "Accept": "application/json",
        }
