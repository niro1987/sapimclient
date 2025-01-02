"""Base models."""

from datetime import datetime
from importlib import import_module
from typing import Any, ClassVar, Literal

from pydantic import Field, model_validator

from sapimclient.model.base import (
    Assignment,
    Endpoint,
    Reference,
    Resource,
    RuleUsage,
    RuleUsageList,
)


class LegacyResource(Resource):
    """Base class for Oracle and HANA resources."""

    attr_endpoint_prefix: ClassVar[str] = '/api'


class LegacyReference(Reference):
    """Expanded reference to a Legacy resource.

    Parameters:
        seq (str): System unique identifier for the referred resource.
        resource_cls: type[Resource]: Class of the referred resource.
        exra (dict[str, Any]): Extra attributes of the resource.
    """

    resource_cls: type[LegacyResource]

    @model_validator(mode='before')
    @classmethod
    def resolve_reference(cls, values: dict[str, Any]) -> dict[str, Any]:
        """Resolve reference."""
        # Example values:
        # {
        #   'key': 'spam',
        #   'display_name': 'eggs',
        #   'object_type': 'Title',
        #   'key_string': 'spam',
        #   'logical_keys': {'name': 'eggs'},
        # }

        module = import_module('sapimclient.model.legacy')
        try:
            object_type = getattr(module, values['object_type'])
        except AttributeError as err:
            msg = f'Could not find LegacyResource: {values["object_type"]}'
            raise ValueError(msg) from err

        return {
            'seq': values['key'],
            'resource_cls': object_type,
            'extra': values.get('logical_keys', {}),
        }


class LegacyDataType(LegacyResource):
    """Base class for Legacy DataType resources."""

    attr_seq: ClassVar[str] = 'data_type_seq'
    data_type_seq: str | None = None
    description: str | None = None
    create_date: datetime | None = Field(None, exclude=True, repr=False)
    created_by: str | None = Field(None, exclude=True, repr=False)
    modified_by: str | None = Field(None, exclude=True, repr=False)
    not_allow_update: bool | None = None


class LegacyRuleElementOwner(LegacyResource):
    """Base class for Rule Element Owner resources.

    TODO: ``variable_assignments`` should be ``LegacyReference``?
    TODO: ``business_units`` should be ``LegacyReference``?
    """

    attr_seq: ClassVar[str] = 'rule_element_owner_seq'
    rule_element_owner_seq: str | None = None
    name: str
    description: str | None = None
    effective_start_date: datetime
    effective_end_date: datetime
    create_date: datetime | None = Field(None, exclude=True, repr=False)
    created_by: str | None = Field(None, exclude=True, repr=False)
    modified_by: str | None = Field(None, exclude=True, repr=False)
    business_units: list[str] | None = None
    variable_assignments: list[Assignment] | Assignment | None = None
    model_seq: str | None = None


class LegacyRuleElement(LegacyResource):
    """Base class for Rule Element resources.

    TODO: What does ``owning_element`` represent?
    """

    attr_seq: ClassVar[str] = 'rule_element_seq'
    rule_element_seq: str | None = None
    name: str
    description: str | None = None
    calendar: LegacyReference | str | None = None
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


class LegacyPipelineJob(Endpoint):
    """Base class for a Pipeline Job."""

    attr_endpoint_prefix: ClassVar[str] = '/api'
    attr_endpoint: ClassVar[str] = '/v2/pipelines'
    command: Literal['PipelineRun', 'Import', 'XMLImport']
    run_stats: bool = False
