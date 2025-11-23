from abc import ABC, abstractmethod
from typing import Any, Dict

class Agent(ABC):
    def __init__(self, llm):
        self.llm = llm

    @abstractmethod
    async def run(self, **kwargs) -> Dict[str, Any]:
        pass
