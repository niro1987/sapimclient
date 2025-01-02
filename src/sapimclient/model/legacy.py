"""Pydantic models for Python SAP Incentive Management Client (Legacy Tenants)."""
# pylint: disable=duplicate-code,too-many-lines

from __future__ import annotations

from datetime import datetime
from importlib import import_module
from typing import Any, ClassVar, Literal

from pydantic import (
    AliasChoices,
    Field,
    computed_field,
    field_validator,
    model_validator,
)

from sapimclient import const

from .base import (
    AdjustmentContext,
    Assignment,
    BusinessUnitAssignment,
    Endpoint,
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
    'Allocate',
    'AppliedDeposit',
    'AuditLog',
    'Balance',
    'BusinessUnit',
    'Calendar',
    'Category',
    'CategoryClassifier',
    'CategoryTree',
    'CFixedValue',
    'Classify',
    'CleanupDefferedResults',
    'Commission',
    'CommissionRule',
    'Compensate',
    'CompensateAndPay',
    'Credit',
    'CreditRule',
    'CreditType',
    'Deposit',
    'DepositRule',
    'EarningCode',
    'EarningGroup',
    'EarningGroupCode',
    'EventType',
    'Finalize',
    'FixedValue',
    'FixedValueType',
    'FixedValueVariable',
    'Formula',
    'GenericClassifier',
    'GenericClassifierType',
    'GlobalFieldName',
    'Incentive',
    'LegacyReference',
    'LegacyResource',
    'LookUpTableVariable',
    'Measurement',
    'MeasurementRule',
    'Message',
    'MessageLog',
    'Participant',
    'Pay',
    'PaymentMapping',
    'PaymentSummary',
    'Period',
    'PeriodType',
    'Pipeline',
    'PipelineJob',
    'Plan',
    'PlanComponent',
    'Position',
    'PositionGroup',
    'PositionRelation',
    'PositionRelationType',
    'Post',
    'PostalCode',
    'PrimaryMeasurement',
    'ProcessingUnit',
    'Product',
    'Purge',
    'Quota',
    'RateTable',
    'RateTableVariable',
    'Reason',
    'RelationalMDLT',
    'ReportsGeneration',
    'ResetFromAllocate',
    'ResetFromClassify',
    'ResetFromPay',
    'ResetFromReward',
    'ResetFromValidate',
    'Reward',
    'Rule',
    'SalesOrder',
    'SalesTransaction',
    'SecondaryMeasurement',
    'StatusCode',
    'Summarize',
    'Territory',
    'TerritoryVariable',
    'Title',
    'Transfer',
    'TransferIfAllValid',
    'UndoFinalize',
    'UndoPost',
    'UnitType',
    'UpdateAnalytics',
    'User',
    'Validate',
    'ValidateAndTransfer',
    'ValidateAndTransferIfAllValid',
    'Variable',
    'XMLImport',
]

STAGETABLES: dict[str, list[str]] = {
    'TransactionalData': [
        'TransactionAndCredit',
        'Deposit',
    ],
    'OrganizationData': [
        'Participant',
        'Position',
        'Title',
        'PositionRelation',
    ],
    'ClassificationData': [
        'Category',
        'Category_Classifiers',
        'Customer',
        'Product',
        'PostalCode',
        'GenericClassifier',
    ],
    'PlanRelatedData': [
        'FixedValue',
        'VariableAssignment',
        'Quota',
        'RelationalMDLT',
    ],
}


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


class DataType(LegacyResource):
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


class PipelineJob(Endpoint):
    """Base class for a Pipeline Job."""

    attr_endpoint_prefix: ClassVar[str] = '/api'
    attr_endpoint: ClassVar[str] = '/v2/pipelines'
    command: Literal['PipelineRun', 'Import', 'XMLImport']
    run_stats: bool = False


class ResetFromValidate(PipelineJob):
    """Run a ResetFromValidate pipeline."""

    attr_endpoint: ClassVar[str] = '/v2/pipelines/resetfromvalidate'
    command: Literal['Import'] = 'Import'
    calendar_seq: str
    period_seq: str
    batch_name: str | None = None


class Purge(PipelineJob):
    """Run a Purge pipeline."""

    stage_type_seq: Literal[const.PipelineRunStages.Purge] = (
        const.PipelineRunStages.Purge
    )
    command: Literal['PipelineRun'] = 'PipelineRun'
    batch_name: str
    module: const.StageTables

    @computed_field
    def stage_tables(self) -> list[str]:
        """Compute stageTables field based on module."""
        return STAGETABLES[self.module]


