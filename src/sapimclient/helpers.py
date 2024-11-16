"""Helpers for Python SAP Incentive Management Client."""

import logging
from collections.abc import AsyncIterator, Callable
from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Any, TypeVar

LOGGER: logging.Logger = logging.getLogger(__name__)


@dataclass
class LogicalOperator:
    """Base class for Logical Operators.

    You cannot create a direct instance of LogicalOperator,
    use one of the subclasses instead.
    - Equals
    - NotEquals
    - GreaterThen
    - GreaterThenOrEqual
    - LesserThen
    - LesserThenOrEqual
    """

    _operator: str = field(init=False, repr=False)
    first: str
    second: str | int | date | datetime | bool

    def __str__(self) -> str:
        """Return a string representation of the object."""
        if isinstance(self.second, bool):
            second = str(self.second).lower()
        elif isinstance(self.second, int):
            second = f"'{self.second} integer'"
        elif isinstance(self.second, date | datetime):
            second = self.second.isoformat()
        else:  # str
            second = f"'{self.second}'"

        return f'{self.first} {self._operator} {second}'


class Equals(LogicalOperator):
    """Equal to.

    Supports wildcard operator '*', for example: `Equals('name', 'John *')`.
    Supports `null` operator, for example: `Equals('name', 'null')`.
    """

    _operator: str = 'eq'


class NotEquals(LogicalOperator):
    """Not equal to.

    Supports wildcard operator '*', for example: `Equals('name', 'John*')`.
    Supports `null` operator, for example: `NotEquals('name', 'null')`.
    """

    _operator: str = 'ne'


class GreaterThen(LogicalOperator):
    """Greater then."""

    _operator: str = 'gt'


class GreaterThenOrEqual(LogicalOperator):
    """Greater then or equals."""

    _operator: str = 'ge'


class LesserThen(LogicalOperator):
    """Lesser then."""

    _operator: str = 'lt'


class LesserThenOrEqual(LogicalOperator):
    """Lesser then or equals."""

    _operator: str = 'le'


@dataclass(init=False)
class BooleanOperator:
    """Base class for Boolean Operators.

    You cannot create a direct instance of LogicalOperator,
    use one of the subclasses instead.
    - And
    - Or
    """

    _operator: str = field(init=False, repr=False)

    def __init__(self, *conditions: 'LogicalOperator | BooleanOperator') -> None:
        """Initialize the BooleanExpression with conditions.

        Attributes:
        ----
            *conditions: Instances of LogicalOperator or BooleanOperator.

        """
        if not all(
            isinstance(m, LogicalOperator | BooleanOperator)
            and type(m) not in (LogicalOperator, BooleanOperator)
            for m in conditions
        ):
            msg = 'All conditions must be instance of Boolean- or LogicalOperator'
            raise ValueError(msg)
        self.conditions = conditions

    def __str__(self) -> str:
        """Return a string representation of the object."""
        if not self.conditions:
            return ''
        text: str = f' {self._operator} '.join(str(m) for m in self.conditions)
        return f'({text})' if len(self.conditions) > 1 else text


class And(BooleanOperator):
    """All conditions must be true."""

    _operator: str = 'and'


class Or(BooleanOperator):
    """Any condition must be true."""

    _operator: str = 'or'


T = TypeVar('T')


class AsyncLimitedGenerator:
    """Async generator to limit the number of yielded items."""

    def __init__(self, iterable: AsyncIterator[T], limit: int) -> None:
        """Initialize the async iterator."""
        self.iterable = iterable
        self.limit = limit

    def __aiter__(self) -> AsyncIterator[T]:
        """Return the async iterator."""
        return self

    async def __anext__(self) -> T:
        """Return the next item in the async iterator."""
        if self.limit == 0:
            raise StopAsyncIteration
        self.limit -= 1
        return await self.iterable.__anext__()


async def retry(
    coroutine_function: Callable,
    *args: Any,
    exceptions: type[BaseException] | tuple[type[BaseException], ...],
    max_attempts: int = 3,
    **kwargs: Any,
) -> Any:
    """Retry a coroutine function a specified number of times."""
    if not isinstance(exceptions, tuple):
        exceptions = (exceptions,)

    for attempt in range(max_attempts):
        try:
            return await coroutine_function(*args, **kwargs)
        except exceptions as err:
            LOGGER.debug('Failed attempt %s: %s', attempt + 1, err)
            if attempt >= max_attempts - 1:
                raise
    return None
