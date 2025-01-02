"""PaymentSummary."""

from datetime import datetime
from typing import ClassVar

from sapimclient.model.base import Value

from ._base import GCPReference, GCPResource
from .participant import Participant
from .period import Period
from .position import Position


class PaymentSummary(GCPResource):
    """Payment Summary."""

    attr_endpoint: ClassVar[str] = '/v2/paymentSummarys'
    attr_seq: ClassVar[str] = 'payment_summary_seq'
    payment_summary_seq: str | None = None
    position: GCPReference[Position] | str
    participant: GCPReference[Participant] | str
    period: GCPReference[Period] | str
    earning_group_id: str
    pipeline_run: str | None = None
    pipeline_run_date: datetime | None = None
    applied_deposit: Value | None = None
    balance: Value | None = None
    prior_balance: Value | None = None
    outstanding_balance: Value | None = None
    payment: Value | None = None
    business_units: list[str] | None = None
    processing_unit: str | None = None
