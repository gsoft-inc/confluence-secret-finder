from abc import ABC, abstractmethod


class BasePlugin(ABC):
    @abstractmethod
    def find_secrets(self, line: str):
        return []
