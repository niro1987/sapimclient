"""Pydantic models for Python SAP Incentive Management Client (GCP Tenants)."""
# pylint: disable=duplicate-code,too-many-lines

from __future__ import annotations

import logging
from datetime import datetime
from typing import Any, ClassVar, Generic, Literal, TypeVar, get_args

from pydantic import AliasChoices, Field, field_validator, model_validator

from sapimclient import const

from .base import (
    AdjustmentContext,
    Assignment,
    BusinessUnitAssignment,
    Generic16Mixin,
    Generic32Mixin,
    Reference,
    Resource,
    RuleUsage,
    RuleUsageList,
    SalesTransactionAssignment,
    Value,
    ValueClass,
)

__all__ = [
    'AppliedDeposit',
    'AuditLog',
    'Balance',
    'BusinessUnit',
    'Calendar',
    'Category',
    'CategoryClassifier',
    'CategoryTree',
    'Commission',
    'CommissionRule',
    'Credit',
    'CreditRule',
    'CreditType',
    'Deposit',
    'DepositRule',
    'EarningCode',
    'EarningGroup',
    'EarningGroupCode',
    'EventType',
    'FixedValue',
    'FixedValueType',
    'FixedValueVariable',
    'Formula',
    'GCPReference',
    'GCPResource',
    'GenericClassifier',
    'GenericClassifierType',
    'GlobalFieldName',
    'Incentive',
    'LookUpTableVariable',
    'Measurement',
    'MeasurementRule',
    'Message',
    'MessageLog',
    'Participant',
    'PaymentMapping',
    'PaymentSummary',
    'Period',
    'PeriodType',
    'Pipeline',
    'Plan',
    'PlanComponent',
    'Position',
    'PositionGroup',
    'PositionRelation',
    'PositionRelationType',
    'PostalCode',
    'PrimaryMeasurement',
    'ProcessingUnit',
    'Product',
    'Quota',
    'RateTable',
    'RateTableVariable',
    'Reason',
    'RelationalMDLT',
    'Rule',
    'SalesOrder',
    'SalesTransaction',
    'SecondaryMeasurement',
    'StatusCode',
    'Territory',
    'TerritoryVariable',
    'Title',
    'UnitType',
    'User',
    'Variable',
]

LOGGER = logging.getLogger(__name__)


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


class AppliedDeposit(GCPResource):
    """AppliedDeposit.

    Note:
        Supports only read operations.
    """

    attr_endpoint: ClassVar[str] = '/v2/appliedDeposits'
    attr_seq: ClassVar[str] = 'applied_deposit_seq'
    applied_deposit_seq: str | None = None
    position: GCPReference[Position] | str
    payee: GCPReference[Participant] | str
    period: GCPReference[Period] | str
    earning_group_id: str
    earning_code_id: str
    trial_pipeline_run: str
    trial_pipeline_run_date: datetime
    post_pipeline_run: str | None = None
    post_pipeline_run_date: datetime | None = None
    entry_number: str
    value: Value
    processing_unit: str | None = None


class AuditLog(GCPResource):
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


class BusinessUnit(GCPResource):
    """Business Unit."""

    attr_endpoint: ClassVar[str] = '/v2/businessUnits'
    attr_seq: ClassVar[str] = 'business_unit_seq'
    business_unit_seq: str | None = None
    name: str
    description: str | None = None
    mask: str | None = None
    processing_unit: str | None = None


class Calendar(GCPResource):
    """Calendar."""

    attr_endpoint: ClassVar[str] = '/v2/calendars'
    attr_seq: ClassVar[str] = 'calendar_seq'
    calendar_seq: str | None = None
    name: str
    description: str | None = None
    minor_period_type: GCPReference[PeriodType] | str | None = None
    major_period_type: GCPReference[PeriodType] | str | None = None
    created_by: str | None = Field(None, exclude=True, repr=False)
    create_date: datetime | None = Field(None, exclude=True, repr=False)
    modified_by: str | None = Field(None, exclude=True, repr=False)


