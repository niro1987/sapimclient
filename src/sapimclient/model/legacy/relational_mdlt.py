"""RelationalMDLT."""

from typing import ClassVar

from sapimclient.model.base import Assignment

from ._base import LegacyReference, LegacyRuleElement


class RelationalMDLT(LegacyRuleElement):
    """Relational MDLT (Lookup Table).

    Multi Dimensional Lookup Table.

    TODO: Does this endpoint return ``default_element``?
    TODO: Are ``dimensions`` and ``indices`` expandable?
    TODO: What does ``expression_type_counts`` represent?
    """

    attr_endpoint: ClassVar[str] = '/v2/relationalMDLTs'
    default_element: LegacyReference | str | None = None
    required_period_type: LegacyReference | str | None = None
    return_unit_type: LegacyReference | str | None = None
    treat_null_as_zero: bool | None = None
    dimensions: list[Assignment] | Assignment | None = None
    indices: list[Assignment] | Assignment | None = None
    expression_type_counts: str | None = None
