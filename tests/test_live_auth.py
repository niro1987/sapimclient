"""Tests for auth module."""

import logging
import os

import pytest
from dotenv import load_dotenv

from sapimclient.auth import BasicAuthenticator, Token

LOGGER = logging.getLogger(__name__)

pytest.skip('Runs on live tenant', allow_module_level=True)


async def test_basic_auth() -> None:
    """Test BasicAuthenticator."""
    load_dotenv()

    tenant = os.environ['SAP_TENANT']
    username = os.environ['SAP_USERNAME']
    password = os.environ['SAP_PASSWORD']

    auth = BasicAuthenticator(username, password)
    header = await auth.get_auth(tenant)
    LOGGER.info('Auth Header: %s', header)
    assert header

    auth._token = Token(
        token_type=auth._token.token_type,
        access_token=auth._token.access_token,
        refresh_token=auth._token.refresh_token,
    )
    assert auth._token.is_expired
    header = await auth.get_auth(tenant)
    assert header
    assert not auth._token.is_expired
