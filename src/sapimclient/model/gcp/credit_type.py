"""CreditType."""

from typing import ClassVar

from pydantic import AliasChoices, Field

from ._base import GCPDataType


class CreditType(GCPDataType):
    """Credit Type."""

    attr_endpoint: ClassVar[str] = '/v2/creditTypes'
    credit_type_id: str = Field(validation_alias=AliasChoices('creditTypeId', 'id'))
