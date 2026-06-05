@echo off
chcp 65001 >nul
cd /d "%~dp0"

set "ZIP=FreelanceMonitor-bot.zip"
set "STAGE=%TEMP%\FreelanceMonitor-bot-package"

echo Создание архива для распространения...
echo В архив не попадут .env, config.yaml, .venv, data, база и установщики Python.
echo.

powershell -NoProfile -ExecutionPolicy Bypass -Command ^
  "$ErrorActionPreference = 'Stop';" ^
  "$root = (Get-Location).Path;" ^
  "$stage = $env:STAGE;" ^
  "$zip = Join-Path $root $env:ZIP;" ^
  "if (Test-Path $stage) { Remove-Item $stage -Recurse -Force };" ^
  "New-Item -ItemType Directory -Path $stage | Out-Null;" ^
  "$items = @('app','install.bat','install_python.bat','start_bot.bat','setup_filters.bat','reset_database.bat','make_archive.bat','main.py','check_connection.py','setup_filters.py','config.example.yaml','requirements.txt','.env.example','.gitignore','README.md','INSTRUCTION.md');" ^
  "foreach ($item in $items) { Copy-Item -LiteralPath (Join-Path $root $item) -Destination $stage -Recurse -Force };" ^
  "Get-ChildItem -LiteralPath $stage -Recurse -Directory -Filter '__pycache__' | Remove-Item -Recurse -Force;" ^
  "Get-ChildItem -LiteralPath $stage -Recurse -File | Where-Object { $_.Extension -in @('.pyc','.pyo','.db','.exe') } | Remove-Item -Force;" ^
  "if (Test-Path $zip) { Remove-Item $zip -Force };" ^
  "$archiveItems = Get-ChildItem -LiteralPath $stage -Force;" ^
  "Compress-Archive -LiteralPath $archiveItems.FullName -DestinationPath $zip -Force;" ^
  "Remove-Item $stage -Recurse -Force;" ^
  "$sizeKb = [math]::Round((Get-Item $zip).Length / 1KB, 1);" ^
  "Write-Host ('Готово: {0}' -f $zip);" ^
  "Write-Host ('Размер: {0} КБ' -f $sizeKb);"

if errorlevel 1 (
    echo.
    echo [ОШИБКА] Не удалось создать архив.
    pause
    exit /b 1
)

echo.
echo ========================================
echo  Архив готов: %CD%\%ZIP%
echo  Инструкция: INSTRUCTION.md
echo ========================================
pause
