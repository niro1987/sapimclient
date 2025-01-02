"""RateTable."""

from typing import ClassVar

from ._base import LegacyRuleElement


class RateTable(LegacyRuleElement):
    """Rate Table.

    TODO: Does this endpoint return ``default_element``?
    """

    attr_endpoint: ClassVar[str] = '/v2/rateTables'
