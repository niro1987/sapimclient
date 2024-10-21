"""Test for SAP Incentive Management Client."""

import logging
import re
from datetime import date, datetime
from typing import ClassVar

import pytest
from aiohttp import ClientError
from aioresponses import aioresponses

from sapimclient import Tenant, exceptions, model
from sapimclient.const import HTTPMethod

LOGGER: logging.Logger = logging.getLogger(__name__)


class MockResource(model.Resource):
    """MockResource resource."""

    attr_endpoint: ClassVar[str] = 'api/v2/eggs'
    attr_seq: ClassVar[str] = 'egg_seq'
    egg_seq: str | None = None
    name: str
    ref: str | model.Reference | None = None


mock_url = re.compile(r'^.*api/v2/eggs.*$')


async def test_tenant_request(
    tenant: Tenant,
    mocked: aioresponses,
) -> None:
    """Test tenant request happy flow."""
    mocked.get(
        url=f'{tenant.host}/spamm',
        status=200,
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
        payload={'eggs': 'bacon'},
    )
    response = await tenant._request(method=HTTPMethod.GET, uri='200')
    assert response.get('eggs') == 'bacon'

    mocked.get(
        url=f'{tenant.host}/300',
        status=300,
        payload={'eggs': 'bacon'},
    )
    with pytest.raises(exceptions.SAPBadRequestError):
        await tenant._request(method=HTTPMethod.GET, uri='300')

    mocked.post(
        url=f'{tenant.host}/200',
        status=200,
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
        payload={'eggs': 'bacon'},
    )
    response = await tenant._request(method=HTTPMethod.PUT, uri='200')
    assert response.get('eggs') == 'bacon'

    mocked.put(
        url=f'{tenant.host}/300',
        status=300,
        payload={'eggs': 'bacon'},
    )
    with pytest.raises(exceptions.SAPBadRequestError):
        await tenant._request(method=HTTPMethod.PUT, uri='300')

    mocked.delete(
        url=f'{tenant.host}/200',
        status=200,
        payload={'eggs': 'bacon'},
    )
    response = await tenant._request(method=HTTPMethod.DELETE, uri='200')
    assert response.get('eggs') == 'bacon'

    mocked.delete(
        url=f'{tenant.host}/300',
        status=300,
        payload={'eggs': 'bacon'},
    )
    with pytest.raises(exceptions.SAPBadRequestError):
        await tenant._request(method=HTTPMethod.DELETE, uri='300')


async def test_tenant_create(
    tenant: Tenant,
    mocked: aioresponses,
) -> None:
    """Test tenant create happy flow."""
    resource = MockResource(name='spamm')
    mocked.post(
        url=mock_url,
        status=201,
        payload={'eggs': [{'eggSeq': '12345', 'name': 'eggs'}]},
    )
    response = await tenant.create(resource)
    assert response.seq == '12345'
    assert response.name == 'eggs'


async def test_tenant_create_error(
    tenant: Tenant,
    mocked: aioresponses,
) -> None:
    """Test tenant create error invalid payload status.

    Response status indicates an error (400).
    Error data does not mention resource.
    """
    resource = MockResource(name='Spamm')
    mocked.post(
        url=mock_url,
        status=400,
        payload={
            'timeStamp': '2024-01-01T01:02:03.04+05:06',
            'message': 'Invalid Resource.',
        },
    )

    with pytest.raises(exceptions.SAPResponseError) as err:
        await tenant.create(resource)
    assert 'Invalid Resource' in str(err.value)


async def test_tenant_create_error_already_exists(
    tenant: Tenant,
    mocked: aioresponses,
) -> None:
    """Test tenant create error already exists.

    Response status indicates an error (400).
    Error data indicates resource already exists.
    """

    class MockResource(model.Resource):
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
        url=mock_url,
        status=400,
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
    """Test tenant create error missing field.

    Response status indicates an error (400).
    Error data indicates resource is missing a required field.
    """

    class MockResource(model.Resource):
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
        url=mock_url,
        status=400,
        payload={'eggs': [{'name': 'TCMP_1002:E: A value is required'}]},
    )

    with pytest.raises(exceptions.SAPMissingFieldError) as err:
        await tenant.create(resource)
    assert 'TCMP_1002' in str(err.value)


