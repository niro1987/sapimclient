"""Message."""

from datetime import datetime
from typing import ClassVar

from ._base import LegacyReference, LegacyResource


class Message(LegacyResource):
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
    rule: LegacyReference | str | None = None
    payee: LegacyReference | str | None = None
    message_type: str
    run_period: LegacyReference | str | None = None
    object_seq: str | None = None
    sales_transaction: str | None = None
    position: LegacyReference | str | None = None
    category: str | None = None
    credit: str | None = None
