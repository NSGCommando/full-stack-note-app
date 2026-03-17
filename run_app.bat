@echo off
REM: Works only for Windows, for now
REM: Start Backend (Flask) server in new terminal:
start cmd /k ".venv\Scripts\activate.bat && python -m backend.my_react_app"
REM: Start Frontend (Vite) server this terminal:
npm run dev --prefix frontend