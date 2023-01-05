"""
    Autore : Cavallo Luigi
"""
import logging
from flask import abort, jsonify
from functools import wraps

################################################################
#                       CUSTOM lOGGER                          #
################################################################

def setup_logger(logger_name, log_file, level=logging.INFO):
    """
        Setup system logger
    """
    l = logging.getLogger(logger_name)
    formatter = logging.Formatter('%(asctime)s : %(message)s')
    fileHandler = logging.FileHandler(log_file, mode='w')
    fileHandler.setFormatter(formatter)
    l.setLevel(level)
    l.addHandler(fileHandler)


################################################################
#                   CUSTOM DECORATOR                           #
################################################################

def is_user_logged(session, logger=None):
    """
        Check if the user is logged.
    """
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            if not session.get("authenticated"):
                if logger:
                    logger.warning("[USER_NOT_AUTHENTICATED] no session was created")
                return abort(403)
            return f(*args, **kwargs)
        return wrapper
    return decorator

################################################################
#                ENUMERATION TOOL FILTER                       #
################################################################

def filter_enumeration_tools_by_user_agent(request_agent):
    """
        Watch each request filtering some enumeration tool by user-agent
    """
    tools: set = {
        "-"                             # Empty
        "Nmap Scripting Engine",        # Nmap
        "Nikto/",                       # Nikto
        "Windows NT 5.1",               # Dirb
        "DirBuster-",                   # Dirbuster
        "gobuster/",                    # Gobuster
        "WPScan",                       # WPscan
        "Hydra",                        # Hydra
        "feroxbuster/"                  # Feroxbuster
    }
    for t in tools:
        if request_agent.find(t) >= 0:
            return abort(418)
    