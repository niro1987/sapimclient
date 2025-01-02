"""Incentive."""

from datetime import datetime
from typing import ClassVar

from sapimclient.model.base import Generic16Mixin, Value

from ._base import LegacyReference, LegacyResource


class Incentive(LegacyResource, Generic16Mixin):
    """Incentive."""

    attr_endpoint: ClassVar[str] = '/v2/incentives'
    attr_seq: ClassVar[str] = 'incentive_seq'
    incentive_seq: str | None = None
    name: str | None = None
    quota: Value | None = None
    attainment: Value | None = None
    position: LegacyReference | str
    payee: LegacyReference | str
    period: LegacyReference | str
    rule: LegacyReference | str | None = None
    value: Value
    release_date: datetime | None = None
    pipeline_run: str | None = None
    pipeline_run_date: datetime | None = None
    is_active: bool = True
    is_private: bool | None = None
    processing_unit: str | None = None
    business_units: list[str] | None = None
