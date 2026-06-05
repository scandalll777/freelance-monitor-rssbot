@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo ========================================
echo  Установка Python
echo ========================================
echo.
echo Сейчас откроется официальный сайт Python:
echo https://www.python.org/downloads/
echo.
echo Что сделать на сайте:
echo 1. Нажмите Download Python (версия 3.10 или новее)
echo 2. Запустите скачанный .exe
echo 3. ВАЖНО: включите галочку "Add python.exe to PATH"
echo 4. Нажмите Install Now
echo.
echo После установки закройте это окно и запустите install.bat
echo.

start https://www.python.org/downloads/

pause