class XMLImport(PipelineJob):
    """Run an XML Import pipeline."""

    command: Literal['XMLImport'] = 'XMLImport'
    stage_type_seq: Literal[const.XMLImportStages.XMLImport] = (
        const.XMLImportStages.XMLImport
    )
    xml_file_name: str
    xml_file_content: str
    update_existing_objects: bool = False


class _PipelineRunJob(PipelineJob):
    """Base class for a PipelineRun job."""

    command: Literal['PipelineRun'] = 'PipelineRun'
    period_seq: str
    calendar_seq: str
    stage_type_seq: const.PipelineRunStages
    run_mode: const.PipelineRunMode = const.PipelineRunMode.Full
    position_groups: list[str] | None = None
    position_seqs: list[str] | None = None
    processing_unit_seq: str | None = None

    @model_validator(mode='after')
    def check_runmode(self) -> _PipelineRunJob:
        """Validate run_mode together with position_groups and position_seqs."""
        if self.run_mode in (
            const.PipelineRunMode.Full,
            const.PipelineRunMode.Incremental,
        ) and not (self.position_groups is None and self.position_seqs is None):
            msg = (
                "When run_mode is 'full' or 'incremental' "
                'position_groups and position_seqs must be None'
            )
            raise ValueError(msg)
        if self.run_mode == const.PipelineRunMode.Positions and not (
            self.position_groups or self.position_seqs
        ):
            msg = (
                "When run_mode is 'positions' "
                'provide either position_groups or position_seqs, not both'
            )
            raise ValueError(msg)

        if self.position_groups and self.position_seqs:
            msg = 'Provide either position_groups or position_seqs, not both'
            raise ValueError(msg)

        return self


class Classify(_PipelineRunJob):
    """Run a Classify pipeline."""

    stage_type_seq: Literal[const.PipelineRunStages.Classify] = (
        const.PipelineRunStages.Classify
    )
    run_mode: Literal[const.PipelineRunMode.Full, const.PipelineRunMode.Incremental] = (
        const.PipelineRunMode.Full
    )
    position_groups: None = None
    position_seqs: None = None


class Allocate(_PipelineRunJob):
    """Run an Allocate pipeline."""

    stage_type_seq: Literal[const.PipelineRunStages.Allocate] = (
        const.PipelineRunStages.Allocate
    )


class Reward(_PipelineRunJob):
    """Run a Reward pipeline."""

    stage_type_seq: Literal[const.PipelineRunStages.Reward] = (
        const.PipelineRunStages.Reward
    )
    run_mode: Literal[const.PipelineRunMode.Full, const.PipelineRunMode.Positions] = (
        const.PipelineRunMode.Full
    )


class Pay(_PipelineRunJob):
    """Run a Pay pipeline."""

    stage_type_seq: Literal[const.PipelineRunStages.Pay] = const.PipelineRunStages.Pay
    run_mode: Literal[const.PipelineRunMode.Full, const.PipelineRunMode.Positions] = (
        const.PipelineRunMode.Full
    )
    position_seqs: None = None


class Summarize(_PipelineRunJob):
    """Run a Summarize pipeline."""

    stage_type_seq: Literal[const.PipelineRunStages.Summarize] = (
        const.PipelineRunStages.Summarize
    )


class Compensate(_PipelineRunJob):
    """Run a Compensate pipeline."""

    stage_type_seq: Literal[const.PipelineRunStages.Compensate] = (
        const.PipelineRunStages.Compensate
    )
    remove_stale_results: bool = False


class CompensateAndPay(_PipelineRunJob):
    """Run a CompensateAndPay pipeline."""

    stage_type_seq: Literal[const.PipelineRunStages.CompensateAndPay] = (
        const.PipelineRunStages.CompensateAndPay
    )
    remove_stale_results: bool = False


class ResetFromClassify(_PipelineRunJob):
    """Run a ResetFromClassify pipeline."""

    stage_type_seq: Literal[const.PipelineRunStages.ResetFromClassify] = (
        const.PipelineRunStages.ResetFromClassify
    )


class ResetFromAllocate(_PipelineRunJob):
    """Run a ResetFromAllocate pipeline."""

    stage_type_seq: Literal[const.PipelineRunStages.ResetFromAllocate] = (
        const.PipelineRunStages.ResetFromAllocate
    )


