"""Title."""

from typing import ClassVar

from sapimclient.model.base import Generic16Mixin

from ._base import GCPReference, GCPRuleElementOwner
from .plan import Plan


class Title(GCPRuleElementOwner, Generic16Mixin):
    """Title."""

    attr_endpoint: ClassVar[str] = '/v2/titles'
    plan: GCPReference[Plan] | str | None = None
