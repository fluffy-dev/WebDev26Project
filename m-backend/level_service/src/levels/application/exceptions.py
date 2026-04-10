"""Application-level exceptions for the levels domain."""


class ApplicationError(Exception):
    """Base class for all application errors."""


class LevelNotFoundError(ApplicationError):
    """Raised when a requested level does not exist."""


class InvalidWpmError(ApplicationError):
    """Raised when the submitted WPM value is not positive."""