class CategoryClassifier(GCPResource):
    """categoryClassifier."""

    attr_endpoint: ClassVar[str] = '/v2/categoryClassifiers'
    attr_seq: ClassVar[str] = 'category_classifiers_seq'
    category_classifiers_seq: str | None = None
    category_tree: GCPReference[CategoryTree] | str
    category: GCPReference[Category] | str
    classifier: GCPReference[GenericClassifier] | str
    effective_start_date: datetime
    effective_end_date: datetime
    created_by: str | None = Field(None, exclude=True, repr=False)
    create_date: datetime | None = Field(None, exclude=True, repr=False)
    modified_by: str | None = Field(None, exclude=True, repr=False)


class CategoryTree(GCPResource):
    """CategoryTree."""

    attr_endpoint: ClassVar[str] = '/v2/categoryTrees'
    attr_seq: ClassVar[str] = 'category_tree_seq'
    category_tree_seq: str | None = None
    name: str
    description: str | None = None
    classifier_selector_id: str | None = None
    classifier_class: str
    effective_start_date: datetime
    effective_end_date: datetime
    business_units: list[str] | None = None
    created_by: str | None = Field(None, exclude=True, repr=False)
    create_date: datetime | None = Field(None, exclude=True, repr=False)
    modified_by: str | None = Field(None, exclude=True, repr=False)


class Commission(GCPResource):
    """Commission.

    TODO: No results.
    """

    attr_endpoint: ClassVar[str] = '/v2/commissions'
    attr_seq: ClassVar[str] = 'commission_seq'
    commission_seq: str | None = None
    position: GCPReference[Position] | str
    payee: GCPReference[Participant] | str
    period: GCPReference[Period] | str
    incentive: GCPReference[Incentive] | str
    credit: GCPReference[Credit] | str
    pipeline_run: str
    pipeline_run_date: datetime
    value: Value
    rate_value: Value
    entry_number: Value
    business_units: list[str] | None = None
    processing_unit: str | None = None
    is_private: bool | None = None
    origin_type_id: str


class Credit(GCPResource, Generic16Mixin):
    """Credit."""

    attr_endpoint: ClassVar[str] = '/v2/credits'
    attr_seq: ClassVar[str] = 'credit_seq'
    credit_seq: str | None = None
    name: str
    position: GCPReference[Position] | str
    payee: GCPReference[Participant] | str
    sales_order: GCPReference[SalesOrder] | str
    sales_transaction: GCPReference[SalesTransaction] | str | None = None
    period: GCPReference[Period] | str
    credit_type: GCPReference[CreditType] | str
    value: Value
    preadjusted_value: Value
    origin_type_id: str
    reason: GCPReference[Reason] | str | None = None
    rule: GCPReference[Rule] | str | None = None
    is_rollable: bool | None = None
    roll_date: datetime | None = None
    is_held: bool | None = None
    release_date: datetime | None = None
    pipeline_run: str | None = None
    pipeline_run_date: datetime | None = None
    compensation_date: datetime | None = None
    comments: str | None = None
    is_private: bool | None = None
    business_units: list[str] | None = None
    processing_unit: str | None = None


class Deposit(GCPResource, Generic16Mixin):
    """Deposit."""

    attr_endpoint: ClassVar[str] = '/v2/deposits'
    attr_seq: ClassVar[str] = 'deposit_seq'
    deposit_seq: str | None = None
    name: str
    earning_group_id: str
    earning_code_id: str
    payee: GCPReference[Participant] | str
    position: GCPReference[Position] | str
    period: GCPReference[Period] | str
    value: Value
    preadjusted_value: Value
    origin_type_id: str
    reason: str | None = None
    business_units: list[str] | None = None
    rule: GCPReference[Rule] | str | None = None
    deposit_date: datetime | None = None
    is_held: bool | None = None
    release_date: datetime | None = None
    pipeline_run: str | None = None
    pipeline_run_date: datetime | None = None
    processing_unit: str | None = None
    comments: str | None = None
    is_private: bool | None = None
    model_seq: str | None = None


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


