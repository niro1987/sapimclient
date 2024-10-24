"""Tests for the deploy module."""

import logging
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any

import pytest
from pytest_mock import MockerFixture

from sapimclient import Tenant, const, deploy, model
from sapimclient.exceptions import SAPAlreadyExistsError
from sapimclient.model.data_type import _DataType

LOGGER = logging.getLogger(__name__)


def mockeffect_datatypes_from_file(
    client: Tenant,  # noqa: ARG001
    file: Path,  # noqa: ARG001
    resource_cls: type[_DataType],
) -> list[_DataType]:
    """Mocked side effect of deploy_datatypes_from_file."""
    return [
        resource_cls(data_type_seq='123', id='Spam'),
        resource_cls(data_type_seq='456', id='Eggs', description='Bacon'),
    ]


def mockeffect_pipeline(*args: Any, **kwargs: Any) -> model.Pipeline:  # noqa: ARG001
    """Mocked side effect of deploy_xml."""
    return model.Pipeline(
        pipeline_run_seq='123',
        command='XMLImport',
        stage_type=const.XMLImportStages.XMLImport,
        date_submitted=datetime.now(),
        state=const.PipelineState.Done,
        status=const.PipelineStatus.Successful,
        user_id='spam',
    )


@pytest.mark.parametrize(
    ('src_file', 'resource_cls'),
    [
        ('Credit Type.txt', model.CreditType),
        ('Earning Code.txt', model.EarningCode),
        ('Earning Group.txt', model.EarningGroup),
        ('Event Type.txt', model.EventType),
        ('Fixed Value Type.txt', model.FixedValueType),
        ('Reason Code.txt', model.Reason),
        ('plan.xml', model.XMLImport),
    ],
)
def test_file_class(
    dir_deploy: Path,
    tmp_path: Path,
    src_file: str,
    resource_cls: type[_DataType | model.XMLImport],
) -> None:
    """Test file class function."""
    # Setup temporary directory
    tmp_file = tmp_path / src_file
    shutil.copy(dir_deploy / src_file, tmp_file)

    # Test resource class
    assert deploy._file_cls(tmp_file) is resource_cls


def test_file_class_unknown(
    tmp_path: Path,
) -> None:
    """Test file class function error."""
    # Setup temporary directory
    tmp_file = tmp_path / 'unknown.txt'
    tmp_file.write_text('unknown', encoding='utf-8')

    # Test unknown file
    with pytest.raises(ValueError) as err:
        deploy._file_cls(tmp_file)
    assert 'unknown.txt' in str(err.value)


async def test_deploy_from_path(
    dir_deploy: Path,
    tmp_path: Path,
    mocker: MockerFixture,
    tenant: Tenant,
) -> None:
    """Test the deploy_from_path function."""
    # Setup temporary directory
    txt_files = 0
    xml_files = 0
    for file in dir_deploy.iterdir():
        if file.suffix == '.txt':
            txt_files += 1
        if file.suffix == '.xml':
            xml_files += 1
        shutil.copy(file, tmp_path / file.name)

    # # Setup mocker
    mock_file = mocker.patch(
        target='sapimclient.deploy.deploy_datatypes_from_file',
        side_effect=mockeffect_datatypes_from_file,
    )
    mock_xml = mocker.patch(
        target='sapimclient.deploy.deploy_xml',
        side_effect=mockeffect_pipeline,
    )

    # Test all files processed
    results = await deploy.deploy_from_path(
        client=tenant,
        path=tmp_path,
    )

    assert mock_file.call_count == txt_files
    assert mock_xml.call_count == xml_files

    for file in tmp_path.iterdir():
        assert file in results


async def test_deploy_from_path_pipeline_failure(
    dir_deploy: Path,
    tmp_path: Path,
    mocker: MockerFixture,
    tenant: Tenant,
) -> None:
    """Test the deploy_from_path function with pipeline failure."""
    # Setup temporary directory
    src_file = dir_deploy / 'plan.xml'
    tmp_file = tmp_path / 'plan.xml'
    shutil.copy(src_file, tmp_file)

    # Setup mocker
    mock = mocker.patch('sapimclient.deploy.deploy_xml')
    mock.return_value.status = const.PipelineStatus.Failed

    results = await deploy.deploy_from_path(tenant, tmp_path)
    assert results == {}
    assert mock.call_count == 1


@pytest.mark.parametrize(
    ('src_file', 'resource_cls'),
    [
        ('Credit Type.txt', model.CreditType),
        ('Earning Code.txt', model.EarningCode),
        ('Earning Group.txt', model.EarningGroup),
        ('Event Type.txt', model.EventType),
        ('Fixed Value Type.txt', model.FixedValueType),
        ('Reason Code.txt', model.Reason),
    ],
)
async def test_deploy_datatypes_from_file(  # noqa: PLR0913
    dir_deploy: Path,
    tmp_path: Path,
    mocker: MockerFixture,
    tenant: Tenant,
    src_file: str,
    resource_cls: type[_DataType],
) -> None:
    """Test the deploy_datatypes_from_file function."""
    # Setup temporary directory
    tmp_file = tmp_path / src_file
    shutil.copy(dir_deploy / src_file, tmp_file)

    # Setup mocker
    def mockeffect(
        client: Tenant,  # noqa: ARG001
        resource: _DataType,
    ) -> _DataType:
        """Mockeffect of deploy_datatype."""
        return resource

    mock = mocker.patch(
        target='sapimclient.deploy.deploy_datatype',
        side_effect=mockeffect,
    )

    # Test resources processed
    results = await deploy.deploy_datatypes_from_file(tenant, tmp_file, resource_cls)
    assert len(results) == 2
    assert mock.call_count == 2
    assert all(isinstance(result, resource_cls) for result in results)


