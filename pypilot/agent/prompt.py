import typing
import pydantic

from pypilot import oai_utils

class Prompt(pydantic.BaseModel):
    messages: typing.List[typing.Dict[str,str]]
    
    def format(self, **kwargs) -> list:
        formatted_messages = [
            {
                "role": msg["role"],
                "content": msg["content"].format(**kwargs)
            } for msg in self.messages
        ]
        return formatted_messages
    
    def get_token_count(self, **kwargs):
        messages=self.format(**kwargs)
        return oai_utils.num_tokens_from_messages(messages)