class ResetFromReward(_PipelineRunJob):
    """Run a ResetFromReward pipeline."""

    stage_type_seq: Literal[const.PipelineRunStages.ResetFromReward] = (
        const.PipelineRunStages.ResetFromReward
    )


class ResetFromPay(_PipelineRunJob):
    """Run a ResetFromPay pipeline."""

    stage_type_seq: Literal[const.PipelineRunStages.ResetFromPay] = (
        const.PipelineRunStages.ResetFromPay
    )


class Post(_PipelineRunJob):
    """Run a Post pipeline."""

    stage_type_seq: Literal[const.PipelineRunStages.Post] = const.PipelineRunStages.Post


class Finalize(_PipelineRunJob):
    """Run a Finalize pipeline."""

    stage_type_seq: Literal[const.PipelineRunStages.Finalize] = (
        const.PipelineRunStages.Finalize
    )


class ReportsGeneration(_PipelineRunJob):
    """Run a ReportsGeneration pipeline."""

    stage_type_seq: Literal[const.PipelineRunStages.ReportsGeneration] = (
        const.PipelineRunStages.ReportsGeneration
    )
    generate_ods_reports: Literal[True] = Field(
        default=True,
        alias='generateODSReports',
    )
    report_type_name: const.ReportType = const.ReportType.Crystal
    report_formats_list: list[const.ReportFormat]
    ods_report_list: list[str]
    bo_groups_list: list[str]
    run_mode: Literal[const.PipelineRunMode.Full, const.PipelineRunMode.Positions] = (
        const.PipelineRunMode.Full
    )


class UndoPost(_PipelineRunJob):
    """Run a UndoPost pipeline."""

    stage_type_seq: Literal[const.PipelineRunStages.UndoPost] = (
        const.PipelineRunStages.UndoPost
    )


class UndoFinalize(_PipelineRunJob):
    """Run a UndoFinalize pipeline."""

    stage_type_seq: Literal[const.PipelineRunStages.UndoFinalize] = (
        const.PipelineRunStages.UndoFinalize
    )


class CleanupDefferedResults(_PipelineRunJob):
    """Run a CleanupDefferedResults pipeline."""

    stage_type_seq: Literal[const.PipelineRunStages.CleanupDefferedResults] = (
        const.PipelineRunStages.CleanupDefferedResults
    )


class UpdateAnalytics(_PipelineRunJob):
    """Run a UpdateAnalytics pipeline."""

    stage_type_seq: Literal[const.PipelineRunStages.UpdateAnalytics] = (
        const.PipelineRunStages.UpdateAnalytics
    )


class _ImportJob(PipelineJob):
    """Base class for an Import job."""

    command: Literal['Import'] = 'Import'
    stage_type_seq: const.ImportStages
    calendar_seq: str
    batch_name: str
    module: const.StageTables
    run_mode: const.ImportRunMode = const.ImportRunMode.All

    @computed_field
    def stage_tables(self) -> list[str]:
        """Compute stageTables field based on module."""
        return STAGETABLES[self.module]

    @model_validator(mode='after')
    def validate_conditional_fields(self) -> _ImportJob:
        """Validate conditional required fields.

        Validations:
        ------------
            run_mode can only be 'new' when importing TransactionalData
        """
        if (
            self.module != const.StageTables.TransactionalData
            and self.run_mode == const.ImportRunMode.New
        ):
            msg = ("run_mode can only be 'new' when importing TransactionalData",)
            raise ValueError(msg)

        return self


class Validate(_ImportJob):
    """Run a Validate pipeline."""

    stage_type_seq: Literal[const.ImportStages.Validate] = const.ImportStages.Validate
    revalidate: const.RevalidateMode = const.RevalidateMode.All


class Transfer(_ImportJob):
    """Run a Transfer pipeline."""

    stage_type_seq: Literal[const.ImportStages.Transfer] = const.ImportStages.Transfer


class ValidateAndTransfer(_ImportJob):
    """Run a ValidateAndTransfer pipeline."""

    stage_type_seq: Literal[const.ImportStages.ValidateAndTransfer] = (
        const.ImportStages.ValidateAndTransfer
    )
    revalidate: const.RevalidateMode = const.RevalidateMode.All


