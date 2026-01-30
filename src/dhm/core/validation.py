"""
Input validation utilities for DHM.

Provides validation functions for package names, paths, and other user inputs
to prevent security issues like path traversal and injection attacks.
"""

import re
from pathlib import Path
from urllib.parse import quote

from dhm.core.exceptions import ValidationError

# PEP 503 normalized package name pattern
# https://peps.python.org/pep-0503/#normalized-names
_PACKAGE_NAME_PATTERN = re.compile(r"^([A-Z0-9]|[A-Z0-9][A-Z0-9._-]*[A-Z0-9])$", re.IGNORECASE)

# Maximum recursion depth for -r includes in requirements files
MAX_INCLUDE_DEPTH = 5

# Maximum response size (10 MB)
MAX_RESPONSE_SIZE = 10 * 1024 * 1024


def validate_package_name(name: str) -> str:
    """Validate and normalize a package name according to PEP 503.

    Args:
        name: Package name to validate.

    Returns:
        Normalized package name (lowercase, hyphens replaced with dashes).

    Raises:
        ValidationError: If the package name is invalid.
    """
    if not name:
        raise ValidationError("package_name", name or "", "Package name cannot be empty")

    # Check length (PyPI limit is 150 characters)
    if len(name) > 150:
        raise ValidationError(
            "package_name", name[:50] + "...", "Package name exceeds 150 character limit"
        )

    # Check for null bytes or control characters
    if any(ord(c) < 32 or ord(c) == 127 for c in name):
        raise ValidationError(
            "package_name", repr(name), "Package name contains invalid control characters"
        )

    # Validate against PEP 503 pattern
    if not _PACKAGE_NAME_PATTERN.match(name):
        raise ValidationError(
            "package_name",
            name,
            "Package name must start and end with alphanumeric characters "
            "and contain only alphanumerics, dots, hyphens, and underscores",
        )

    # Normalize: lowercase and replace underscores/dots with hyphens
    normalized = re.sub(r"[-_.]+", "-", name.lower())
    return normalized


def encode_package_name_for_url(name: str) -> str:
    """URL-encode a package name for use in API URLs.

    Args:
        name: Package name to encode.

    Returns:
        URL-encoded package name.
    """
    return quote(name, safe="")


def validate_include_path(
    include_path: str,
    base_path: Path,
    current_file: Path,
) -> Path:
    """Validate an include path from a requirements file.

    Ensures the include path stays within the project directory to prevent
    path traversal attacks.

    Args:
        include_path: The path specified in the -r directive.
        base_path: The root project directory (boundary).
        current_file: The file containing the -r directive.

    Returns:
        Resolved, validated Path object.

    Raises:
        ValidationError: If the path escapes the project boundary or is invalid.
    """
    if not include_path:
        raise ValidationError("include_path", "", "Include path cannot be empty")

    # Check for null bytes
    if "\x00" in include_path:
        raise ValidationError("include_path", repr(include_path), "Path contains null bytes")

    # Resolve the include path relative to the current file's directory
    resolved_path = (current_file.parent / include_path).resolve()

    # Resolve the base path to ensure consistent comparison
    resolved_base = base_path.resolve()

    # Check if the resolved path is within the base directory
    try:
        resolved_path.relative_to(resolved_base)
    except ValueError:
        raise ValidationError(
            "include_path",
            include_path,
            f"Path escapes project directory (resolves to {resolved_path})",
        )

    # Check for symlinks pointing outside the project
    if resolved_path.is_symlink():
        real_path = resolved_path.resolve(strict=True)
        try:
            real_path.relative_to(resolved_base)
        except ValueError:
            raise ValidationError(
                "include_path",
                include_path,
                "Symlink target escapes project directory",
            )

    return resolved_path


def check_recursion_depth(depth: int, max_depth: int = MAX_INCLUDE_DEPTH) -> None:
    """Check if recursion depth exceeds the limit.

    Args:
        depth: Current recursion depth.
        max_depth: Maximum allowed depth.

    Raises:
        ValidationError: If depth exceeds the limit.
    """
    if depth > max_depth:
        raise ValidationError(
            "include_depth",
            str(depth),
            f"Include depth exceeds maximum of {max_depth} "
            "(possible circular include or deeply nested files)",
        )


def validate_response_size(
    content_length: int | None,
    max_size: int = MAX_RESPONSE_SIZE,
) -> None:
    """Validate that a response size is within acceptable limits.

    Args:
        content_length: The Content-Length header value (may be None).
        max_size: Maximum allowed response size in bytes.

    Raises:
        ValidationError: If the response is too large.
    """
    if content_length is not None and content_length > max_size:
        size_mb = content_length / (1024 * 1024)
        max_mb = max_size / (1024 * 1024)
        raise ValidationError(
            "response_size",
            f"{size_mb:.1f} MB",
            f"Response exceeds maximum size of {max_mb:.0f} MB",
        )