class GenericClassifier(GCPResource, Generic16Mixin):
    """Generic Classifier."""

    attr_endpoint: ClassVar[str] = '/v2/genericClassifiers'
    attr_seq: ClassVar[str] = 'generic_classifier_seq'
    generic_classifier_seq: str | None = None
    name: str | None = None
    description: str | None = None
    classifier_id: str
    classifier_seq: str
    selector_id: str
    effective_start_date: datetime
    effective_end_date: datetime
    business_units: list[str] | None = None
    created_by: str | None = Field(None, exclude=True, repr=False)
    create_date: datetime | None = Field(None, exclude=True, repr=False)
    modified_by: str | None = Field(None, exclude=True, repr=False)


class GenericClassifierType(GCPResource):
    """Generic Classifier Type."""

    attr_endpoint: ClassVar[str] = '/v2/genericClassifierTypes'
    attr_seq: ClassVar[str] = 'generic_classifier_type_seq'
    generic_classifier_type_seq: int | None = None
    name: str


class GlobalFieldName(GCPResource):
    """Global Field Name."""

    attr_endpoint: ClassVar[str] = '/v2/globalFieldNames'
    attr_seq: ClassVar[str] = 'global_field_name_seq'
    global_field_name_seq: str | None = None
    name: str
    description: str | None = None
    global_field_name_data_type_length: int


# class Group(GCPResource):
#     """Group."""

#     attr_endpoint: ClassVar[str] = "api/v2/groups"
#     attr_seq: ClassVar[str] = "group_seq"
#     group_seq: str | None = None
#     name: str
#     description: str | None = None


class Incentive(GCPResource, Generic16Mixin):
    """Incentive."""

    attr_endpoint: ClassVar[str] = '/v2/incentives'
    attr_seq: ClassVar[str] = 'incentive_seq'
    incentive_seq: str | None = None
    name: str | None = None
    quota: Value | None = None
    attainment: Value | None = None
    position: GCPReference[Position] | str
    payee: GCPReference[Participant] | str
    period: GCPReference[Period] | str
    rule: GCPReference[Rule] | str | None = None
    value: Value
    release_date: datetime | None = None
    pipeline_run: str | None = None
    pipeline_run_date: datetime | None = None
    is_active: bool = True
    is_private: bool | None = None
    processing_unit: str | None = None
    business_units: list[str] | None = None


class Measurement(GCPResource, Generic16Mixin):
    """Measurement."""

    attr_endpoint: ClassVar[str] = '/v2/measurements'
    attr_seq: ClassVar[str] = 'measurement_seq'
    measurement_seq: str | None = None
    name: str
    position: GCPReference[Position] | str
    payee: GCPReference[Participant] | str
    period: GCPReference[Period] | str
    rule: GCPReference[Rule] | str | None = None
    value: Value
    pipeline_run: str | None = None
    pipeline_run_date: datetime | None = None
    number_of_credits: Value
    is_private: bool | None = None
    processing_unit: str | None = None
    business_units: list[str] | None = None


class PrimaryMeasurement(Measurement):
    """Primary Measurement."""

    attr_endpoint: ClassVar[str] = '/v2/primaryMeasurements'


class SecondaryMeasurement(Measurement):
    """Secondary Measurement."""

    attr_endpoint: ClassVar[str] = '/v2/secondaryMeasurements'


class Message(GCPResource):
    """Message."""

    attr_endpoint: ClassVar[str] = '/v2/messages'
    attr_seq: ClassVar[str] = 'message_seq'
    message_seq: str | None = None
    message_key: str
    message_time_stamp: datetime
    argument_count: int
    sub_category: str
    message_log: str
    module: str
    rule: GCPReference[Rule] | str | None = None
    payee: GCPReference[Participant] | str | None = None
    message_type: str
    run_period: GCPReference[Period] | str | None = None
    object_seq: str | None = None
    sales_transaction: str | None = None
    position: GCPReference[Position] | str | None = None
    category: str | None = None
    credit: str | None = None


class MessageLog(GCPResource):
    """Message Log."""

    attr_endpoint: ClassVar[str] = '/v2/messageLogs'
    attr_seq: ClassVar[str] = 'message_log_seq'
    message_log_seq: str | None = None
    source_seq: str | None = None
    component_name: str
    log_date: datetime
    log_name: str


