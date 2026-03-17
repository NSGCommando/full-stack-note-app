@echo off
REM: Set environment variables for this session only
set TESTING_MODE=True
set FLASK_DEBUG=1
set PYTHONPATH=.

REM: Start Backend (Flask) server in a new terminal pointing to TEST DB
start cmd /k ".venv\Scripts\activate.bat && python -m backend.my_react_app"

echo Backend started in TEST MODE (test_db.db)
echo running tests

timeout /t 10

@echo off
REM: -v : set pytest verbosity, for individual test name and status
REM: -p : option for plugin(loading/disabling), adding no:plugin disables "plugin"
call .venv\Scripts\activate.bat && pytest -v -p no:logging testing/backend/test_API.py
pause