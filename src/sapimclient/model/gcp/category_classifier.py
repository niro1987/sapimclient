"""CategoryClassifier."""

from datetime import datetime
from typing import ClassVar

from pydantic import Field

from ._base import GCPReference, GCPResource
from .category import Category
from .category_tree import CategoryTree
from .generic_classifier import GenericClassifier


class CategoryClassifier(GCPResource):
    """categoryClassifier."""

    attr_endpoint: ClassVar[str] = '/v2/categoryClassifiers'
    attr_seq: ClassVar[str] = 'category_classifiers_seq'
    category_classifiers_seq: str | None = None
    category_tree: GCPReference[CategoryTree] | str
    category: GCPReference[Category] | str
    classifier: GCPReference[GenericClassifier] | str
    effective_start_date: datetime
    effective_end_date: datetime
    created_by: str | None = Field(None, exclude=True, repr=False)
    create_date: datetime | None = Field(None, exclude=True, repr=False)
    modified_by: str | None = Field(None, exclude=True, repr=False)