async def test_tenant_create_error_unexpected(
    tenant: Tenant,
    mocked: aioresponses,
) -> None:
    """Test tenant create error unexpected.

    Response status indicates an error (400).
    Error data does not mention any known error message.
    """

    class MockResource(model.Resource):
        """MockResource resource."""

        attr_endpoint: ClassVar[str] = 'api/v2/eggs'
        attr_seq: ClassVar[str] = 'egg_seq'
        egg_seq: str | None = None
        bacon: bool

    resource = MockResource(
        bacon=False,
    )
    mocked.post(
        url=mock_url,
        status=400,
        payload={'eggs': [{'bacon': 'eggs need bacon'}]},
    )

    with pytest.raises(exceptions.SAPResponseError):
        await tenant.create(resource)


async def test_tenant_create_error_payload(
    tenant: Tenant,
    mocked: aioresponses,
) -> None:
    """Test tenant create error payload.

    Request status indicates success.
    Response payload does not match expected schema.
    """
    resource = MockResource(
        name='Spamm',
    )
    mocked.post(
        url=mock_url,
        status=200,
        payload={'bacon': 'out of bacon'},
    )

    with pytest.raises(exceptions.SAPResponseError) as err:
        await tenant.create(resource)
    assert 'Unexpected payload' in str(err.value)


async def test_tenant_create_error_validation(
    tenant: Tenant,
    mocked: aioresponses,
) -> None:
    """Test tenant create error model validation.

    Response status indicates success.
    Response payload did not pass model validation.
    """
    resource = MockResource(name='spamm')
    mocked.post(
        url=mock_url,
        status=201,
        payload={'eggs': [{'eggSeq': '12345', 'needs': 'bacon'}]},
    )
    with pytest.raises(exceptions.SAPResponseError) as err:
        await tenant.create(resource)
    assert 'name' in str(err.value)


async def test_tenant_update(
    tenant: Tenant,
    mocked: aioresponses,
) -> None:
    """Test tenant update happy flow."""
    resource = MockResource(name='Spamm')
    mocked.post(
        url=mock_url,
        status=201,
        payload={'eggs': [{'eggSeq': '12345', 'name': 'eggs'}]},
    )

    resource = await tenant.create(resource)
    assert resource.seq == '12345'
    assert resource.name == 'eggs'

    resource.name = 'bacon'
    mocked.put(
        url=mock_url,
        status=200,
        payload={'eggs': [{'eggSeq': '12345', 'name': 'bacon'}]},
    )
    response = await tenant.update(resource)
    assert response.seq == '12345'
    assert response.name == 'bacon'


async def test_tenant_update_error_not_modified(
    tenant: Tenant,
    mocked: aioresponses,
) -> None:
    """Test tenant update not modified.

    Response status indicates not modified (304).
    """
    resource = MockResource(name='Spamm')
    mocked.put(
        url=mock_url,
        status=304,
    )
    response = await tenant.update(resource)
    assert response.name == 'Spamm'


async def test_tenant_update_error(
    tenant: Tenant,
    mocked: aioresponses,
) -> None:
    """Test tenant create error invalid payload status.

    Response status indicates an error (400).
    Error data does not mention resource.
    """
    resource = MockResource(name='Spamm')
    mocked.put(
        url=mock_url,
        status=400,
        payload={
            'timeStamp': '2024-01-01T01:02:03.04+05:06',
            'message': 'Invalid Resource.',
        },
    )

    with pytest.raises(exceptions.SAPResponseError) as err:
        await tenant.update(resource)
    assert 'Invalid Resource' in str(err.value)


async def test_tenant_update_error_on_field(
    tenant: Tenant,
    mocked: aioresponses,
) -> None:
    """Test tenant create error on field.

    Response status indicates an error (400).
    Error data indicates resource field has an error.
    """

    class MockResource(model.Resource):
        """MockResource resource."""

        attr_endpoint: ClassVar[str] = 'api/v2/eggs'
        attr_seq: ClassVar[str] = 'egg_seq'
        egg_seq: str | None = None
        effective_start_date: datetime
        effective_end_date: datetime

    resource = MockResource(
        effective_start_date=date(2025, 1, 1),
        effective_end_date=date(2024, 1, 1),
    )
    mocked.put(
        url=mock_url,
        status=400,
        payload={
            'eggs': [
                {
                    '_ERROR_': 'TCMP_09022:E: The effective range is invalid.',
                },
            ],
        },
    )

    with pytest.raises(exceptions.SAPResponseError) as err:
        await tenant.update(resource)
    assert 'TCMP_09022' in str(err.value)


