"""Territory."""

from typing import ClassVar

from ._base import LegacyRuleElement


class Territory(LegacyRuleElement):
    """Territory."""

    attr_endpoint: ClassVar[str] = '/v2/territories'
