"""Product."""

from datetime import datetime
from typing import ClassVar

from pydantic import Field

from sapimclient.model.base import Generic16Mixin, Value

from ._base import GCPResource


class Product(GCPResource, Generic16Mixin):
    """Product."""

    attr_endpoint: ClassVar[str] = '/v2/products'
    attr_seq: ClassVar[str] = 'classifier_seq'
    classifier_seq: str | None = None
    classifier_id: str
    name: str | None = None
    cost: Value | None = None
    price: Value | None = None
    description: str | None = None
    selector_id: str | None = None
    effective_start_date: datetime
    effective_end_date: datetime
    business_units: list[str] | None = None
    created_by: str | None = Field(None, exclude=True, repr=False)
    create_date: datetime | None = Field(None, exclude=True, repr=False)
    modified_by: str | None = Field(None, exclude=True, repr=False)
