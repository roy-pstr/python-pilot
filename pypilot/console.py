import code
import io
import readline # This imports all key bindings for the terminal!
import sys
import contextlib

from pypilot import utils
from pypilot.parser import parser      
from pypilot.agent.base import AgentBase

class InteractiveConsoleWithHistory(code.InteractiveConsole):
    """
    Support history, all lines from terminal are appended to the history list, including errors.
    Also added support to inject a line of code to the terminal before the user input.

    """
    def __init__(self, history=None, inject_lines=None, **kwargs):
        
        super().__init__(**kwargs)
        self._history = history or []
        self.initial_lines = inject_lines
        self._init_state_locals = self.locals.copy()
        self._custom_commands = {}
        self._set_custom_commands({
                'reset': self.reset, 
                'clear': self.clear,  
                'history': self.history, 
                'ulocals': self.get_user_locals,
                'dump': self.dump
            }
        )
        
    def _set_custom_commands(self, cmds):
        self._custom_commands = self._custom_commands | cmds
        self.locals = self.locals | cmds

    def repr_custom_commands(self):
        cmds = list(self._custom_commands.keys())
        if len(cmds) == 0:
            return ''
        str = ", ".join([k+'()' for k in cmds[:-1]])
        return str + " or " + cmds[-1]+'()'
    
    def pop_injected_line(self):
        line = self.inject_first_line
        self.inject_first_line = None
        return line
    
    def reset_locals(self):
        self.locals = self._init_state_locals.copy()
    
    def get_user_locals(self):
        ignore_keys = ['__builtins__', '__doc__', '__name__']
        user_locals = {k:v for k,v in self.locals.items() if not k in ignore_keys}
        return user_locals
    
    def history(self, tail=None):
        if tail is None:
            return self._history
        return self._history[-tail:]
    
    def _inject_lines():
        pass
    
    def _start_interact(self, banner):
        try:
            sys.ps1
        except AttributeError:
            sys.ps1 = ">>> "
        try:
            sys.ps2
        except AttributeError:
            sys.ps2 = "... "
        cprt = 'Type "help", "copyright", "credits" or "license" for more information.'
        # if banner is None:
        self.write("Python %s on %s\n%s\n" %
                    (sys.version, sys.platform, cprt))
        # elif banner:
        if banner is not None:
            self.write("%s\n" % str(banner))
    
    def _end_interact(self, exitmsg):
        if exitmsg is None:
            self.write('now exiting %s...\n' % self.__class__.__name__)
        elif exitmsg != '':
            self.write('%s\n' % exitmsg)
    
    def _interact(self):
        """Closely emulate the interactive Python console.
        """
        more = 0
        while 1:
            try:
                if more:
                    prompt = sys.ps2
                else:
                    prompt = sys.ps1
                try:
                    line = self.raw_input(prompt)
                except EOFError:
                    self.write("\n")
                    break
                else:
                    self._history.append(line)
                    more = self.push(line)
            except KeyboardInterrupt:
                self.write("\nKeyboardInterrupt\n")
                self.resetbuffer()
                more = 0
            
    def interact(self, banner=None, exitmsg=None):
        """Closely emulate the interactive Python console.

        The optional banner argument specifies the banner to print
        before the first interaction; by default it prints a banner
        similar to the one printed by the real Python interpreter,
        followed by the current class name in parentheses (so as not
        to confuse this with the real interpreter -- since it's so
        close!).

        The optional exitmsg argument specifies the exit message
        printed when exiting. Pass the empty string to suppress
        printing an exit message. If exitmsg is not given or None,
        a default message is printed.

        """
        self._start_interact(banner)
        self._interact()
        self._end_interact(exitmsg)
    
    
    
    def runsource(self, source: str, filename: str = "<input>", symbol: str = "single") -> bool:
        """Same as the original runsource but with the addition of catching the syntax error and appending it to the history.
        """
        with io.StringIO() as redirected_stderr:
            with contextlib.redirect_stderr(redirected_stderr): # we use this to catch the syntax error that is written to the sys.stderr. see InteractiveConsole.write
                result = super().runsource(source, filename, symbol)

            if redirected_stderr.getvalue(): # if there is an error, write it (which will print it) and append it to the history
                self.write(redirected_stderr.getvalue())
                self._history.append(redirected_stderr.getvalue())
            
        return result

    def _execute_lines(self, lines):
        for line in lines:
            self.push(line)
    
    def clear(self):
        self._history = []
    
    def reset(self):
        self.clear() # clean history
        self.reset_locals() 
    
    def dump(self):
        import json
        with open('console-agent.txt', 'w') as f:
            json.dump(self.history(-1), f, indent=2) # dump all history without the dump() command itself
    
    def load(self, history_path: str):
        import json
        with open(history_path, 'r') as f:
            initial_history = json.load(f)  
            self._execute_lines(initial_history)
            self._history.extend(initial_history)
            
