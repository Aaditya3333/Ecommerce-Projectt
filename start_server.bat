@echo off
echo Starting Django development server with HTTPS error suppression...
echo.
echo Server will start at: http://127.0.0.1:8000/
echo Press Ctrl+C to stop the server
echo.

call venv\Scripts\activate
python manage.py runserver --noreload --verbosity=0 2>nul

echo.
echo Server stopped.
pause
