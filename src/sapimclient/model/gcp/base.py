"""Pydantic models for Python SAP Incentive Management Client (GCP Tenants).

These classes are generally not used directly but can be usefull
for type checking and type hints. Used to inherrit function on
all other models.
"""
# pylint: disable=duplicate-code

from typing import ClassVar

from sapimclient.model.base import Expandable, Resource


class GCPResource(Resource):
    """Base class for GCP resources."""

    attr_endpoint_prefix: ClassVar[str] = '/mtsvc/tcmp/rest'


class Reference(Expandable):
    """Reference model for GCP resources."""
