"""Deposit."""

from datetime import datetime
from typing import ClassVar

from sapimclient.model.base import Generic16Mixin, Value

from ._base import GCPReference, GCPResource
from .participant import Participant
from .period import Period
from .position import Position
from .rule import Rule


class Deposit(GCPResource, Generic16Mixin):
    """Deposit."""

    attr_endpoint: ClassVar[str] = '/v2/deposits'
    attr_seq: ClassVar[str] = 'deposit_seq'
    deposit_seq: str | None = None
    name: str
    earning_group_id: str
    earning_code_id: str
    payee: GCPReference[Participant] | str
    position: GCPReference[Position] | str
    period: GCPReference[Period] | str
    value: Value
    preadjusted_value: Value
    origin_type_id: str
    reason: str | None = None
    business_units: list[str] | None = None
    rule: GCPReference[Rule] | str | None = None
    deposit_date: datetime | None = None
    is_held: bool | None = None
    release_date: datetime | None = None
    pipeline_run: str | None = None
    pipeline_run_date: datetime | None = None
    processing_unit: str | None = None
    comments: str | None = None
    is_private: bool | None = None
    model_seq: str | None = None
