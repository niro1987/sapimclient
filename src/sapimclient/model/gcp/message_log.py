"""MessageLog."""

from datetime import datetime
from typing import ClassVar

from ._base import GCPResource


class MessageLog(GCPResource):
    """Message Log."""

    attr_endpoint: ClassVar[str] = '/v2/messageLogs'
    attr_seq: ClassVar[str] = 'message_log_seq'
    message_log_seq: str | None = None
    source_seq: str | None = None
    component_name: str
    log_date: datetime
    log_name: str