async def test_tenant_update_error_unexpected(
    tenant: Tenant,
    mocked: aioresponses,
) -> None:
    """Test tenant create error unexpected.

    Response status indicates an error (400).
    Error data does not mention any known error message.
    """

    class MockResource(model.Resource):
        """MockResource resource."""

        attr_endpoint: ClassVar[str] = 'api/v2/eggs'
        attr_seq: ClassVar[str] = 'egg_seq'
        egg_seq: str | None = None
        bacon: bool

    resource = MockResource(
        bacon=False,
    )
    mocked.put(
        url=mock_url,
        status=400,
        payload={'eggs': [{'bacon': 'eggs need bacon'}]},
    )

    with pytest.raises(exceptions.SAPResponseError):
        await tenant.update(resource)


async def test_tenant_update_error_payload(
    tenant: Tenant,
    mocked: aioresponses,
) -> None:
    """Test tenant create error payload.

    Request status indicates success.
    Response payload does not match expected schema.
    """
    resource = MockResource(
        name='Spamm',
    )
    mocked.put(
        url=mock_url,
        status=200,
        payload={'bacon': 'out of bacon'},
    )

    with pytest.raises(exceptions.SAPResponseError) as err:
        await tenant.update(resource)
    assert 'Unexpected payload' in str(err.value)


async def test_tenant_update_error_validation(
    tenant: Tenant,
    mocked: aioresponses,
) -> None:
    """Test tenant create error model validation.

    Response status indicates success.
    Response payload did not pass model validation.
    """
    resource = MockResource(name='spamm')
    mocked.put(
        url=mock_url,
        status=200,
        payload={'eggs': [{'eggSeq': '12345', 'needs': 'bacon'}]},
    )
    with pytest.raises(exceptions.SAPResponseError) as err:
        await tenant.update(resource)
    assert 'name' in str(err.value)


async def test_tenant_delete(
    tenant: Tenant,
    mocked: aioresponses,
) -> None:
    """Test tenant delete happy flow."""
    resource = MockResource(egg_seq='spamm', name='spamm')
    mocked.delete(
        url=mock_url,
        status=200,
        payload={
            'eggs': {
                'spamm': 'The record is successfully deleted.',
            },
        },
    )
    response = await tenant.delete(resource)
    assert response is True


async def test_tenant_delete_error_seq_none(
    tenant: Tenant,
    mocked: aioresponses,
) -> None:
    """Test tenant delete on resource without seq attribute.

    The resource seq attribute is `None` or falsy.
    Request is never sent.
    """
    resource = MockResource(name='spamm')
    with pytest.raises(exceptions.SAPDeleteFailedError) as err:
        await tenant.delete(resource)
    assert 'no unique identifier' in str(err.value)
    assert len(mocked.requests) == 0

    resource = MockResource(attr_seq=0, name='spamm')
    with pytest.raises(exceptions.SAPDeleteFailedError) as err:
        await tenant.delete(resource)
    assert 'no unique identifier' in str(err.value)
    assert len(mocked.requests) == 0


async def test_tenant_delete_error_seq_invalid(
    tenant: Tenant,
    mocked: aioresponses,
) -> None:
    """Test tenant delete with invalid seq.

    Response status indicates an error (500).
    Error data does not mention resource.
    """
    resource = MockResource(egg_seq='123', name='spamm')
    mocked.delete(
        url=mock_url,
        status=500,
        payload={
            'timeStamp': '2024-01-01T01:02:03.04+05:06',
            'message': 'Invalid Resource Payload',
        },
    )
    with pytest.raises(exceptions.SAPResponseError) as err:
        await tenant.delete(resource)
    assert 'Invalid Resource Payload' in str(err.value)


