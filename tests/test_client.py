"""Test for SAP Incentive Management Client."""

import logging
from datetime import date, datetime
from typing import ClassVar

import pytest
from aiohttp import ClientError
from aioresponses import aioresponses

from sapimclient import Tenant, exceptions
from sapimclient.const import HTTPMethod
from sapimclient.model.base import Resource

LOGGER: logging.Logger = logging.getLogger(__name__)


async def test_tenant_request(
    tenant: Tenant,
    mocked: aioresponses,
) -> None:
    """Test tenant request happy flow."""
    mocked.get(
        url=f'{tenant.host}/spamm',
        status=200,
        headers={'Content-Type': 'application/json'},
        payload={'eggs': 'bacon'},
    )

    response = await tenant._request(method=HTTPMethod.GET, uri='spamm')
    assert response == {'eggs': 'bacon'}


async def test_tenant_request_error_timeout(
    tenant: Tenant,
    mocked: aioresponses,
) -> None:
    """Test tenant request exceed timeout."""
    mocked.get(
        url=f'{tenant.host}/spamm',
        exception=TimeoutError(),
    )
    with pytest.raises(exceptions.SAPConnectionError):
        await tenant._request(method=HTTPMethod.GET, uri='spamm')

    mocked.get(
        url=f'{tenant.host}/eggs',
        timeout=True,
    )
    with pytest.raises(exceptions.SAPConnectionError):
        await tenant._request(method=HTTPMethod.GET, uri='eggs')


async def test_tenant_request_error_no_connection(
    tenant: Tenant,
    mocked: aioresponses,
) -> None:
    """Test tenant request ClientError."""
    mocked.get(
        url=f'{tenant.host}/spamm',
        exception=ClientError(),
    )
    with pytest.raises(exceptions.SAPConnectionError):
        await tenant._request(method=HTTPMethod.GET, uri='spamm')


async def test_tenant_request_error_not_modified(
    tenant: Tenant,
    mocked: aioresponses,
) -> None:
    """Test tenant request happy flow."""
    mocked.post(
        url=f'{tenant.host}/spamm',
        status=304,
    )

    with pytest.raises(exceptions.SAPNotModifiedError):
        await tenant._request(
            method=HTTPMethod.POST,
            uri='spamm',
            json=[{'eggs': 'bacon'}],
        )


async def test_tenant_request_error_maintenance(
    tenant: Tenant,
    mocked: aioresponses,
) -> None:
    """Test tenant request happy flow."""
    mocked.get(
        url=f'{tenant.host}/spamm',
        status=200,
        headers={'Content-Type': 'text/html'},
        payload='<html><body>Server Maintenance</body></html>',
    )

    with pytest.raises(exceptions.SAPResponseError):
        await tenant._request(method=HTTPMethod.GET, uri='spamm')


