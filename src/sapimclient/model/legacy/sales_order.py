"""SalesOrder."""

from datetime import datetime
from typing import ClassVar

from pydantic import Field

from sapimclient.model.base import Generic16Mixin

from ._base import LegacyResource


class SalesOrder(LegacyResource, Generic16Mixin):
    """Sales Order."""

    attr_endpoint: ClassVar[str] = '/v2/salesOrders'
    attr_seq: ClassVar[str] = 'sales_order_seq'
    sales_order_seq: str | None = None
    order_id: str
    pipeline_run: str | None = None
    business_units: list[str] | None = None
    processing_unit: str | None = None
    model_seq: str | None = None
    created_by: str | None = Field(None, exclude=True, repr=False)
    create_date: datetime | None = Field(None, exclude=True, repr=False)
    modified_by: str | None = Field(None, exclude=True, repr=False)
