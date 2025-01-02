"""User."""

from datetime import datetime
from typing import ClassVar, Literal

from pydantic import Field

from ._base import GCPResource


class User(GCPResource):
    """User."""

    attr_endpoint: ClassVar[str] = '/v2/users'
    attr_seq: ClassVar[str] = 'user_seq'
    user_seq: str | None = None
    id: str
    user_name: str | None = None
    description: str | None = None
    email: str | None = None
    read_only_business_unit_list: list[dict[Literal['name'], str]] | None = None
    full_access_business_unit_list: list[dict[Literal['name'], str]] | None = None
    preferred_language: str | None = None
    last_login: datetime | None = None
    created_by: str | None = Field(None, exclude=True, repr=False)
    create_date: datetime | None = Field(None, exclude=True, repr=False)
    modified_by: str | None = Field(None, exclude=True, repr=False)
