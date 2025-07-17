'''
Helpers for the panel
interface
'''

import glob
import json


def read_history(loc="./chathistory/*.json"):
    """
    Read chat history files and extract summary information.
    
    Args:
        loc (str, optional): Glob pattern for history files. Defaults to "./chathistory/*.json".
        
    Returns:
        list: List of dictionaries with filename and summary pairs.
    """
    files = glob.glob(loc)
    fcont = []
    for f in files:
        with open(f, 'r') as fi:
            jl = json.load(fi)
            fcont.append({f.replace("./chathistory\\",""):jl['summary']})
    return fcont


def dropdown_history(loc="./chathistory/*.json"):
    """
    Create dropdown menu items from chat history files.
    
    Args:
        loc (str, optional): Glob pattern for history files. Defaults to "./chathistory/*.json".
        
    Returns:
        list: List of strings formatted as "filename: summary" for dropdown display.
    """
    hist_files = read_history(loc)
    dropdown = []
    for h in hist_files:
        file, summary = list(h.items())[0]
        dropdown.append(f'{file.replace(".json","")}: {summary}')
    return dropdown


def parse_dropdown(x):
    """
    Extract filename from dropdown selection string.
    
    Args:
        x (str): Dropdown selection string in format "filename: summary"
        
    Returns:
        str: Extracted filename without .json extension
    """
    file = x[:x.find(":")]
    return file.replace(".json","")

def load_history(file,chatbot,chatinterface,selectinterface):
    """
    Load chat history into interface components.
    
    Args:
        file (str): Filename of chat history to load
        chatbot: Chatbot instance to load history into
        chatinterface: Chat interface component to update
        selectinterface: Selection interface component to update
        
    Note:
        This is a placeholder function not yet implemented.
    """
    pass