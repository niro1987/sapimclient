"""StatusCode."""

from typing import ClassVar

from ._base import LegacyDataType


class StatusCode(LegacyDataType):
    """Status Code."""

    attr_endpoint: ClassVar[str] = '/v2/statusCodes'
    status: str
    name: str | None = None
    type: str | None = None
    is_active: bool = True
