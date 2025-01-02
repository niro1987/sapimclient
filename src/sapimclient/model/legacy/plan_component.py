"""PlanComponent."""

from datetime import datetime
from typing import ClassVar

from pydantic import Field

from ._base import LegacyReference, LegacyResource


class PlanComponent(LegacyResource):
    """Plan."""

    attr_endpoint: ClassVar[str] = '/v2/planComponents'
    attr_seq: ClassVar[str] = 'plan_component_seq'
    plan_component_seq: str | None = None
    name: str
    description: str | None = None
    calendar: LegacyReference | str
    effective_start_date: datetime
    effective_end_date: datetime
    business_units: list[str] | None = None
    not_allow_update: bool = False
    model_seq: str | None = None
    created_by: str | None = Field(None, exclude=True, repr=False)
    create_date: datetime | None = Field(None, exclude=True, repr=False)
    modified_by: str | None = Field(None, exclude=True, repr=False)
