"""Calendar."""

from datetime import datetime
from typing import ClassVar

from pydantic import Field

from ._base import LegacyReference, LegacyResource


class Calendar(LegacyResource):
    """Calendar."""

    attr_endpoint: ClassVar[str] = '/v2/calendars'
    attr_seq: ClassVar[str] = 'calendar_seq'
    calendar_seq: str | None = None
    name: str
    description: str | None = None
    minor_period_type: LegacyReference | str | None = None
    major_period_type: LegacyReference | str | None = None
    created_by: str | None = Field(None, exclude=True, repr=False)
    create_date: datetime | None = Field(None, exclude=True, repr=False)
    modified_by: str | None = Field(None, exclude=True, repr=False)
