"""Reason."""

from typing import ClassVar

from pydantic import AliasChoices, Field

from ._base import GCPDataType


class Reason(GCPDataType):
    """Reason."""

    attr_endpoint: ClassVar[str] = '/v2/reasons'
    reason_id: str = Field(validation_alias=AliasChoices('reasonId', 'id'))
