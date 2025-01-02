"""Tests for auth module."""

import logging
import time

import pytest
from aiohttp import ClientError
from aioresponses import aioresponses

from sapimclient import auth, const, exceptions

LOGGER = logging.getLogger(__name__)


class DummyAuth(auth.Authenticator):
    """Dummy Authenticator."""

    async def get_auth(self, tenant: str) -> dict[str, str]:
        """Return Token Header."""
        self._token = auth.Token('spam', tenant, 60)
        return self._token.as_header


class TestToken:
    """Tests for Token."""

    token = auth.Token('spam', 'eggs', 60)

    def test_is_expired(self) -> None:
        """Token should expire after 'expires_in' seconds."""
        assert not self.token.is_expired

        expired_token = auth.Token('spam', 'eggs', 1, created_at=time.time() - 2)
        assert expired_token.is_expired

    def test_as_header(self) -> None:
        """Token should return valid http authorization header."""
        as_header = self.token.as_header
        assert as_header == {'Authorization': 'spam eggs'}


class TestAuthenticator:
    """Tests for Authenticator."""

    tenant: str = 'eggs'
    authenticator: auth.Authenticator = DummyAuth()

    async def test_get_auth(self) -> dict[str, str]:
        """Test that get_auth returns a valid http Authorization header."""
        auth_header = await self.authenticator.get_auth(self.tenant)

        assert isinstance(auth_header, dict)
        assert 'Authorization' in auth_header
        assert isinstance(auth_header['Authorization'], str)

        return auth_header


