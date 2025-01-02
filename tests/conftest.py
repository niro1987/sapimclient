"""Config for Pytest."""

# pylint: disable=protected-access

from collections.abc import AsyncGenerator, Generator, Iterable
from typing import Any

import pytest
from aioresponses import aioresponses
from pytest_asyncio import is_async_test

from sapimclient import GCPTenant, LegacyTenant
from sapimclient.auth import Authenticator, Token


class DummyAuth(Authenticator):
    """Dummy Authenticator."""

    async def get_auth(self, tenant: str) -> dict[str, str]:
        """Return Token Header."""
        self._token = Token('spam', tenant, 60)
        return self._token.as_header


def pytest_collection_modifyitems(items: Iterable[Any]) -> None:
    """Add the session scope marker to async tests."""
    pytest_asyncio_tests = (item for item in items if is_async_test(item))
    session_scope_marker = pytest.mark.asyncio(scope='session')
    for async_test in pytest_asyncio_tests:
        async_test.add_marker(session_scope_marker, append=False)


@pytest.fixture(name='legacy_tenant', scope='session')
async def fixture_legacy_tenant() -> AsyncGenerator[LegacyTenant, None]:
    """Yield a LegacyTenant instance."""
    async with LegacyTenant('TEST', DummyAuth()) as tenant:
        yield tenant


@pytest.fixture(name='gcp_tenant', scope='session')
async def fixture_gcp_tenant() -> AsyncGenerator[LegacyTenant, None]:
    """Yield a LegacyTenant instance."""
    async with GCPTenant('TEST', DummyAuth()) as tenant:
        yield tenant


@pytest.fixture(name='mocked')
def fixture_mocked_responses() -> Generator[aioresponses, None, None]:
    """Return aioresponses fixture."""
    with aioresponses() as mocker:
        yield mocker
