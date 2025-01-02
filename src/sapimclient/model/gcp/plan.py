"""Plan."""

from typing import ClassVar

from ._base import GCPReference, GCPRuleElementOwner
from .calendar import Calendar


class Plan(GCPRuleElementOwner):
    """Plan.

    Parameters:
        rule_element_owner_seq (str | None): System Unique Identifier.
        name (str): Name of the plan.
        description (str | None): Description of the plan.
        calendar (GCPReference[Calendar] | str): Reference to ``Calendar`` associated
            with the plan.
        effective_start_date (datetime): Effective start date of the plan
            version.
        effective_end_date (datetime): Effective end date of the plan version.
        create_date (datetime | None): Date when plan was created.
        created_by (str | None): User ID that created the plan.
        modified_by (str | None): User ID that last modified the plan.
        business_units (list[str] | None): Business units associated with the
            plan.
        variable_assignments (list[Assignment] | Assignment | None): Variable
            Assignments on the plan level.
        model_seq (str | None): System Unique Identifier for the model.

    TODO: Add GenericMixin?
    TODO: is ``variable_assignments`` expandable?
    """

    attr_endpoint: ClassVar[str] = '/v2/plans'
    calendar: GCPReference[Calendar] | str
