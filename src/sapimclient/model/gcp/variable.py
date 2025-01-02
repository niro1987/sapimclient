"""Variable."""

from typing import ClassVar

from ._base import GCPReference, GCPRuleElement
from .calendar import Calendar
from .period_type import PeriodType


class Variable(GCPRuleElement):
    """Variable.

    TODO: ``default_element`` can refer FixedValue, RateTable or RelationalMDLT.
    """

    attr_endpoint: ClassVar[str] = '/v2/variables'
    calendar: GCPReference[Calendar] | str | None = None
    default_element: str | None = None
    required_period_type: GCPReference[PeriodType] | str | None = None