class Participant(GCPResource, Generic16Mixin):
    """Participant."""

    attr_endpoint: ClassVar[str] = '/v2/participants'
    attr_seq: ClassVar[str] = 'payee_seq'
    payee_seq: str | None = None
    payee_id: str
    first_name: str | None = None
    middle_name: str | None = None
    last_name: str
    participant_email: str | None = None
    prefix: str | None = None
    suffix: str | None = None
    effective_start_date: datetime
    effective_end_date: datetime
    hire_date: datetime | None = None
    termination_date: datetime | None = None
    salary: Value | None = None
    user_id: str
    preferred_language: str | None = None
    event_calendar: GCPReference[Calendar] | str | None = None
    tax_id: str | None = None
    business_units: list[str] | None = None
    created_by: str | None = Field(None, exclude=True, repr=False)
    create_date: datetime | None = Field(None, exclude=True, repr=False)
    modified_by: str | None = Field(None, exclude=True, repr=False)


# class Payment(GCPResource):
#     """Payment."""

#     attr_endpoint: ClassVar[str] = "api/v2/payments"
#     attr_seq: ClassVar[str] = "payment_seq"
#     payment_seq: str | None = None
#     position: GCPReference[Position] | str
#     payee: GCPReference[Participant] | str
#     period: GCPReference[Period] | str
#     earning_group_id: str
#     earning_code_id: str
#     trial_pipeline_run: str | None = None
#     trial_pipeline_run_date: datetime | None = None
#     post_pipeline_run: str | None = None
#     post_pipeline_run_date: datetime | None = None
#     reason: str | None = None
#     value: Value
#     processing_unit: str | None = None


class PaymentMapping(GCPResource):
    """Payment Mapping."""

    attr_endpoint: ClassVar[str] = '/v2/paymentMappings'
    attr_seq: ClassVar[str] = 'payment_mapping_seq'
    payment_mapping_seq: str | None = None
    source_table_name: str
    source_attribute: str
    payment_attribute: str


class PaymentSummary(GCPResource):
    """Payment Summary."""

    attr_endpoint: ClassVar[str] = '/v2/paymentSummarys'
    attr_seq: ClassVar[str] = 'payment_summary_seq'
    payment_summary_seq: str | None = None
    position: GCPReference[Position] | str
    participant: GCPReference[Participant] | str
    period: GCPReference[Period] | str
    earning_group_id: str
    pipeline_run: str | None = None
    pipeline_run_date: datetime | None = None
    applied_deposit: Value | None = None
    balance: Value | None = None
    prior_balance: Value | None = None
    outstanding_balance: Value | None = None
    payment: Value | None = None
    business_units: list[str] | None = None
    processing_unit: str | None = None


class Period(GCPResource):
    """Period."""

    attr_endpoint: ClassVar[str] = '/v2/periods'
    attr_seq: ClassVar[str] = 'period_seq'
    period_seq: str | None = None
    name: str
    short_name: str
    start_date: datetime
    end_date: datetime
    period_type: GCPReference[PeriodType] | str
    calendar: GCPReference[Calendar] | str
    description: str | None = None
    parent: GCPReference[Period] | str | None = None
    created_by: str | None = Field(None, exclude=True, repr=False)
    create_date: datetime | None = Field(None, exclude=True, repr=False)
    modified_by: str | None = Field(None, exclude=True, repr=False)


class PeriodType(GCPResource):
    """Period Type."""

    attr_endpoint: ClassVar[str] = '/v2/periodTypes'
    attr_seq: ClassVar[str] = 'period_type_seq'
    period_type_seq: str | None = None
    name: str
    description: str | None = None
    level: int | None = None
    created_by: str | None = Field(None, exclude=True, repr=False)
    create_date: datetime | None = Field(None, exclude=True, repr=False)
    modified_by: str | None = Field(None, exclude=True, repr=False)


