"""Authentication for SAP Incentive Management client."""

import asyncio
import logging
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from urllib.parse import urlparse

from aiohttp import (
    BasicAuth,
    ClientError,
    ClientResponseError,
    ClientSession,
)

from sapimclient import exceptions
from sapimclient.const import (
    GCP_HOSTNAME,
    LEGACY_HOSTNAME,
    REQUEST_TIMEOUT,
    VERIFY_SSL,
)

LOGGER: logging.Logger = logging.getLogger(__name__)

LEGACY_TOKEN_ENDPOINT: str = '/CallidusPortal/services/v2/Tokenization/access_token'
LEGACY_REFRESH_ENDPOINT: str = LEGACY_TOKEN_ENDPOINT + '/refresh'
GCP_RESOLVE_IAS: str = '/iamsvc/CallidusPortal/startPortal.do'
GCP_TOKEN_ENDPOINT: str = '/oauth2/token'


@dataclass(frozen=True)
class Token:
    """Token data."""

    token_type: str
    access_token: str
    refresh_token: str | None = None
    expires_in: int = 0
    obtained_at: float = field(default_factory=time.time)

    @property
    def is_expired(self) -> bool:
        """Return True if token is expired."""
        return self.obtained_at + self.expires_in - 60 < time.time()

    @property
    def as_header(self) -> dict[str, str]:
        """Return token as header."""
        return {'Authorization': f'{self.token_type} {self.access_token}'}


@dataclass
class Authenticator(ABC):
    """Abstract class for authentication."""

    _token: Token | None = field(default=None, init=False, repr=False)

    @abstractmethod
    async def get_auth(self, tenant: str) -> dict[str, str]:
        """Return authentication context."""


@dataclass
class BasicAuthenticator(Authenticator):
    """Basic authentication for SAP Incentive Management client."""

    username: str
    password: str = field(repr=False)

    async def get_auth(self, tenant: str) -> dict[str, str]:
        """Return authentication context."""
        if not self._token:
            self._token = await self.get_token(tenant)
        elif self._token.is_expired:
            self._token = await self.refresh_token(tenant)
        return self._token.as_header

    async def get_token(self, tenant: str) -> Token:
        """Get auth-token."""
        token_url = LEGACY_HOSTNAME.format(tenant=tenant) + LEGACY_TOKEN_ENDPOINT
        async with ClientSession() as session:
            try:
                async with asyncio.timeout(REQUEST_TIMEOUT):
                    response = await session.post(
                        token_url,
                        auth=BasicAuth(self.username, self.password),
                        ssl=VERIFY_SSL,
                        json={'username': self.username, 'password': self.password},
                    )
                    response.raise_for_status()
                    data = await response.json()
            except TimeoutError as err:
                msg = 'Timeout while connecting'
                LOGGER.exception(msg)
                raise exceptions.SAPConnectionError(msg) from err
            except ClientResponseError as err:
                msg = f'Invalid User name or Password for {self.username}'
                LOGGER.exception(msg)
                raise exceptions.SAPNotAuthorizedError(msg) from err
            except ClientError as err:
                msg = f'Failed to obtain token: {err}'
                LOGGER.exception(msg)
                raise exceptions.SAPConnectionError(msg) from err

        token = Token(
            token_type=data['token_type'],
            access_token=data['access_token'],
            refresh_token=data['refresh_token'],
            expires_in=int(data['expires_in']),
        )
        LOGGER.debug('Successfully obtained authorization token')
        return token

    async def refresh_token(self, tenant: str) -> Token:
        """Get auth-token."""
        if not (token := self._token) or token.refresh_token is None:
            return await self.get_token(tenant)

        token_url = LEGACY_HOSTNAME.format(tenant=tenant) + LEGACY_REFRESH_ENDPOINT
        async with ClientSession() as session:
            try:
                async with asyncio.timeout(REQUEST_TIMEOUT):
                    response = await session.post(
                        token_url,
                        headers=token.as_header,
                        ssl=VERIFY_SSL,
                        json={'refresh_token': self._token.refresh_token},
                    )
                    response.raise_for_status()
                    data = await response.json()
            except TimeoutError as err:
                msg = 'Timeout while connecting'
                LOGGER.exception(msg)
                raise exceptions.SAPConnectionError(msg) from err
            except ClientResponseError as err:
                msg = f'Invalid User name or Password for {self.username}'
                LOGGER.exception(msg)
                raise exceptions.SAPNotAuthorizedError(msg) from err
            except ClientError as err:
                msg = f'Failed to obtain token: {err}'
                LOGGER.exception(msg)
                raise exceptions.SAPConnectionError(msg) from err

        token = Token(
            token_type=data['token_type'],
            access_token=data['access_token'],
            refresh_token=data['refresh_token'],
            expires_in=int(data['expires_in']),
        )
        LOGGER.debug('Successfully refreshed authorization token')
        return token


