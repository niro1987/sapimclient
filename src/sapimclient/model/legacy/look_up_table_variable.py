"""LookUpTableVariable."""

from typing import ClassVar

from ._base import LegacyReference, LegacyRuleElement


class LookUpTableVariable(LegacyRuleElement):
    """LookUp Table Variable."""

    attr_endpoint: ClassVar[str] = '/v2/lookUpTableVariables'
    default_element: LegacyReference | str | None = None
    required_period_type: LegacyReference | str | None = None