class Pipeline(GCPResource):
    """Pipeline."""

    attr_endpoint: ClassVar[str] = '/v2/pipelines'
    attr_seq: ClassVar[str] = 'pipeline_run_seq'
    pipeline_run_seq: str | None = None
    command: (
        Literal[
            'PipelineRun',
            'Import',
            'XMLImport',
            'ModelRun',
            'MaintenanceRun',
            'CleanupDeferredPipelineResults',
        ]
        | None
    )
    stage_type: (
        const.PipelineRunStages
        | const.ImportStages
        | const.XMLImportStages
        | const.MaintenanceStages
        | None
    )
    date_submitted: datetime
    state: const.PipelineState
    user_id: str
    processing_unit: str | None = None
    period: GCPReference[Period] | str | None = None
    description: str | None = None
    status: const.PipelineStatus | None = None
    run_progress: float | None = None
    start_time: datetime | None = None
    stop_time: datetime | None = None
    start_date_scheduled: datetime | None = None
    batch_name: str | None = None
    priority: int | None = Field(None, repr=False)
    message: str | None = None
    num_errors: int | None = Field(None, repr=False)
    num_warnings: int | None = Field(None, repr=False)
    run_mode: const.ImportRunMode | const.PipelineRunMode | None = Field(
        None,
        repr=False,
    )
    product_version: str | None = None
    stored_proc_version: str | None = None
    schema_version: str | None = None
    remove_date: datetime | None = None
    end_date_scheduled: datetime | None = None
    run_parameters: str | None = None
    trace_level: str | None = None
    report_type_name: str | None = None
    target_database: str | None = None
    schedule_frequency: str | None = None
    group_name: str | None = None
    isolation_level: str | None = None
    schedule_day: str | None = None
    stage_tables: list[Assignment] | Assignment | None = Field(None, repr=False)
    model_seq: str | None = None
    model_run: str | None = None

    @field_validator('run_progress', mode='before')
    @classmethod
    def percent_as_float(cls, value: str) -> float | None:
        """Convert percentage string to float."""
        return int(value.removesuffix('%')) / 100 if value else None


class PositionGroup(GCPResource):
    """Position."""

    attr_endpoint: ClassVar[str] = '/v2/positionGroups'
    attr_seq: ClassVar[str] = 'position_group_seq'
    position_group_seq: str | None = None
    name: str
    business_units: list[str] | None = None
    created_by: str | None = Field(None, exclude=True, repr=False)
    create_date: datetime | None = Field(None, exclude=True, repr=False)
    modified_by: str | None = Field(None, exclude=True, repr=False)


class PositionRelation(GCPResource):
    """Position Relation."""

    attr_endpoint: ClassVar[str] = '/v2/positionRelations'
    attr_seq: ClassVar[str] = 'position_relation_seq'
    position_relation_seq: str | None = None
    name: str | None = None
    effective_start_date: datetime
    effective_end_date: datetime
    parent_position: GCPReference[Position] | str
    position_relation_type: str
    child_position: GCPReference[Position] | str
    created_by: str | None = Field(None, exclude=True, repr=False)
    create_date: datetime | None = Field(None, exclude=True, repr=False)
    modified_by: str | None = Field(None, exclude=True, repr=False)


class PostalCode(GCPResource, Generic16Mixin):
    """Postal Code."""

    attr_endpoint: ClassVar[str] = '/v2/postalCodes'
    attr_seq: ClassVar[str] = 'classifier_seq'
    classifier_seq: str | None = None
    classifier_id: str
    low_postal_code: str
    high_postal_code: str
    country: str
    name: str | None = None
    description: str | None = None
    selector_id: str | None = None
    effective_start_date: datetime
    effective_end_date: datetime
    business_units: list[str] | None = None


class ProcessingUnit(GCPResource):
    """Processing Unit."""

    attr_endpoint: ClassVar[str] = '/v2/processingUnits'
    attr_seq: ClassVar[str] = 'processing_unit_seq'
    processing_unit_seq: str | None = None
    name: str
    description: str | None = None


class Product(GCPResource, Generic16Mixin):
    """Product."""

    attr_endpoint: ClassVar[str] = '/v2/products'
    attr_seq: ClassVar[str] = 'classifier_seq'
    classifier_seq: str | None = None
    classifier_id: str
    name: str | None = None
    cost: Value | None = None
    price: Value | None = None
    description: str | None = None
    selector_id: str | None = None
    effective_start_date: datetime
    effective_end_date: datetime
    business_units: list[str] | None = None
    created_by: str | None = Field(None, exclude=True, repr=False)
    create_date: datetime | None = Field(None, exclude=True, repr=False)
    modified_by: str | None = Field(None, exclude=True, repr=False)


