"""RateTable."""

from typing import ClassVar

from ._base import GCPReference, GCPRuleElement
from .calendar import Calendar


class RateTable(GCPRuleElement):
    """Rate Table."""

    attr_endpoint: ClassVar[str] = '/v2/rateTables'
    calendar: GCPReference[Calendar] | str | None = None
