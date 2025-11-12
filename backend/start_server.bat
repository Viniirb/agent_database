@echo off
echo ========================================
echo   Iniciando Backend Server
echo ========================================
echo.

cd /d "%~dp0"

REM Verificar se Docker está rodando
echo Verificando Docker...
docker ps >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [AVISO] Docker nao esta rodando. Dragonfly cache nao sera iniciado.
    echo         O backend usara cache em memoria.
    echo.
    goto :skip_dragonfly
)

REM Iniciar Dragonfly
echo Iniciando Dragonfly cache...
docker-compose up -d >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo [OK] Dragonfly cache iniciado com sucesso!
    echo.
) else (
    echo [AVISO] Nao foi possivel iniciar Dragonfly.
    echo         O backend usara cache em memoria.
    echo.
)

:skip_dragonfly
echo Ativando ambiente virtual...
call venvback\Scripts\activate.bat

echo.
echo Iniciando servidor FastAPI...
echo Acesse: http://localhost:8000
echo Documentacao: http://localhost:8000/docs
echo.

uvicorn main:app --reload --host 0.0.0.0 --port 8000 --log-config logging.ini