"""GenericClassifier."""

from datetime import datetime
from typing import ClassVar

from pydantic import Field

from sapimclient.model.base import Generic16Mixin

from ._base import LegacyResource


class GenericClassifier(LegacyResource, Generic16Mixin):
    """Generic Classifier."""

    attr_endpoint: ClassVar[str] = '/v2/genericClassifiers'
    attr_seq: ClassVar[str] = 'generic_classifier_seq'
    generic_classifier_seq: str | None = None
    name: str | None = None
    description: str | None = None
    classifier_id: str
    classifier_seq: str
    selector_id: str
    effective_start_date: datetime
    effective_end_date: datetime
    business_units: list[str] | None = None
    created_by: str | None = Field(None, exclude=True, repr=False)
    create_date: datetime | None = Field(None, exclude=True, repr=False)
    modified_by: str | None = Field(None, exclude=True, repr=False)
