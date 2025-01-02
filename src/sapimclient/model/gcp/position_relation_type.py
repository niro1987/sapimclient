"""PositionRelationType."""

from typing import ClassVar

from ._base import GCPDataType


class PositionRelationType(GCPDataType):
    """Position Relation Type."""

    attr_endpoint: ClassVar[str] = '/v2/positionRelationTypes'
    name: str
