"""FixedValueType."""

from typing import ClassVar

from pydantic import AliasChoices, Field

from ._base import GCPDataType


class FixedValueType(GCPDataType):
    """Fixed Value Type."""

    attr_endpoint: ClassVar[str] = '/v2/fixedValueTypes'
    fixed_value_type_id: str = Field(
        validation_alias=AliasChoices('fixedValueTypeId', 'id'),
    )
