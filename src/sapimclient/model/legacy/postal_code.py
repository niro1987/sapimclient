"""PostalCode."""

from datetime import datetime
from typing import ClassVar

from sapimclient.model.base import Generic16Mixin

from ._base import LegacyResource


class PostalCode(LegacyResource, Generic16Mixin):
    """Postal Code."""

    attr_endpoint: ClassVar[str] = '/v2/postalCodes'
    attr_seq: ClassVar[str] = 'classifier_seq'
    classifier_seq: str | None = None
    classifier_id: str
    low_postal_code: str
    high_postal_code: str
    country: str
    name: str | None = None
    description: str | None = None
    selector_id: str | None = None
    effective_start_date: datetime
    effective_end_date: datetime
    business_units: list[str] | None = None
