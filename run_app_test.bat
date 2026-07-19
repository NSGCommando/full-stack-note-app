@echo off
REM: Works only for Windows, for now
set TESTING_MODE=1
set FLASK_DEBUG=1
set PYTHONPATH=.
REM: Start Backend (Flask) server in new terminal:
start cmd /k ".venv\Scripts\activate.bat && python -m backend.my_react_app"

echo [SYSTEM] Backend started in TEST MODE. Waiting for server to stabilize...
timeout /t 10

REM: Start Frontend (Vite) server in another new terminal:
npm run dev --prefix frontend