"""Quota."""

from datetime import datetime
from typing import ClassVar

from pydantic import Field

from ._base import LegacyReference, LegacyResource


class Quota(LegacyResource):
    """Quota."""

    attr_endpoint: ClassVar[str] = '/v2/quotas'
    attr_seq: ClassVar[str] = 'quota_seq'
    quota_seq: str | None = None
    calendar: LegacyReference | str
    name: str
    description: str | None = None
    effective_start_date: datetime
    effective_end_date: datetime
    unit_type: LegacyReference | str
    model_seq: str | None = None
    business_units: list[str] | None = None
    created_by: str | None = Field(None, exclude=True, repr=False)
    create_date: datetime | None = Field(None, exclude=True, repr=False)
    modified_by: str | None = Field(None, exclude=True, repr=False)
