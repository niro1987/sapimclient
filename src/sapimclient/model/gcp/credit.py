"""Credit."""

from datetime import datetime
from typing import ClassVar

from sapimclient.model.base import Generic16Mixin, Value

from ._base import GCPReference, GCPResource
from .credit_type import CreditType
from .participant import Participant
from .period import Period
from .position import Position
from .reason import Reason
from .rule import Rule
from .sales_order import SalesOrder
from .sales_transaction import SalesTransaction


class Credit(GCPResource, Generic16Mixin):
    """Credit."""

    attr_endpoint: ClassVar[str] = '/v2/credits'
    attr_seq: ClassVar[str] = 'credit_seq'
    credit_seq: str | None = None
    name: str
    position: GCPReference[Position] | str
    payee: GCPReference[Participant] | str
    sales_order: GCPReference[SalesOrder] | str
    sales_transaction: GCPReference[SalesTransaction] | str | None = None
    period: GCPReference[Period] | str
    credit_type: GCPReference[CreditType] | str
    value: Value
    preadjusted_value: Value
    origin_type_id: str
    reason: GCPReference[Reason] | str | None = None
    rule: GCPReference[Rule] | str | None = None
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