class ValidateAndTransferIfAllValid(_ImportJob):
    """Run a ValidateAndTransferIfAllValid pipeline."""

    stage_type_seq: Literal[const.ImportStages.ValidateAndTransferIfAllValid] = (
        const.ImportStages.ValidateAndTransferIfAllValid
    )
    revalidate: const.RevalidateMode = const.RevalidateMode.All


class TransferIfAllValid(_ImportJob):
    """Run a TransferIfAllValid pipeline."""

    stage_type_seq: Literal[const.ImportStages.TransferIfAllValid] = (
        const.ImportStages.TransferIfAllValid
    )


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


class AuditLog(LegacyResource):
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


class BusinessUnit(LegacyResource):
    """Business Unit."""

    attr_endpoint: ClassVar[str] = '/v2/businessUnits'
    attr_seq: ClassVar[str] = 'business_unit_seq'
    business_unit_seq: str | None = None
    name: str
    description: str | None = None
    mask: str | None = None
    processing_unit: str | None = None


class Calendar(LegacyResource):
    """Calendar."""

    attr_endpoint: ClassVar[str] = '/v2/calendars'
    attr_seq: ClassVar[str] = 'calendar_seq'
    calendar_seq: str | None = None
    name: str
    description: str | None = None
    minor_period_type: LegacyReference | str | None = None
    major_period_type: LegacyReference | str | None = None
    created_by: str | None = Field(None, exclude=True, repr=False)
    create_date: datetime | None = Field(None, exclude=True, repr=False)
    modified_by: str | None = Field(None, exclude=True, repr=False)


class CategoryClassifier(LegacyResource):
    """categoryClassifier."""

    attr_endpoint: ClassVar[str] = '/v2/categoryClassifiers'
    attr_seq: ClassVar[str] = 'category_classifiers_seq'
    category_classifiers_seq: str | None = None
    category_tree: LegacyReference | str
    category: LegacyReference | str
    classifier: LegacyReference | str
    effective_start_date: datetime
    effective_end_date: datetime
    created_by: str | None = Field(None, exclude=True, repr=False)
    create_date: datetime | None = Field(None, exclude=True, repr=False)
    modified_by: str | None = Field(None, exclude=True, repr=False)


class CategoryTree(LegacyResource):
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


class Commission(LegacyResource):
    """Commission.

    TODO: No results.
    """

    attr_endpoint: ClassVar[str] = '/v2/commissions'
    attr_seq: ClassVar[str] = 'commission_seq'
    commission_seq: str | None = None
    position: LegacyReference | str
    payee: LegacyReference | str
    period: LegacyReference | str
    incentive: LegacyReference | str
    credit: LegacyReference | str
    pipeline_run: str
    pipeline_run_date: datetime
    value: Value
    rate_value: Value
    entry_number: Value
    business_units: list[str] | None = None
    processing_unit: str | None = None
    is_private: bool | None = None
    origin_type_id: str


class Credit(LegacyResource, Generic16Mixin):
    """Credit."""

    attr_endpoint: ClassVar[str] = '/v2/credits'
    attr_seq: ClassVar[str] = 'credit_seq'
    credit_seq: str | None = None
    name: str
    position: LegacyReference | str
    payee: LegacyReference | str
    sales_order: LegacyReference | str
    sales_transaction: LegacyReference | str | None = None
    period: LegacyReference | str
    credit_type: LegacyReference | str
    value: Value
    preadjusted_value: Value
    origin_type_id: str
    reason: LegacyReference | str | None = None
    rule: LegacyReference | str | None = None
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


class Deposit(LegacyResource, Generic16Mixin):
    """Deposit."""

    attr_endpoint: ClassVar[str] = '/v2/deposits'
    attr_seq: ClassVar[str] = 'deposit_seq'
    deposit_seq: str | None = None
    name: str
    earning_group_id: str
    earning_code_id: str
    payee: LegacyReference | str
    position: LegacyReference | str
    period: LegacyReference | str
    value: Value
    preadjusted_value: Value
    origin_type_id: str
    reason: str | None = None
    business_units: list[str] | None = None
    rule: LegacyReference | str | None = None
    deposit_date: datetime | None = None
    is_held: bool | None = None
    release_date: datetime | None = None
    pipeline_run: str | None = None
    pipeline_run_date: datetime | None = None
    processing_unit: str | None = None
    comments: str | None = None
    is_private: bool | None = None
    model_seq: str | None = None


class EarningGroupCode(LegacyResource):
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


class GenericClassifier(LegacyResource, Generic16Mixin):
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


