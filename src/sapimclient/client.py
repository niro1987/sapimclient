"""Asynchronous Client to interact with SAP Incentive Management REST API."""

import asyncio
import logging
from collections.abc import AsyncGenerator
from dataclasses import dataclass
from typing import Any, TypeVar

from aiohttp import ClientError, ClientSession
from pydantic.fields import FieldInfo
from pydantic_core import ValidationError

from sapimclient import exceptions, model
from sapimclient.const import HTTPMethod
from sapimclient.helpers import BooleanOperator, LogicalOperator, retry

LOGGER: logging.Logger = logging.getLogger(__name__)
T = TypeVar('T', bound=model.Resource)

REQUEST_TIMEOUT: int = 60
STATUS_NOT_MODIFIED: int = 304
STATUS_BAD_REQUEST: int = 400
STATUS_SERVER_ERROR: int = 500
REQUIRED_STATUS: dict[str, tuple[int, ...]] = {
    HTTPMethod.GET: (200,),
    HTTPMethod.POST: (200, 201),
    HTTPMethod.PUT: (200,),
    HTTPMethod.DELETE: (200,),
}
ATTR_ERROR: str = '_ERROR_'
ATTR_EXPAND: str = 'expand'
ATTR_FILTER: str = '$filter'
ATTR_ORDERBY: str = 'orderBy'
ATTR_INLINECOUNT: str = 'inlineCount'
ATTR_NEXT: str = 'next'
ATTR_SKIP: str = 'skip'
ATTR_TOP: str = 'top'
ATTR_TOTAL: str = 'total'
ERROR_ALREADY_EXISTS: str = 'TCMP_35004'
ERROR_DELETE_PIPELINE: str = 'TCMP_60255'
ERROR_MISSING_FIELD: str = 'TCMP_1002'
ERROR_NOT_FOUND: str = 'TCMP_09007'
ERROR_REFERRED_BY: str = 'TCMP_35001'
ERROR_OBTAIN_ACCESS: str = 'TCMP_09012'
ERROR_REMOVE_FAILED: str = 'TCMP_35243'
MIN_PAGE_SIZE: int = 1
MAX_PAGE_SIZE: int = 100


