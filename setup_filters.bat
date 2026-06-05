@echo off
chcp 65001 >nul
cd /d "%~dp0"
title Настройка фильтров FL.ru

if not exist ".venv\Scripts\python.exe" (
    echo [ОШИБКА] Сначала установите зависимости:
    echo   python -m venv .venv
    echo   .venv\Scripts\pip install -r requirements.txt
    pause
    exit /b 1
)

call ".venv\Scripts\activate.bat"
python setup_filters.py
