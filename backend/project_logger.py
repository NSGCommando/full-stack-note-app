"""
project_logger.py

This module configures a backend-level logger factory 'get_project_logger'.
It writes logs to 'logs/moduleName.log' where 'moduleName' is the importing module
It also outputs to the console.
Usage:
    from app.project_logger import get_project_logger
    logger = get_project_logger(?Level=logging.[INFO|WARNING|ERROR])
    logger.info("Some message")
"""
import logging, os, inspect

# Start from this file's location
current_file = os.path.abspath(__file__)  # full path to this logger file
backend_dir = os.path.dirname(current_file)  # the folder containing this file

# Desired log folder inside backend
log_dir = os.path.join(backend_dir, "logs")

# Fallback: if somehow backend_dir doesn't exist, use cwd/logs
if not os.path.exists(backend_dir):
    log_dir = os.path.join(os.getcwd(), "logs")

# Ensure the folder exists
os.makedirs(log_dir, exist_ok=True)

def get_project_logger(level=logging.INFO):
    """
    Returns a logger that logs to both console and a file named after the caller module.
    Logging level default is INFO, pass logging.WARNING or other levels to change at call
    """
    # Determine the calling file name
    caller_file = inspect.stack()[1].filename
    module_name = os.path.splitext(os.path.basename(caller_file))[0]
    log_filename = module_name + ".log"
    log_path = os.path.join(log_dir,log_filename)

    # Create logger
    logger_name = f"logger_{module_name}"
    logger = logging.getLogger(logger_name)
    
    if not logger.hasHandlers():  # Prevent adding multiple handlers if imported multiple times
        logger.setLevel(level)
        
        # File handler
        file_handler = logging.FileHandler(log_path)
        file_formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(file_formatter)
        logger.addHandler(console_handler)

    return logger