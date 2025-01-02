"""Category."""

from typing import ClassVar

from sapimclient.model.base import Generic16Mixin

from ._base import LegacyReference, LegacyRuleElement


class Category(LegacyRuleElement, Generic16Mixin):
    """Category."""

    attr_endpoint: ClassVar[str] = '/v2/categories'
    owner: LegacyReference | str
    parent: LegacyReference | str | None = None