async def test_tenant_delete_error_seq_not_found(
    tenant: Tenant,
    mocked: aioresponses,
) -> None:
    """Test tenant delete seq not found.

    Response status indicates an error (400).
    Error data indicates why delete failed.
    """
    resource = MockResource(egg_seq='123', name='spamm')
    mocked.delete(
        url=mock_url,
        status=400,
        payload={
            'eggs': {
                '123': 'TCMP_09007:E: Unable to find the Egg "123".',
            },
        },
    )
    with pytest.raises(exceptions.SAPDeleteFailedError) as err:
        await tenant.delete(resource)
    assert 'TCMP_09007' in str(err.value)

    mocked.delete(
        url=mock_url,
        status=400,
        payload={
            'eggs': {
                '123': (
                    'TCMP_35001:E: The Egg spamm could not be removed '
                    'from Jan 1, 2025 to Dec 31, 2199 because it is referenced '
                    'during that time by the Bacon, Cheese.'
                ),
            },
        },
    )
    with pytest.raises(exceptions.SAPDeleteFailedError) as err:
        await tenant.delete(resource)
    assert 'TCMP_35001' in str(err.value)

    # This should not happen, including it here to satify coverage
    mocked.delete(
        url=mock_url,
        status=500,
        payload={
            'eggs': {
                'timeStamp': '2024-01-01T01:02:03.04+05:06',
                'message': 'Invalid Resource Payload',
            },
        },
    )
    with pytest.raises(exceptions.SAPResponseError) as err:
        await tenant.delete(resource)
    assert 'Unexpected payload' in str(err.value)

    mocked.delete(
        url=mock_url,
        status=200,
        payload={
            'timeStamp': '2024-01-01T01:02:03.04+05:06',
            'message': 'Invalid Resource Payload',
        },
    )
    with pytest.raises(exceptions.SAPResponseError) as err:
        await tenant.delete(resource)


async def test_tenant_delete_error_unexpected(
    tenant: Tenant,
    mocked: aioresponses,
) -> None:
    """Test tenant delete unexpected error.

    Response status indicated success.
    Response payload does not mention resource seq.
    """
    resource = MockResource(egg_seq='123', name='spamm')
    mocked.delete(
        url=mock_url,
        status=200,
        payload={
            'timeStamp': '2024-01-01T01:02:03.04+05:06',
            'message': 'Invalid Resource Payload',
        },
    )
    with pytest.raises(exceptions.SAPResponseError) as err:
        await tenant.delete(resource)
    assert 'Invalid Resource Payload' in str(err.value)

    mocked.delete(
        url=mock_url,
        status=200,
        payload={
            'eggs': {
                'timeStamp': '2024-01-01T01:02:03.04+05:06',
                'message': 'Invalid Resource Payload',
            },
        },
    )
    with pytest.raises(exceptions.SAPResponseError) as err:
        await tenant.delete(resource)
    assert 'Invalid Resource Payload' in str(err.value)


async def test_tenant_read_all(
    tenant: Tenant,
    mocked: aioresponses,
) -> None:
    """Test tenant read all happy flow."""
    mocked.get(
        url=mock_url,
        status=200,
        payload={
            'eggs': [{'eggSeq': '123', 'name': 'spamm'}],
            'next': '/v2/eggs?top=1&skip=1',
        },
    )
    mocked.get(
        url=mock_url,
        status=200,
        payload={
            'eggs': [{'eggSeq': '456', 'name': 'eggs'}],
        },
    )
    resources = [
        resource async for resource in tenant.read_all(MockResource, page_size=1)
    ]
    assert len(mocked.requests) == 2
    assert len(resources) == 2
    assert resources[0].egg_seq == '123'
    assert resources[1].egg_seq == '456'


async def test_tenant_read_all_page_size(
    tenant: Tenant,
    mocked: aioresponses,
) -> None:
    """Test tenant read all page size.

    page_size within bounds, page_size=2.
    """
    mocked.get(
        url=mock_url,
        status=200,
        payload={'eggs': []},
    )
    _ = [resource async for resource in tenant.read_all(MockResource, page_size=2)]
    assert len(mocked.requests) == 1
    for request in mocked.requests:
        assert mock_url.match(str(request[1]))
        assert 'top=2' in str(request[1])


async def test_tenant_read_all_page_size_salestransactions(
    tenant: Tenant,
    mocked: aioresponses,
) -> None:
    """Test tenant read all adjust page size.

    page_size gets adjusted to 1 for salesTransactions.
    """
    mocked.get(
        url=re.compile(r'^.*/api/v2/salesTransactions.*$'),
        status=200,
        payload={'salesTransactions': []},
    )
    _ = [
        resource
        async for resource in tenant.read_all(model.SalesTransaction, page_size=2)
    ]
    assert len(mocked.requests) == 1
    for request in mocked.requests:
        assert '/api/v2/salesTransactions' in str(request[1])
        assert 'top=1' in str(request[1])


