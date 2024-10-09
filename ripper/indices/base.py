from abc import ABC, abstractmethod
from typing import Generic, List, Tuple, TypeVar

from ripper.models.match import Match

T = TypeVar("T")


class BaseIndex(ABC, Generic[T]):
    @abstractmethod
    def calculate(self, matches: list[Match]) -> list[tuple[int, str, T]]:
        pass
