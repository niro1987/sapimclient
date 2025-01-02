"""Period."""

from datetime import datetime
from typing import ClassVar

from pydantic import Field

from ._base import LegacyReference, LegacyResource


class Period(LegacyResource):
    """Period."""

    attr_endpoint: ClassVar[str] = '/v2/periods'
    attr_seq: ClassVar[str] = 'period_seq'
    period_seq: str | None = None
    name: str
    short_name: str
    start_date: datetime
    end_date: datetime
    period_type: LegacyReference | str
    calendar: LegacyReference | str
    description: str | None = None
    parent: LegacyReference | str | None = None
    created_by: str | None = Field(None, exclude=True, repr=False)
    create_date: datetime | None = Field(None, exclude=True, repr=False)
    modified_by: str | None = Field(None, exclude=True, repr=False)
