@echo off
setlocal

py Main.py

if errorlevel 1 (
    echo.
    echo Media Tagger exited with an error.
    pause
)