async def test_tenant_read_all_page_size_below_bounds(
    tenant: Tenant,
    mocked: aioresponses,
) -> None:
    """Test tenant read all adjust page size.

    page_size out of bounds, page_size = 0.
    """
    mocked.get(
        url=mock_url,
        status=200,
        payload={'eggs': []},
    )
    _ = [resource async for resource in tenant.read_all(MockResource, page_size=0)]
    assert len(mocked.requests) == 1
    for request in mocked.requests:
        assert mock_url.match(str(request[1]))
        assert 'top=1' in str(request[1])


async def test_tenant_read_all_page_size_above_bounds(
    tenant: Tenant,
    mocked: aioresponses,
) -> None:
    """Test tenant read all adjust page size.

    page_size out of bounds, page_size = 1000.
    """
    mocked.get(
        url=mock_url,
        status=200,
        payload={'eggs': []},
    )
    _ = [resource async for resource in tenant.read_all(MockResource, page_size=1000)]
    assert len(mocked.requests) == 1
    for request in mocked.requests:
        assert mock_url.match(str(request[1]))
        assert 'top=100' in str(request[1])


async def test_tenant_read_all_filter(
    tenant: Tenant,
    mocked: aioresponses,
) -> None:
    """Test tenant read all apply filter."""
    mocked.get(
        url=mock_url,
        status=200,
        payload={'eggs': []},
    )
    _ = [
        resource
        async for resource in tenant.read_all(
            MockResource,
            filters="spamm eq 'eggs'",
        )
    ]
    assert len(mocked.requests) == 1
    for request in mocked.requests:
        assert mock_url.match(str(request[1]))
        assert all(
            item in str(request[1]) for item in ['filter', 'spamm', 'eq', 'eggs']
        )


async def test_tenant_read_all_order_by(
    tenant: Tenant,
    mocked: aioresponses,
) -> None:
    """Test tenant read all order_by."""
    mocked.get(
        url=mock_url,
        status=200,
        payload={'eggs': []},
    )
    _ = [
        resource
        async for resource in tenant.read_all(
            MockResource,
            order_by=['spamm', 'eggs', 'bacon'],
        )
    ]
    assert len(mocked.requests) == 1
    for request in mocked.requests:
        assert mock_url.match(str(request[1]))
        assert all(
            item in str(request[1]) for item in ['orderBy', 'spamm', 'eggs', 'bacon']
        )


async def test_tenant_read_all_error_unexpected(
    tenant: Tenant,
    mocked: aioresponses,
) -> None:
    """Test tenant read all error unexpected.

    Response status indices success.
    Response payload does not contain resource.
    """
    mocked.get(
        url=mock_url,
        status=200,
        payload={'bacon': 'cheese'},
    )
    with pytest.raises(exceptions.SAPResponseError) as err:
        _ = [resource async for resource in tenant.read_all(MockResource)]
    assert 'Unexpected payload' in str(err.value)


async def test_tenant_read_all_error_validation(
    tenant: Tenant,
    mocked: aioresponses,
) -> None:
    """Test tenant read all error unexpected.

    Response status indices success.
    Response payload does not contain resource.
    """
    mocked.get(
        url=mock_url,
        status=200,
        payload={
            'eggs': [
                {'eggSeq': '123', 'name': 'spamm'},
                {'eggSeq': '456'},
            ],
        },
    )
    with pytest.raises(exceptions.SAPResponseError) as err:
        _ = [resource async for resource in tenant.read_all(MockResource)]
    assert 'name' in str(err.value)


async def test_tenant_read_first(
    tenant: Tenant,
    mocked: aioresponses,
) -> None:
    """Test tenant read first happy flow."""
    mocked.get(
        url=mock_url,
        status=200,
        payload={
            'eggs': [{'eggSeq': '123', 'name': 'spamm'}],
            'next': '/v2/eggs?top=1&skip=1',
        },
    )
    mocked.get(
        url=mock_url,
        status=200,
        payload={
            'eggs': [{'eggSeq': '456', 'name': 'eggs'}],
        },
    )
    resource = await tenant.read_first(MockResource)
    assert len(mocked.requests) == 1
    assert resource.seq == '123'
    assert resource.name == 'spamm'


