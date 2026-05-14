@echo off
REM: Works only for Windows, for now
set TESTING_MODE=True
set FLASK_DEBUG=1
set PYTHONPATH=.
REM: Start Backend (Flask) server in new terminal:
start cmd /k ".venv\Scripts\activate.bat && python -m backend.my_react_app"
REM: Start Frontend (Vite) server in another new terminal:
npm run dev --prefix frontend