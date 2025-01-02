"""PositionRelationType."""

from typing import ClassVar

from ._base import LegacyDataType


class PositionRelationType(LegacyDataType):
    """Position Relation Type."""

    attr_endpoint: ClassVar[str] = '/v2/positionRelationTypes'
    name: str
