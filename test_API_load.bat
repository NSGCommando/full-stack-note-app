@echo off
REM: Set environment variables
set TESTING_MODE=True
set FLASK_DEBUG=1
set PYTHONPATH=.

REM: Start Backend (Flask) server in a new terminal
start cmd /k ".venv\Scripts\activate.bat && python -m backend.my_react_app"

echo [SYSTEM] Backend started in TEST MODE. Waiting for server to stabilize...
timeout /t 10

echo [SYSTEM] Starting Headless Load Test...

:: -u 10 : Total simulated users
:: -r 2  : Add 2 users every second until we hit 10
:: -t 1m : Run for 1 minute then stop
:: --host: specify the api url to locust
:: --csv : Save results to files
call .venv\Scripts\activate.bat && locust -f testing/backend/test_API_load.py --headless -u 10 -r 2 -t 1m --host http://127.0.0.1:5000 --csv=testing/backend/results/load_report

echo [SYSTEM] Load test finished. See testing/backend/results/ for CSV data.
pause