# PyPilot
A python terminal with an AI assistant.</br>
Use it as a regular python terminal and whenever you need the copilot assistance just write it as a comment.</br>
Don't forget to set the API KEY (supports only OPENAI for now).
# Demo
<img src="./assets/demo.gif" />

## Features
- Code generation inside the python terminal.
- Your comments are used to communicate with the assistant.
- The assistant is aware of the terminal history and locals.
- Supports system commands from within the terminal (e.g. !pip install <package_name>).
- Supports all OpenAI models.

## Installation
```bash
$ pip install python-pilot
```

## Usage
```bash
$ pypilot --api-key sk-....
```
or
```bash
$ export OPENAI_API_KEY=sk-... 
$ pypilot
```

# TODO
- add a way to use history only with headers of functions...
- docker containers
- add a selector step that decide what context the next llm prompt should have:
    - history: code executed (w/wo expressions), errors, llm requests
    - locals: vars, functions, modules
 (full terminal history, locals only) and if the output should be code or chat
- add support in llm config file