@dataclass
class Tenant:
    """Asynchronous interface to interacting with SAP Incentive Management REST API.

    Parameters:
        tenant (str): Your tenant ID. For example, if the login url is
            `https://cald-prd.callidusondemand.com/SalesPortal/#!/`,
            the tenant ID is `cald-prd`.
        session (ClientSession): An aiohttp ClientSession.
        verify_ssl (bool, optional): Enable SSL verification.
            Defaults to True.
        request_timeout (int, optional): Request timeout in seconds.
            Defaults to 60.
    """

    tenant: str
    session: ClientSession
    verify_ssl: bool = True
    request_timeout: int = REQUEST_TIMEOUT

    @property
    def host(self) -> str:
        """The fully qualified hostname."""
        return f'https://{self.tenant}.callidusondemand.com'

    async def _request(
        self,
        method: HTTPMethod,
        uri: str,
        params: dict | None = None,
        json: list | None = None,
    ) -> dict[str, Any]:
        """Send a request.

        Parameters:
            method (str): HTTP method (GET, POST, PUT, DELETE, UDPATE).
            uri (str): API endpoint URI.
            params (dict, optional): Query parameters.
            json (list, optional): JSON payload.

        Returns:
            dict: The JSON response.

        Raises:
            SAPConnectionError: If the connection fails.
            SAPNotModifiedError: If the resource has not been modified.
            SAPResponseError: If the response status is not as expected.
            SAPBadRequestError: If the request status indicates an error.
        """
        LOGGER.debug('Request: %s, %s, %s', method, uri, params)

        try:
            async with asyncio.timeout(self.request_timeout):
                response = await self.session.request(
                    method=method,
                    url=f'{self.host}/{uri}',
                    params=params,
                    json=json,
                    ssl=self.verify_ssl,
                )
        except TimeoutError as err:
            msg = 'Timeout while connecting'
            LOGGER.exception(msg)
            raise exceptions.SAPConnectionError(msg) from err
        except ClientError as err:
            msg = 'Could not connect'
            LOGGER.exception(msg)
            raise exceptions.SAPConnectionError(msg) from err

        # Status code 304 Not Modified is successful but does not include
        # any json data for us to work with.
        if response.status == STATUS_NOT_MODIFIED:
            raise exceptions.SAPNotModifiedError

        # During maintenance hours we recieve an html response, let it burn!
        # In all other cases we expect to recieve a JSON response.
        if (content_type := response.headers.get('Content-Type')) != 'application/json':
            msg = f'Unexpected Content-Type: {content_type}'
            LOGGER.error(msg)
            raise exceptions.SAPResponseError(msg)

        response_json = await response.json()

        # Validate the required status code.
        if response.status not in REQUIRED_STATUS[method]:
            msg = f'Unexpected response status: {response.status}'
            LOGGER.error(msg)
            raise exceptions.SAPBadRequestError(msg, response_json)

        return response_json

    async def create(self, resource: T) -> T:
        """Create a new resource.

        Parameters:
            resource (T): The resource to create.

        Returns:
            T: The created resource.

        Raises:
            SAPAlreadyExistsError: If the resource already exists.
            SAPMissingFieldError: If one or more required fields are missing.
            SAPResponseError: If the creation encountered an error.
        """
        cls = type(resource)
        LOGGER.debug('Create %s(%s)', cls.__name__, resource)

        attr_resource: str = resource.attr_endpoint.split('/')[-1]
        json: dict[str, Any] = resource.model_dump(
            mode='json',
            by_alias=True,
            exclude_none=True,
        )

        try:
            response: dict[str, Any] = await self._request(
                method=HTTPMethod.POST,
                uri=resource.attr_endpoint,
                json=[json],
            )
        except exceptions.SAPBadRequestError as err:
            if attr_resource not in err.data:
                msg = f'Unexpected payload. {err.data}'
                LOGGER.exception(msg)
                raise exceptions.SAPResponseError(msg) from err

            error_data: list[dict[str, Any]] = err.data[attr_resource]
            for errors in error_data:
                error_message = errors.get(ATTR_ERROR)
                if error_message and ERROR_ALREADY_EXISTS in error_message:
                    raise exceptions.SAPAlreadyExistsError(error_message) from err
                if any(ERROR_MISSING_FIELD in value for value in errors.values()):
                    LOGGER.exception(errors)
                    raise exceptions.SAPMissingFieldError(errors) from err
            msg = f'Unexpected error. {error_data}'
            LOGGER.exception(msg)
            raise exceptions.SAPResponseError(msg) from err

        if attr_resource not in response:
            msg = f'Unexpected payload. {response}'
            LOGGER.error(msg)
            raise exceptions.SAPResponseError(msg)

        json_data: list[dict[str, Any]] = response[attr_resource]
        data: dict[str, Any] = json_data[0]
        try:
            return cls(**data)
        except ValidationError as exc:
            for error in exc.errors():
                LOGGER.exception('%s on %s', error, data)
            raise exceptions.SAPResponseError(str(exc)) from exc

    async def update(self, resource: T) -> T:
        """Update an existing resource.

        Parameters:
            resource (T): The resource to update.

        Returns:
            T: The updated resource.

        Raises:
            SAPResponseError: If the update encountered an error.
        """
        cls = type(resource)
        LOGGER.debug('Update %s(%s)', cls.__name__, resource)

        attr_resource: str = resource.attr_endpoint.split('/')[-1]
        json: dict[str, Any] = resource.model_dump(
            mode='json',
            by_alias=True,
            exclude_none=True,
        )

        try:
            response: dict[str, Any] = await self._request(
                method=HTTPMethod.PUT,
                uri=resource.attr_endpoint,
                json=[json],
            )
        except exceptions.SAPNotModifiedError:
            return resource
        except exceptions.SAPBadRequestError as err:
            if attr_resource not in err.data:
                msg = f'Unexpected payload. {err.data}'
                LOGGER.exception(msg)
                raise exceptions.SAPResponseError(msg) from err

            error_data: list[dict[str, Any]] = err.data[attr_resource]
            for errors in error_data:
                if error_message := errors.get(ATTR_ERROR):
                    LOGGER.exception(error_message)
                    raise exceptions.SAPResponseError(error_message) from err
            msg = f'Unexpected error. {error_data}'
            LOGGER.exception(msg)
            raise exceptions.SAPResponseError(msg) from err

        if attr_resource not in response:
            msg = f'Unexpected payload. {response}'
            LOGGER.error(msg)
            raise exceptions.SAPResponseError(msg)

        json_data: list[dict[str, Any]] = response[attr_resource]
        data: dict[str, Any] = json_data[0]
        try:
            return cls(**data)
        except ValidationError as exc:
            for error in exc.errors():
                LOGGER.exception('%s on %s', error, data)
            raise exceptions.SAPResponseError(str(exc)) from exc

    async def delete(self, resource: T) -> bool:
        """Delete a resource.

        Parameters:
            resource (T): The resource to delete.

        Returns:
            bool: True if the resource was deleted. Raises an exception othwise.

        Raises:
            SAPDeleteFailedError: If the deletion failed.
            SAPResponseError: If the deletion encountered an error.
        """
        cls = type(resource)
        LOGGER.debug('Delete %s(%s)', cls.__name__, resource)

        attr_resource: str = resource.attr_endpoint.split('/')[-1]
        if not (seq := resource.seq):
            msg = f'Resource {cls.__name__} has no unique identifier'
            raise exceptions.SAPDeleteFailedError(msg)
        uri: str = f'{resource.attr_endpoint}({seq})'

        try:
            response: dict[str, Any] = await self._request(
                method=HTTPMethod.DELETE,
                uri=uri,
            )
        except exceptions.SAPBadRequestError as err:
            if attr_resource not in err.data:
                msg = f'Unexpected payload. {err.data}'
                LOGGER.exception(msg)
                raise exceptions.SAPResponseError(msg) from err

            error_data: dict[str, str] = err.data[attr_resource]
            if seq not in error_data:
                msg = f'Unexpected payload. {error_data}'
                LOGGER.exception(msg)
                raise exceptions.SAPResponseError(msg) from err

            error_message: str = error_data[seq]
            LOGGER.exception(error_message)
            raise exceptions.SAPDeleteFailedError(error_message) from err

        if attr_resource not in response:
            msg = f'Unexpected payload. {response}'
            LOGGER.error(msg)
            raise exceptions.SAPResponseError(msg)

        json: dict[str, Any] = response[attr_resource]
        if seq not in json:
            msg = f'Unexpected payload. {json}'
            LOGGER.error(msg)
            raise exceptions.SAPResponseError(msg)

        return True

    async def read_all(  # pylint: disable=too-many-arguments,too-many-locals # noqa: C901
        self,
        resource_cls: type[T],
        *,
        filters: BooleanOperator | LogicalOperator | str | None = None,
        order_by: list[str] | None = None,
        page_size: int = 10,
    ) -> AsyncGenerator[T, None]:
        """Read all matching resources.

        Parameters:
            resource_cls (type[T]): The type of the resource to list.
            filters (BooleanOperator | LogicalOperator | str, optional): The filters to
                apply.
            order_by (list[str], optional): The fields to order by.
            page_size (int, optional): The number of resources per page. Defaults to 10.

        Yields:
            T: Matching resource.

        Raises:
            SAPResponseError: If the read encountered an error.
        """
        page_size = min(max(page_size, MIN_PAGE_SIZE), MAX_PAGE_SIZE)

        # FIX: Issue #30
        if resource_cls is model.SalesTransaction and page_size != 1:
            LOGGER.warning(
                'See issue https://github.com/niro1987/sapimclient/issues/30',
            )
            page_size = 1

        LOGGER.debug(
            'List %s filters=%s order_by=%s page_size=%s',
            resource_cls.__name__,
            str(filters),
            ','.join(order_by) if order_by else 'None',
            page_size,
        )

        attr_resource: str = resource_cls.attr_endpoint.split('/')[-1]
        params: dict[str, str | int] = {ATTR_TOP: page_size}
        if filters:
            params[ATTR_FILTER] = str(filters)
        if order_by:
            params[ATTR_ORDERBY] = ','.join(order_by)
        expands: dict[str, FieldInfo] = resource_cls.expands()
        if expand_alias := [
            field_info.alias for field_info in expands.values() if field_info.alias
        ]:
            params[ATTR_EXPAND] = ','.join(expand_alias)

        uri: str = resource_cls.attr_endpoint
        while True:
            response = await retry(
                self._request,
                'GET',
                uri=uri,
                params=params,
                exceptions=exceptions.SAPConnectionError,
            )

            if attr_resource not in response:
                msg = f'Unexpected payload. {response}'
                LOGGER.error(msg)
                raise exceptions.SAPResponseError(msg)

            json: list[dict[str, Any]] = response[attr_resource]
            for item in json:
                try:
                    yield resource_cls(**item)
                except ValidationError as exc:
                    for error in exc.errors():
                        LOGGER.exception('%s on %s', error, item)
                    raise exceptions.SAPResponseError(str(exc)) from exc

            if not (next_uri := response.get(ATTR_NEXT)):
                break

            params = {}
            uri = 'api' + next_uri

    async def read_first(
        self,
        resource_cls: type[T],
        *,
        filters: BooleanOperator | LogicalOperator | str | None = None,
        order_by: list[str] | None = None,
    ) -> T:
        """Read the first matching resource.

        A convenience method for `await anext(read_all(...))` with `page_size=1`.

        Parameters:
            resource_cls (type[T]): The type of the resource to read.
            filters (BooleanOperator | LogicalOperator | str, optional): The filters to
                apply.
            order_by (list[str], optional): The fields to order by.

        Returns:
            T: The first matching resource.

        Raises:
            SAPNotFoundError: If no matching resource is found.
        """
        LOGGER.debug('Read %s %s', resource_cls.__name__, f'filters={filters}')
        list_resources = self.read_all(
            resource_cls,
            filters=filters,
            order_by=order_by,
            page_size=1,
        )
        try:
            return await anext(list_resources)  # type: ignore[arg-type]
        except StopAsyncIteration as err:
            raise exceptions.SAPNotFoundError(resource_cls.__name__) from err

    async def read_seq(self, resource_cls: type[T], seq: str) -> T:
        """Read the specified resource.

        Parameters:
            resource_cls (type[T]): The type of the resource to read.
            seq (str): The unique identifier of the resource.

        Returns:
            T: The specified resource. Raises an exception if the resource is not found.

        Raises:
            SAPBadRequestError: If the resource was not found.
            SAPResponseError: If the read encountered an error.
        """
        LOGGER.debug('Read Seq %s(%s)', resource_cls.__name__, seq)

        uri: str = f'{resource_cls.attr_endpoint}({seq})'
        params: dict[str, str] = {}
        expands: dict[str, FieldInfo] = resource_cls.expands()
        if expand_alias := [
            field_info.alias for field_info in expands.values() if field_info.alias
        ]:
            params[ATTR_EXPAND] = ','.join(expand_alias)

        response: dict[str, Any] = await self._request(
            method=HTTPMethod.GET,
            uri=uri,
            params=params,
        )
        try:
            return resource_cls(**response)
        except ValidationError as exc:
            for error in exc.errors():
                LOGGER.exception('%s on %s', error, response)
            raise exceptions.SAPResponseError(str(exc)) from exc

    async def read(self, resource: T) -> T:
        """Reload a fully initiated resource.

        A convenience method for `await read_seq(resource.__class__, resource.seq)`.

        Parameters:
            resource (T): The fully initiated resource.

        Returns:
            T: The fully initiated resource.

        Raises:
            SAPNotFoundError: If the resource does not contain a unique identifier.

        Example:
            When running a pipeline job, you can wait for the job to complete:

            .. code-block:: python

                pipeline = await run_pipeline(job)
                while pipeline.state != PipelineState.Done:
                    await asyncio.sleep(30)
                    pipeline = client.read(pipeline)
        """
        cls = type(resource)
        LOGGER.debug('Read %s(%s)', cls.__name__, resource.seq)
        if not (seq := resource.seq):
            msg = f'Resource {cls.__name__} has no unique identifier'
            raise exceptions.SAPNotFoundError(msg)
        return await self.read_seq(cls, seq)

    async def run_pipeline(self, job: model.pipeline._PipelineJob) -> model.Pipeline:
        """Run a pipeline and retrieves the created Pipeline.

        Parameters:
            job (model.pipeline._PipelineJob): The pipeline job to run.

        Returns:
            model.Pipeline: The created Pipeline.

        Raises:
            SAPResponseError: If the pipeline failed to run.
        """
        LOGGER.debug('Run pipeline %s', type(job).__name__)
        json: dict[str, Any] = job.model_dump(
            mode='json',
            by_alias=True,
            exclude_none=True,
        )

        try:
            response: dict[str, Any] = await self._request(
                method=HTTPMethod.POST,
                uri=job.attr_endpoint,
                json=[json],
            )
        except exceptions.SAPBadRequestError as err:
            if 'pipelines' not in err.data:
                msg = f'Unexpected payload. {err.data}'
                LOGGER.exception(msg)
                raise exceptions.SAPResponseError(msg) from err

            error_data: dict[str, str] = err.data['pipelines']
            if '0' not in error_data:
                msg = f'Unexpected payload. {error_data}'
                LOGGER.exception(msg)
                raise exceptions.SAPResponseError(msg) from err

            msg = error_data['0']
            LOGGER.exception(msg)
            raise exceptions.SAPResponseError(msg) from err

        if 'pipelines' not in response:
            msg = f'Unexpected payload. {response}'
            LOGGER.error(msg)
            raise exceptions.SAPResponseError(msg)

        json_data: dict[str, list[str]] = response['pipelines']
        if '0' not in json_data:
            msg = f'Unexpected payload. {json_data}'
            LOGGER.error(msg)
            raise exceptions.SAPResponseError(msg)

        seq: str = json_data['0'][0]
        return await self.read_seq(model.Pipeline, seq)

    async def cancel_pipeline(self, job: model.Pipeline) -> bool:
        """Cancel a running pipeline.

        Parameters:
            job (model.Pipeline): The running pipeline job to cancel.

        Returns:
            bool: True if the pipeline was successfully canceled. Raises an exception
                othwise.

        Raises:
            SAPResponseError: If the deletion encountered an error.
        """
        LOGGER.debug('Cancel %s(%s)', job.command, job.pipeline_run_seq)

        uri: str = f'{job.attr_endpoint}({job.pipeline_run_seq})'
        try:
            response: dict[str, Any] = await self._request(
                method=HTTPMethod.DELETE,
                uri=uri,
            )
        except exceptions.SAPBadRequestError as err:
            if job.pipeline_run_seq not in err.data:
                msg = f'Unexpected payload. {err.data}'
                LOGGER.exception(msg)
                raise exceptions.SAPResponseError(msg) from err

            error_message: str = err.data[job.pipeline_run_seq]
            if ERROR_DELETE_PIPELINE in error_message:
                # TCMP_60255:E: An error occurred while attempting to delete a job.
                # The Grid Server returned with the message:
                # [GSVRH] Setting Job runStatus to Cancel, but the Controller returned
                # the following error: ++-error::[Controller] unknown command: delJob
                return True
            msg = f'Unexpected payload. {error_message}'
            LOGGER.exception(msg)
            raise exceptions.SAPResponseError(msg) from err

        if job.pipeline_run_seq not in response:
            msg = f'Unexpected payload. {response}'
            LOGGER.error(msg)
            raise exceptions.SAPResponseError(msg)

        return True
