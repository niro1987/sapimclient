"""Rule."""

from datetime import datetime
from typing import ClassVar

from pydantic import Field

from sapimclient.model.base import BusinessUnitAssignment, RuleUsage

from ._base import LegacyReference, LegacyResource


class Rule(LegacyResource):
    """Rule."""

    attr_endpoint: ClassVar[str] = '/v2/rules'
    attr_seq: ClassVar[str] = 'rule_seq'
    rule_seq: str | None = None
    name: str
    description: str | None = None
    calendar: LegacyReference | str
    effective_start_date: datetime
    effective_end_date: datetime
    business_unit: list[BusinessUnitAssignment] | BusinessUnitAssignment | None = None
    type: RuleUsage | None = None
    not_allow_update: bool = False
    model_seq: str | None = None
    created_by: str | None = Field(None, exclude=True, repr=False)
    create_date: datetime | None = Field(None, exclude=True, repr=False)
    modified_by: str | None = Field(None, exclude=True, repr=False)


class CommissionRule(Rule):
    """Alias for Rule."""


class CreditRule(Rule):
    """Alias for Rule."""


class DepositRule(Rule):
    """Alias for Rule."""


class MeasurementRule(Rule):
    """Alias for Rule."""
