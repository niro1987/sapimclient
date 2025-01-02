"""CategoryTree."""

from datetime import datetime
from typing import ClassVar

from pydantic import Field

from ._base import GCPResource


class CategoryTree(GCPResource):
    """CategoryTree."""

    attr_endpoint: ClassVar[str] = '/v2/categoryTrees'
    attr_seq: ClassVar[str] = 'category_tree_seq'
    category_tree_seq: str | None = None
    name: str
    description: str | None = None
    classifier_selector_id: str | None = None
    classifier_class: str
    effective_start_date: datetime
    effective_end_date: datetime
    business_units: list[str] | None = None
    created_by: str | None = Field(None, exclude=True, repr=False)
    create_date: datetime | None = Field(None, exclude=True, repr=False)
    modified_by: str | None = Field(None, exclude=True, repr=False)
