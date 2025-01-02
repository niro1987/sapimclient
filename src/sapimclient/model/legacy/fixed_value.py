"""FixedValue."""

from typing import ClassVar

from sapimclient.model.base import Value

from ._base import LegacyReference, LegacyRuleElement


class FixedValue(LegacyRuleElement):
    """Fixed Value."""

    attr_endpoint: ClassVar[str] = '/v2/fixedValues'
    value: Value | None = None
    fixed_value_type: LegacyReference | str | None = None
    period_type: LegacyReference | str | None = None


class CFixedValue(FixedValue):
    """Alias for ``FixedValue``."""
