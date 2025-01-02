"""Category."""

from typing import ClassVar

from sapimclient.model.base import Generic16Mixin

from ._base import GCPReference, GCPRuleElement
from .calendar import Calendar
from .category_tree import CategoryTree


class Category(GCPRuleElement, Generic16Mixin):
    """Category."""

    attr_endpoint: ClassVar[str] = '/v2/categories'
    calendar: GCPReference[Calendar] | str | None = None
    owner: GCPReference[CategoryTree] | str
    parent: 'GCPReference[Category] | str | None' = None
