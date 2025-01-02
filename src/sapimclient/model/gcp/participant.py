"""Participant."""

from datetime import datetime
from typing import ClassVar

from pydantic import Field

from sapimclient.model.base import Generic16Mixin, Value

from ._base import GCPReference, GCPResource
from .calendar import Calendar


class Participant(GCPResource, Generic16Mixin):
    """Participant."""

    attr_endpoint: ClassVar[str] = '/v2/participants'
    attr_seq: ClassVar[str] = 'payee_seq'
    payee_seq: str | None = None
    payee_id: str
    first_name: str | None = None
    middle_name: str | None = None
    last_name: str
    participant_email: str | None = None
    prefix: str | None = None
    suffix: str | None = None
    effective_start_date: datetime
    effective_end_date: datetime
    hire_date: datetime | None = None
    termination_date: datetime | None = None
    salary: Value | None = None
    user_id: str
    preferred_language: str | None = None
    event_calendar: GCPReference[Calendar] | str | None = None
    tax_id: str | None = None
    business_units: list[str] | None = None
    created_by: str | None = Field(None, exclude=True, repr=False)
    create_date: datetime | None = Field(None, exclude=True, repr=False)
    modified_by: str | None = Field(None, exclude=True, repr=False)
