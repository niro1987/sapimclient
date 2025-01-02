"""PeriodType."""

from datetime import datetime
from typing import ClassVar

from pydantic import Field

from ._base import GCPResource


class PeriodType(GCPResource):
    """Period Type."""

    attr_endpoint: ClassVar[str] = '/v2/periodTypes'
    attr_seq: ClassVar[str] = 'period_type_seq'
    period_type_seq: str | None = None
    name: str
    description: str | None = None
    level: int | None = None
    created_by: str | None = Field(None, exclude=True, repr=False)
    create_date: datetime | None = Field(None, exclude=True, repr=False)
    modified_by: str | None = Field(None, exclude=True, repr=False)
