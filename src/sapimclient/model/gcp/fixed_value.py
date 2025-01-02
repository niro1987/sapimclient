"""FixedValue."""

from typing import ClassVar

from sapimclient.model.base import Value

from ._base import GCPReference, GCPRuleElement
from .calendar import Calendar
from .fixed_value_type import FixedValueType
from .period_type import PeriodType


class FixedValue(GCPRuleElement):
    """Fixed Value."""

    attr_endpoint: ClassVar[str] = '/v2/fixedValues'
    calendar: GCPReference[Calendar] | str | None = None
    value: Value | None = None
    fixed_value_type: GCPReference[FixedValueType] | str | None = None
    period_type: GCPReference[PeriodType] | str | None = None
