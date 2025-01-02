"""RateTableVariable."""

from typing import ClassVar

from ._base import GCPReference, GCPRuleElement
from .calendar import Calendar
from .period_type import PeriodType
from .rate_table import RateTable


class RateTableVariable(GCPRuleElement):
    """Rate Table Variable."""

    attr_endpoint: ClassVar[str] = '/v2/rateTableVariables'
    calendar: GCPReference[Calendar] | str | None = None
    default_element: GCPReference[RateTable] | str | None = None
    required_period_type: GCPReference[PeriodType] | str | None = None
