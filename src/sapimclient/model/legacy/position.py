"""Position."""

from datetime import datetime
from typing import ClassVar

from sapimclient.model.base import Generic16Mixin

from ._base import LegacyReference, LegacyRuleElementOwner


class Position(LegacyRuleElementOwner, Generic16Mixin):
    """Position.

    TODO: ``target_compensation`` is ``Value``?
    TODO: ``processing_unit`` should be ``LegacyReference``?
    """

    attr_endpoint: ClassVar[str] = '/v2/positions'
    payee: LegacyReference | str | None = None
    plan: LegacyReference | str | None = None
    title: LegacyReference | str | None = None
    manager: LegacyReference | str | None = None
    position_group: LegacyReference | str | None = None
    target_compensation: dict | None = None
    credit_start_date: datetime | None = None
    credit_end_date: datetime | None = None
    processing_start_date: datetime | None = None
    processing_end_date: datetime | None = None
    processing_unit: str | None = None
