"""AuditLog."""

from datetime import datetime
from typing import ClassVar

from sapimclient.model.base import BusinessUnitAssignment

from ._base import LegacyResource


class AuditLog(LegacyResource):
    """Audit Log.

    Note:
        Supports only ``read`` operations.
    """

    attr_endpoint: ClassVar[str] = '/v2/auditLogs'
    attr_seq: ClassVar[str] = 'audit_log_seq'
    audit_log_seq: str | None = None
    event_date: datetime
    event_type: str
    event_description: str | None = None
    business_unit: BusinessUnitAssignment
    object_seq: str
    object_name: str
    object_type: str
    user_id: str
    model_seq: str | None = None
