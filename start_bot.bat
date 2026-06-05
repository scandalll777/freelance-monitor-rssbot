@echo off
chcp 65001 >nul
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
    echo [ОШИБКА] Сначала запустите install.bat
    pause
    exit /b 1
)

if not exist ".env" (
    echo [ОШИБКА] Нет файла .env — запустите install.bat
    pause
    exit /b 1
)

call .venv\Scripts\activate.bat
python main.py

pause
