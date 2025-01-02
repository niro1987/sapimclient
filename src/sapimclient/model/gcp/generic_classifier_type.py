"""GenericClassifierType."""

from typing import ClassVar

from ._base import GCPResource


class GenericClassifierType(GCPResource):
    """Generic Classifier Type."""

    attr_endpoint: ClassVar[str] = '/v2/genericClassifierTypes'
    attr_seq: ClassVar[str] = 'generic_classifier_type_seq'
    generic_classifier_type_seq: int | None = None
    name: str
