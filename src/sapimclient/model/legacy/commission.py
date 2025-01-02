"""Commission."""

from datetime import datetime
from typing import ClassVar

from sapimclient.model.base import Value

from ._base import LegacyReference, LegacyResource


class Commission(LegacyResource):
    """Commission.

    TODO: No results.
    """

    attr_endpoint: ClassVar[str] = '/v2/commissions'
    attr_seq: ClassVar[str] = 'commission_seq'
    commission_seq: str | None = None
    position: LegacyReference | str
    payee: LegacyReference | str
    period: LegacyReference | str
    incentive: LegacyReference | str
    credit: LegacyReference | str
    pipeline_run: str
    pipeline_run_date: datetime
    value: Value
    rate_value: Value
    entry_number: Value
    business_units: list[str] | None = None
    processing_unit: str | None = None
    is_private: bool | None = None
    origin_type_id: str
