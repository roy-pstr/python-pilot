
from typing import List


def parser(text: str, starting_separators: List[str], ending_separators: List[str]) -> str:
    """
    Extract the text from within the starting and ending separators.
    Starting and ending separators are lists of strings which are possible values for separators sorted by priority.
    This is a greedy parser and it will use the first separator it finds.
    
    Returns the text between the separators.
    """
    _end_index=None
    
    # find start index
    _start_index = 0
    for sep in starting_separators:
        if text.find(sep) != -1:
            _start_index = text.find(sep) + len(sep)
            break
    temp = text[_start_index:]
    
    # find last index
    for sep in ending_separators:
        if temp.rfind(sep) != -1:
            _end_index = temp.rfind(sep)
            break
    result = temp[:_end_index]
    return result

import re
import json

def fix_trailing_commas(json_string):
    # Use regular expression to remove trailing commas
    fixed_json = re.sub(r',(\s*[\]}])', r'\1', json_string) # TODO: write test for this regex!!!!
    return fixed_json

def json_parser(output: str) -> dict:
    output = parser(output,['```json','```'],['```'])
    try:                
        parsed_output = json.loads(output)
    except json.decoder.JSONDecodeError as e:
        try:
            # Try to solve the trailing comma issue
            output = fix_trailing_commas(output) 
            parsed_output = json.loads(output)
        except json.decoder.JSONDecodeError as e:
            print(output)
            raise e
    
    return parsed_output