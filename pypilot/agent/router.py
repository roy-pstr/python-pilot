from pypilot.agent import base
from pypilot.parser import json_parser      
from pypilot.agent.prompt import Prompt
PROMPT = Prompt(messages=[
        {"role": "system", "content": """
Given a user request inside a python terminal, select the best suited agent to handle the request. 

Answer with a markdown code snippet with a JSON object formatted to look like:
```json
{{
    "thought": explain your thought process of selecting the agent,
    "agent": name of the agent,
}}
```

Agents:
- PythonCodeAgent: A python coding assistant that writes python code.
- ChatAgent: A chatbot that engage in a conversation mostly about coding and python.

Here is the python terminal recent history:
{history}

Always prefer the PythonCodeAgent. Use ChatAgent only when the user request can not be solved with code.

"""},
            {"role": "user", "content": "{instruction}"}
    ])

OUTPUT_PARSER = json_parser

class RouterAgent(base.AgentBase):
    output_parser = OUTPUT_PARSER
    prompt: Prompt = PROMPT