@pytest.mark.parametrize(
    'resource_cls',
    [
        model.CreditType,
        model.EarningCode,
        model.EarningGroup,
        model.EventType,
        model.FixedValueType,
        model.Reason,
    ],
)
async def test_deploy_datatype_created(
    tenant: Tenant,
    mocker: MockerFixture,
    resource_cls: type[_DataType],
) -> None:
    """Test the deploy_datatype function."""

    # Setup mocker
    def mockeffect(
        resource: _DataType,
    ) -> _DataType:
        """Mockeffect of deploy_datatype."""
        return resource

    mock = mocker.patch(
        target='sapimclient.client.Tenant.create',
        side_effect=mockeffect,
    )

    resource = resource_cls(id='spam', description='eggs')
    result = await deploy.deploy_datatype(tenant, resource)
    assert result == resource
    mock.assert_called_once_with(resource)


@pytest.mark.parametrize(
    'resource_cls',
    [
        model.CreditType,
        model.EarningCode,
        model.EarningGroup,
        model.EventType,
        model.FixedValueType,
        model.Reason,
    ],
)
async def test_deploy_datatype_updated(
    tenant: Tenant,
    mocker: MockerFixture,
    resource_cls: type[_DataType],
) -> None:
    """Test the deploy_datatype function."""

    # Setup mocker
    def mockeffect(
        resource: _DataType,
    ) -> _DataType:
        """Mockeffect of deploy_datatype."""
        return resource

    mock_create = mocker.patch(
        target='sapimclient.client.Tenant.create',
        side_effect=SAPAlreadyExistsError('bacon'),
    )
    mock_update = mocker.patch(
        target='sapimclient.client.Tenant.update',
        side_effect=mockeffect,
    )

    resource = resource_cls(id='spam', description='eggs')
    result = await deploy.deploy_datatype(tenant, resource)
    assert result == resource
    mock_create.assert_called_once_with(resource)
    mock_update.assert_called_once_with(resource)


async def test_deploy_xml(
    dir_deploy: Path,
    tmp_path: Path,
    tenant: Tenant,
    mocker: MockerFixture,
) -> None:
    """Test the deploy_xml function."""
    # Setup temporary directory
    src_file = dir_deploy / 'plan.xml'
    tmp_file = tmp_path / 'plan.xml'
    shutil.copy(src_file, tmp_file)

    # Setup mocker
    mock = mocker.patch(
        target='sapimclient.client.Tenant.run_pipeline',
        return_value=mockeffect_pipeline(),
    )

    result = await deploy.deploy_xml(tenant, tmp_file)
    assert isinstance(result, model.Pipeline)
    assert result.state == const.PipelineState.Done
    assert result.status == const.PipelineStatus.Successful
    assert mock.call_count == 1


async def test_deploy_xml_failure(
    dir_deploy: Path,
    tmp_path: Path,
    tenant: Tenant,
    mocker: MockerFixture,
) -> None:
    """Test the deploy_xml function."""
    # Setup temporary directory
    src_file = dir_deploy / 'plan.xml'
    tmp_file = tmp_path / 'plan.xml'
    shutil.copy(src_file, tmp_file)

    # Setup mocker
    pipeline: model.Pipeline = mockeffect_pipeline()
    pipeline.status = const.PipelineStatus.Failed
    pipeline.num_errors = 1
    mock = mocker.patch(
        target='sapimclient.client.Tenant.run_pipeline',
        return_value=pipeline,
    )

    result = await deploy.deploy_xml(tenant, tmp_file)
    assert isinstance(result, model.Pipeline)
    assert result.state == const.PipelineState.Done
    assert result.status == const.PipelineStatus.Failed
    assert mock.call_count == 1


async def test_deploy_xml_sleep(
    dir_deploy: Path,
    tmp_path: Path,
    tenant: Tenant,
    mocker: MockerFixture,
) -> None:
    """Test the deploy_xml function."""
    # Setup temporary directory
    src_file = dir_deploy / 'plan.xml'
    tmp_file = tmp_path / 'plan.xml'
    shutil.copy(src_file, tmp_file)

    # Setup mocker
    pipeline_running = mockeffect_pipeline()
    pipeline_running.state = const.PipelineState.Running

    mock_sleep = mocker.patch('asyncio.sleep', return_value=None)
    mock_running = mocker.patch(
        target='sapimclient.client.Tenant.run_pipeline',
        return_value=pipeline_running,
    )
    mock_done = mocker.patch(
        target='sapimclient.client.Tenant.read',
        return_value=mockeffect_pipeline(),
    )

    result = await deploy.deploy_xml(tenant, tmp_file)
    assert isinstance(result, model.Pipeline)
    assert result.state == const.PipelineState.Done
    assert result.status == const.PipelineStatus.Successful
    assert mock_running.call_count == 1
    assert mock_sleep.call_count == 1
    assert mock_done.call_count == 1
