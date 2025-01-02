"""EventType."""

from typing import ClassVar

from pydantic import AliasChoices, Field

from ._base import GCPDataType


class EventType(GCPDataType):
    """Event Type."""

    attr_endpoint: ClassVar[str] = '/v2/eventTypes'
    event_type_id: str = Field(validation_alias=AliasChoices('eventTypeId', 'id'))
