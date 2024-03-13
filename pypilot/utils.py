def add_color(message, color):
    colors = {
        'red': '\033[91m',
        'green': '\033[92m',
        'yellow': '\033[93m',
        'blue': '\033[94m',
        'purple': '\033[95m',
        'cyan': '\033[96m',
        'orange': '\x1b[38;2;255;165;0m',
    }

    if color not in colors:
        raise ValueError("Invalid color specified. Available colors are: red, green, yellow, blue, purple, cyan")
    
    return f"{colors[color]}{message}\033[0m"
    
def print_color(message, color, end='\n'):
    print(add_color(message, color), end=end)

def run_system_command(command):
    """
    This function takes a command as input, runs it using subprocess, and return the output.

    Args:
    command (str): The command to be executed.

    Returns:
    str: The output of the command.
    """
    import subprocess
    result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode == 0:
        return result.stdout.decode('utf-8')
    else:
        return f"{result.stderr.decode('utf-8')}"

def run_system_command_and_stream_output(command):
    """
    This function takes a command as input, runs it using subprocess, and return the output.

    Args:
    command (str): The command to be executed.

    Returns:
    str: The output of the command.
    """
    import subprocess
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    
    for line in iter(process.stdout.readline, ""):
        if line == '' and process.poll() is not None:
            break
        if line is not None:
            print(line.strip())
            process.stdout.flush()
