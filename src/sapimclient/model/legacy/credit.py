"""Credit."""

from datetime import datetime
from typing import ClassVar

from sapimclient.model.base import Generic16Mixin, Value

from ._base import LegacyReference, LegacyResource


class Credit(LegacyResource, Generic16Mixin):
    """Credit."""

    attr_endpoint: ClassVar[str] = '/v2/credits'
    attr_seq: ClassVar[str] = 'credit_seq'
    credit_seq: str | None = None
    name: str
    position: LegacyReference | str
    payee: LegacyReference | str
    sales_order: LegacyReference | str
    sales_transaction: LegacyReference | str | None = None
    period: LegacyReference | str
    credit_type: LegacyReference | str
    value: Value
    preadjusted_value: Value
    origin_type_id: str
    reason: LegacyReference | str | None = None
    rule: LegacyReference | str | None = None
    is_rollable: bool | None = None
    roll_date: datetime | None = None
    is_held: bool | None = None
    release_date: datetime | None = None
    pipeline_run: str | None = None
    pipeline_run_date: datetime | None = None
    compensation_date: datetime | None = None
    comments: str | None = None
    is_private: bool | None = None
    business_units: list[str] | None = None
    processing_unit: str | None = None
