"""EventType."""

from typing import ClassVar

from pydantic import AliasChoices, Field

from ._base import LegacyDataType


class EventType(LegacyDataType):
    """Event Type."""

    attr_endpoint: ClassVar[str] = '/v2/eventTypes'
    event_type_id: str = Field(validation_alias=AliasChoices('eventTypeId', 'id'))
