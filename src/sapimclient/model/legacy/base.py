"""Pydantic models for Python SAP Incentive Management Client (Oracle and HANA Tenants).

These classes are generally not used directly but can be usefull
for type checking and type hints. Used to inherrit function on
all other models.
"""
# pylint: disable=duplicate-code

import logging
from importlib import import_module
from types import ModuleType
from typing import Any, ClassVar

from pydantic import field_serializer, field_validator

from sapimclient.model.base import Expandable, Resource

LOGGER = logging.getLogger(__name__)


class LegacyResource(Resource):
    """Base class for Oracle and HANA resources."""

    attr_endpoint_prefix: ClassVar[str] = '/api'


class Reference(Expandable):
    """Expanded reference to a resource.

    Parameters:
        key (str): System unique identifier for the referred resource.
        display_name (str): Name of the referred resource.
        object_type (type[model.Resource]): Class of the referred resource.
        key_string (str): Seems to always be the same as ``key``.
        logical_keys (dict[str, Any]): Some key
            attributes of the referred resource.

    TODO: Fix model_json error on object_type.
    """

    key: str
    display_name: str
    object_type: type[LegacyResource]
    key_string: str | None = None
    logical_keys: dict[str, Any] | None = None

    @field_validator('object_type', mode='before')
    @classmethod
    def convert_object_type(cls, object_type: str) -> type[LegacyResource]:
        """Convert object_type to class."""
        module: ModuleType = import_module('sapimclient.model.legacy')
        try:
            return getattr(module, object_type)
        except AttributeError as err:
            msg = f'Could not find LegacyResource: {object_type}'
            raise ValueError(msg) from err

    @field_serializer('object_type', when_used='json')
    @staticmethod
    def serialize_object_type(object_type: type[LegacyResource]) -> str:
        """Serialize object_type to string."""
        return object_type.__name__

    def __str__(self) -> str:
        """Return key value."""
        return self.key
