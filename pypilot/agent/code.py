import functools

from pypilot.agent import base
from pypilot.parser import parser      
from pypilot.agent.prompt import Prompt
PROMPT = Prompt(messages=[
        {"role": "system", "content": """
You are a python coding assistant that exists inside a python console.
This is the console history of code that already executed:
{history}

This are the locals you have access to:
{locals}

Answer only with valid python code and nothing else, your answer should be python code that can run as is inside a python terminal.
Do not repeat unnecessary code that is already in the history.
Remember that expressions will not evaluate, if you want to print something to the user add print().
Always add docstrings to your code to explain what it does.
"""},
            {"role": "user", "content": "{instruction}"}
    ])

OUTPUT_PARSER = functools.partial(parser, starting_separators=["```python", "```"], ending_separators=["```"])

class PythonCodeAgent(base.AgentBase):
    output_parser = OUTPUT_PARSER
    prompt: Prompt = PROMPT