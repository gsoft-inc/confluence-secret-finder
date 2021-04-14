from abc import ABC, abstractmethod
from typing import List


class BasePlugin(ABC):
    @abstractmethod
    def find_secrets(self, lines: List[str]):
        return []
