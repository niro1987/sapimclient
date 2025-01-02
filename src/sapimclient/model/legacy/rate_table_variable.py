"""RateTableVariable."""

from typing import ClassVar

from ._base import LegacyReference, LegacyRuleElement


class RateTableVariable(LegacyRuleElement):
    """Rate Table Variable."""

    attr_endpoint: ClassVar[str] = '/v2/rateTableVariables'
    default_element: LegacyReference | str | None = None
    required_period_type: LegacyReference | str | None = None