class TestBasicAuthenticator(TestAuthenticator):
    """Test BasicAuthenticator."""

    authenticator: auth.BasicAuthenticator

    def setup_method(self) -> None:
        """Reset the authenticator before each test."""
        self.authenticator = auth.BasicAuthenticator('spam', 'eggs')

    async def test_get_auth(self, mocked: aioresponses) -> None:
        """Test that get_auth return a valid http Authorization header."""
        url = (
            const.LEGACY_HOSTNAME.format(tenant=self.tenant)
            + auth.LEGACY_TOKEN_ENDPOINT
        )
        mocked.post(  # get_token
            url=url,
            status=200,
            payload={
                'token_type': 'Bearer',
                'access_token': 'spam',
                'refresh_token': 'eggs',
                'expires_in': '-1',
            },
        )
        auth_header = await super().test_get_auth()
        assert len(mocked.requests) == 1
        assert auth_header == {'Authorization': 'Bearer spam'}
        assert self.authenticator._token.is_expired

        url = (
            const.LEGACY_HOSTNAME.format(tenant=self.tenant)
            + auth.LEGACY_REFRESH_ENDPOINT
        )
        mocked.post(  # refresh_token
            url=url,
            status=200,
            payload={
                'token_type': 'Bearer',
                'access_token': 'eggs',
                'refresh_token': 'bacon',
                'expires_in': '60',
            },
        )
        auth_header = await super().test_get_auth()
        assert len(mocked.requests) == 2
        assert auth_header == {'Authorization': 'Bearer eggs'}
        assert not self.authenticator._token.is_expired

        # Since token is not expired, we should not refresh token
        auth_header = await super().test_get_auth()
        assert len(mocked.requests) == 2  # no additional requests are made
        assert auth_header == {'Authorization': 'Bearer eggs'}

    async def test_get_auth_not_authorized(self, mocked: aioresponses) -> None:
        """Test not authorized raises SAPNotAuthorizedError."""
        url = (
            const.LEGACY_HOSTNAME.format(tenant=self.tenant)
            + auth.LEGACY_TOKEN_ENDPOINT
        )
        mocked.post(url=url, status=400)
        with pytest.raises(exceptions.SAPNotAuthorizedError):
            await self.authenticator.get_auth(tenant=self.tenant)

    async def test_get_auth_timeout(self, mocked: aioresponses) -> None:
        """Test timeout raises SAPConnectionError."""
        url = (
            const.LEGACY_HOSTNAME.format(tenant=self.tenant)
            + auth.LEGACY_TOKEN_ENDPOINT
        )
        mocked.post(url=url, exception=TimeoutError())
        with pytest.raises(exceptions.SAPConnectionError) as err:
            await self.authenticator.get_auth(tenant=self.tenant)
        assert 'Timeout while connecting' in str(err)

    async def test_get_auth_bad_request(self, mocked: aioresponses) -> None:
        """Test bad request raises SAPConnectionError."""
        url = (
            const.LEGACY_HOSTNAME.format(tenant=self.tenant)
            + auth.LEGACY_TOKEN_ENDPOINT
        )
        mocked.post(url=url, exception=ClientError())
        with pytest.raises(exceptions.SAPConnectionError) as err:
            await self.authenticator.get_auth(tenant=self.tenant)
        assert 'Failed to obtain token' in str(err)

    async def test_refresh_token_no_token(self, mocked: aioresponses) -> None:
        """Test refresh without refresh token."""
        url = (
            const.LEGACY_HOSTNAME.format(tenant=self.tenant)
            + auth.LEGACY_TOKEN_ENDPOINT
        )
        mocked.post(  # get_token
            url=url,
            status=200,
            payload={
                'token_type': 'Bearer',
                'access_token': 'spam',
                'refresh_token': None,
                'expires_in': '-1',
            },
            repeat=True,
        )
        await super().test_get_auth()
        mocked.assert_called_once()
        assert self.authenticator._token.refresh_token is None

        mocked.requests.clear()
        await super().test_get_auth()
        mocked.assert_called_once()

    async def test_refresh_token_not_authorized(self, mocked: aioresponses) -> None:
        """Test not authorized raises SAPNotAuthorizedError."""
        url = (
            const.LEGACY_HOSTNAME.format(tenant=self.tenant)
            + auth.LEGACY_TOKEN_ENDPOINT
        )
        mocked.post(  # get_token
            url=url,
            status=200,
            payload={
                'token_type': 'Bearer',
                'access_token': 'spam',
                'refresh_token': 'eggs',
                'expires_in': '-1',
            },
        )
        await super().test_get_auth()

        url = (
            const.LEGACY_HOSTNAME.format(tenant=self.tenant)
            + auth.LEGACY_REFRESH_ENDPOINT
        )
        mocked.post(url=url, status=400)
        with pytest.raises(exceptions.SAPNotAuthorizedError):
            await self.authenticator.get_auth(tenant=self.tenant)

    async def test_refresh_token_timeout(self, mocked: aioresponses) -> None:
        """Test not authorized raises SAPNotAuthorizedError."""
        url = (
            const.LEGACY_HOSTNAME.format(tenant=self.tenant)
            + auth.LEGACY_TOKEN_ENDPOINT
        )
        mocked.post(  # get_token
            url=url,
            status=200,
            payload={
                'token_type': 'Bearer',
                'access_token': 'spam',
                'refresh_token': 'eggs',
                'expires_in': '-1',
            },
        )
        await super().test_get_auth()

        url = (
            const.LEGACY_HOSTNAME.format(tenant=self.tenant)
            + auth.LEGACY_REFRESH_ENDPOINT
        )
        mocked.post(url=url, exception=TimeoutError())
        with pytest.raises(exceptions.SAPConnectionError) as err:
            await self.authenticator.get_auth(tenant=self.tenant)
        assert 'Timeout while connecting' in str(err)

    async def test_refresh_token_bad_request(self, mocked: aioresponses) -> None:
        """Test not authorized raises SAPNotAuthorizedError."""
        url = (
            const.LEGACY_HOSTNAME.format(tenant=self.tenant)
            + auth.LEGACY_TOKEN_ENDPOINT
        )
        mocked.post(  # get_token
            url=url,
            status=200,
            payload={
                'token_type': 'Bearer',
                'access_token': 'spam',
                'refresh_token': 'eggs',
                'expires_in': '-1',
            },
        )
        await super().test_get_auth()

        url = (
            const.LEGACY_HOSTNAME.format(tenant=self.tenant)
            + auth.LEGACY_REFRESH_ENDPOINT
        )
        mocked.post(url=url, exception=ClientError())
        with pytest.raises(exceptions.SAPConnectionError) as err:
            await self.authenticator.get_auth(tenant=self.tenant)
        assert 'Failed to obtain token' in str(err)


