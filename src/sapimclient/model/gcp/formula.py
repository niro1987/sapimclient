"""Formula."""

from typing import ClassVar

from ._base import GCPReference, GCPRuleElement
from .calendar import Calendar


class Formula(GCPRuleElement):
    """Formula."""

    attr_endpoint: ClassVar[str] = '/v2/formulas'
    calendar: GCPReference[Calendar] | str | None = None
