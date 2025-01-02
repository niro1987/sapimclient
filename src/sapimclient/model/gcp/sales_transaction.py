"""SalesTransaction."""

from datetime import datetime
from typing import ClassVar

from sapimclient.model.base import (
    AdjustmentContext,
    Generic32Mixin,
    SalesTransactionAssignment,
    Value,
)

from ._base import GCPReference, GCPResource
from .event_type import EventType
from .sales_order import SalesOrder


class SalesTransaction(GCPResource, Generic32Mixin):
    """Sales Transaction."""

    attr_endpoint: ClassVar[str] = '/v2/salesTransactions'
    attr_seq: ClassVar[str] = 'sales_transaction_seq'
    sales_transaction_seq: str | None = None
    sales_order: GCPReference[SalesOrder] | str
    line_number: Value
    sub_line_number: Value
    event_type: GCPReference[EventType] | str
    product_id: str | None = None
    product_name: str | None = None
    product_description: str | None = None
    value: Value
    preadjusted_value: Value | None = None
    is_runnable: bool | None = None
    compensation_date: datetime
    number_of_units: Value | None = None
    unit_value: Value | None = None
    business_units: list[str] | None = None
    processing_unit: str | None = None
    model_seq: str | None = None
    ship_to_address: str | None = None
    bill_to_address: str | None = None
    other_to_address: str | None = None
    transaction_assignments: list[SalesTransactionAssignment] | None = None
    payment_terms: str | None = None
    accounting_date: datetime | None = None
    discount_percent: Value | None = None
    comments: str | None = None
    native_currency_amount: Value | None = None
    native_currency: str | None = None
    pipeline_run: str | None = None
    alternate_order_number: str | None = None
    origin_type_id: str | None = None
    adjustment_context: AdjustmentContext | None = None
    is_purged: bool | None = None
    reason: str | None = None
    channel: str | None = None
    po_number: str | None = None
    data_source: str | None = None
    discount_type: str | None = None
    modification_date: datetime | None = None
