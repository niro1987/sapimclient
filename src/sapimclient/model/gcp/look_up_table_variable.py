"""LookUpTableVariable."""

from typing import ClassVar

from ._base import GCPReference, GCPRuleElement
from .calendar import Calendar
from .period_type import PeriodType
from .relational_mdlt import RelationalMDLT


class LookUpTableVariable(GCPRuleElement):
    """LookUp Table Variable."""

    attr_endpoint: ClassVar[str] = '/v2/lookUpTableVariables'
    calendar: GCPReference[Calendar] | str | None = None
    default_element: GCPReference[RelationalMDLT] | str | None = None
    required_period_type: GCPReference[PeriodType] | str | None = None