class GenericClassifierType(LegacyResource):
    """Generic Classifier Type."""

    attr_endpoint: ClassVar[str] = '/v2/genericClassifierTypes'
    attr_seq: ClassVar[str] = 'generic_classifier_type_seq'
    generic_classifier_type_seq: int | None = None
    name: str


class GlobalFieldName(LegacyResource):
    """Global Field Name."""

    attr_endpoint: ClassVar[str] = '/v2/globalFieldNames'
    attr_seq: ClassVar[str] = 'global_field_name_seq'
    global_field_name_seq: str | None = None
    name: str
    description: str | None = None
    global_field_name_data_type_length: int


# class Group(LegacyResource):
#     """Group."""

#     attr_endpoint: ClassVar[str] = "api/v2/groups"
#     attr_seq: ClassVar[str] = "group_seq"
#     group_seq: str | None = None
#     name: str
#     description: str | None = None


class Incentive(LegacyResource, Generic16Mixin):
    """Incentive."""

    attr_endpoint: ClassVar[str] = '/v2/incentives'
    attr_seq: ClassVar[str] = 'incentive_seq'
    incentive_seq: str | None = None
    name: str | None = None
    quota: Value | None = None
    attainment: Value | None = None
    position: LegacyReference | str
    payee: LegacyReference | str
    period: LegacyReference | str
    rule: LegacyReference | str | None = None
    value: Value
    release_date: datetime | None = None
    pipeline_run: str | None = None
    pipeline_run_date: datetime | None = None
    is_active: bool = True
    is_private: bool | None = None
    processing_unit: str | None = None
    business_units: list[str] | None = None


class Measurement(LegacyResource, Generic16Mixin):
    """Measurement."""

    attr_endpoint: ClassVar[str] = '/v2/measurements'
    attr_seq: ClassVar[str] = 'measurement_seq'
    measurement_seq: str | None = None
    name: str
    position: LegacyReference | str
    payee: LegacyReference | str
    period: LegacyReference | str
    rule: LegacyReference | str | None = None
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


class Message(LegacyResource):
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
    rule: LegacyReference | str | None = None
    payee: LegacyReference | str | None = None
    message_type: str
    run_period: LegacyReference | str | None = None
    object_seq: str | None = None
    sales_transaction: str | None = None
    position: LegacyReference | str | None = None
    category: str | None = None
    credit: str | None = None


class MessageLog(LegacyResource):
    """Message Log."""

    attr_endpoint: ClassVar[str] = '/v2/messageLogs'
    attr_seq: ClassVar[str] = 'message_log_seq'
    message_log_seq: str | None = None
    source_seq: str | None = None
    component_name: str
    log_date: datetime
    log_name: str


class Participant(LegacyResource, Generic16Mixin):
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
    event_calendar: LegacyReference | str | None = None
    tax_id: str | None = None
    business_units: list[str] | None = None
    created_by: str | None = Field(None, exclude=True, repr=False)
    create_date: datetime | None = Field(None, exclude=True, repr=False)
    modified_by: str | None = Field(None, exclude=True, repr=False)


# class Payment(LegacyResource):
#     """Payment."""

#     attr_endpoint: ClassVar[str] = "api/v2/payments"
#     attr_seq: ClassVar[str] = "payment_seq"
#     payment_seq: str | None = None
#     position: LegacyReference | str
#     payee: LegacyReference | str
#     period: LegacyReference | str
#     earning_group_id: str
#     earning_code_id: str
#     trial_pipeline_run: str | None = None
#     trial_pipeline_run_date: datetime | None = None
#     post_pipeline_run: str | None = None
#     post_pipeline_run_date: datetime | None = None
#     reason: str | None = None
#     value: Value
#     processing_unit: str | None = None


class PaymentMapping(LegacyResource):
    """Payment Mapping."""

    attr_endpoint: ClassVar[str] = '/v2/paymentMappings'
    attr_seq: ClassVar[str] = 'payment_mapping_seq'
    payment_mapping_seq: str | None = None
    source_table_name: str
    source_attribute: str
    payment_attribute: str


class PaymentSummary(LegacyResource):
    """Payment Summary."""

    attr_endpoint: ClassVar[str] = '/v2/paymentSummarys'
    attr_seq: ClassVar[str] = 'payment_summary_seq'
    payment_summary_seq: str | None = None
    position: LegacyReference | str
    participant: LegacyReference | str
    period: LegacyReference | str
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


