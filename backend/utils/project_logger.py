"""
project_logger.py

This module configures a backend-level logger factory 'get_project_logger'.
It writes logs to 'logs/moduleName.log' where 'moduleName' is the importing module.
It also outputs to the console.
Usage:
    from app.project_logger import get_project_logger
    logger = get_project_logger(?Level=logging.[INFO|WARNING|ERROR])
    logger.info("Some message")
"""
import logging
from pathlib import Path
from backend.utils.backend_functions import get_caller_filename

# Start from this file's location
current_file = Path(__file__).resolve()  # full path to this logger file
backend_dir = current_file.parents[1]  # the folder containing this file's folder

def get_project_logger(level:int=logging.INFO,log_dir:Path|None=None, stack_level:int=2)->logging.Logger:
    """
    Returns a logger that logs to both console and a file named after the caller module.
    {stack_level} argument can be overriden to manually set depth for returned module.
    Logging level default is INFO, pass logging.WARNING or other levels to change at call.
    Log folder directory default is /backend/, can be overriden by caller.
    """
    # Determine calling fn's filename
    caller_file = get_caller_filename(stack_level).get("caller_filename") # get the file name that called the logger
    if caller_file is None:
        raise RuntimeError(f"Cannot determine module Name for get_project_logger from {__file__}.")
    module_name = Path(caller_file).stem
    # Determine log file save location
    if log_dir is not None and not isinstance(log_dir,Path): # check for type-safety of the path override
        raise RuntimeError(f"'log_dir' must be a 'Path' object if passed as an argument.")
    log_dir = backend_dir/"logs" if log_dir is None else log_dir/"logs"
    log_dir.mkdir(parents=True, exist_ok=True)  # Ensure the folder exists
    log_filename = f"{module_name}.log"
    log_path = log_dir/log_filename

    # Create logger
    logger_name = f"logger_{module_name}"
    logger = logging.getLogger(logger_name)
    
    if not logger.hasHandlers():  # Prevent adding multiple handlers if imported multiple times
        logger.setLevel(level)
        logger.propagate = False
        
        # File handler
        file_handler = logging.FileHandler(log_path)
        # set formatter with autofill default variables
        file_formatter = logging.Formatter("%(asctime)s [%(levelname)s] [%(module)s] %(message)s")
        file_handler.setFormatter(file_formatter)
        file_handler.setLevel(level)
        logger.addHandler(file_handler)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_formatter = logging.Formatter("[%(levelname)s] [%(module)s] %(message)s")
        console_handler.setFormatter(console_formatter)
        console_handler.setLevel(level)
        logger.addHandler(console_handler)
    return logger