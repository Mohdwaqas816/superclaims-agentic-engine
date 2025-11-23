from abc import ABC, abstractmethod

class LLMInterface(ABC):
    @abstractmethod
    async def call(self, prompt: str):
        """Call the model with prompt. Return either raw string or parsed dict."""
        raise NotImplementedError()

    def parse_json(self, raw: str):
        """Helper to parse simple JSON strings into dict (implementations may vary)."""
        import json
        return json.loads(raw)
