"""GenericClassifierType."""

from typing import ClassVar

from ._base import LegacyResource


class GenericClassifierType(LegacyResource):
    """Generic Classifier Type."""

    attr_endpoint: ClassVar[str] = '/v2/genericClassifierTypes'
    attr_seq: ClassVar[str] = 'generic_classifier_type_seq'
    generic_classifier_type_seq: int | None = None
    name: str
