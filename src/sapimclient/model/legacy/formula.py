"""Formula."""

from typing import ClassVar

from ._base import LegacyRuleElement


class Formula(LegacyRuleElement):
    """Formula."""

    attr_endpoint: ClassVar[str] = '/v2/formulas'