async def test_tenant_request_error_status(
    tenant: Tenant,
    mocked: aioresponses,
) -> None:
    """Test tenant request status code."""
    mocked.get(
        url=f'{tenant.host}/200',
        status=200,
        headers={'Content-Type': 'application/json'},
        payload={'eggs': 'bacon'},
    )
    response = await tenant._request(method=HTTPMethod.GET, uri='200')
    assert response.get('eggs') == 'bacon'

    mocked.get(
        url=f'{tenant.host}/300',
        status=300,
        headers={'Content-Type': 'application/json'},
        payload={'eggs': 'bacon'},
    )
    with pytest.raises(exceptions.SAPBadRequestError):
        await tenant._request(method=HTTPMethod.GET, uri='300')

    mocked.post(
        url=f'{tenant.host}/200',
        status=200,
        headers={'Content-Type': 'application/json'},
        payload={'eggs': 'bacon'},
    )
    response = await tenant._request(
        method=HTTPMethod.POST,
        uri='200',
        json=[{'eggs': 'bacon'}],
    )
    assert response.get('eggs') == 'bacon'

    mocked.post(
        url=f'{tenant.host}/201',
        status=201,
        headers={'Content-Type': 'application/json'},
        payload={'eggs': 'bacon'},
    )
    response = await tenant._request(
        method=HTTPMethod.POST,
        uri='201',
        json=[{'eggs': 'bacon'}],
    )
    assert response.get('eggs') == 'bacon'

    mocked.post(
        url=f'{tenant.host}/300',
        status=300,
        headers={'Content-Type': 'application/json'},
        payload={'eggs': 'bacon'},
    )
    with pytest.raises(exceptions.SAPBadRequestError):
        await tenant._request(
            method=HTTPMethod.POST,
            uri='300',
            json=[{'eggs': 'bacon'}],
        )

    mocked.put(
        url=f'{tenant.host}/200',
        status=200,
        headers={'Content-Type': 'application/json'},
        payload={'eggs': 'bacon'},
    )
    response = await tenant._request(method=HTTPMethod.PUT, uri='200')
    assert response.get('eggs') == 'bacon'

    mocked.put(
        url=f'{tenant.host}/300',
        status=300,
        headers={'Content-Type': 'application/json'},
        payload={'eggs': 'bacon'},
    )
    with pytest.raises(exceptions.SAPBadRequestError):
        await tenant._request(method=HTTPMethod.PUT, uri='300')

    mocked.delete(
        url=f'{tenant.host}/200',
        status=200,
        headers={'Content-Type': 'application/json'},
        payload={'eggs': 'bacon'},
    )
    response = await tenant._request(method=HTTPMethod.DELETE, uri='200')
    assert response.get('eggs') == 'bacon'

    mocked.delete(
        url=f'{tenant.host}/300',
        status=300,
        headers={'Content-Type': 'application/json'},
        payload={'eggs': 'bacon'},
    )
    with pytest.raises(exceptions.SAPBadRequestError):
        await tenant._request(method=HTTPMethod.DELETE, uri='300')


async def test_tenant_create(
    tenant: Tenant,
    mocked: aioresponses,
) -> None:
    """Test tenant create happy flow."""

    class MockResource(Resource):
        """MockResource resource."""

        attr_endpoint: ClassVar[str] = 'api/v2/eggs'
        attr_seq: ClassVar[str] = 'egg_seq'
        egg_seq: str | None = None
        name: str

    resource = MockResource(name='spamm')
    mocked.post(
        url=f'{tenant.host}/api/v2/eggs',
        status=201,
        headers={'Content-Type': 'application/json'},
        payload={'eggs': [{'eggSeq': '12345', 'name': 'eggs'}]},
    )
    response = await tenant.create(resource)
    assert response.seq == '12345'
    assert response.name == 'eggs'


async def test_tenant_create_error_response(
    tenant: Tenant,
    mocked: aioresponses,
) -> None:
    """Test tenant create error."""

    class MockResource(Resource):
        """MockResource resource."""

        attr_endpoint: ClassVar[str] = 'api/v2/eggs'
        attr_seq: ClassVar[str] = 'egg_seq'
        egg_seq: str | None = None
        name: str

    resource = MockResource(name='Spamm')
    mocked.post(
        url=f'{tenant.host}/api/v2/eggs',
        status=400,
        headers={'Content-Type': 'application/json'},
        payload={
            'data': {
                'timeStamp': '2024-01-01T01:02:03.04+05:06',
                'message': 'Invalid Resource.',
            },
        },
    )

    with pytest.raises(exceptions.SAPResponseError) as err:
        await tenant.create(resource)
    assert 'Invalid Resource' in str(err.value)


