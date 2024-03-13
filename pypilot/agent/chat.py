from pypilot.agent import base
from pypilot.agent.prompt import Prompt
PROMPT = Prompt(messages=[
        {"role": "system", "content": """
You are a chatbot interface for a python terminal. You are a python expert and can answer any question related to python.
Be concise and clear in your answers.

This is the console history of code that already executed:
{history}

This are the locals you have access to:
{locals}
"""},
            {"role": "user", "content": "{instruction}"}
    ])

class ConversationalAgent(base.AgentBase):
    prompt: Prompt = PROMPT