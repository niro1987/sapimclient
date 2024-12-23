"""Exceptions for Python SAP Incentive Management Client."""

from typing import Any


class SAPExceptionError(Exception):
    """Base exception for Python SAP Incentive Management Client."""


class SAPConnectionError(SAPExceptionError):
    """Exception to indicate connection error."""

    def __init__(self, message: str) -> None:
        """Initialize a Not Found exception."""
        super().__init__(message)


class SAPResponseError(SAPExceptionError):
    """Exception to indicate an unexpected response."""

    def __init__(self, message: str) -> None:
        """Initialize a Not Found exception."""
        super().__init__(message)


class SAPBadRequestError(SAPExceptionError):
    """Exception to indicate an error with the request."""

    def __init__(self, message: str, data: dict[str, Any]) -> None:
        """Initialize a Bad Request exception."""
        self.data = data
        super().__init__(message, {'data': data})


class SAPNotModifiedError(SAPExceptionError):
    """Exception to indicate 304 - Not Modified response."""


class SAPAlreadyExistsError(SAPExceptionError):
    """Exception to indicate resource with same key already exists."""

    def __init__(self, message: str) -> None:
        """Initialize a Not Found exception."""
        super().__init__(message)


class SAPMissingFieldError(SAPExceptionError):
    """Exception to indicate one or more required fields are missing."""

    def __init__(self, fields: dict[str, Any]) -> None:
        """Initialize a Missing Required Field exception."""
        self.fields = fields
        super().__init__('Missing Required Field(s)', {'fields': fields})


class SAPNotFoundError(SAPExceptionError):
    """Exception to indicate resource does not exist."""

    def __init__(self, value: str) -> None:
        """Initialize a Not Found exception."""
        super().__init__(f'{value} not found.')


class SAPDeleteFailedError(SAPExceptionError):
    """Exception to indicate resource could not be deleted."""

    def __init__(self, reason: str) -> None:
        """Initialize a Delete Failed exception."""
        super().__init__(reason)
