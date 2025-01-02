"""PositionGroup."""

from datetime import datetime
from typing import ClassVar

from pydantic import Field

from ._base import LegacyResource


class PositionGroup(LegacyResource):
    """Position."""

    attr_endpoint: ClassVar[str] = '/v2/positionGroups'
    attr_seq: ClassVar[str] = 'position_group_seq'
    position_group_seq: str | None = None
    name: str
    business_units: list[str] | None = None
    created_by: str | None = Field(None, exclude=True, repr=False)
    create_date: datetime | None = Field(None, exclude=True, repr=False)
    modified_by: str | None = Field(None, exclude=True, repr=False)
