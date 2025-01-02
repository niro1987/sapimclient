"""PositionRelation."""

from datetime import datetime
from typing import ClassVar

from pydantic import Field

from ._base import GCPReference, GCPResource
from .position import Position


class PositionRelation(GCPResource):
    """Position Relation."""

    attr_endpoint: ClassVar[str] = '/v2/positionRelations'
    attr_seq: ClassVar[str] = 'position_relation_seq'
    position_relation_seq: str | None = None
    name: str | None = None
    effective_start_date: datetime
    effective_end_date: datetime
    parent_position: GCPReference[Position] | str
    position_relation_type: str
    child_position: GCPReference[Position] | str
    created_by: str | None = Field(None, exclude=True, repr=False)
    create_date: datetime | None = Field(None, exclude=True, repr=False)
    modified_by: str | None = Field(None, exclude=True, repr=False)
