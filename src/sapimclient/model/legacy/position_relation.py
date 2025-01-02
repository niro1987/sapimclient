"""PositionRelation."""

from datetime import datetime
from typing import ClassVar

from pydantic import Field

from ._base import LegacyReference, LegacyResource


class PositionRelation(LegacyResource):
    """Position Relation."""

    attr_endpoint: ClassVar[str] = '/v2/positionRelations'
    attr_seq: ClassVar[str] = 'position_relation_seq'
    position_relation_seq: str | None = None
    name: str | None = None
    effective_start_date: datetime
    effective_end_date: datetime
    parent_position: LegacyReference | str
    position_relation_type: str
    child_position: LegacyReference | str
    created_by: str | None = Field(None, exclude=True, repr=False)
    create_date: datetime | None = Field(None, exclude=True, repr=False)
    modified_by: str | None = Field(None, exclude=True, repr=False)