class InteractiveConsoleAgent(InteractiveConsoleWithHistory):
    def __init__(self, agent: AgentBase, auto_approve_llm_use=True, stream=True, token_count_limit=None, **kwargs):
        super().__init__(**kwargs)
        self.auto_approve_llm_use = auto_approve_llm_use
        self.stream = stream
        self.token_count_limit = token_count_limit
        self.agent = agent
        
        self._set_custom_commands({
                'set_api_key': self.set_api_key,
                'run_system_command': utils.run_system_command_and_stream_output
        })
                
    def _is_llm_line(self, line):
        return line.strip().startswith('#')
    
    def _is_system_command(self, line):
        return line.strip().startswith('!')
    
    def _read_line_from_llm(self):
        line, is_code = None, None
        
        last_line = self._history[-1]
        token_count = self.agent.get_token_count(instruction=last_line, history=self._history, locals=self.get_user_locals())
        if self.token_count_limit is not None and token_count > self.token_count_limit:
            utils.print_color(f"LLM[tokens:{token_count}] exceeds token count limit of {self.token_count_limit}, consider using 'clear()' to clear history", 'red')
        else:
            if not self.auto_approve_llm_use:
                input(utils.add_color(f"LLM[tokens:~{token_count}]?>", 'green')) # any key will approve, ctrl+c will cancel
            if self.stream:
                utils.print_color(f"LLM[tokens:~{token_count}]> ", 'cyan')
                line, is_code = self.stream_llm_input(instruction_line=last_line)
            else:
                line, is_code = self.llm_input(instruction_line=last_line)
                if line is not None:
                    utils.print_color(f"LLM[tokens:{token_count}]>\n```{line}\n```", 'cyan')
        
        if not is_code and line is not None: # convert the chat response to string expression so we can execute it later...
            line = f"'''{line}'''"
                
        return line, is_code
    
    def _read_line(self, more, llm):
        line = None
        is_code = False
        
        if more:
            prompt = sys.ps2
        else:
            prompt = sys.ps1
        if llm:
            line, is_code = self._read_line_from_llm() # if llm is true, we generate the next line from with the llm
            if line is None:
                llm = 0

        else:
            line = self.raw_input(prompt)
            
        return line, is_code
    
    def _interact(self):
        line = None
        
        more = 0
        llm = 0
        while 1:
            try:
                try:
                    line, is_code = self._read_line(more, llm)
                    if line is None:
                        llm = 0
                        continue
                    if is_code:
                        input(utils.add_color("EXECUTE?>",'green')) # any key will approve, ctrl+c will cancel
                    if self._is_system_command(line):
                        line = f"run_system_command('{line[1:]}')" # replace !pip install numpy -> print(run_system_command('pip install numpy'))
                        
                except EOFError:
                    self.write("\n")
                    break
                else:
                    self._history.append(line)
                    more = self.push(line, is_exec=llm)
                    llm = self._is_llm_line(line) and not llm # if the current line was generated by llm it cannot be a user instruction to a llm.
            except KeyboardInterrupt:
                self.write("\nKeyboardInterrupt\n")
                self.resetbuffer()
                more = 0
                llm = 0
                
    def llm_input(self, instruction_line):
        if instruction_line.strip().startswith('#'):
            instruction_line = instruction_line.strip()[1:]
        selection = self.agent.select(instruction=instruction_line, history=self.history(3))
        generated_code = self.agent.generate(next_agent=selection, instruction=instruction_line, history=self._history, locals=self.get_user_locals())
        return generated_code, selection=="PythonCodeAgent"

    def stream_llm_input(self, instruction_line):
        if instruction_line.strip().startswith('#'):
            instruction_line = instruction_line.strip()[1:] 
        
        answer = ''
        selection = self.agent.select(instruction=instruction_line, history=self.history(3))
        # print(f"Selected agent: {selection}")
        first_chunk = False
        for chunk in self.agent.stream(next_agent=selection, instruction=instruction_line, history=self._history, locals=self.get_user_locals()):
            if chunk is not None:
                if chunk=='\n' and not first_chunk:
                    continue
                if not first_chunk:
                    first_chunk = True
                utils.print_color(chunk, 'cyan', end="")
                answer += chunk
                    
        print()
        parsed_answer = parser(answer, starting_separators=["```python", "```"], ending_separators=["```"])
        return parsed_answer, selection=="PythonCodeAgent"
        
    def push(self, line, is_exec=False):
        """Push a line to the interpreter.

        The line should not have a trailing newline; it may have
        internal newlines.  The line is appended to a buffer and the
        interpreter's runsource() method is called with the
        concatenated contents of the buffer as source.  If this
        indicates that the command was executed or invalid, the buffer
        is reset; otherwise, the command is incomplete, and the buffer
        is left as it was after the line was appended.  The return
        value is 1 if more input is required, 0 if the line was dealt
        with in some way (this is the same as runsource()).

        """
        self.buffer.append(line)
        source = "\n".join(self.buffer)
        symbol="single" if not is_exec else "exec" # single is the original behavior, exec is the behavior we want when we are executing llm generated code.
        more = self.runsource(source, self.filename, symbol=symbol)
        if not more:
            self.resetbuffer()
        return more
    
    def set_api_key(self, api_key):
        self.agent.update_api_key(api_key)

