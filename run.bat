@echo off
cd /d "%~dp0"
echo Starting Life Insurance CRM...
echo Open http://localhost:8000 in your browser
echo.
python -m uvicorn backend.main:app --reload --port 8000
