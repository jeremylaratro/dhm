"""
Custom exceptions for the Dependency Health Monitor.
"""


class DHMError(Exception):
    """Base exception for all DHM errors."""

    def __init__(self, message: str, details: str | None = None):
        super().__init__(message)
        self.message = message
        self.details = details

    def __str__(self) -> str:
        if self.details:
            return f"{self.message}: {self.details}"
        return self.message


class PackageNotFoundError(DHMError):
    """Raised when a package cannot be found on PyPI."""

    def __init__(self, package_name: str):
        super().__init__(
            f"Package not found: {package_name}",
            details="The package does not exist on PyPI or may have been removed.",
        )
        self.package_name = package_name


class RepositoryNotFoundError(DHMError):
    """Raised when a repository cannot be found on GitHub/GitLab."""

    def __init__(self, repo_identifier: str):
        super().__init__(
            f"Repository not found: {repo_identifier}",
            details="The repository does not exist or is private.",
        )
        self.repo_identifier = repo_identifier


class RateLimitError(DHMError):
    """Raised when an API rate limit is exceeded."""

    def __init__(
        self,
        service: str,
        reset_time: int | None = None,
    ):
        details = None
        if reset_time:
            details = f"Rate limit resets in {reset_time} seconds."
        super().__init__(f"Rate limit exceeded for {service}", details=details)
        self.service = service
        self.reset_time = reset_time


class CacheError(DHMError):
    """Raised when a cache operation fails."""

    def __init__(self, operation: str, details: str | None = None):
        super().__init__(f"Cache error during {operation}", details=details)
        self.operation = operation


class ParsingError(DHMError):
    """Raised when a dependency file cannot be parsed."""

    def __init__(self, file_path: str, details: str | None = None):
        super().__init__(f"Failed to parse dependency file: {file_path}", details=details)
        self.file_path = file_path


class ValidationError(DHMError):
    """Raised when data validation fails."""

    def __init__(self, field: str, value: str, reason: str):
        super().__init__(
            f"Validation failed for {field}",
            details=f"Value '{value}' is invalid: {reason}",
        )
        self.field = field
        self.value = value
        self.reason = reason


class NetworkError(DHMError):
    """Raised when a network request fails."""

    def __init__(self, url: str, status_code: int | None = None, details: str | None = None):
        message = f"Network request failed: {url}"
        if status_code:
            message += f" (status {status_code})"
        super().__init__(message, details=details)
        self.url = url
        self.status_code = status_code
