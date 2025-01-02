"""Balance."""

from datetime import datetime
from typing import ClassVar

from sapimclient.model.base import Value

from ._base import LegacyReference, LegacyResource


class Balance(LegacyResource):
    """Balance.

    Note:
        Supports only ``read`` operations.
    """

    attr_endpoint: ClassVar[str] = '/v2/balances'
    attr_seq: ClassVar[str] = 'balance_seq'
    balance_seq: str | None = None
    position: LegacyReference | str
    payee: LegacyReference | str
    period: LegacyReference | str
    earning_group_id: str
    earning_code_id: str
    trial_pipeline_run: str
    trial_pipeline_run_date: datetime
    apply_pipeline_run: str | None = None
    apply_pipeline_run_date: datetime | None = None
    post_pipeline_run: str | None = None
    post_pipeline_run_date: datetime | None = None
    balance_status_id: str
    value: Value
    processing_unit: str | None = None
