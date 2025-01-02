"""Quota."""

from datetime import datetime
from typing import ClassVar

from pydantic import Field

from ._base import GCPReference, GCPResource
from .calendar import Calendar
from .unit_type import UnitType


class Quota(GCPResource):
    """Quota."""

    attr_endpoint: ClassVar[str] = '/v2/quotas'
    attr_seq: ClassVar[str] = 'quota_seq'
    quota_seq: str | None = None
    calendar: GCPReference[Calendar] | str
    name: str
    description: str | None = None
    effective_start_date: datetime
    effective_end_date: datetime
    unit_type: GCPReference[UnitType] | str
    model_seq: str | None = None
    business_units: list[str] | None = None
    created_by: str | None = Field(None, exclude=True, repr=False)
    create_date: datetime | None = Field(None, exclude=True, repr=False)
    modified_by: str | None = Field(None, exclude=True, repr=False)
