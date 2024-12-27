"""Temporary test file for development purposes."""

import logging
import os

import pytest
from dotenv import load_dotenv

from sapimclient import BasicAuthenticator, GCPTenant, LegacyTenant, OAuth2Authenticator
from sapimclient.model import gcp, legacy

LOGGER = logging.getLogger(__name__)

pytest.skip('Runs on live tenant', allow_module_level=True)


async def test_oracle_client() -> None:
    """Test Oracle Client."""
    load_dotenv()

    async with LegacyTenant(
        tenant=os.environ['SAP_TENANT'],
        authenticator=BasicAuthenticator(
            username=os.environ['SAP_USERNAME'],
            password=os.environ['SAP_PASSWORD'],
        ),
    ) as tenant:
        LOGGER.info('Tenant: %s', tenant)
        first = await tenant.read_first(legacy.RateTable)
        LOGGER.info('First: %s', first)


async def test_gcp_client() -> None:
    """Test GCP Client."""
    load_dotenv()

    async with GCPTenant(
        tenant=os.environ['GCP_TENANT'],
        authenticator=OAuth2Authenticator(
            client_id=os.environ['GCP_CLIENT_ID'],
            client_secret=os.environ['GCP_CLIENT_SECRET'],
        ),
    ) as tenant:
        LOGGER.info('Tenant: %s', tenant)
        item = await tenant.read_first(gcp.CreditType)
        LOGGER.info('First: %s', item)