async def test_tenant_create_error_already_exists(
    tenant: Tenant,
    mocked: aioresponses,
) -> None:
    """Test tenant create error already exists."""

    class MockResource(Resource):
        """MockResource resource."""

        attr_endpoint: ClassVar[str] = 'api/v2/eggs'
        attr_seq: ClassVar[str] = 'egg_seq'
        egg_seq: str | None = None
        name: str
        effective_start_date: datetime
        effective_end_date: datetime

    resource = MockResource(
        name='Spamm',
        effective_start_date=date(2025, 1, 1),
        effective_end_date=date(2200, 1, 1),
    )
    mocked.post(
        url=f'{tenant.host}/api/v2/eggs',
        status=400,
        headers={'Content-Type': 'application/json'},
        payload={
            'eggs': [
                {
                    '_ERROR_': (
                        'TCMP_35004:E: Another object already has the '
                        'key (Name=Spamm) within the period from '
                        'Jan 1, 2025 to Jan 1, 2200.'
                    ),
                },
            ],
        },
    )

    with pytest.raises(exceptions.SAPAlreadyExistsError) as err:
        await tenant.create(resource)
    assert 'TCMP_35004' in str(err.value)


async def test_tenant_create_error_missing_field(
    tenant: Tenant,
    mocked: aioresponses,
) -> None:
    """Test tenant create error missing field."""

    class MockResource(Resource):
        """MockResource resource."""

        attr_endpoint: ClassVar[str] = 'api/v2/eggs'
        attr_seq: ClassVar[str] = 'egg_seq'
        egg_seq: str | None = None
        # name: str # missing field
        effective_start_date: datetime
        effective_end_date: datetime

    resource = MockResource(
        effective_start_date=date(2025, 1, 1),
        effective_end_date=date(2200, 1, 1),
    )
    mocked.post(
        url=f'{tenant.host}/api/v2/eggs',
        status=400,
        headers={'Content-Type': 'application/json'},
        payload={'eggs': [{'name': 'TCMP_1002:E: A value is required'}]},
    )

    with pytest.raises(exceptions.SAPMissingFieldError) as err:
        await tenant.create(resource)
    assert 'TCMP_1002' in str(err.value)


async def test_tenant_create_error_unexpected(
    tenant: Tenant,
    mocked: aioresponses,
) -> None:
    """Test tenant create error unexpected."""

    class MockResource(Resource):
        """MockResource resource."""

        attr_endpoint: ClassVar[str] = 'api/v2/eggs'
        attr_seq: ClassVar[str] = 'egg_seq'
        egg_seq: str | None = None
        bacon: bool

    resource = MockResource(
        bacon=False,
    )
    mocked.post(
        url=f'{tenant.host}/api/v2/eggs',
        status=400,
        headers={'Content-Type': 'application/json'},
        payload={'eggs': [{'bacon': 'eggs need bacon'}]},
    )

    with pytest.raises(exceptions.SAPResponseError):
        await tenant.create(resource)


async def test_tenant_create_error_payload(
    tenant: Tenant,
    mocked: aioresponses,
) -> None:
    """Test tenant create error payload."""

    class MockResource(Resource):
        """MockResource resource."""

        attr_endpoint: ClassVar[str] = 'api/v2/eggs'
        attr_seq: ClassVar[str] = 'egg_seq'
        egg_seq: str | None = None
        name: str

    resource = MockResource(
        name='Spamm',
    )
    mocked.post(
        url=f'{tenant.host}/api/v2/eggs',
        status=200,
        headers={'Content-Type': 'application/json'},
        payload={'bacon': 'out of bacon'},
    )

    with pytest.raises(exceptions.SAPResponseError) as err:
        await tenant.create(resource)
    assert 'Unexpected payload' in str(err.value)


async def test_tenant_create_error_validation(
    tenant: Tenant,
    mocked: aioresponses,
) -> None:
    """Test tenant create error model validation."""

    class MockResource(Resource):
        """MockResource resource."""

        attr_endpoint: ClassVar[str] = 'api/v2/eggs'
        attr_seq: ClassVar[str] = 'egg_seq'
        egg_seq: str | None = None
        name: str

    resource = MockResource(name='spamm')
    mocked.post(
        url=f'{tenant.host}/api/v2/eggs',
        status=201,
        headers={'Content-Type': 'application/json'},
        payload={'eggs': [{'eggSeq': '12345', 'needs': 'bacon'}]},
    )
    with pytest.raises(exceptions.SAPResponseError) as err:
        await tenant.create(resource)
    assert 'name' in str(err.value)