class TestOAuth2Authenticator(TestAuthenticator):
    """Test OAuth2Authenticator."""

    authenticator: auth.OAuth2Authenticator

    def setup_method(self) -> None:
        """Reset the authenticator before each test."""
        self.authenticator = auth.OAuth2Authenticator('spam', 'eggs')

    async def test_get_auth(self, mocked: aioresponses) -> None:
        """Test that get_auth return a valid http Authorization header."""
        mocked.get(  # resolve_ias_url
            url=const.GCP_HOSTNAME.format(tenant=self.tenant) + auth.GCP_RESOLVE_IAS,
            status=302,
            headers={'Location': 'https://spam.eggs.com/bacon'},
        )
        url = 'https://spam.eggs.com' + auth.GCP_TOKEN_ENDPOINT
        mocked.post(  # get_token
            url=url,
            status=200,
            payload={
                'token_type': 'Bearer',
                'access_token': 'spam',
                'expires_in': '-1',
            },
        )
        auth_header = await super().test_get_auth()
        assert len(mocked.requests) == 2
        assert auth_header == {'Authorization': 'Bearer spam'}
        assert self.authenticator._token.is_expired

        mocked.requests.clear()
        mocked.post(  # get_token since it is expired
            url=url,
            status=200,
            payload={
                'token_type': 'Bearer',
                'access_token': 'eggs',
                'expires_in': '60',
            },
        )
        auth_header = await super().test_get_auth()
        assert len(mocked.requests) == 1  # ias_host is already resolved
        assert auth_header == {'Authorization': 'Bearer eggs'}
        assert not self.authenticator._token.is_expired

        # Since token is not expired, we should not refresh token
        auth_header = await super().test_get_auth()
        assert len(mocked.requests) == 1  # no additional requests are made
        assert auth_header == {'Authorization': 'Bearer eggs'}

    async def test_get_auth_not_authorized(self, mocked: aioresponses) -> None:
        """Test not authorized raises SAPNotAuthorizedError."""
        mocked.get(  # resolve_ias_url
            url=const.GCP_HOSTNAME.format(tenant=self.tenant) + auth.GCP_RESOLVE_IAS,
            status=302,
            headers={'Location': 'https://spam.eggs.com/bacon'},
        )
        url = 'https://spam.eggs.com' + auth.GCP_TOKEN_ENDPOINT
        mocked.post(url=url, status=400)  # get_token
        with pytest.raises(exceptions.SAPNotAuthorizedError):
            await self.authenticator.get_auth(tenant=self.tenant)

    async def test_get_auth_timeout(self, mocked: aioresponses) -> None:
        """Test timeout raises SAPConnectionError."""
        mocked.get(  # resolve_ias_url
            url=const.GCP_HOSTNAME.format(tenant=self.tenant) + auth.GCP_RESOLVE_IAS,
            status=302,
            headers={'Location': 'https://spam.eggs.com/bacon'},
        )
        url = 'https://spam.eggs.com' + auth.GCP_TOKEN_ENDPOINT
        mocked.post(url=url, exception=TimeoutError())
        with pytest.raises(exceptions.SAPConnectionError) as err:
            await self.authenticator.get_auth(tenant=self.tenant)
        assert 'Timeout while connecting' in str(err)

    async def test_get_auth_bad_request(self, mocked: aioresponses) -> None:
        """Test bad request raises SAPConnectionError."""
        mocked.get(  # resolve_ias_url
            url=const.GCP_HOSTNAME.format(tenant=self.tenant) + auth.GCP_RESOLVE_IAS,
            status=302,
            headers={'Location': 'https://spam.eggs.com/bacon'},
        )
        url = 'https://spam.eggs.com' + auth.GCP_TOKEN_ENDPOINT
        mocked.post(url=url, exception=ClientError())
        with pytest.raises(exceptions.SAPConnectionError) as err:
            await self.authenticator.get_auth(tenant=self.tenant)
        assert 'Failed to obtain token' in str(err)

    async def test_resolve_ias_timeout(self, mocked: aioresponses) -> None:
        """Test timeout raises SAPConnectionError."""
        mocked.get(  # resolve_ias_url
            url=const.GCP_HOSTNAME.format(tenant=self.tenant) + auth.GCP_RESOLVE_IAS,
            exception=TimeoutError(),
        )
        with pytest.raises(exceptions.SAPConnectionError) as err:
            await self.authenticator.get_auth(tenant=self.tenant)
        assert 'Timeout while connecting' in str(err)

    async def test_resolve_ias_bad_request(self, mocked: aioresponses) -> None:
        """Test bad request raises SAPConnectionError."""
        mocked.get(  # resolve_ias_url
            url=const.GCP_HOSTNAME.format(tenant=self.tenant) + auth.GCP_RESOLVE_IAS,
            exception=ClientError(),
        )
        with pytest.raises(exceptions.SAPConnectionError) as err:
            await self.authenticator.get_auth(tenant=self.tenant)
        assert 'Failed to resolve ias host' in str(err)

    async def test_resolve_ias_no_header(self, mocked: aioresponses) -> None:
        """Test bad request raises SAPConnectionError."""
        mocked.get(  # resolve_ias_url
            url=const.GCP_HOSTNAME.format(tenant=self.tenant) + auth.GCP_RESOLVE_IAS,
            status=200,
        )
        with pytest.raises(exceptions.SAPConnectionError) as err:
            await self.authenticator.get_auth(tenant=self.tenant)
        assert 'Location header not found' in str(err)
