"""Custom exceptions and CLI error handling for the assistant."""

from functools import wraps

ERROR_PREFIX = "[ERROR] "


class AssistantError(Exception):
    """Base exception for all assistant-specific errors."""


class ValidationError(AssistantError):
    """Raised when provided data is invalid."""


class NotFoundError(AssistantError):
    """Raised when the requested entity was not found."""


class CommandError(AssistantError):
    """Raised when a command is incomplete or malformed."""


class StorageError(AssistantError):
    """Raised when storage read/write operations fail."""


def format_error(error: Exception) -> str:
    """Convert exceptions into user-friendly CLI messages."""
    if isinstance(error, AssistantError):
        return f"{ERROR_PREFIX}{error}"

    if isinstance(error, KeyError):
        if error.args:
            return f"{ERROR_PREFIX}{error.args[0]}"
        return f"{ERROR_PREFIX}Entity not found."

    if isinstance(error, ValueError):
        return f"{ERROR_PREFIX}{error}"

    if isinstance(error, IndexError):
        return f"{ERROR_PREFIX}Enter the required arguments for the command."

    return f"{ERROR_PREFIX}Unexpected error occurred. Please try again."


def input_error(func):
    """Decorator for handling command errors in CLI handlers."""

    @wraps(func)
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as error:
            return format_error(error)

    return inner