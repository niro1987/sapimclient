"""Message."""

from datetime import datetime
from typing import ClassVar

from ._base import GCPReference, GCPResource
from .participant import Participant
from .period import Period
from .position import Position
from .rule import Rule


class Message(GCPResource):
    """Message."""

    attr_endpoint: ClassVar[str] = '/v2/messages'
    attr_seq: ClassVar[str] = 'message_seq'
    message_seq: str | None = None
    message_key: str
    message_time_stamp: datetime
    argument_count: int
    sub_category: str
    message_log: str
    module: str
    rule: GCPReference[Rule] | str | None = None
    payee: GCPReference[Participant] | str | None = None
    message_type: str
    run_period: GCPReference[Period] | str | None = None
    object_seq: str | None = None
    sales_transaction: str | None = None
    position: GCPReference[Position] | str | None = None
    category: str | None = None
    credit: str | None = None
