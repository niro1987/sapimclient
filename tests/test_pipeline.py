"""Tests for running pipelines."""

import logging
from collections.abc import AsyncGenerator
from typing import TypeVar

import pytest
from pydantic import ValidationError

from sapimclient import LegacyTenant, const, helpers
from sapimclient.model import legacy
from sapimclient.model.legacy.pipeline import STAGETABLES, _ImportJob, _PipelineRunJob

LOGGER: logging.Logger = logging.getLogger(__name__)
T = TypeVar('T', bound=_PipelineRunJob)


@pytest.mark.parametrize(
    'module',
    list(STAGETABLES.keys()),
)
def test_purge_stage_tables(module: str) -> None:
    """Test stage_tables property for Purge pipeline."""
    job = legacy.Purge(
        batch_name='spam',
        module=module,
    )

    assert job.stage_tables == STAGETABLES[module]


@pytest.mark.parametrize(
    'module',
    list(STAGETABLES.keys()),
)
def test_import_stage_tables(module: str) -> None:
    """Test stage_tables property for Purge pipeline."""

    class DummyJob(_ImportJob):
        """Dummy import job."""

        calendar_seq: str = 'spam'
        batch_name: str = 'eggs'
        stage_type_seq: str = 'bacon'

    job = DummyJob(module=module)
    assert job.stage_tables == STAGETABLES[module]


@pytest.mark.parametrize(
    'module',
    [e.value for e in const.StageTables],
)
def test_import_model_validator(module: str) -> None:
    """Test model validator for _ImportJob pipelines.

    run_mode can only be 'new' when importing TransactionalData
    """

    class DummyJob(_ImportJob):
        """Dummy import job."""

        calendar_seq: str = 'spam'
        batch_name: str = 'eggs'
        stage_type_seq: str = 'bacon'

    if module != const.StageTables.TransactionalData:
        with pytest.raises(ValidationError):
            DummyJob(
                module=module,
                run_mode=const.ImportRunMode.New,
            )

    job = DummyJob(
        module=module,
        run_mode=const.ImportRunMode.All,
    )
    assert job.run_mode == const.ImportRunMode.All


def test_pipeline_run_mode_validator() -> None:
    """Test PipelineRunJob validator run_mode."""

    class DummyJob(_PipelineRunJob):
        """Dummy pipeline run job."""

        calendar_seq: str = 'spam'
        period_seq: str = 'eggs'
        stage_type_seq: str = 'bacon'

    job = DummyJob(
        run_mode=const.PipelineRunMode.Full,
    )
    assert job.run_mode == const.PipelineRunMode.Full

    job = DummyJob(
        run_mode=const.PipelineRunMode.Positions,
        position_groups=['spam'],
    )
    assert job.run_mode == const.PipelineRunMode.Positions
    assert job.position_groups == ['spam']
    assert job.position_seqs is None

    job = DummyJob(
        run_mode=const.PipelineRunMode.Positions,
        position_seqs=['spam'],
    )
    assert job.run_mode == const.PipelineRunMode.Positions
    assert job.position_seqs == ['spam']
    assert job.position_groups is None

    # When run_mode is 'full' or 'incremental',
    # 'position_groups and position_seqs must be None'
    with pytest.raises(ValidationError) as err:
        DummyJob(
            run_mode=const.PipelineRunMode.Full,
            position_groups=['spam'],
        )
    assert 'position_groups' in str(err.value)

    with pytest.raises(ValidationError) as err:
        DummyJob(
            run_mode=const.PipelineRunMode.Full,
            position_seqs=['spam'],
        )
    assert 'position_seqs' in str(err.value)

    # When run_mode is 'positions',
    # either position_groups or position_seqs mut be provided
    with pytest.raises(ValidationError) as err:
        DummyJob(
            run_mode=const.PipelineRunMode.Positions,
        )
    assert 'position_groups' in str(err.value)
    assert 'position_seqs' in str(err.value)

    # Must not provide both position_groups and position_seqs
    with pytest.raises(ValidationError) as err:
        DummyJob(
            run_mode=const.PipelineRunMode.Positions,
            position_groups=['spam'],
            position_seqs=['eggs'],
        )
    assert 'position_groups' in str(err.value)
    assert 'position_seqs' in str(err.value)


