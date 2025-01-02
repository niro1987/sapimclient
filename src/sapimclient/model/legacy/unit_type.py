"""UnitType."""

from typing import ClassVar

from sapimclient.model.base import ValueClass

from ._base import LegacyResource


class UnitType(LegacyResource):
    """Unit Type."""

    attr_endpoint: ClassVar[str] = '/v2/unitTypes'
    unit_type_seq: str
    name: str
    symbol: str | None = None
    scale: int
    reporting_scale: int
    position_of_symbol: int
    currency_locale: str | None = None
    value_class: ValueClass
    formatting: str | None = None
