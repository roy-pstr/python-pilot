
import typing
import pydantic

from pypilot.agent import prompt
from pypilot import oai_utils

class AgentBase(pydantic.BaseModel):
    provider: str
    model: str
    max_tokens: int = 256
    temperature: float = 0.7
    prompt: typing.Optional[prompt.Prompt]
    output_parser: typing.Optional[typing.Callable] = None
    api_key: typing.Optional[str] = None
    model_config = pydantic.ConfigDict(arbitrary_types_allowed=True)
    def get_token_count(self, **kwargs):
        return self.prompt.get_token_count(**kwargs)
    
    def generate(self, api_key: typing.Optional[str] = None, **kwargs) -> str:
        response = oai_utils.make_chat_completion(
            messages=self.prompt.format(**kwargs),
            provider=self.provider,
            model=self.model,
            api_key=self.api_key or api_key,
            max_tokens=self.max_tokens,
            temperature=self.temperature
        )
        answer = response.get("answer").get("content")
        if self.output_parser is not None:
            parsed_answer = self.output_parser(answer)
            return parsed_answer
        return answer

    def stream(self, api_key: typing.Optional[str] = None, **kwargs) -> str:
        return oai_utils.stream_chat_completion(
            messages=self.prompt.format(**kwargs),
            provider=self.provider,
            model=self.model,
            api_key=self.api_key or api_key,
            max_tokens=self.max_tokens,
            temperature=self.temperature
        )