class Period(LegacyResource):
    """Period."""

    attr_endpoint: ClassVar[str] = '/v2/periods'
    attr_seq: ClassVar[str] = 'period_seq'
    period_seq: str | None = None
    name: str
    short_name: str
    start_date: datetime
    end_date: datetime
    period_type: LegacyReference | str
    calendar: LegacyReference | str
    description: str | None = None
    parent: LegacyReference | str | None = None
    created_by: str | None = Field(None, exclude=True, repr=False)
    create_date: datetime | None = Field(None, exclude=True, repr=False)
    modified_by: str | None = Field(None, exclude=True, repr=False)


class PeriodType(LegacyResource):
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


class Pipeline(LegacyResource):
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
    period: LegacyReference | str | None = None
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


class PositionGroup(LegacyResource):
    """Position."""

    attr_endpoint: ClassVar[str] = '/v2/positionGroups'
    attr_seq: ClassVar[str] = 'position_group_seq'
    position_group_seq: str | None = None
    name: str
    business_units: list[str] | None = None
    created_by: str | None = Field(None, exclude=True, repr=False)
    create_date: datetime | None = Field(None, exclude=True, repr=False)
    modified_by: str | None = Field(None, exclude=True, repr=False)


class PositionRelation(LegacyResource):
    """Position Relation."""

    attr_endpoint: ClassVar[str] = '/v2/positionRelations'
    attr_seq: ClassVar[str] = 'position_relation_seq'
    position_relation_seq: str | None = None
    name: str | None = None
    effective_start_date: datetime
    effective_end_date: datetime
    parent_position: LegacyReference | str
    position_relation_type: str
    child_position: LegacyReference | str
    created_by: str | None = Field(None, exclude=True, repr=False)
    create_date: datetime | None = Field(None, exclude=True, repr=False)
    modified_by: str | None = Field(None, exclude=True, repr=False)


class PostalCode(LegacyResource, Generic16Mixin):
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


class ProcessingUnit(LegacyResource):
    """Processing Unit."""

    attr_endpoint: ClassVar[str] = '/v2/processingUnits'
    attr_seq: ClassVar[str] = 'processing_unit_seq'
    processing_unit_seq: str | None = None
    name: str
    description: str | None = None


class Product(LegacyResource, Generic16Mixin):
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


class Quota(LegacyResource):
    """Quota."""

    attr_endpoint: ClassVar[str] = '/v2/quotas'
    attr_seq: ClassVar[str] = 'quota_seq'
    quota_seq: str | None = None
    calendar: LegacyReference | str
    name: str
    description: str | None = None
    effective_start_date: datetime
    effective_end_date: datetime
    unit_type: LegacyReference | str
    model_seq: str | None = None
    business_units: list[str] | None = None
    created_by: str | None = Field(None, exclude=True, repr=False)
    create_date: datetime | None = Field(None, exclude=True, repr=False)
    modified_by: str | None = Field(None, exclude=True, repr=False)


class SalesOrder(LegacyResource, Generic16Mixin):
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


class SalesTransaction(LegacyResource, Generic32Mixin):
    """Sales Transaction."""

    attr_endpoint: ClassVar[str] = '/v2/salesTransactions'
    attr_seq: ClassVar[str] = 'sales_transaction_seq'
    sales_transaction_seq: str | None = None
    sales_order: LegacyReference | str
    line_number: Value
    sub_line_number: Value
    event_type: LegacyReference | str
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


class User(LegacyResource):
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


class PlanComponent(LegacyResource):
    """Plan."""

    attr_endpoint: ClassVar[str] = '/v2/planComponents'
    attr_seq: ClassVar[str] = 'plan_component_seq'
    plan_component_seq: str | None = None
    name: str
    description: str | None = None
    calendar: LegacyReference | str
    effective_start_date: datetime
    effective_end_date: datetime
    business_units: list[str] | None = None
    not_allow_update: bool = False
    model_seq: str | None = None
    created_by: str | None = Field(None, exclude=True, repr=False)
    create_date: datetime | None = Field(None, exclude=True, repr=False)
    modified_by: str | None = Field(None, exclude=True, repr=False)


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


class CreditRule(Rule):
    """Alias for Rule."""


class CommissionRule(Rule):
    """Alias for Rule."""


class DepositRule(Rule):
    """Alias for Rule."""


class MeasurementRule(Rule):
    """Alias for Rule."""


