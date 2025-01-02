"""Territory."""

from typing import ClassVar

from ._base import GCPReference, GCPRuleElement
from .calendar import Calendar


class Territory(GCPRuleElement):
    """Territory."""

    attr_endpoint: ClassVar[str] = '/v2/territories'
    calendar: GCPReference[Calendar] | str | None = None