@pytest.fixture(name='cleanup', scope='session')
async def fixture_delete_pipeline(
    live_tenant: LegacyTenant,
) -> AsyncGenerator[list[legacy.Pipeline], None]:
    """Fixture to delete the created pipeline."""
    pipelines: list[legacy.Pipeline] = []
    yield pipelines

    for pipeline in pipelines:
        reloaded = await live_tenant.read(pipeline)
        if reloaded.state == const.PipelineState.Done:
            LOGGER.info('Pipeline state done: %s', pipeline.pipeline_run_seq)
            continue
        try:
            await live_tenant.cancel_pipeline(pipeline)
            LOGGER.info('Pipeline cancelled: %s', pipeline.pipeline_run_seq)
        except Exception:  # pylint: disable=broad-except
            LOGGER.exception('Error deleting pipeline')


@pytest.fixture(name='calendar', scope='session')
async def fixture_calendar(live_tenant: LegacyTenant) -> legacy.Calendar:
    """Fixture to return first calendar instance."""
    if not (calendar := await live_tenant.read_first(legacy.Calendar)):
        pytest.skip('No calendar returned from tenant.')
    assert calendar.seq is not None, 'calendar.seq invalid.'

    LOGGER.debug('Calendar %s: %s', calendar.seq, calendar.name)
    return calendar


@pytest.fixture(name='period', scope='session')
async def fixture_period(
    live_tenant: LegacyTenant,
    calendar: legacy.Calendar,
) -> legacy.Period:
    """Fixture to return first calendar period instance."""
    if not (
        period := await live_tenant.read_first(
            legacy.Period,
            filters=helpers.And(
                helpers.Equals('calendar', str(calendar.seq)),
                helpers.Equals('periodType', str(calendar.minor_period_type)),
            ),
        ),
    ):
        pytest.skip('No period returned from tenant.')
    assert period.seq, 'period.seq invalid.'

    LOGGER.debug('Period %s: %s', period.seq, period.name)
    return period


@pytest.mark.skip('Runs on live tenant')
@pytest.mark.parametrize(
    'pipeline_job',
    [
        legacy.Classify,
        legacy.Allocate,
        legacy.Reward,
        legacy.Pay,
        legacy.Summarize,
        legacy.Compensate,
        legacy.CompensateAndPay,
        legacy.ResetFromClassify,
        legacy.ResetFromAllocate,
        legacy.ResetFromReward,
        legacy.ResetFromPay,
        legacy.Post,
        legacy.Finalize,
        legacy.UndoPost,
        legacy.UndoFinalize,
        legacy.CleanupDefferedResults,
        legacy.UpdateAnalytics,
    ],
)
async def test_pipelinerun(
    live_tenant: LegacyTenant,
    pipeline_job: type[T],
    cleanup: list[legacy.Pipeline],
    period: legacy.Period,
) -> None:
    """Test running a pipeline on a calendar period."""
    job: T = pipeline_job(  # type: ignore[call-arg]
        calendar_seq=str(period.calendar),
        period_seq=period.period_seq,
    )
    result: legacy.Pipeline = await live_tenant.run_pipeline(job)
    LOGGER.info(result)
    assert result.pipeline_run_seq is not None
    cleanup.append(result)
    assert result.command == job.command
    assert result.stage_type == job.stage_type_seq
    assert str(result.period) == period.seq


