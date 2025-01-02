"""GlobalFieldName."""

from typing import ClassVar

from ._base import GCPResource


class GlobalFieldName(GCPResource):
    """Global Field Name."""

    attr_endpoint: ClassVar[str] = '/v2/globalFieldNames'
    attr_seq: ClassVar[str] = 'global_field_name_seq'
    global_field_name_seq: str | None = None
    name: str
    description: str | None = None
    global_field_name_data_type_length: int
