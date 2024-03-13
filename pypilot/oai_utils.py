import asyncio
import time
from typing import List, Literal, Optional
import openai
import tiktoken

# def num_tokens_from_text(txt: str, model="gpt-3.5-turbo-0301") -> int:
#     try: 
#         encoding = tiktoken.encoding_for_model(model_name=model)
#     except KeyError as e:
#         encoding = tiktoken.get_encoding(encoding_name='cl100k_base')
#     num_tokens = 0
#     num_tokens += len(encoding.encode(txt))
#     return num_tokens

def num_tokens_from_messages(messages: List[dict], model="gpt-3.5-turbo-0301") -> int:
    try: 
        encoding = tiktoken.encoding_for_model(model_name=model)
    except KeyError as e:
        encoding = tiktoken.get_encoding(encoding_name='cl100k_base')
    num_tokens = 0
    for message in messages:
        num_tokens += 4  # every message follows <im_start>{role/name}\n{content}<im_end>\n
        for key, value in message.items():
            num_tokens += len(encoding.encode(value))
            if key == "name":  # if there's a name, the role is omitted
                num_tokens += -1  # role is always required and always 1 token
    num_tokens += 2  # every reply is primed with <im_start>assistant
    return num_tokens

    
async def amake_chat_completion(
    messages: List[dict],
    provider: Literal["azure", "openai"],
    model: str = None,
    api_key: Optional[str] = None,
    api_version: Optional[str] = None,    
    endpoint: Optional[str] = None,
    stream: bool = False,
    **model_kwargs
) -> str:
    """
    Sends a request to the ChatCompletion API to retrieve a response based on a list of previous messages.
    Returns a dictionary with assistant's response and usage statistics.
    """   

    kwargs = {}
    kwargs["model"] = model
    
    if provider=="openai":
        aclient = openai.AsyncOpenAI(api_key=api_key)
    elif provider=="azure":
        aclient = openai.AsyncAzureOpenAI(api_key=api_key, api_version=api_version, azure_endpoint=endpoint)
    else:
        raise ValueError("Provider must be either 'azure' or 'openai'")
    
    kwargs = {**kwargs, **model_kwargs}
    
    start_time = time.time()  
    response = await aclient.chat.completions.create(messages=messages,stream=stream,**kwargs)
    if stream:
        collected_chunks = []
        collected_messages = []
        async for chunk in response:
            collected_chunks.append(chunk)  # save the event response
            chunk_message = chunk.choices[0].delta.content  # extract the message
            collected_messages.append(chunk_message)  # save the message
        collected_messages = [m for m in collected_messages if m is not None]
        top_result = ''.join([m for m in collected_messages])
        duration = 0
        usage_stats = {}
    else:
        completion= response
        duration = round((time.time() - start_time) * 1000, 3)
        usage_stats = completion.usage.model_dump()
        top_result = completion.choices[0].message.content.strip()
    
    # Organize response and usage statistics in a single dictionary
    response = {
        "answer": {
            "role": "assistant",
            "content": top_result
        },
        "usage_statistics": usage_stats,
        "duration": duration
    }
    
    return response

def make_chat_completion(
        messages: List[dict],
    provider: Literal["azure", "openai"],
    model: str = None,
    api_key: Optional[str] = None,
    api_version: Optional[str] = None,    
    endpoint: Optional[str] = None,
    stream: bool = False,
    **model_kwargs
) -> str:
    """
    Sends a request to the ChatCompletion API to retrieve a response based on a list of previous messages.
    Returns a dictionary with assistant's response and usage statistics.
    """   

    kwargs = {}
    kwargs["model"] = model
    
    if provider=="openai":
        client = openai.OpenAI(api_key=api_key)
    elif provider=="azure":
        client = openai.AzureOpenAI(api_key=api_key, api_version=api_version, azure_endpoint=endpoint)
    elif provider=="llama":
        client = LLAMA()
    else:
        raise ValueError("Provider must be either 'azure', 'openai' or 'llama'")
    
    kwargs = {**kwargs, **model_kwargs}
    
    start_time = time.time()  
    if provider=="llama":
        response = client.create(messages=messages,**kwargs)
    else:
        response = client.chat.completions.create(messages=messages,**kwargs)

    completion= response
    duration = round((time.time() - start_time) * 1000, 3)
    usage_stats = completion.usage.model_dump()
    top_result = completion.choices[0].message.content.strip()
    
    # Organize response and usage statistics in a single dictionary
    response = {
        "answer": {
            "role": "assistant",
            "content": top_result
        },
        "usage_statistics": usage_stats,
        "duration": duration
    }
    
    return response

def stream_chat_completion( 
    messages: List[dict],
    provider: Literal["azure", "openai"],
    model: str = None,
    api_key: Optional[str] = None,
    api_version: Optional[str] = None,    
    endpoint: Optional[str] = None,
    **model_kwargs
) -> str:
    """
    Sends a request to the ChatCompletion API to retrieve a response based on a list of previous messages.
    Returns a dictionary with assistant's response and usage statistics.
    """   

    kwargs = {}
    kwargs["model"] = model
    
    if provider=="openai":
        client = openai.OpenAI(api_key=api_key)
    elif provider=="azure":
        client = openai.AzureOpenAI(api_key=api_key, api_version=api_version, azure_endpoint=endpoint)
    elif provider=="llama":
        client = LLAMA()
    else:
        raise ValueError("Provider must be either 'azure', 'openai' or 'llama'")
    
    kwargs = {**kwargs, **model_kwargs}
    
    if provider=="llama":
        response = client.create(messages=messages,stream=True,**kwargs)
    else:
        response = client.chat.completions.create(messages=messages,stream=True,**kwargs)
    for chunk in response:
        yield chunk.choices[0].delta.content
        
class LLAMA:
    def __init__(self):
        from llama_cpp import Llama
        self.llm = Llama.from_pretrained(
            repo_id="Qwen/Qwen1.5-0.5B-Chat-GGUF",
            filename="*q8_0.gguf",
            verbose=False
        )

        
    def create(self, messages: List[dict], stream=False, **kwargs):
        return self.llm.create_chat_completion_openai_v1(messages=messages, stream=stream, **kwargs)