class UnitType(LegacyResource):
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


class _RuleElementOwner(LegacyResource):
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


class Plan(_RuleElementOwner):
    """Plan.

    Parameters:
        rule_element_owner_seq (str | None): System Unique Identifier.
        name (str): Name of the plan.
        description (str | None): Description of the plan.
        calendar (LegacyReference | str): LegacyReference to ``Calendar`` associated
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
    calendar: LegacyReference | str


class Position(_RuleElementOwner, Generic16Mixin):
    """Position.

    TODO: ``target_compensation`` is ``Value``?
    TODO: ``processing_unit`` should be ``LegacyReference``?
    """

    attr_endpoint: ClassVar[str] = '/v2/positions'
    payee: LegacyReference | str | None = None
    plan: LegacyReference | str | None = None
    title: LegacyReference | str | None = None
    manager: LegacyReference | str | None = None
    position_group: LegacyReference | str | None = None
    target_compensation: dict | None = None
    credit_start_date: datetime | None = None
    credit_end_date: datetime | None = None
    processing_start_date: datetime | None = None
    processing_end_date: datetime | None = None
    processing_unit: str | None = None


class Title(_RuleElementOwner, Generic16Mixin):
    """Title."""

    attr_endpoint: ClassVar[str] = '/v2/titles'
    plan: LegacyReference | str | None = None


class _RuleElement(LegacyResource):
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


class Category(_RuleElement, Generic16Mixin):
    """Category."""

    attr_endpoint: ClassVar[str] = '/v2/categories'
    owner: LegacyReference | str
    parent: LegacyReference | str | None = None


class FixedValue(_RuleElement):
    """Fixed Value."""

    attr_endpoint: ClassVar[str] = '/v2/fixedValues'
    value: Value | None = None
    fixed_value_type: LegacyReference | str | None = None
    period_type: LegacyReference | str | None = None


class CFixedValue(FixedValue):
    """Alias for ``FixedValue``."""


class Formula(_RuleElement):
    """Formula."""

    attr_endpoint: ClassVar[str] = '/v2/formulas'


class FixedValueVariable(_RuleElement):
    """Fixed Value Variable."""

    attr_endpoint: ClassVar[str] = '/v2/fixedValueVariables'
    default_element: LegacyReference | str | None = None
    required_period_type: LegacyReference | str | None = None


class LookUpTableVariable(_RuleElement):
    """LookUp Table Variable."""

    attr_endpoint: ClassVar[str] = '/v2/lookUpTableVariables'
    default_element: LegacyReference | str | None = None
    required_period_type: LegacyReference | str | None = None


class RateTable(_RuleElement):
    """Rate Table.

    TODO: Does this endpoint return ``default_element``?
    """

    attr_endpoint: ClassVar[str] = '/v2/rateTables'


class RateTableVariable(_RuleElement):
    """Rate Table Variable."""

    attr_endpoint: ClassVar[str] = '/v2/rateTableVariables'
    default_element: LegacyReference | str | None = None
    required_period_type: LegacyReference | str | None = None


class RelationalMDLT(_RuleElement):
    """Relational MDLT (Lookup Table).

    Multi Dimensional Lookup Table.

    TODO: Does this endpoint return ``default_element``?
    TODO: Are ``dimensions`` and ``indices`` expandable?
    TODO: What does ``expression_type_counts`` represent?
    """

    attr_endpoint: ClassVar[str] = '/v2/relationalMDLTs'
    default_element: LegacyReference | str | None = None
    required_period_type: LegacyReference | str | None = None
    return_unit_type: LegacyReference | str | None = None
    treat_null_as_zero: bool | None = None
    dimensions: list[Assignment] | Assignment | None = None
    indices: list[Assignment] | Assignment | None = None
    expression_type_counts: str | None = None


class Territory(_RuleElement):
    """Territory."""

    attr_endpoint: ClassVar[str] = '/v2/territories'


class TerritoryVariable(_RuleElement):
    """Territory Variable."""

    attr_endpoint: ClassVar[str] = '/v2/territoryVariables'
    default_element: LegacyReference | str | None = None
    required_period_type: LegacyReference | str | None = None


class Variable(_RuleElement):
    """Variable.

    TODO: What does ``default_element`` refer to?
    """

    attr_endpoint: ClassVar[str] = '/v2/variables'
    default_element: LegacyReference | str | None = None
    required_period_type: LegacyReference | str | None = None
