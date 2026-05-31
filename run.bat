@echo off
setlocal enabledelayedexpansion

cd %~dp0

REM Generate a random delay between 1 and 80 seconds
set /a "delay=!random! %% 8 + 1"

set "LOGFILE=%~dp0last_job.log"

echo Waiting for !delay! seconds... > "%LOGFILE%"
timeout /t !delay! > nul

cd src
python.exe -m __init__ >> "%LOGFILE%" 2>&1