@dataclass
class OAuth2Authenticator(Authenticator):
    """OAuth authentication for SAP Incentive Management client."""

    client_id: str
    client_secret: str = field(repr=False)
    _ias_host: str | None = None

    async def get_auth(self, tenant: str) -> dict[str, str]:
        """Return authentication context."""
        if not self._token or self._token.is_expired:
            self._token = await self.get_token(tenant)
        return self._token.as_header

    async def get_token(self, tenant: str) -> Token:
        """Get OAuth token."""
        ias_host = await self.resolve_ias_url(tenant)
        token_url = ias_host + GCP_TOKEN_ENDPOINT
        async with ClientSession() as session:
            try:
                async with asyncio.timeout(REQUEST_TIMEOUT):
                    response = await session.post(
                        url=token_url,
                        auth=BasicAuth(self.client_id, self.client_secret),
                        data={
                            'grant_type': 'client_credentials',
                            'client_id': self.client_id,
                        },
                        ssl=VERIFY_SSL,
                    )
                    response.raise_for_status()
                    data = await response.json()
            except TimeoutError as err:
                msg = 'Timeout while connecting'
                LOGGER.exception(msg)
                raise exceptions.SAPConnectionError(msg) from err
            except ClientResponseError as err:
                msg = f'Invalid credentials for {ias_host}'
                LOGGER.exception(msg)
                raise exceptions.SAPNotAuthorizedError(msg) from err
            except ClientError as err:
                msg = f'Failed to obtain token: {err}'
                LOGGER.exception(msg)
                raise exceptions.SAPConnectionError(msg) from err

        token = Token(
            token_type=data['token_type'],
            access_token=data['access_token'],
            expires_in=int(data['expires_in']),
        )
        LOGGER.debug('Successfully obtained authorization token')
        return token

    async def resolve_ias_url(self, tenant: str) -> str:
        """Resolve the IAS host."""
        if self._ias_host:
            return self._ias_host

        resolve_url = GCP_HOSTNAME.format(tenant=tenant) + GCP_RESOLVE_IAS
        async with ClientSession() as session:
            try:
                async with asyncio.timeout(REQUEST_TIMEOUT):
                    response = await session.get(
                        url=resolve_url,
                        ssl=VERIFY_SSL,
                        allow_redirects=False,
                    )
                    response.raise_for_status()
            except TimeoutError as err:
                msg = 'Timeout while connecting'
                LOGGER.exception(msg)
                raise exceptions.SAPConnectionError(msg) from err
            except ClientError as err:
                msg = f'Failed to obtain token: {err}'
                LOGGER.exception(msg)
                raise exceptions.SAPConnectionError(msg) from err

        if not (location := response.headers.get('Location')):
            raise exceptions.SAPResponseError('Location header not found.')

        url = urlparse(location)
        self._ias_host = f'{url.scheme}://{url.hostname}'
        LOGGER.debug('IAS Host: %s', self._ias_host)
        return self._ias_host
