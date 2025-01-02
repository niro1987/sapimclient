"""EarningGroup."""

from typing import ClassVar

from pydantic import AliasChoices, Field

from ._base import LegacyDataType


class EarningGroup(LegacyDataType):
    """Earning Group."""

    attr_endpoint: ClassVar[str] = '/v2/earningGroups'
    earning_group_id: str = Field(validation_alias=AliasChoices('earningGroupId', 'id'))