async def test_tenant_read_first_error_not_found(
    tenant: Tenant,
    mocked: aioresponses,
) -> None:
    """Test tenant read first error not found."""
    mocked.get(
        url=mock_url,
        status=200,
        payload={'eggs': []},
    )
    with pytest.raises(exceptions.SAPNotFoundError):
        await tenant.read_first(MockResource)


async def test_tenant_read_seq(
    tenant: Tenant,
    mocked: aioresponses,
) -> None:
    """Test tenant read seq happy flow."""
    mocked.get(
        url=mock_url,
        status=200,
        payload={'eggSeq': '123', 'name': 'spamm'},
    )
    resource = await tenant.read_seq(MockResource, '123')
    assert resource.seq == '123'


async def test_tenant_read_seq_error_validation(
    tenant: Tenant,
    mocked: aioresponses,
) -> None:
    """Test tenant read seq error validation."""
    mocked.get(
        url=mock_url,
        status=200,
        payload={'eggSeq': '123', 'needs': 'bacon'},
    )
    with pytest.raises(exceptions.SAPResponseError) as err:
        await tenant.read_seq(MockResource, '123')
    assert 'name' in str(err.value)


async def test_tenant_read(
    tenant: Tenant,
    mocked: aioresponses,
) -> None:
    """Test tenant read happy flow."""
    mocked.get(
        url=mock_url,
        status=200,
        payload={'eggSeq': '123', 'name': 'spamm'},
    )
    mock_resource = MockResource(
        egg_seq='123',
        name='spamm',
    )
    resource = await tenant.read(mock_resource)
    assert mock_resource == resource


async def test_tenant_read_error_seq_none(
    tenant: Tenant,
    mocked: aioresponses,
) -> None:
    """Test tenant read error seq none.

    The resource seq attribute is `None` or falsy.
    Request is never sent.
    """
    resource = MockResource(name='spamm')
    with pytest.raises(exceptions.SAPNotFoundError) as err:
        await tenant.read(resource)
    assert 'no unique identifier' in str(err.value)
    assert len(mocked.requests) == 0

    resource = MockResource(attr_seq=0, name='spamm')
    with pytest.raises(exceptions.SAPNotFoundError) as err:
        await tenant.read(resource)
    assert 'no unique identifier' in str(err.value)
    assert len(mocked.requests) == 0


async def test_tenant_run_pipeline(
    tenant: Tenant,
    mocked: aioresponses,
) -> None:
    """Test tenant run pipeline happy flow."""

    class MockPipeline(model.Endpoint):
        """Mock pipeline job."""

        attr_endpoint: ClassVar[str] = 'api/v2/pipelines'
        command: str = 'PipelineRun'
        stage_type_seq: str = '21673573206720532'
        calendar_seq: str = '123'
        period_seq: str = '456'

    mock_job = MockPipeline()
    mocked.post(
        url=f'{tenant.host}/api/v2/pipelines',
        status=200,
        payload={'pipelines': {'0': ['123']}},
    )
    mocked.get(
        url=re.compile(r'^.*/api/v2/pipelines\(123\).*$'),
        status=200,
        payload={
            'pipelineRunSeq': '123',
            'command': 'PipelineRun',
            'stageType': '21673573206720532',
            'dateSubmitted': '2024-01-01',
            'state': 'Running',
            'userId': 'spamm',
            'processingUnit': '999',
            'period': '456',
        },
    )
    response = await tenant.run_pipeline(mock_job)
    assert isinstance(response, model.Pipeline)
    assert response.seq == '123'


