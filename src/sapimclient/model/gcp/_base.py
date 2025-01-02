"""Base models for GCP endpoints."""

from datetime import datetime
from typing import Any, ClassVar, Generic, TypeVar, get_args

from pydantic import Field, model_validator

from sapimclient.model.base import (
    Assignment,
    Reference,
    Resource,
    RuleUsage,
    RuleUsageList,
)


class GCPResource(Resource):
    """Base class for GCP resources."""

    attr_endpoint_prefix: ClassVar[str] = '/mtsvc/tcmp/rest'


T = TypeVar('T', bound=GCPResource)


class GCPReference(Reference, Generic[T]):
    """Expanded reference to a GCP resource.

    Parameters:
        seq (str): System unique identifier for the referred resource.
        resource_cls: type[Resource]: Class of the referred resource.
        exra (dict[str, Any]): Extra attributes of the resource.
    """

    resource_cls: type[T]

    @model_validator(mode='before')
    @classmethod
    def resolve_reference(cls, values: dict[str, Any]) -> dict[str, Any]:
        """Resolve reference."""
        # Example value:
        # {
        #   'ruleElementOwnerSeq': 'spam',
        #   'name': 'bacon'
        # }

        # Get resource_cls annotations
        type_args: tuple[type[GCPResource], ...] = get_args(
            cls.model_fields['resource_cls'].annotation,
        )

        # There should always be one type argument
        if len(type_args) != 1:
            raise ValueError('Invalid Reference Type Annotation')

        # Get resource_cls
        resource_cls: type[GCPResource] = type_args[0]

        # First key is the seq
        seq: str = values.pop(next(iter(values)))

        return {
            'seq': seq,
            'resource_cls': resource_cls,
            'extra': values,
        }


class GCPDataType(GCPResource):
    """Base class for GCP DataType resources."""

    attr_seq: ClassVar[str] = 'data_type_seq'
    data_type_seq: str | None = None
    description: str | None = None
    create_date: datetime | None = Field(None, exclude=True, repr=False)
    created_by: str | None = Field(None, exclude=True, repr=False)
    modified_by: str | None = Field(None, exclude=True, repr=False)
    not_allow_update: bool | None = None


class GCPRuleElementOwner(GCPResource):
    """Base class for Rule Element Owner resources.

    TODO: ``variable_assignments`` should be ``GCPReference``?
    TODO: ``business_units`` should be ``GCPReference``?
    """

    attr_seq: ClassVar[str] = 'rule_element_owner_seq'
    rule_element_owner_seq: str | None = None
    name: str
    description: str | None = None
    effective_start_date: datetime | None = None
    effective_end_date: datetime | None = None
    create_date: datetime | None = Field(None, exclude=True, repr=False)
    created_by: str | None = Field(None, exclude=True, repr=False)
    modified_by: str | None = Field(None, exclude=True, repr=False)
    business_units: list[str] | None = None
    variable_assignments: list[Assignment] | Assignment | None = None
    model_seq: str | None = None


class GCPRuleElement(GCPResource):
    """Base class for Rule Element resources.

    TODO: What does ``owning_element`` represent?
    """

    attr_seq: ClassVar[str] = 'rule_element_seq'
    rule_element_seq: str | None = None
    name: str
    description: str | None = None
    effective_start_date: datetime
    effective_end_date: datetime
    business_units: list[str] | None = None
    not_allow_update: bool = False
    reference_class_type: str | None = None
    return_type: str | None = None
    owning_element: str | None = None
    rule_usage: RuleUsageList | RuleUsage | None = None
    input_signature: str | None = None
    created_by: str | None = Field(None, exclude=True, repr=False)
    create_date: datetime | None = Field(None, exclude=True, repr=False)
    modified_by: str | None = Field(None, exclude=True, repr=False)
    model_seq: str | None = None
