@echo off
:: Цей скрипт устанавливает зависимости из файла requirements.txt
pip install -r requirements.txt
if %ERRORLEVEL% NEQ 0 (
  echo Installation failed.
  exit /b %ERRORLEVEL%
)
echo Dependencies installed successfully.
