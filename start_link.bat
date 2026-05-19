@echo off
title Hardware Link
color 0B
echo =========================================
echo       Hardware Linker (Arduino - PC)
echo =========================================
echo.

cd /d "%~dp0backend"

echo [*] Installing required libraries...
"C:\Users\Peter.Net\anaconda3\python.exe" -m pip install pyserial requests >nul 2>&1

echo [*] Starting the bridge...
echo.
"C:\Users\Peter.Net\anaconda3\python.exe" link_hardware.py

pause
