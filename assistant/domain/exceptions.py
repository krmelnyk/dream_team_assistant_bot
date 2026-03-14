"""Application-specific exceptions and CLI error formatting."""

from __future__ import annotations

from functools import wraps


class AssistantError(Exception):
    """Base exception for all assistant-specific errors."""


class ValidationError(AssistantError):
    """Raised when provided data is invalid."""


class NotFoundError(AssistantError):
    """Raised when the requested entity does not exist."""


class CommandError(AssistantError):
    """Raised when a command is malformed or unsupported."""


class StorageError(AssistantError):
    """Raised when data cannot be read or written."""


def format_error(error: Exception) -> str:
    """Convert exceptions into user-friendly CLI messages."""

    if isinstance(error, AssistantError):
        return str(error)

    if isinstance(error, KeyError) and error.args:
        return str(error.args[0])

    if isinstance(error, ValueError):
        return str(error)

    if isinstance(error, IndexError):
        return "Enter the required arguments for the command."

    return "Unexpected error occurred. Please try again."


def input_error(func):
    """Decorator for CLI handlers that formats exceptions for output."""

    @wraps(func)
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as error:
            return format_error(error)

    return inner