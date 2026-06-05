@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo Установка Freelance Monitor Bot...
echo.

python --version >nul 2>&1
if errorlevel 1 (
    echo [ОШИБКА] Python не найден.
    echo.
    echo Установите Python одним из способов:
    echo   1. Двойной клик по install_python.bat ^(откроется python.org^)
    echo   2. Сайт: https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

if not exist ".venv\Scripts\python.exe" (
    echo Создание виртуального окружения...
    python -m venv .venv
)

call .venv\Scripts\activate.bat
pip install -r requirements.txt

if not exist ".env" (
    copy .env.example .env
    echo Создан файл .env — укажите токен бота и chat_id.
)

if not exist "config.yaml" (
    copy config.example.yaml config.yaml
    echo Создан файл config.yaml — настройте фильтры.
)

echo.
echo.
echo ========================================
echo  Готово!
echo  Дальше откройте INSTRUCTION.md
echo  (шаги 4-7: токен, Chat ID, файл .env)
echo  Затем запустите start_bot.bat
echo ========================================
pause
