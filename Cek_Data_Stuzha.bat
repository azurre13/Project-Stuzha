@echo off
title Periksa data Stuzha v4
if "%~1"=="" (
  echo Seret CSV hasil downloader baru ke file BAT ini.
  pause
  exit /b 2
)
python "%~dp0Program\analyze_session.py" "%~1" --require-v4
pause
