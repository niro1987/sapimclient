"""PaymentMapping."""

from typing import ClassVar

from ._base import GCPResource


class PaymentMapping(GCPResource):
    """Payment Mapping."""

    attr_endpoint: ClassVar[str] = '/v2/paymentMappings'
    attr_seq: ClassVar[str] = 'payment_mapping_seq'
    payment_mapping_seq: str | None = None
    source_table_name: str
    source_attribute: str
    payment_attribute: str
