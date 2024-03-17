# PyPilot
A python terminal with a coding copilot inside.</br>
This is a regular python terminal, only that your comments are used as requests queries for the copilot.</br>
Don't forget to set the API KEY (supports only OPENAI for now).

## Demo
<img src="./assets/demo.gif" />

## Features
- Code generation inside the python terminal.
- Your comments are used to communicate with the copilot.
- The copilot is aware of the terminal history and locals.
- Both code and chat responses are supported.
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