"""Deploy module for Python SAP Incentive Management Client."""

import asyncio
import csv
import logging
import re
from pathlib import Path
from typing import Final

from sapimclient import Tenant, model
from sapimclient.const import PipelineState, PipelineStatus
from sapimclient.exceptions import SAPAlreadyExistsError, SAPConnectionError
from sapimclient.helpers import retry
from sapimclient.model.data_type import _DataType

LOGGER: logging.Logger = logging.getLogger(__name__)

RE_CREDIT_TYPE: Final[re.Pattern] = re.compile(
    r'^[a-z0-9_.\- ]*(Credit Type)\.txt$',
    flags=re.IGNORECASE,
)
RE_EARNING_CODE: Final[re.Pattern] = re.compile(
    r'^[a-z0-9_.\- ]*(Earning Code)\.txt$',
    flags=re.IGNORECASE,
)
RE_EARNING_GROUP: Final[re.Pattern] = re.compile(
    r'^[a-z0-9_.\- ]*(Earning Group)\.txt$',
    flags=re.IGNORECASE,
)
RE_EVENT_TYPE: Final[re.Pattern] = re.compile(
    r'^[a-z0-9_.\- ]*(Event Type)\.txt$',
    flags=re.IGNORECASE,
)
RE_FIXED_VALUE_TYPE: Final[re.Pattern] = re.compile(
    r'^[a-z0-9_.\- ]*(Fixed Value Type)\.txt$',
    flags=re.IGNORECASE,
)
RE_REASON_CODE: Final[re.Pattern] = re.compile(
    r'^[a-z0-9_.\- ]*(Reason Code)\.txt$',
    flags=re.IGNORECASE,
)
RE_XML: Final[re.Pattern] = re.compile(
    r'^[a-z0-9_.\- ]*[a-z0-9_.\- ]+\.xml$',
    flags=re.IGNORECASE,
)


def _file_cls(file: Path) -> type[_DataType | model.XMLImport]:
    """Determine the endpoint based on the filename."""
    file_mapping: dict[re.Pattern, type[_DataType | model.XMLImport]] = {
        RE_CREDIT_TYPE: model.CreditType,
        RE_EARNING_CODE: model.EarningCode,
        RE_EARNING_GROUP: model.EarningGroup,
        RE_EVENT_TYPE: model.EventType,
        RE_FIXED_VALUE_TYPE: model.FixedValueType,
        RE_REASON_CODE: model.Reason,
        RE_XML: model.XMLImport,
    }
    for pattern, resource_cls in file_mapping.items():
        if re.match(pattern, file.name):
            return resource_cls
    msg = f'No known file type for {file.name}'
    raise ValueError(msg)


async def deploy_from_path(
    client: Tenant,
    path: Path,
) -> dict[Path, list[_DataType] | list[model.Pipeline]]:
    """Deploy."""
    LOGGER.debug('Deploy %s', path)
    # This is to make sure we recognize each file before we attempt to deploy.
    files_with_cls: list[tuple[Path, type[_DataType | model.XMLImport]]] = [
        (file, _file_cls(file))
        for file in sorted(path.iterdir(), key=lambda x: x.name)
        if file.is_file()
    ]
    results: dict[Path, list[_DataType] | list[model.Pipeline]] = {}
    for file, resource_cls in files_with_cls:
        if issubclass(resource_cls, _DataType):
            results[file] = await deploy_datatypes_from_file(client, file, resource_cls)
        if resource_cls is model.XMLImport:
            result: model.Pipeline = await deploy_xml(client, file)
            if result.status != PipelineStatus.Successful:
                break
            results[file] = [result]
    return results


async def deploy_datatypes_from_file(
    client: Tenant,
    file: Path,
    resource_cls: type[_DataType],
) -> list[_DataType]:
    """Deploy file."""
    LOGGER.info('Deploy file: %s', file)
    resources: list[_DataType] = []
    with file.open(encoding='utf-8', newline='') as f_in:
        reader = csv.reader(f_in)
        next(reader)  # Skip header
        resources.extend(
            resource_cls(id=row[0], description=row[1] if row[1] else None)
            for row in reader
        )
    tasks = [deploy_datatype(client, resource) for resource in resources]
    return await asyncio.gather(*tasks)


async def deploy_datatype(
    client: Tenant,
    resource: _DataType,
) -> _DataType:
    """Deploy DataType."""
    resource_cls: type[_DataType] = resource.__class__
    LOGGER.debug('Deploy %s: %s', resource_cls.__name__, resource)

    try:
        created: _DataType = await retry(
            client.create,
            resource,
            exceptions=SAPConnectionError,
        )
        LOGGER.info('%s created: %s', resource_cls.__name__, created)
    except SAPAlreadyExistsError:  # DataType exists, update instead
        updated: _DataType = await retry(
            client.update,
            resource,
            exceptions=SAPConnectionError,
        )
        LOGGER.info('%s updated: %s', resource_cls.__name__, updated)
        return updated

    return created


async def deploy_xml(
    client: Tenant,
    file: Path,
) -> model.Pipeline:
    """Deploy XML data."""
    LOGGER.info('Deploy XML data: %s', file)

    job: model.XMLImport = model.XMLImport(
        xml_file_name=file.name,
        xml_file_content=file.read_text('UTF-8'),
        update_existing_objects=True,
    )
    result: model.Pipeline = await retry(
        client.run_pipeline,
        job,
        exceptions=SAPConnectionError,
    )
    while result.state != PipelineState.Done:
        await asyncio.sleep(2)
        result = await retry(
            client.read,
            result,
            exceptions=SAPConnectionError,
        )

    if result.status != PipelineStatus.Successful:
        LOGGER.error('XML Import failed (errors: %s)!', result.num_errors)
    else:
        LOGGER.info('XML data imported: %s', file)
    return result
