"""Test the resource interaction with the client."""
# pylint: disable=protected-access

import logging
from typing import Any, TypeVar

import pytest
from pydantic_core import ValidationError

from sapcommissions import CommissionsClient, model
from tests.conftest import AsyncLimitedGenerator, list_resource_cls

LOGGER = logging.getLogger(__name__)
T = TypeVar("T", bound=model._Resource)


@pytest.mark.parametrize(
    "resource_cls",
    list_resource_cls(),
)
async def test_list_resources(client: CommissionsClient, resource_cls: type[T]) -> None:
    """Test listing resources."""
    LOGGER.info("Testing list %s", resource_cls.__name__)

    extra: dict[str, set[Any]] = {}

    generator = client.read_all(resource_cls, page_size=100, raw=True)
    async for resource in AsyncLimitedGenerator(generator, 1_000):
        # LOGGER.info("Resource: %s", resource)
        try:
            instance: T = resource_cls(**resource)
        except ValidationError as exc:
            for err in exc.errors():
                LOGGER.error("%s(%s): %s", err["msg"], err["loc"][0], err["input"])
            raise
        assert isinstance(instance, resource_cls)

        if model_extra := instance.model_extra:
            for key, value in model_extra.items():
                if key not in ("etag",):
                    if key not in extra:
                        extra[key] = set()
                    try:
                        extra[key].add(value)
                    except TypeError:
                        extra[key].add(str(value))
    assert not extra, f"Extra keys: {extra}"