@pytest.mark.skip('Runs on live tenant')
async def test_xmlimport(
    live_tenant: LegacyTenant,
    cleanup: list[legacy.Pipeline],
) -> None:
    """Test running an XML import."""
    job = legacy.XMLImport(
        xml_file_name='test.xml',
        xml_file_content='<xml></xml>',
        update_existing_objects=True,
    )
    result: legacy.Pipeline = await live_tenant.run_pipeline(job)
    LOGGER.info(result)
    assert result.pipeline_run_seq is not None
    cleanup.append(result)
    assert result.command == job.command
    assert result.stage_type == job.stage_type_seq


@pytest.mark.skip('Runs on live tenant')
@pytest.mark.parametrize(
    'pipeline_job',
    [
        legacy.Validate,
        legacy.Transfer,
        legacy.ValidateAndTransfer,
        legacy.ValidateAndTransferIfAllValid,
        legacy.TransferIfAllValid,
    ],
)
async def test_import(
    live_tenant: LegacyTenant,
    pipeline_job: type[legacy.pipeline._ImportJob],
    cleanup: list[legacy.Pipeline],
    calendar: legacy.Calendar,
) -> None:
    """Test running an import job."""
    batch_name: str = 'test.txt'
    job: legacy.pipeline._ImportJob = pipeline_job(  # type: ignore[call-arg]
        calendar_seq=calendar.seq,
        batch_name=batch_name,
        module=const.StageTables.TransactionalData,
    )
    result: legacy.Pipeline = await live_tenant.run_pipeline(job)
    LOGGER.info(result)
    assert result.pipeline_run_seq is not None
    cleanup.append(result)
    assert result.stage_type == job.stage_type_seq
    assert result.command == job.command
    assert result.batch_name == job.batch_name


@pytest.mark.skip('Runs on live tenant')
async def test_purge(
    live_tenant: LegacyTenant,
    cleanup: list[legacy.Pipeline],
) -> None:
    """Test running a Purge pipeline."""
    batch_name: str = 'test.txt'
    job = legacy.Purge(
        batch_name=batch_name,
        module=const.StageTables.TransactionalData,
    )
    result: legacy.Pipeline = await live_tenant.run_pipeline(job)
    LOGGER.info(result)
    assert result.pipeline_run_seq is not None
    cleanup.append(result)
    assert result.stage_type == job.stage_type_seq
    assert result.command == job.command
    assert result.batch_name == job.batch_name


@pytest.mark.skip('Runs on live tenant')
async def test_resetfromvalidate(
    live_tenant: LegacyTenant,
    cleanup: list[legacy.Pipeline],
    period: legacy.Period,
) -> None:
    """Test running a ResetFromValidate pipeline."""
    batch_name: str = 'test.txt'
    job: legacy.ResetFromValidate = legacy.ResetFromValidate(
        calendar_seq=str(period.calendar),
        period_seq=period.seq,
        batch_name=batch_name,
    )
    result: legacy.Pipeline = await live_tenant.run_pipeline(job)
    LOGGER.info(result)
    assert result.pipeline_run_seq is not None
    cleanup.append(result)
    assert result.stage_type == const.ImportStages.ResetFromValidate
    assert result.command == 'Import'
    assert result.batch_name == job.batch_name


@pytest.mark.skip('Runs on live tenant')
async def test_resetfromvalidate_no_batch(
    live_tenant: LegacyTenant,
    cleanup: list[legacy.Pipeline],
    period: legacy.Period,
) -> None:
    """Test running a ResetFromValidate pipeline without batch_name."""
    job: legacy.ResetFromValidate = legacy.ResetFromValidate(
        calendar_seq=str(period.calendar),
        period_seq=period.seq,
    )
    result: legacy.Pipeline = await live_tenant.run_pipeline(job)
    LOGGER.info(result)
    assert result.pipeline_run_seq is not None
    cleanup.append(result)
    assert result.stage_type == const.ImportStages.ResetFromValidate
    assert result.command == 'Import'
    assert result.batch_name is None
