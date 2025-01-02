"""FixedValueVariable."""

from typing import ClassVar

from ._base import LegacyReference, LegacyRuleElement


class FixedValueVariable(LegacyRuleElement):
    """Fixed Value Variable."""

    attr_endpoint: ClassVar[str] = '/v2/fixedValueVariables'
    default_element: LegacyReference | str | None = None
    required_period_type: LegacyReference | str | None = None
