"""
This module contains date iterators that generate date tuples.
"""

from datetime import datetime, timedelta
from typing import Iterator, Tuple


class BaseDateIterator:
    """
    Base class for date iterators
    """

    def __iter__(self) -> Iterator[Tuple[int, int, int]]:
        """
        Return the iterator object
        :return:
        """
        return self

    def __next__(self) -> Tuple[int, int, int]:
        """
        Get the next date tuple
        :return:
        """
        raise NotImplementedError("Subclasses must implement __next__ method")


class DateRangeIterator(BaseDateIterator):
    """
    An iterator that generates date tuples from a start date to an end date
    """

    def __init__(self, start_date: datetime, end_date: datetime):
        """
        Constructor for the DateRangeIterator class

        :param start_date: The start date
        :param end_date: The end date
        """
        self.current_date = start_date
        self.end_date = end_date

    def __next__(self) -> Tuple[int, int, int]:
        if self.current_date > self.end_date:
            raise StopIteration
        date_tuple = (
            self.current_date.year,
            self.current_date.month,
            self.current_date.day,
        )
        self.current_date += timedelta(days=1)
        return date_tuple


class DateCountIterator(BaseDateIterator):
    def __init__(self, start_date: datetime, days: int):
        """
        Constructor for the DateCountIterator class

        :param start_date: The start date
        :param days: The number of days to iterate over
        """
        self.current_date = start_date
        self.end_date = start_date + timedelta(days=days - 1)

    def __next__(self) -> Tuple[int, int, int]:
        """
        Get the next date tuple

        :return:
        """
        if self.current_date > self.end_date:
            raise StopIteration

        date_tuple = (
            self.current_date.year,
            self.current_date.month,
            self.current_date.day,
        )
        self.current_date += timedelta(days=1)

        return date_tuple


class DateUntilCurrentIterator(BaseDateIterator):
    """
    An iterator that generates date tuples from a start date to the current date
    """

    def __init__(
        self, start_date: datetime, current_date_func: callable = datetime.now
    ):
        """
        Constructor for the DateUntilCurrentIterator class

        :param start_date: The start date
        """
        self.current_date = start_date
        self.end_date = current_date_func()

    def __next__(self) -> Tuple[int, int, int]:
        """
        Get the next date tuple

        :return: A date tuple
        """
        if self.current_date > self.end_date:
            raise StopIteration

        date_tuple = (
            self.current_date.year,
            self.current_date.month,
            self.current_date.day,
        )
        self.current_date += timedelta(days=1)

        return date_tuple
