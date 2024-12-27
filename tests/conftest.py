"""Config for Pytest."""

# pylint: disable=protected-access

import os
from collections.abc import AsyncGenerator, Generator, Iterable
from inspect import isclass
from pathlib import Path
from typing import Any

import pytest
from aioresponses import aioresponses
from dotenv import load_dotenv
from pytest_asyncio import is_async_test

from sapimclient import LegacyTenant
from sapimclient.auth import Authenticator, BasicAuthenticator
from sapimclient.model import Endpoint, legacy
from sapimclient.model.legacy.base import LegacyResource
from sapimclient.model.legacy.pipeline import PipelineJob


def pytest_collection_modifyitems(items: Iterable[Any]) -> None:
    """Add the session scope marker to async tests."""
    pytest_asyncio_tests = (item for item in items if is_async_test(item))
    session_scope_marker = pytest.mark.asyncio(scope='session')
    for async_test in pytest_asyncio_tests:
        async_test.add_marker(session_scope_marker, append=False)


def legacy_endpoint_cls() -> Generator[type[Endpoint], None, None]:
    """List all endpoint classes in the legacy models."""
    for name in dir(legacy):
        obj = getattr(legacy, name)
        if isclass(obj) and issubclass(obj, Endpoint):
            yield obj


def legacy_pipeline_job_cls() -> Generator[type[legacy.PipelineJob], None, None]:
    """List all pipeline job classes in the legacy models."""
    for name in dir(legacy):
        obj = getattr(legacy, name)
        if isclass(obj) and issubclass(obj, PipelineJob) and obj is not PipelineJob:
            yield obj


def legacy_resource_cls() -> Generator[type[LegacyResource], None, None]:
    """List all resource classes in the legacy models."""
    for name in dir(legacy):
        obj = getattr(legacy, name)
        if isclass(obj) and issubclass(obj, LegacyResource):
            yield obj


@pytest.fixture(name='dir_deploy')
def fixture_deploy() -> Path:
    """Yield the path to the deploy directory."""
    return Path('tests/fixtures/deploy')


@pytest.fixture(name='live_tenant', scope='session')
async def fixture_live_tenant() -> AsyncGenerator[LegacyTenant, None]:
    """Yield a LegacyTenant instance."""
    load_dotenv('tests/.env')

    if not (tenant := os.environ.get('SAP_TENANT')):
        pytest.fail('SAP_TENANT must be set in the environment.')

    username: str | None = os.environ.get('SAP_USERNAME')
    password: str | None = os.environ.get('SAP_PASSWORD')
    if not (username and password):
        pytest.fail('SAP_USERNAME and SAP_PASSWORD must be set in the environment.')

    auth = BasicAuthenticator(username, password)
    async with LegacyTenant(tenant, auth) as tenant:
        yield tenant


@pytest.fixture(name='tenant', scope='session')
async def fixture_tenant() -> AsyncGenerator[LegacyTenant, None]:
    """Yield a LegacyTenant instance."""

    class DummyAuth(Authenticator):
        """Dummy Authenticator."""

        async def get_auth(self, tenant: str) -> dict[str, str]:
            """Return authentication context."""
            return {'Authorization': tenant}

    async with LegacyTenant('TEST', DummyAuth()) as tenant:
        yield tenant


@pytest.fixture(name='mocked')
def fixture_mocked_responses() -> Generator[aioresponses, None, None]:
    """Return aioresponses fixture."""
    with aioresponses() as mocker:
        yield mocker
