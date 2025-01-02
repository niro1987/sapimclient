"""Pipeline."""

from datetime import datetime
from typing import ClassVar, Literal

from pydantic import Field, field_validator

from sapimclient import const
from sapimclient.model.base import Assignment

from ._base import LegacyReference, LegacyResource


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