async def test_tenant_run_pipeline_error(
    tenant: Tenant,
    mocked: aioresponses,
) -> None:
    """Test tenant run pipeline error."""

    class MockPipeline(model.Endpoint):
        """Mock pipeline job."""

        attr_endpoint: ClassVar[str] = 'api/v2/pipelines'
        command: str = 'PipelineRun'
        stage_type_seq: str = '21673573206720532'
        calendar_seq: str = '123'
        period_seq: str = '456'

    mock_job = MockPipeline()

    # 500 - without mention of resource.
    mocked.post(
        url=f'{tenant.host}/api/v2/pipelines',
        status=500,
        payload={
            'timestamp': '2024-01-01',
            'message': 'Could not run pipeline job',
        },
    )
    with pytest.raises(exceptions.SAPResponseError) as err:
        await tenant.run_pipeline(mock_job)
    assert 'Could not run pipeline job' in str(err.value)

    # 500 - with mention of resource and job.
    mocked.post(
        url=f'{tenant.host}/api/v2/pipelines',
        status=500,
        payload={'pipelines': {'0': {'spamm': 'Value for spamm is required'}}},
    )
    with pytest.raises(exceptions.SAPResponseError) as err:
        await tenant.run_pipeline(mock_job)
    assert 'Value for spamm is required' in str(err.value)

    # 500 - with mention of resource without job.
    mocked.post(
        url=f'{tenant.host}/api/v2/pipelines',
        status=500,
        payload={'pipelines': {'_ERROR_': 'Server did not respond'}},
    )
    with pytest.raises(exceptions.SAPResponseError) as err:
        await tenant.run_pipeline(mock_job)
    assert 'Server did not respond' in str(err.value)

    # 200 - without mention of resource.
    mocked.post(
        url=f'{tenant.host}/api/v2/pipelines',
        status=200,
        payload={
            'timestamp': '2024-01-01',
            'message': 'Unexpected response',
        },
    )
    with pytest.raises(exceptions.SAPResponseError) as err:
        await tenant.run_pipeline(mock_job)
    assert 'Unexpected response' in str(err.value)

    # 200 - with mention of resource without job
    mocked.post(
        url=f'{tenant.host}/api/v2/pipelines',
        status=200,
        payload={'pipelines': {'_ERROR_': 'Server did not respond'}},
    )
    with pytest.raises(exceptions.SAPResponseError) as err:
        await tenant.run_pipeline(mock_job)
    assert 'Server did not respond' in str(err.value)


async def test_tenant_cancel_pipeline(
    tenant: Tenant,
    mocked: aioresponses,
) -> None:
    """Test tenant cancel pipeline happy flow."""

    class MockPipeline(model.Resource):
        """Mock pipeline."""

        attr_endpoint: ClassVar[str] = 'api/v2/pipelines'
        attr_seq: ClassVar[str] = 'pipeline_run_seq'
        pipeline_run_seq: str | None = None
        command: str = 'PipelineRun'

    mock_job = MockPipeline(pipeline_run_seq='123')
    mocked.delete(
        url=f'{tenant.host}/api/v2/pipelines(123)',
        status=200,
        payload={'123': 'Job cancelled'},
    )
    response = await tenant.cancel_pipeline(mock_job)
    assert response is True

    # 500 - with mention of job.
    mocked.delete(
        url=f'{tenant.host}/api/v2/pipelines(123)',
        status=500,
        payload={'123': 'TCMP_60255:Job deleted.'},
    )
    response = await tenant.cancel_pipeline(mock_job)
    assert response is True


async def test_tenant_cancel_pipeline_error(
    tenant: Tenant,
    mocked: aioresponses,
) -> None:
    """Test tenant cancel pipeline error."""

    class MockPipeline(model.Resource):
        """Mock pipeline."""

        attr_endpoint: ClassVar[str] = 'api/v2/pipelines'
        attr_seq: ClassVar[str] = 'pipeline_run_seq'
        pipeline_run_seq: str | None = None
        command: str = 'PipelineRun'

    mock_job = MockPipeline(pipeline_run_seq='123')

    # 500 - without mention of job.
    mocked.delete(
        url=f'{tenant.host}/api/v2/pipelines(123)',
        status=500,
        payload={'error': 'Job not found.'},
    )
    with pytest.raises(exceptions.SAPResponseError) as err:
        await tenant.cancel_pipeline(mock_job)
    assert 'Job not found' in str(err.value)

    # 500 - with mention of job.
    mocked.delete(
        url=f'{tenant.host}/api/v2/pipelines(123)',
        status=500,
        payload={'123': 'Job already cancelled.'},
    )
    with pytest.raises(exceptions.SAPResponseError) as err:
        await tenant.cancel_pipeline(mock_job)
    assert 'Job already cancelled' in str(err.value)

    # 200 - without mention of job.
    mocked.delete(
        url=f'{tenant.host}/api/v2/pipelines(123)',
        status=200,
        payload={'error': 'Unexpected response'},
    )
    with pytest.raises(exceptions.SAPResponseError) as err:
        await tenant.cancel_pipeline(mock_job)
    assert 'Unexpected response' in str(err.value)