class Quota(GCPResource):
    """Quota."""

    attr_endpoint: ClassVar[str] = '/v2/quotas'
    attr_seq: ClassVar[str] = 'quota_seq'
    quota_seq: str | None = None
    calendar: GCPReference[Calendar] | str
    name: str
    description: str | None = None
    effective_start_date: datetime
    effective_end_date: datetime
    unit_type: GCPReference[UnitType] | str
    model_seq: str | None = None
    business_units: list[str] | None = None
    created_by: str | None = Field(None, exclude=True, repr=False)
    create_date: datetime | None = Field(None, exclude=True, repr=False)
    modified_by: str | None = Field(None, exclude=True, repr=False)


class SalesOrder(GCPResource, Generic16Mixin):
    """Sales Order."""

    attr_endpoint: ClassVar[str] = '/v2/salesOrders'
    attr_seq: ClassVar[str] = 'sales_order_seq'
    sales_order_seq: str | None = None
    order_id: str
    pipeline_run: str | None = None
    business_units: list[str] | None = None
    processing_unit: str | None = None
    model_seq: str | None = None
    created_by: str | None = Field(None, exclude=True, repr=False)
    create_date: datetime | None = Field(None, exclude=True, repr=False)
    modified_by: str | None = Field(None, exclude=True, repr=False)


class SalesTransaction(GCPResource, Generic32Mixin):
    """Sales Transaction."""

    attr_endpoint: ClassVar[str] = '/v2/salesTransactions'
    attr_seq: ClassVar[str] = 'sales_transaction_seq'
    sales_transaction_seq: str | None = None
    sales_order: GCPReference[SalesOrder] | str
    line_number: Value
    sub_line_number: Value
    event_type: GCPReference[EventType] | str
    product_id: str | None = None
    product_name: str | None = None
    product_description: str | None = None
    value: Value
    preadjusted_value: Value | None = None
    is_runnable: bool | None = None
    compensation_date: datetime
    number_of_units: Value | None = None
    unit_value: Value | None = None
    business_units: list[str] | None = None
    processing_unit: str | None = None
    model_seq: str | None = None
    ship_to_address: str | None = None
    bill_to_address: str | None = None
    other_to_address: str | None = None
    transaction_assignments: list[SalesTransactionAssignment] | None = None
    payment_terms: str | None = None
    accounting_date: datetime | None = None
    discount_percent: Value | None = None
    comments: str | None = None
    native_currency_amount: Value | None = None
    native_currency: str | None = None
    pipeline_run: str | None = None
    alternate_order_number: str | None = None
    origin_type_id: str | None = None
    adjustment_context: AdjustmentContext | None = None
    is_purged: bool | None = None
    reason: str | None = None
    channel: str | None = None
    po_number: str | None = None
    data_source: str | None = None
    discount_type: str | None = None
    modification_date: datetime | None = None


class User(GCPResource):
    """User."""

    attr_endpoint: ClassVar[str] = '/v2/users'
    attr_seq: ClassVar[str] = 'user_seq'
    user_seq: str | None = None
    id: str
    user_name: str | None = None
    description: str | None = None
    email: str | None = None
    read_only_business_unit_list: list[dict[Literal['name'], str]] | None = None
    full_access_business_unit_list: list[dict[Literal['name'], str]] | None = None
    preferred_language: str | None = None
    last_login: datetime | None = None
    created_by: str | None = Field(None, exclude=True, repr=False)
    create_date: datetime | None = Field(None, exclude=True, repr=False)
    modified_by: str | None = Field(None, exclude=True, repr=False)


class PlanComponent(GCPResource):
    """Plan."""

    attr_endpoint: ClassVar[str] = '/v2/planComponents'
    attr_seq: ClassVar[str] = 'plan_component_seq'
    plan_component_seq: str | None = None
    name: str
    description: str | None = None
    calendar: GCPReference[Calendar] | str
    effective_start_date: datetime
    effective_end_date: datetime
    business_units: list[str] | None = None
    not_allow_update: bool = False
    model_seq: str | None = None
    created_by: str | None = Field(None, exclude=True, repr=False)
    create_date: datetime | None = Field(None, exclude=True, repr=False)
    modified_by: str | None = Field(None, exclude=True, repr=False)


