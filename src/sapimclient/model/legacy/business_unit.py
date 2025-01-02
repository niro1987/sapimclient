"""BusinessUnit."""

from typing import ClassVar

from ._base import LegacyResource


class BusinessUnit(LegacyResource):
    """Business Unit."""

    attr_endpoint: ClassVar[str] = '/v2/businessUnits'
    attr_seq: ClassVar[str] = 'business_unit_seq'
    business_unit_seq: str | None = None
    name: str
    description: str | None = None
    mask: str | None = None
    processing_unit: str | None = None
