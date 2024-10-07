# tests/test_date_iterators.py
from datetime import datetime

import pytest

from ripper.tools.date import (
    BaseDateIterator,
    DateCountIterator,
    DateRangeIterator,
    DateUntilCurrentIterator,
)


class IncompleteDateIterator(BaseDateIterator):
    def __init__(self, start_date: datetime):
        self.current_date = start_date

    def __iter__(self):
        return self


def test_base_date_iterator_not_implemented_error():
    iterator = IncompleteDateIterator(datetime(2023, 1, 1))
    with pytest.raises(
        NotImplementedError, match="Subclasses must implement __next__ method"
    ):
        next(iterator)


@pytest.mark.parametrize(
    "start_date, end_date, expected_dates",
    [
        (
            datetime(2023, 1, 1),
            datetime(2023, 1, 3),
            [(2023, 1, 1), (2023, 1, 2), (2023, 1, 3)],
        ),
        (
            datetime(2023, 12, 30),
            datetime(2024, 1, 1),
            [(2023, 12, 30), (2023, 12, 31), (2024, 1, 1)],
        ),
        (datetime(2023, 2, 28), datetime(2023, 3, 1), [(2023, 2, 28), (2023, 3, 1)]),
        (datetime(2023, 1, 1), datetime(2023, 1, 1), [(2023, 1, 1)]),
        (
            datetime(2023, 1, 1),
            datetime(2022, 12, 31),
            [],
        ),  # end_date before start_date
    ],
)
def test_date_range_iterator(start_date, end_date, expected_dates):
    iterator = DateRangeIterator(start_date, end_date)
    result = [date_tuple for date_tuple in iterator]
    assert result == expected_dates


@pytest.mark.parametrize(
    "start_date, days, expected_dates",
    [
        (datetime(2023, 1, 1), 3, [(2023, 1, 1), (2023, 1, 2), (2023, 1, 3)]),
        (datetime(2023, 12, 30), 3, [(2023, 12, 30), (2023, 12, 31), (2024, 1, 1)]),
        (datetime(2023, 2, 28), 2, [(2023, 2, 28), (2023, 3, 1)]),
        (datetime(2023, 1, 1), 1, [(2023, 1, 1)]),
        (datetime(2023, 1, 1), 0, []),  # zero days
    ],
)
def test_date_count_iterator(start_date, days, expected_dates):
    iterator = DateCountIterator(start_date, days)
    result = [date_tuple for date_tuple in iterator]
    assert result == expected_dates


@pytest.mark.parametrize(
    "start_date, current_date, expected_dates",
    [
        (
            datetime(2023, 1, 1),
            datetime(2023, 1, 3),
            [(2023, 1, 1), (2023, 1, 2), (2023, 1, 3)],
        ),
        (
            datetime(2023, 12, 30),
            datetime(2024, 1, 1),
            [(2023, 12, 30), (2023, 12, 31), (2024, 1, 1)],
        ),
    ],
)
def test_date_until_current_iterator(start_date, current_date, expected_dates):
    current_date_func = lambda: current_date
    iterator = DateUntilCurrentIterator(start_date, current_date_func)
    result = [date_tuple for date_tuple in iterator]
    assert result == expected_dates