class Rule(GCPResource):
    """Rule."""

    attr_endpoint: ClassVar[str] = '/v2/rules'
    attr_seq: ClassVar[str] = 'rule_seq'
    rule_seq: str | None = None
    name: str
    description: str | None = None
    calendar: GCPReference[Calendar] | str
    effective_start_date: datetime
    effective_end_date: datetime
    business_unit: list[BusinessUnitAssignment] | BusinessUnitAssignment | None = None
    type: RuleUsage | None = None
    not_allow_update: bool = False
    model_seq: str | None = None
    created_by: str | None = Field(None, exclude=True, repr=False)
    create_date: datetime | None = Field(None, exclude=True, repr=False)
    modified_by: str | None = Field(None, exclude=True, repr=False)


class CreditRule(Rule):
    """Alias for Rule."""


class CommissionRule(Rule):
    """Alias for Rule."""


class DepositRule(Rule):
    """Alias for Rule."""


class MeasurementRule(Rule):
    """Alias for Rule."""


class UnitType(GCPResource):
    """Unit Type."""

    attr_endpoint: ClassVar[str] = '/v2/unitTypes'
    unit_type_seq: str
    name: str
    symbol: str | None = None
    scale: int
    reporting_scale: int
    position_of_symbol: int
    currency_locale: str | None = None
    value_class: ValueClass
    formatting: str | None = None


class _RuleElementOwner(GCPResource):
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


class Plan(_RuleElementOwner):
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


class Title(_RuleElementOwner, Generic16Mixin):
    """Title."""

    attr_endpoint: ClassVar[str] = '/v2/titles'
    plan: GCPReference[Plan] | str | None = None


class Position(_RuleElementOwner, Generic16Mixin):
    """Position.

    TODO: ``target_compensation`` is ``Value``?
    TODO: ``processing_unit`` should be ``GCPReference``?
    """

    attr_endpoint: ClassVar[str] = '/v2/positions'
    payee: GCPReference[Participant] | str | None = None
    plan: GCPReference[Plan] | str | None = None
    title: GCPReference[Title] | str | None = None
    manager: GCPReference[Position] | str | None = None
    position_group: GCPReference[PositionGroup] | str | None = None
    target_compensation: dict | None = None
    credit_start_date: datetime | None = None
    credit_end_date: datetime | None = None
    processing_start_date: datetime | None = None
    processing_end_date: datetime | None = None
    processing_unit: str | None = None


class _RuleElement(GCPResource):
    """Base class for Rule Element resources.

    TODO: What does ``owning_element`` represent?
    """

    attr_seq: ClassVar[str] = 'rule_element_seq'
    rule_element_seq: str | None = None
    name: str
    description: str | None = None
    calendar: GCPReference[Calendar] | str | None = None
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


class Category(_RuleElement, Generic16Mixin):
    """Category."""

    attr_endpoint: ClassVar[str] = '/v2/categories'
    owner: GCPReference[CategoryTree] | str
    parent: GCPReference[Category] | str | None = None


class FixedValue(_RuleElement):
    """Fixed Value."""

    attr_endpoint: ClassVar[str] = '/v2/fixedValues'
    value: Value | None = None
    fixed_value_type: GCPReference[FixedValueType] | str | None = None
    period_type: GCPReference[PeriodType] | str | None = None


class Formula(_RuleElement):
    """Formula."""

    attr_endpoint: ClassVar[str] = '/v2/formulas'


class FixedValueVariable(_RuleElement):
    """Fixed Value Variable."""

    attr_endpoint: ClassVar[str] = '/v2/fixedValueVariables'
    default_element: GCPReference[FixedValue] | str | None = None
    required_period_type: GCPReference[PeriodType] | str | None = None


class RateTable(_RuleElement):
    """Rate Table."""

    attr_endpoint: ClassVar[str] = '/v2/rateTables'


