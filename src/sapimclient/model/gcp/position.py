"""Position."""

from datetime import datetime
from typing import ClassVar

from sapimclient.model.base import Generic16Mixin

from ._base import GCPReference, GCPRuleElementOwner
from .participant import Participant
from .plan import Plan
from .position_group import PositionGroup
from .title import Title


class Position(GCPRuleElementOwner, Generic16Mixin):
    """Position.

    TODO: ``target_compensation`` is ``Value``?
    TODO: ``processing_unit`` should be ``GCPReference``?
    """

    attr_endpoint: ClassVar[str] = '/v2/positions'
    payee: GCPReference[Participant] | str | None = None
    plan: GCPReference[Plan] | str | None = None
    title: GCPReference[Title] | str | None = None
    manager: 'GCPReference[Position] | str | None' = None
    position_group: GCPReference[PositionGroup] | str | None = None
    target_compensation: dict | None = None
    credit_start_date: datetime | None = None
    credit_end_date: datetime | None = None
    processing_start_date: datetime | None = None
    processing_end_date: datetime | None = None
    processing_unit: str | None = None
