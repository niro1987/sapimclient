"""RelationalMDLT."""

from typing import ClassVar

from sapimclient.model.base import Assignment

from ._base import GCPReference, GCPRuleElement
from .calendar import Calendar
from .unit_type import UnitType


class RelationalMDLT(GCPRuleElement):
    """Relational MDLT (Lookup Table).

    Multi Dimensional Lookup Table.

    TODO: Are ``dimensions`` and ``indices`` expandable?
            Yes
    TODO: What does ``expression_type_counts`` represent?
    """

    attr_endpoint: ClassVar[str] = '/v2/relationalMDLTs'
    calendar: GCPReference[Calendar] | str | None = None
    return_unit_type: GCPReference[UnitType] | str | None = None
    treat_null_as_zero: bool | None = None
    dimensions: list[Assignment] | Assignment | None = None
    indices: list[Assignment] | Assignment | None = None
    expression_type_counts: str | None = None
