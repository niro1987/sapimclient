"""Test for SAP Incentive Management Helpers."""

from collections.abc import AsyncGenerator
from datetime import date, datetime

import pytest

from sapimclient import helpers


def test_logical() -> None:
    """Test LogicalOperator.

    string, int, date, datetime, bool
    """

    class Spamm(helpers.LogicalOperator):
        """Spamm Logical Operator."""

        _operator: str = '=='

    assert str(Spamm('spamm', 'eggs')) == "spamm == 'eggs'"
    assert str(Spamm('int', 1)) == "int == '1 integer'"
    assert str(Spamm('int', -1)) == "int == '-1 integer'"
    assert str(Spamm('date', date(2023, 1, 1))) == 'date == 2023-01-01'
    assert (
        str(Spamm('datetime', datetime(2023, 1, 1, 12, 0, 0)))
        == 'datetime == 2023-01-01T12:00:00'
    )
    assert str(Spamm('bool', True)) == 'bool == true'  # noqa: FBT003
    assert str(Spamm('bool', False)) == 'bool == false'  # noqa: FBT003


def test_boolean() -> None:
    """Test BooleanOperator.

    single, many, complex, error, empty
    """

    class Spamm(helpers.LogicalOperator):
        """Spamm Logical Operator."""

        _operator: str = 'needs'

    # single
    assert str(helpers.And(Spamm('spam', 'eggs'))) == "spam needs 'eggs'"
    # many
    assert (
        str(helpers.And(Spamm('eggs', 'bacon'), Spamm('bacon', 'eggs')))
        == "(eggs needs 'bacon' and bacon needs 'eggs')"
    )
    assert (
        str(helpers.Or(Spamm('spam', 'eggs'), Spamm('spam', 'bacon')))
        == "(spam needs 'eggs' or spam needs 'bacon')"
    )
    # complex
    assert (
        str(
            helpers.And(
                Spamm('spam', 'eggs'),
                helpers.Or(Spamm('eggs', 'bacon'), Spamm('bacon', 'eggs')),
            ),
        )
        == "(spam needs 'eggs' and (eggs needs 'bacon' or bacon needs 'eggs'))"
    )

    # error
    with pytest.raises(ValueError) as err:
        helpers.And(Spamm('spam', 'eggs'), 'bacon')
    assert 'conditions must be instance' in str(err.value)

    # empty
    assert str(helpers.And()) == ''


async def test_async_limited_generator_stops_at_limit() -> None:
    """Test AsyncLimitedGenerator stops yielding at limit."""

    async def sample_generator() -> AsyncGenerator[int, None]:
        for i in range(10):
            yield i

    limit = 5
    generator = helpers.AsyncLimitedGenerator(sample_generator(), limit)

    result = [item async for item in generator]

    assert len(result) == limit
    assert result == list(range(limit))


async def test_async_limited_generator_handles_limit_greater_than_items() -> None:
    """Test AsyncLimitedGenerator handles limit greater than number of items."""

    async def sample_generator() -> AsyncGenerator[int, None]:
        for i in range(3):
            yield i

    limit = 5
    generator = helpers.AsyncLimitedGenerator(sample_generator(), limit)

    result = [item async for item in generator]

    assert len(result) == 3
    assert result == [0, 1, 2]


async def test_retry_max_attempts() -> None:
    """Test retry function retries exactly max_attempts times on exception."""
    call_count = 0

    async def failing_function() -> None:
        nonlocal call_count
        call_count += 1
        raise ValueError

    max_attempts = 3
    with pytest.raises(ValueError):
        await helpers.retry(
            failing_function,
            exceptions=ValueError,
            max_attempts=max_attempts,
        )

    assert call_count == max_attempts


async def test_retry_raises_last_exception() -> None:
    """Test retry function raises the last exception when all attempts fail."""
    call_count = 0

    async def failing_function() -> None:
        nonlocal call_count
        call_count += 1
        msg = f'Attempt {call_count}'
        raise ValueError(msg)

    max_attempts = 3
    with pytest.raises(ValueError, match='Attempt 3'):
        await helpers.retry(
            failing_function,
            exceptions=ValueError,
            max_attempts=max_attempts,
        )

    assert call_count == max_attempts


async def test_retry_returns_immediately_on_success() -> None:
    """Test retry function returns immediately if the first attempt succeeds."""
    call_count = 0

    async def successful_function() -> str:
        nonlocal call_count
        call_count += 1
        return 'Success'

    result = await helpers.retry(
        successful_function,
        exceptions=ValueError,
        max_attempts=3,
    )

    assert result == 'Success'
    assert call_count == 1


async def test_retry_handles_multiple_exception_types() -> None:
    """Test retry function handles multiple exception types specified as a tuple."""
    call_count = 0

    async def failing_function() -> None:
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            raise ValueError
        if call_count == 2:
            raise TypeError
        return 'Success'

    result = await helpers.retry(
        failing_function,
        exceptions=(ValueError, TypeError),
        max_attempts=3,
    )

    assert result == 'Success'
    assert call_count == 3


async def test_retry_raises_exception_if_exception_type_not_specified() -> None:
    """Test retry function raises exception if exception type is not specified."""
    call_count = 0

    async def failing_function() -> None:
        nonlocal call_count
        call_count += 1
        raise ValueError

    with pytest.raises(ValueError):
        await helpers.retry(
            failing_function,
            exceptions=TypeError,  # Specify a different exception type
            max_attempts=3,
        )

    assert call_count == 1  # Function should only be called once


async def test_retry_returns_none_if_max_attempts_below_one() -> None:
    """Test retry function returns None if max_attempts < 1."""
    call_count = 0

    async def successful_function() -> str:
        nonlocal call_count
        call_count += 1
        return 'Success'

    # max_attempts = 0
    result = await helpers.retry(
        successful_function,
        exceptions=ValueError,
        max_attempts=0,
    )

    assert result is None
    assert call_count == 0

    # max_attempts < 0
    result = await helpers.retry(
        successful_function,
        exceptions=ValueError,
        max_attempts=-1,
    )

    assert result is None
    assert call_count == 0
