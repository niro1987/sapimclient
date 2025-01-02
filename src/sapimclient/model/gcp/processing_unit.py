"""ProcessingUnit."""

from typing import ClassVar

from ._base import GCPResource


class ProcessingUnit(GCPResource):
    """Processing Unit."""

    attr_endpoint: ClassVar[str] = '/v2/processingUnits'
    attr_seq: ClassVar[str] = 'processing_unit_seq'
    processing_unit_seq: str | None = None
    name: str
    description: str | None = None
