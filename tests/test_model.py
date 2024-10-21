"""Test for SAP Incentive Management Models."""
# pylint: disable=protected-access

import logging
from datetime import date
from typing import Any

import pytest
from pydantic import BaseModel
from pydantic.fields import FieldInfo

from sapimclient.model import Endpoint, Pipeline, Reference, Resource
from sapimclient.model.pipeline import _PipelineJob

from tests.conftest import list_endpoint_cls, list_pipeline_job_cls, list_resource_cls

LOGGER: logging.Logger = logging.getLogger(__name__)


@pytest.mark.parametrize(
    'endpoint_cls',
    list_endpoint_cls(),
)
def test_endpoint_basics(
    endpoint_cls: type[Endpoint],
) -> None:
    """Test endpoints."""
    assert issubclass(
        endpoint_cls,
        BaseModel,
    ), 'endpoint is not a pydantic model'
    assert issubclass(
        endpoint_cls,
        BaseModel,
    ), "endpoint is not a subclass of '_BaseModel'"
    assert issubclass(
        endpoint_cls,
        Endpoint,
    ), "endpoint is not a subclass of '_Endpoint'"

    # endpoint
    assert hasattr(
        endpoint_cls,
        'attr_endpoint',
    ), "resource does not have attribute 'attr_endpoint'"
    if not endpoint_cls.attr_endpoint.startswith('api/v2/'):
        LOGGER.warning('Endpoint possibly incorrect: %s', endpoint_cls.attr_endpoint)


@pytest.mark.parametrize(
    'resource_cls',
    list_resource_cls(),
)
def test_resource_basics(
    resource_cls: type[Resource],
) -> None:
    """Test resources."""
    # enpoint subclass
    assert issubclass(
        resource_cls,
        Endpoint,
    ), "resource is not a subclass of '_Endpoint'"
    assert issubclass(
        resource_cls,
        Resource,
    ), "resource is not a subclass of '_Resource'"

    # attr_seq
    assert hasattr(
        resource_cls,
        'attr_seq',
    ), "resource does not have attribute 'attr_seq'"
    assert resource_cls.attr_seq.endswith('_seq'), "_attr_seq should end with '_seq'"
    assert resource_cls.attr_seq in resource_cls.model_fields
    seq_field: FieldInfo = resource_cls.model_fields[resource_cls.attr_seq]
    assert seq_field.annotation in (
        int | None,
        str | None,
    ), 'Invalid seq field type'

    # expands class method
    assert hasattr(
        resource_cls,
        'expands',
    ), "resource does not have class method 'expands'"

    expands = resource_cls.expands()
    assert isinstance(expands, dict), "'expands' should return a dict"
    assert all(
        isinstance(field, str) for field in expands
    ), "Invalid field type in 'expands' dict"
    assert all(
        isinstance(item, FieldInfo) for item in expands.values()
    ), "Invalid value type in 'expands' dict"


@pytest.mark.parametrize(
    'pipeline_job',
    list_pipeline_job_cls(),
)
def test_pipeline_job_basics(
    pipeline_job: type[_PipelineJob],
) -> None:
    """Test pipeline jobs."""
    # enpoint subclass
    assert issubclass(
        pipeline_job,
        Endpoint,
    ), "pipeline job is not a subclass of '_Endpoint'"
    assert issubclass(
        pipeline_job,
        _PipelineJob,
    ), "pipeline job is not a subclass of '_PipelineJob'"

    # command
    assert (
        'command' in pipeline_job.model_fields
    ), "pipeline job does not have attribute 'command'"
    command: FieldInfo = pipeline_job.model_fields['command']
    assert command.default in ('PipelineRun', 'Import', 'XMLImport'), 'Invalid command'


# def test_resource_model() -> None:
#     """Test resource models."""

#     class DummyResource(Resource):
#         """Dummy resource model."""

#         attr_seq: ClassVar[str] = 'dummy_seq'
#         dummy_seq: str | None = None
#         name: str
#         dummy_int: int

#     dummy_data: dict[str, Any] = {
#         'dummySeq': 'spam',
#         'name': 'eggs',
#         'dummyInt': 42,
#         'extraField': {'spam': 'eggs'},
#     }

#     dummy_resource: DummyResource = DummyResource(**dummy_data)
#     assert dummy_resource.dummy_seq == 'spam'
#     assert dummy_resource.name == 'eggs'
#     assert dummy_resource.dummy_int == 42

#     dump: dict[str, Any] = dummy_resource.model_dump(by_alias=True, exclude_none=True)
#     assert dump == dummy_data

#     extra: dict[str, Any] | None = dummy_resource.model_extra
#     assert extra is not None
#     # pylint: disable=unsupported-membership-test
#     assert 'dummySeq' not in extra
#     assert 'name' not in extra
#     assert 'dummyInt' not in extra
#     assert 'extraField' in extra
#     # pylint: disable=unsubscriptable-object
#     assert extra['extraField'] == {'spam': 'eggs'}


@pytest.mark.parametrize(
    'resource_cls',
    list_resource_cls(),
)
def test_resource_reference(
    resource_cls: type[Resource],
) -> None:
    """Test resource reference."""
    data: dict[str, Any] = {
        'key': 'spam',
        'displayName': 'eggs',
        'objectType': resource_cls.__name__,
        'logicalKeys': {'name': 'eggs'},
    }
    reference: Reference = Reference(**data)
    assert reference.key == 'spam'
    assert reference.display_name == 'eggs'
    assert reference.object_type is resource_cls


def test_pipeline_resource() -> None:
    """Test Pipeline Resource field validator."""
    pipeline = Pipeline(
        # Required fields
        command=None,
        stage_type=None,
        date_submitted=date(2024, 1, 1),
        state='Running',
        user_id='spam',
        # Test run_progress is converted to float
        run_progress='100%',
    )
    assert isinstance(pipeline.run_progress, float)
