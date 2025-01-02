"""EarningGroupCode."""

from datetime import datetime
from typing import ClassVar

from pydantic import Field

from ._base import GCPResource


class EarningGroupCode(GCPResource):
    """EarningGroupCode."""

    attr_endpoint: ClassVar[str] = '/v2/earningGroupCodes'
    attr_seq: ClassVar[str] = 'earning_group_code_seq'
    earning_group_code_seq: str | None = None
    earning_group_code: str
    earning_code_id: str
    earning_group_id: str
    created_by: str | None = Field(None, exclude=True, repr=False)
    create_date: datetime | None = Field(None, exclude=True, repr=False)
    modified_by: str | None = Field(None, exclude=True, repr=False)
