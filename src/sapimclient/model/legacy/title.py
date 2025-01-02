"""Title."""

from typing import ClassVar

from sapimclient.model.base import Generic16Mixin

from ._base import LegacyReference, LegacyRuleElementOwner


class Title(LegacyRuleElementOwner, Generic16Mixin):
    """Title."""

    attr_endpoint: ClassVar[str] = '/v2/titles'
    plan: LegacyReference | str | None = None
