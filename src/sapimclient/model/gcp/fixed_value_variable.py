"""FixedValueVariable."""

from typing import ClassVar

from ._base import GCPReference, GCPRuleElement
from .calendar import Calendar
from .fixed_value import FixedValue
from .period_type import PeriodType


class FixedValueVariable(GCPRuleElement):
    """Fixed Value Variable."""

    attr_endpoint: ClassVar[str] = '/v2/fixedValueVariables'
    calendar: GCPReference[Calendar] | str | None = None
    default_element: GCPReference[FixedValue] | str | None = None
    required_period_type: GCPReference[PeriodType] | str | None = None
