@echo off
setlocal enabledelayedexpansion

cd %~dp0

REM Generate a random delay between 1 and 80 seconds (you can adjust the range)
set /a "delay=!random! %% 80 + 1"

echo Waiting for !delay! seconds... > last_job.log
timeout /t !delay! > nul

REM Add your further commands here

python.exe -m src.checkin >> last_job.log 2>&1