import os
import typing

from pypilot.agent.prompt import Prompt
from pypilot.agent import base
from pypilot.agent.chat import ConversationalAgent
from pypilot.agent.code import PythonCodeAgent
from pypilot.agent.router import RouterAgent

class PythonTerminalChatAgent(base.AgentBase):
    
    prompt: typing.Optional[Prompt] = None
    auto_select_code: bool = False
    _router: RouterAgent
    _code: PythonCodeAgent
    _chat: ConversationalAgent
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._router: RouterAgent = RouterAgent(provider=self.provider, model=self.model, api_key=self.api_key)
        self._code: PythonCodeAgent = PythonCodeAgent(provider=self.provider, model=self.model, api_key=self.api_key)
        self._chat: ConversationalAgent = ConversationalAgent(provider=self.provider, model=self.model, api_key=self.api_key)
    
    def update_api_key(self, api_key: str):
        self.api_key = api_key
        self._router.api_key = api_key
        self._code.api_key = api_key
        self._chat.api_key = api_key
    
    def get_token_count(self, **kwargs):
        if self.auto_select_code:
            return self._code.get_token_count(**kwargs)
        router_tokens = self._router.get_token_count(**kwargs)
        code_tokens = self._code.get_token_count(**kwargs)
        chat_tokens = self._chat.get_token_count(**kwargs)
        return router_tokens + (code_tokens + chat_tokens)//2
    
    def generate(self, next_agent=None, **kwargs) -> str:
        
            
        if next_agent is None:
            next_agent = self.select(**kwargs)
        if next_agent == "PythonCodeAgent":
            return self._code.generate(**kwargs)
        elif next_agent == "ChatAgent":
            return self._chat.generate(**kwargs)
        else:
            raise ValueError(f"Unknown agent {next_agent}")
    
    def select(self, **kwargs) -> str:
        if self.auto_select_code:
            return "PythonCodeAgent"
        selection = self._router.generate(**kwargs)
        next_agent = selection.get("agent")
        return next_agent
    
    def stream(self, next_agent=None, **kwargs) -> str:

        if next_agent is None:
            next_agent = self.select(**kwargs)
            
        if next_agent == "PythonCodeAgent":
            return self._code.stream(**kwargs)
        elif next_agent == "ChatAgent":
            return self._chat.stream(**kwargs)
        else:
            raise ValueError(f"Unknown agent {next_agent}")