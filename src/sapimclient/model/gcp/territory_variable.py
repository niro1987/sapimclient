"""TerritoryVariable."""

from typing import ClassVar

from ._base import GCPReference, GCPRuleElement
from .calendar import Calendar
from .period_type import PeriodType
from .territory import Territory


class TerritoryVariable(GCPRuleElement):
    """Territory Variable."""

    attr_endpoint: ClassVar[str] = '/v2/territoryVariables'
    calendar: GCPReference[Calendar] | str | None = None
    default_element: GCPReference[Territory] | str | None = None
    required_period_type: GCPReference[PeriodType] | str | None = None