class RateTableVariable(_RuleElement):
    """Rate Table Variable."""

    attr_endpoint: ClassVar[str] = '/v2/rateTableVariables'
    default_element: GCPReference[RateTable] | str | None = None
    required_period_type: GCPReference[PeriodType] | str | None = None


class RelationalMDLT(_RuleElement):
    """Relational MDLT (Lookup Table).

    Multi Dimensional Lookup Table.

    TODO: Are ``dimensions`` and ``indices`` expandable?
            Yes
    TODO: What does ``expression_type_counts`` represent?
    """

    attr_endpoint: ClassVar[str] = '/v2/relationalMDLTs'
    return_unit_type: GCPReference[UnitType] | str | None = None
    treat_null_as_zero: bool | None = None
    dimensions: list[Assignment] | Assignment | None = None
    indices: list[Assignment] | Assignment | None = None
    expression_type_counts: str | None = None


class LookUpTableVariable(_RuleElement):
    """LookUp Table Variable."""

    attr_endpoint: ClassVar[str] = '/v2/lookUpTableVariables'
    default_element: GCPReference[RelationalMDLT] | str | None = None
    required_period_type: GCPReference[PeriodType] | str | None = None


class Territory(_RuleElement):
    """Territory."""

    attr_endpoint: ClassVar[str] = '/v2/territories'


class TerritoryVariable(_RuleElement):
    """Territory Variable."""

    attr_endpoint: ClassVar[str] = '/v2/territoryVariables'
    default_element: GCPReference[Territory] | str | None = None
    required_period_type: GCPReference[PeriodType] | str | None = None


class Variable(_RuleElement):
    """Variable.

    TODO: ``default_element`` can refer FixedValue, RateTable or RelationalMDLT.
    """

    attr_endpoint: ClassVar[str] = '/v2/variables'
    default_element: str | None = None
    required_period_type: GCPReference[PeriodType] | str | None = None


class DataType(GCPResource):
    """Base class for Legacy DataType resources."""

    attr_seq: ClassVar[str] = 'data_type_seq'
    data_type_seq: str | None = None
    description: str | None = None
    create_date: datetime | None = Field(None, exclude=True, repr=False)
    created_by: str | None = Field(None, exclude=True, repr=False)
    modified_by: str | None = Field(None, exclude=True, repr=False)
    not_allow_update: bool | None = None


class CreditType(DataType):
    """Credit Type."""

    attr_endpoint: ClassVar[str] = '/v2/creditTypes'
    credit_type_id: str = Field(validation_alias=AliasChoices('creditTypeId', 'id'))


class EarningCode(DataType):
    """Earning Code."""

    attr_endpoint: ClassVar[str] = '/v2/earningCodes'
    earning_code_id: str = Field(validation_alias=AliasChoices('earningCodeId', 'id'))


class EarningGroup(DataType):
    """Earning Group."""

    attr_endpoint: ClassVar[str] = '/v2/earningGroups'
    earning_group_id: str = Field(validation_alias=AliasChoices('earningGroupId', 'id'))


class EventType(DataType):
    """Event Type."""

    attr_endpoint: ClassVar[str] = '/v2/eventTypes'
    event_type_id: str = Field(validation_alias=AliasChoices('eventTypeId', 'id'))


class FixedValueType(DataType):
    """Fixed Value Type."""

    attr_endpoint: ClassVar[str] = '/v2/fixedValueTypes'
    fixed_value_type_id: str = Field(
        validation_alias=AliasChoices('fixedValueTypeId', 'id'),
    )


class PositionRelationType(DataType):
    """Position Relation Type."""

    attr_endpoint: ClassVar[str] = '/v2/positionRelationTypes'
    name: str


class Reason(DataType):
    """Reason."""

    attr_endpoint: ClassVar[str] = '/v2/reasons'
    reason_id: str = Field(validation_alias=AliasChoices('reasonId', 'id'))


class StatusCode(DataType):
    """Status Code."""

    attr_endpoint: ClassVar[str] = '/v2/statusCodes'
    status: str
    name: str | None = None
    type: str | None = None
    is_active: bool = True
