@echo off
chcp 65001 >nul
cd /d "%~dp0"

title Сброс базы мониторинга

if not exist ".venv\Scripts\python.exe" (
    echo [ОШИБКА] Не найдено виртуальное окружение .venv
    pause
    exit /b 1
)

if exist "data\projects.db" (
    del /f "data\projects.db"
    echo Старая база удалена.
) else (
    echo База ещё не создана — будет создана заново.
)

echo.
echo Заполняю базу текущими проектами по фильтрам из config.yaml
echo (без уведомлений в Telegram)...
echo.

call ".venv\Scripts\activate.bat"
set INITIAL_SEED=true
python main.py --once

echo.
echo Готово. В базе сохранены ID текущих заказов.
echo Новые заказы будут приходить только при появлении на площадках.
echo Запуск мониторинга: двойной клик по start_bot.bat
pause
