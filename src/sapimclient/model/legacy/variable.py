"""Variable."""

from typing import ClassVar

from ._base import LegacyReference, LegacyRuleElement


class Variable(LegacyRuleElement):
    """Variable.

    TODO: What does ``default_element`` refer to?
    """

    attr_endpoint: ClassVar[str] = '/v2/variables'
    default_element: LegacyReference | str | None = None
    required_period_type: LegacyReference | str | None = None
