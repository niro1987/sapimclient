"""AppliedDeposit."""

from datetime import datetime
from typing import ClassVar

from sapimclient.model.base import Value

from ._base import LegacyReference, LegacyResource


class AppliedDeposit(LegacyResource):
    """AppliedDeposit.

    Note:
        Supports only ``read`` operations.
    """

    attr_endpoint: ClassVar[str] = '/v2/appliedDeposits'
    attr_seq: ClassVar[str] = 'applied_deposit_seq'
    applied_deposit_seq: str | None = None
    position: LegacyReference | str
    payee: LegacyReference | str
    period: LegacyReference | str
    earning_group_id: str
    earning_code_id: str
    trial_pipeline_run: str
    trial_pipeline_run_date: datetime
    post_pipeline_run: str | None = None
    post_pipeline_run_date: datetime | None = None
    entry_number: str
    value: Value
    processing_unit: str | None = None
