"""TerritoryVariable."""

from typing import ClassVar

from ._base import LegacyReference, LegacyRuleElement


class TerritoryVariable(LegacyRuleElement):
    """Territory Variable."""

    attr_endpoint: ClassVar[str] = '/v2/territoryVariables'
    default_element: LegacyReference | str | None = None
    required_period_type: LegacyReference | str | None = None
