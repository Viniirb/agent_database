@echo off
echo ========================================
echo   Iniciando Backend Server
echo ========================================
echo.

cd /d "%~dp0"

echo Ativando ambiente virtual...
call venv\Scripts\activate.bat

echo.
echo Iniciando servidor FastAPI...
echo Acesse: http://localhost:8000
echo Documentacao: http://localhost:8000/docs
echo.

uvicorn main:app --reload --host 0.0.0.0 --port 8000 --log-config logging.ini