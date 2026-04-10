class ApplicationError(Exception):
    """Base class for all application-layer errors."""


class BalanceNotFoundError(ApplicationError):
    """Raised when no balance record exists for the given user_id."""


class DuplicateEventError(ApplicationError):
    """Raised when a Kafka event_id has already been applied to the wallet."""
