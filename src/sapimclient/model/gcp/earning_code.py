"""EarningCode."""

from typing import ClassVar

from pydantic import AliasChoices, Field

from ._base import GCPDataType


class EarningCode(GCPDataType):
    """Earning Code."""

    attr_endpoint: ClassVar[str] = '/v2/earningCodes'
    earning_code_id: str = Field(validation_alias=AliasChoices('earningCodeId', 'id'))
