"""Balance."""

from datetime import datetime
from typing import ClassVar

from sapimclient.model.base import Value

from ._base import GCPReference, GCPResource
from .participant import Participant
from .period import Period
from .position import Position


class Balance(GCPResource):
    """Balance.

    Note:
        Supports only ``read`` operations.
    """

    attr_endpoint: ClassVar[str] = '/v2/balances'
    attr_seq: ClassVar[str] = 'balance_seq'
    balance_seq: str | None = None
    position: GCPReference[Position] | str
    payee: GCPReference[Participant] | str
    period: GCPReference[Period] | str
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
