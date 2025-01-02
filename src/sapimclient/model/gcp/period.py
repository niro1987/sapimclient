"""Period."""

from datetime import datetime
from typing import ClassVar

from pydantic import Field

from ._base import GCPReference, GCPResource
from .calendar import Calendar
from .period_type import PeriodType


class Period(GCPResource):
    """Period."""

    attr_endpoint: ClassVar[str] = '/v2/periods'
    attr_seq: ClassVar[str] = 'period_seq'
    period_seq: str | None = None
    name: str
    short_name: str
    start_date: datetime
    end_date: datetime
    period_type: GCPReference[PeriodType] | str
    calendar: GCPReference[Calendar] | str
    description: str | None = None
    parent: 'GCPReference[Period] | str | None' = None
    created_by: str | None = Field(None, exclude=True, repr=False)
    create_date: datetime | None = Field(None, exclude=True, repr=False)
    modified_by: str | None = Field(None, exclude=True, repr=False)
